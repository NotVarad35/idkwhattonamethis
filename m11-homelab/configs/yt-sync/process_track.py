#!/usr/bin/env python3
"""process_track.py - tag, name, route and publish tracks that yt-sync.sh downloaded.

Input : a staging directory holding, per video, <id>.<m4a|opus> + <id>.info.json
        + <id>.jpg (written by yt-dlp).
Output: tagged audio flat in MUSIC_DIR/<PLAYLIST_SUBDIR>/, named
        "{song} - {artist} [{video id}].{ext}", synced lyrics (embedded, or a
        .lrc sidecar logged in SQLite), and new entries at the TOP of
        MUSIC_DIR/<PLAYLIST_SUBDIR>.m3u.

Anything that fails stays in staging and is retried on the next run.
Only third-party dependency: mutagen (pip install mutagen).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import sqlite3
import struct
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from mutagen.flac import Picture
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggopus import OggOpus

# --------------------------------------------------------------------------- #
# Tunables
# --------------------------------------------------------------------------- #
VARIOUS_DIR = "Various Artists"
# Descriptor labels that send a track to Various Artists/ (no compromises).
VARIOUS_LABELS = {"MV", "Live", "Cover", "THE FIRST TAKE"}
MIN_SQUARE_ART_PX = 500        # a "high-res" 1:1 thumbnail is at least this wide
LRCLIB = "https://lrclib.net/api"
LRCLIB_DURATION_TOLERANCE = 6  # seconds; MVs often carry a long intro
HTTP_TIMEOUT = 15
MAX_FILENAME_BYTES = 240       # Android/exFAT limit is 255 *bytes*; kana = 3 bytes each
USER_AGENT = "yt-sync/1.0 (personal homelab script)"
SUPPORTED_EXT = {".m4a", ".opus"}
REMUX_TO_OPUS_EXT = {".webm", ".ogg", ".weba"}

# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #

def log(msg: str) -> None:
    print(msg, flush=True)


def norm_key(s: str) -> str:
    """Case/width/punctuation-insensitive key used for alias matching."""
    s = unicodedata.normalize("NFKC", s).casefold()
    return "".join(ch for ch in s if ch.isalnum())


_WIN_BAD = {"/": "／", "\\": "＼", ":": "：", "*": "＊", "?": "？", '"': "＂",
            "<": "＜", ">": "＞", "|": "｜"}


def safe_name(s: str) -> str:
    """Make a string safe as a single path component on FAT/exFAT/Android."""
    s = "".join(_WIN_BAD.get(ch, ch) for ch in s)
    s = "".join(ch for ch in s if ch >= " " and ch != "\x7f")
    s = re.sub(r"\s+", " ", s).strip().rstrip(". ")
    return s or "_"


# --------------------------------------------------------------------------- #
# artist_map.json
# --------------------------------------------------------------------------- #
class ArtistMap:
    def __init__(self, path: Path) -> None:
        self.canon_by_key: dict[str, str] = {}
        self.variants_by_canon: dict[str, list[str]] = {}
        self.overrides: dict[str, dict] = {}
        if not path.exists():
            log(f"[warn] artist map not found: {path} (continuing with no mappings)")
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        for canon, aliases in (data.get("artists") or {}).items():
            if canon.startswith("_"):
                continue
            names = [canon] + list(aliases or [])
            self.variants_by_canon[canon] = names
            for n in names:
                self.canon_by_key.setdefault(norm_key(n), canon)
        self.overrides = {k: v for k, v in (data.get("overrides") or {}).items()
                          if not k.startswith("_")}

    def has(self, name: str) -> bool:
        return norm_key(clean_channel(name)) in self.canon_by_key or norm_key(name) in self.canon_by_key

    def canonical(self, name: str) -> tuple[str, bool]:
        """Return (canonical name, was_mapped)."""
        for cand in (name, clean_channel(name)):
            hit = self.canon_by_key.get(norm_key(cand))
            if hit:
                return hit, True
        return clean_channel(name).strip() or name.strip(), False

    def variants(self, canon: str) -> list[str]:
        return self.variants_by_canon.get(canon, [canon])


_CHANNEL_NOISE = re.compile(
    r"\s*(?:[-–]\s*Topic|Official(?:\s*YouTube)?(?:\s*Channel)?|VEVO|公式チャンネル|公式)\s*$",
    re.I)


def clean_channel(name: str) -> str:
    prev = None
    while prev != name:
        prev = name
        name = _CHANNEL_NOISE.sub("", name).strip()
    return name


# --------------------------------------------------------------------------- #
# Title parsing: song / artist / version descriptors
# --------------------------------------------------------------------------- #
_BRACKET_RE = re.compile(r"【[^】]*】|\[[^\]]*\]|\([^)]*\)|（[^）]*）|〈[^〉]*〉|《[^》]*》|<[^>]*>")
_SEP_RE = re.compile(r"(\s+[-–—―~]\s+|\s+[/／|｜]\s+|\s*[｜／]\s*)")
_TRAIL_RE = re.compile(
    r"\s+(?:official\s+)?(?:music\s+video|video\s+clip|lyrics?\s+video|m\s*/\s*v|mv|"
    r"video|audio)\s*$", re.I)
_COVER_TAIL_RE = re.compile(r"\s*(?:covered?\s*by|(?<![a-z])cover(?![a-z])|歌ってみた|弾いてみた|叩いてみた).*$", re.I)
_QUOTED_RE = re.compile(r"^(?P<artist>.*?)\s*[「『](?P<song>[^」』]+)[」』]")

_LABEL_RULES: list[tuple[str, re.Pattern]] = [
    ("THE FIRST TAKE", re.compile(r"the\s*first\s*take", re.I)),
    ("Lyric Video", re.compile(r"lyrics?\s+video|リリックビデオ|歌詞付き?", re.I)),
    ("MV", re.compile(r"(?<![a-z])(?:official\s+(?:music\s+)?video|(?:official\s+)?music\s+video|"
                      r"video\s+clip|m\s*/\s*v|mv|pv)(?![a-z])|ミュージックビデオ", re.I)),
    ("Live", re.compile(r"(?<![a-z])live(?![a-z])|ライブ|ライヴ", re.I)),
    ("Cover", re.compile(r"(?<![a-z])cover(?:ed)?(?:\s+by)?(?![a-z])|歌ってみた|カバー|弾いてみた|叩いてみた", re.I)),
    ("Acoustic", re.compile(r"(?<![a-z])acoustic(?![a-z])|アコースティック", re.I)),
]
_NOISE_RE = re.compile(
    r"official|audio|\bhd\b|\b4k\b|full|ver\.?|version|video|channel|music|performance|"
    r"session|\bby\b|\bat\b|公式|オフィシャル|フル", re.I)


def split_descriptor(text: str) -> tuple[list[str], str]:
    """Return (labels found, residual alnum text once labels and noise words are removed)."""
    labels: list[str] = []
    rest = text
    for label, rx in _LABEL_RULES:
        if rx.search(rest):
            labels.append(label)
            rest = rx.sub(" ", rest)
    rest = _NOISE_RE.sub(" ", rest)
    return labels, "".join(ch for ch in rest if ch.isalnum())


class Parsed:
    def __init__(self) -> None:
        self.song = ""
        self.artist: str | None = None
        self.labels: list[str] = []   # descriptors to append to the title as [Label]
        self.flags: set[str] = set()  # labels seen anywhere (routing only)

    def add(self, labels: list[str], *, append: bool) -> None:
        for lb in labels:
            self.flags.add(lb)
            if append and lb not in self.labels:
                self.labels.append(lb)


def parse_title(title: str, alias_hit) -> Parsed:
    """alias_hit(name) -> bool tells whether a string is a known artist/alias."""
    out = Parsed()
    s = title

    # 1) bracket groups made only of descriptors/noise are removed; others are kept
    def _bracket(m: re.Match) -> str:
        inner = m.group(0)[1:-1]
        labels, residual = split_descriptor(inner)
        if residual:                       # real content, e.g. "(feat. X)" or "(Live at Budokan)"
            out.add(labels, append=False)
            return m.group(0)
        out.add(labels, append=True)
        return " "
    s = _BRACKET_RE.sub(_bracket, s)

    # 2) "Main | alt title / romaji": keep the first segment, mine the rest for labels
    parts_pipe = re.split(r"\s*[|｜]\s*", s)
    s = parts_pipe[0]
    for extra in parts_pipe[1:]:
        out.add(split_descriptor(extra)[0], append=True)

    # 3) drop separator-delimited parts that are pure descriptors ("/ THE FIRST TAKE")
    toks = _SEP_RE.split(s)
    kept: list[tuple[str, str]] = []       # (text, separator before it)
    seps = toks[1::2]
    for i, text in enumerate(toks[0::2]):
        sep = seps[i - 1] if i > 0 else ""
        labels, residual = split_descriptor(text)
        if text.strip() and not residual:  # pure descriptor/noise part: drop it and its separator
            out.add(labels, append=True)
            continue
        text = text.strip()
        m = _COVER_TAIL_RE.search(text)    # "... covered by X" / "Cover by X" / "歌ってみた ver.X"
        if m:
            out.add(["Cover"], append=True)
            text = text[:m.start()].rstrip(" -–—/／")
        while True:                        # trailing "Official Music Video" / "MV"
            m = _TRAIL_RE.search(text)
            if not m:
                break
            out.add(split_descriptor(m.group(0))[0], append=True)
            text = text[:m.start()].rstrip()
        if text:
            kept.append((text, sep if kept else ""))
    if not kept:
        out.song = title.strip()
        return out
    s = kept[0][0]
    for text, sep in kept[1:]:
        s += sep + text
    s = re.sub(r"\s+", " ", s).strip()

    # 4) Artist「Song」
    q = _QUOTED_RE.match(s)
    if q:
        out.song = q.group("song").strip()
        art = q.group("artist").strip(" -–—:：")
        out.artist = art or None
        return out

    # 5) "Artist - Song" / "Song / Artist"
    if len(kept) >= 2:
        a = kept[0][0]
        b = kept[1][0]
        for text, sep in kept[2:]:
            b += sep + text
        sep_kind = kept[1][1].strip()
        slash = sep_kind in {"/", "／"}
        first_is_artist = not slash       # "-" => Artist - Song ; "/" => Song / Artist
        a_known, b_known = alias_hit(a), alias_hit(b)
        if a_known and not b_known:
            first_is_artist = True
        elif b_known and not a_known:
            first_is_artist = False
        out.artist, out.song = (a, b) if first_is_artist else (b, a)
        return out

    out.song = s
    return out


# --------------------------------------------------------------------------- #
# Per-track decision: metadata + route + filename
# --------------------------------------------------------------------------- #
class Plan:
    pass


def decide(info: dict, amap: ArtistMap) -> Plan:
    vid = info["id"]
    channel = (info.get("channel") or info.get("uploader") or "").strip()
    chan_clean = clean_channel(channel)

    p = parse_title(info.get("title") or vid, amap.has)
    flags = set(p.flags)
    if norm_key(chan_clean) == norm_key("THE FIRST TAKE"):
        flags.add("THE FIRST TAKE")
        if "THE FIRST TAKE" not in p.labels:
            p.labels.append("THE FIRST TAKE")
    is_cover = "Cover" in flags

    # song / artist: YouTube's own music metadata beats title parsing
    song = (info.get("track") or p.song or info.get("title") or vid).strip()
    meta_artist = None
    arts = info.get("artists")
    if isinstance(arts, list) and arts:
        meta_artist = str(arts[0]).strip()
    elif info.get("artist"):
        meta_artist = str(info["artist"]).split(",")[0].strip()
    parsed_artist = meta_artist or p.artist or chan_clean
    # "YOASOBI · Ayase" (YouTube Music style multi-artist credit): primary artist only
    parsed_artist = re.split(r"\s*·\s*", parsed_artist)[0].strip() or parsed_artist

    mapped = True
    original_artist = None
    if is_cover:
        original_artist = parsed_artist if parsed_artist and norm_key(parsed_artist) != norm_key(chan_clean) else None
        artist, mapped = amap.canonical(chan_clean or channel)      # covers: channel name
    else:
        artist, mapped = amap.canonical(parsed_artist)
    if not artist:
        artist, mapped = "Unknown Artist", False

    # version descriptors stay in the title (skip ones the song text already carries)
    title = song
    for lb in p.labels:
        if lb.casefold() not in title.casefold():
            title += f" [{lb}]"

    route = "various" if (flags & VARIOUS_LABELS) else "official"

    ov = amap.overrides.get(vid) or {}
    artist = ov.get("artist", artist)
    title = ov.get("title", title)
    original_artist = ov.get("original_artist", original_artist)
    route = {"official": "official", "various": "various"}.get(ov.get("route", route), route)
    if "artist" in ov:
        artist, mapped = amap.canonical(artist)[0] if amap.has(artist) else artist, True

    plan = Plan()
    plan.video_id = vid
    plan.song = song
    plan.title = title
    # Every track is its own single: this keeps each track's cover art distinct
    # in Navidrome, and also follows per-video title overrides.
    plan.album = title
    plan.artist = artist
    plan.original_artist = original_artist
    plan.channel = channel
    plan.route = route
    plan.is_cover = is_cover
    plan.mapped = mapped
    plan.duration = int(info.get("duration") or 0)
    year = info.get("release_year") or (info.get("upload_date") or "")[:4]
    plan.year = str(year) if year else ""
    plan.url = info.get("webpage_url") or f"https://www.youtube.com/watch?v={vid}"
    return plan


def build_dest(music_dir: Path, playlist_subdir: str, plan: Plan, ext: str) -> Path:
    """All playlist tracks go flat into one playlist folder (no artist split)."""
    folder = safe_name(playlist_subdir or "ytsync")
    stem_tail = f" - {safe_name(plan.artist)} [{plan.video_id}]"
    title_s = safe_name(plan.title)
    while len((title_s + stem_tail + ext).encode("utf-8")) > MAX_FILENAME_BYTES and len(title_s) > 1:
        title_s = title_s[:-1].rstrip()
    return music_dir / folder / f"{title_s}{stem_tail}{ext}"


# --------------------------------------------------------------------------- #
# Cover art: NEVER rectangular - native 1:1 or ffmpeg-cropped 1:1
# --------------------------------------------------------------------------- #

def http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
        return r.read()


def sniff_image(data: bytes) -> tuple[str, int, int] | None:
    """Return (mime, width, height) for JPEG/PNG, else None (0,0 if size unknown)."""
    if data[:3] == b"\xff\xd8\xff":
        w = h = 0
        try:
            i = 2
            while i + 9 < len(data):
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker = data[i + 1]
                if marker in (0xC0, 0xC1, 0xC2):
                    h, w = struct.unpack(">HH", data[i + 5:i + 9])
                    break
                i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
        except struct.error:
            pass
        return "image/jpeg", w, h
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", data[16:24])
        return "image/png", w, h
    return None


def to_jpeg(data: bytes, workdir: Path) -> bytes | None:
    """Convert webp & friends to JPEG with ffmpeg."""
    src, dst = workdir / ".art_in", workdir / ".art_out.jpg"
    try:
        src.write_bytes(data)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-q:v", "2", str(dst)],
                       check=True, timeout=60)
        return dst.read_bytes()
    except Exception:
        return None
    finally:
        for f in (src, dst):
            f.unlink(missing_ok=True)


def ffmpeg_crop_square(data: bytes, workdir: Path, vf: str) -> bytes | None:
    """Run one ffmpeg crop pass and return JPEG bytes."""
    src, dst = workdir / ".art_crop_in", workdir / ".art_crop_out.jpg"
    try:
        src.write_bytes(data)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                        "-vf", vf, "-frames:v", "1", "-q:v", "2", str(dst)],
                       check=True, timeout=60)
        return dst.read_bytes()
    except Exception as e:
        log(f"    [art] crop failed ({vf}): {e}")
        return None
    finally:
        for f in (src, dst):
            f.unlink(missing_ok=True)


def square_cover(data: bytes, workdir: Path, label: str = "thumbnail") -> tuple[bytes, str, int, int, str] | None:
    """Return (bytes, mime, w, h, '1:1'|'1:1-crop') for ANY input image."""
    meta = sniff_image(data)
    if meta is None or not meta[1] or not meta[2]:
        converted = to_jpeg(data, workdir)
        if converted:
            data = converted
            meta = sniff_image(data)
    if not meta:
        log(f"    [art] cannot read {label}")
        return None
    mime, w, h = meta
    if not w or not h:
        log(f"    [art] cannot sniff dimensions for {label}")
        return None
    if w == h:
        return data, mime, w, h, "1:1"

    # YouTube hqdefault is 480x360 with 45px black bars top/bottom: crop the
    # 270px-tall active picture, not the whole 360px frame.
    if w == 480 and h == 360:
        vf = "crop=270:270"
    else:
        vf = "crop='min(iw,ih)':'min(iw,ih)'"
    log(f"    [art] {w}x{h} {label} is not square; cropping with {vf}")
    out = ffmpeg_crop_square(data, workdir, vf)
    if not out:
        return None
    outmeta = sniff_image(out)
    if not outmeta or outmeta[1] != outmeta[2]:
        log(f"    [art] ffmpeg did not produce a square for {label}")
        return None
    return out, "image/jpeg", outmeta[1], outmeta[2], "1:1-crop"


def pick_cover(info: dict, staged_thumb: Path | None, workdir: Path) -> tuple[bytes, str, int, int, str] | None:
    """Return (bytes, mime, w, h, kind); kind is always '1:1' or '1:1-crop'."""
    seen_urls: set[str] = set()

    def from_url(url: str | None, label: str) -> tuple[bytes, str, int, int, str] | None:
        if not url or url in seen_urls:
            return None
        seen_urls.add(url)
        try:
            return square_cover(http_get(url), workdir, label)
        except Exception as e:
            log(f"    [art] {label} failed ({e})")
            return None

    thumbs = [t for t in (info.get("thumbnails") or []) if isinstance(t, dict)]

    # 1. Metadata says the thumbnail is already square (Topic/auto-generated art).
    squares = [t for t in thumbs
               if t.get("url") and t.get("width") and t.get("height")
               and t["width"] == t["height"] and t["width"] >= MIN_SQUARE_ART_PX]
    squares.sort(key=lambda t: t["width"], reverse=True)
    for t in squares[:2]:
        got = from_url(t.get("url"), "square thumbnail")
        if got:
            return got

    # 2. Googleusercontent thumbs often hide real art in 16:9 wrappers: sniff
    #    the downloaded bytes instead of trusting the metadata.
    google = [t for t in thumbs
              if t.get("url") and "lh3.googleusercontent.com" in urllib.parse.urlparse(t["url"]).netloc]
    google.sort(key=lambda t: (t.get("width") or 0, t.get("height") or 0), reverse=True)
    for t in google[:4]:
        got = from_url(t.get("url"), "lh3 thumbnail")
        if got:
            return got

    # 3. The thumbnail yt-dlp staged next to the audio.
    if staged_thumb and staged_thumb.exists():
        try:
            got = square_cover(staged_thumb.read_bytes(), workdir, "staged thumbnail")
            if got:
                return got
        except Exception as e:
            log(f"    [art] staged thumbnail failed ({e})")

    # 4. Last resort: ask YouTube directly.
    for name in ("maxresdefault", "hqdefault"):
        got = from_url(f"https://i.ytimg.com/vi/{info['id']}/{name}.jpg", name)
        if got:
            return got
    return None


# --------------------------------------------------------------------------- #
# LRCLIB lyrics
# --------------------------------------------------------------------------- #
class LyricsClient:
    def __init__(self) -> None:
        self.disabled = False
        self._net_errors = 0

    def _get(self, path: str, params: dict):
        url = f"{LRCLIB}/{path}?{urllib.parse.urlencode(params)}"
        try:
            data = json.loads(http_get(url))
            self._net_errors = 0
            return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                self._net_errors = 0
                return None
            raise
        except (urllib.error.URLError, TimeoutError, OSError):
            self._net_errors += 1
            if self._net_errors >= 2:
                self.disabled = True
                log("    [lyrics] LRCLIB unreachable; skipping lyrics for the rest of this run")
            return None

    def find(self, plan: Plan, amap: ArtistMap, extra_track: str | None) -> tuple[str | None, str]:
        """Return (lrc text or None, status) where status is 'found'|'missing'|'error'."""
        if self.disabled:
            return None, "error"
        artists: list[str] = []
        for a in ([plan.original_artist] if plan.original_artist else []) + [plan.artist, plan.channel]:
            if a:
                for v in amap.variants(amap.canonical(a)[0])[:3]:
                    if v not in artists:
                        artists.append(v)
        tracks = [t for t in (plan.song, extra_track) if t]
        tracks = list(dict.fromkeys(tracks))
        dur = plan.duration

        def synced(d):
            return d.get("syncedLyrics") if isinstance(d, dict) and d.get("syncedLyrics") else None

        tries = 0
        for tr in tracks:
            for ar in artists[:4]:
                if self.disabled or tries >= 6:
                    break
                tries += 1
                params = {"artist_name": ar, "track_name": tr}
                if dur:
                    params["duration"] = dur
                hit = synced(self._get("get", params))
                if hit:
                    return hit, "found"
        for tr in tracks:
            if self.disabled:
                break
            for ar in [None] + artists[:1]:
                params = {"track_name": tr}
                if ar:
                    params["artist_name"] = ar
                results = self._get("search", params) or []
                good = [r for r in results if synced(r) and
                        (not dur or (r.get("duration") and
                                     abs(r["duration"] - dur) <= LRCLIB_DURATION_TOLERANCE))]
                if good:
                    good.sort(key=lambda r: abs((r.get("duration") or 0) - dur))
                    return synced(good[0]), "found"
        return None, ("error" if self.disabled else "missing")


# --------------------------------------------------------------------------- #
# Tagging
# --------------------------------------------------------------------------- #

def write_tags(path: Path, plan: Plan, cover, lrc: str | None) -> None:
    ext = path.suffix.lower()
    albumartist = VARIOUS_DIR if plan.route == "various" else plan.artist
    if ext == ".m4a":
        a = MP4(str(path))
        if a.tags is None:
            a.add_tags()
        t = a.tags
        t["\xa9nam"] = [plan.title]
        t["\xa9ART"] = [plan.artist]
        t["aART"] = [albumartist]
        t["\xa9alb"] = [plan.album]
        t["\xa9cmt"] = [plan.url]
        if plan.year:
            t["\xa9day"] = [plan.year]
        if plan.route == "various":
            t["cpil"] = True
        if lrc:
            t["\xa9lyr"] = [lrc]
        else:
            t.pop("\xa9lyr", None)         # fallback path: never leave half-embedded lyrics behind
        if cover:
            fmt = MP4Cover.FORMAT_PNG if cover[1] == "image/png" else MP4Cover.FORMAT_JPEG
            t["covr"] = [MP4Cover(cover[0], imageformat=fmt)]
        a.save()
    elif ext == ".opus":
        a = OggOpus(str(path))
        a["title"] = [plan.title]
        a["artist"] = [plan.artist]
        a["albumartist"] = [albumartist]
        a["album"] = [plan.album]
        a["comment"] = [plan.url]
        if plan.year:
            a["date"] = [plan.year]
        if plan.route == "various":
            a["compilation"] = ["1"]
        if lrc:
            a["lyrics"] = [lrc]
        elif "lyrics" in a:
            del a["lyrics"]
        if cover:
            pic = Picture()
            pic.data, pic.mime, pic.width, pic.height = cover[0], cover[1], cover[2], cover[3]
            pic.type, pic.depth = 3, 24
            a["metadata_block_picture"] = [base64.b64encode(pic.write()).decode("ascii")]
        a.save()
    else:
        raise ValueError(f"unsupported container {ext}")


def lyrics_embedded(path: Path) -> bool:
    try:
        if path.suffix.lower() == ".m4a":
            return bool((MP4(str(path)).tags or {}).get("\xa9lyr"))
        return bool(OggOpus(str(path)).get("lyrics"))
    except Exception:
        return False


# --------------------------------------------------------------------------- #
# M3U (newest first)
# --------------------------------------------------------------------------- #

def prepend_m3u(m3u: Path, entries: list[tuple[str, int, str]]) -> int:
    existing: list[str] = []
    if m3u.exists():
        existing = [ln.rstrip("\r\n") for ln in m3u.read_text(encoding="utf-8").splitlines()
                    if ln.strip() and ln.strip() != "#EXTM3U"]
    have = {ln for ln in existing if not ln.startswith("#")}
    fresh: list[str] = []
    for path, dur, label in entries:
        if path in have:
            continue
        fresh += [f"#EXTINF:{dur},{label.replace(chr(10), ' ')}", path]
    if not fresh:
        return 0
    tmp = m3u.with_name(m3u.name + ".tmp")
    tmp.write_text("\n".join(["#EXTM3U"] + fresh + existing) + "\n", encoding="utf-8")
    os.replace(tmp, m3u)
    return len(fresh) // 2


# --------------------------------------------------------------------------- #
# Database
# --------------------------------------------------------------------------- #

def open_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute("""CREATE TABLE IF NOT EXISTS tracks(
        video_id TEXT PRIMARY KEY, path TEXT NOT NULL, artist TEXT, title TEXT,
        route TEXT, art TEXT, lyrics_status TEXT, lrc_path TEXT, added_at TEXT)""")
    db.commit()
    return db


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def find_audio(staging: Path, vid: str) -> Path | None:
    for ext in (".m4a", ".opus", *sorted(REMUX_TO_OPUS_EXT)):
        p = staging / f"{vid}{ext}"
        if p.exists():
            return p
    return None


def find_thumb(staging: Path, vid: str) -> Path | None:
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = staging / f"{vid}{ext}"
        if p.exists():
            return p
    return None


def process_one(info_path: Path, args, amap: ArtistMap, db: sqlite3.Connection, lyr: LyricsClient):
    """Return ('ok'|'skip', entry) or raise. entry = (nav_path, duration, label)."""
    info = json.loads(info_path.read_text(encoding="utf-8"))
    vid = info["id"]
    staging = info_path.parent

    row = db.execute("SELECT path FROM tracks WHERE video_id=?", (vid,)).fetchone()
    if row and Path(row[0]).exists():
        log(f"[skip] {vid} already in library: {row[0]}")
        return "skip", None

    audio = find_audio(staging, vid)
    if audio is None:
        raise FileNotFoundError(f"no audio file for {vid} in staging")
    if audio.suffix.lower() in REMUX_TO_OPUS_EXT:
        out = audio.with_suffix(".opus")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(audio), "-vn", "-c:a", "copy", str(out)],
                       check=True, timeout=300)
        audio.unlink()
        audio = out
    if audio.suffix.lower() not in SUPPORTED_EXT:
        raise ValueError(f"unsupported audio type {audio.suffix}")

    plan = decide(info, amap)
    if not plan.mapped:
        log(f"    [map?] unmapped artist '{plan.artist}' (channel '{plan.channel}', id {vid}) - add to artist_map.json")
    dest = build_dest(Path(args.music_dir), args.playlist_subdir, plan, audio.suffix.lower())

    cover = pick_cover(info, find_thumb(staging, vid), staging)
    art_kind = cover[4] if cover else "none"

    lrc, lyr_status = lyr.find(plan, amap, info.get("track"))

    # Tag in staging; on any lyrics trouble, retry without them and use a sidecar.
    sidecar_needed = False
    if lrc:
        try:
            write_tags(audio, plan, cover, lrc)
            if not lyrics_embedded(audio):
                raise RuntimeError("lyrics not present after save")
            lyr_status = "embedded"
        except Exception as e:
            log(f"    [lyrics] embed failed ({e}); falling back to sidecar .lrc")
            sidecar_needed = True
            write_tags(audio, plan, cover, None)
    else:
        write_tags(audio, plan, cover, None)

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(audio), str(dest))

    lrc_path = None
    if sidecar_needed and lrc:
        lrc_path = dest.with_suffix(".lrc")
        lrc_path.write_text(lrc, encoding="utf-8")
        lyr_status = "sidecar"

    db.execute("INSERT OR REPLACE INTO tracks VALUES(?,?,?,?,?,?,?,?,?)",
               (vid, str(dest), plan.artist, plan.title, plan.route, art_kind, lyr_status,
                str(lrc_path) if lrc_path else None, time.strftime("%Y-%m-%d %H:%M:%S")))
    db.commit()

    for f in staging.glob(f"{vid}.*"):                       # clean staging for this video
        f.unlink(missing_ok=True)

    log(f"[ok]   {plan.route:<8} art={art_kind:<4} lyrics={lyr_status:<8} -> {dest}")

    nav_path = str(dest)
    if args.navidrome_music_dir and args.navidrome_music_dir != args.music_dir:
        nav_path = nav_path.replace(args.music_dir.rstrip("/"), args.navidrome_music_dir.rstrip("/"), 1)
    return "ok", (nav_path, plan.duration, f"{plan.artist} - {plan.title}")


def main() -> int:
    env = os.environ.get
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staging", default=env("STAGING"), required=env("STAGING") is None)
    ap.add_argument("--music-dir", default=env("MUSIC_DIR"), required=env("MUSIC_DIR") is None)
    ap.add_argument("--playlist-subdir", default=env("PLAYLIST_SUBDIR", "ytsync") or "ytsync",
                    help="single folder under MUSIC_DIR for every track in this playlist (default: ytsync)")
    ap.add_argument("--navidrome-music-dir", default=env("NAVIDROME_MUSIC_DIR"),
                    help="music dir as Navidrome sees it, if different (written into the m3u)")
    ap.add_argument("--artist-map", default=env("ARTIST_MAP", str(Path(__file__).with_name("artist_map.json"))))
    ap.add_argument("--m3u", default=env("M3U_FILE"))
    ap.add_argument("--db", default=env("DB"), required=env("DB") is None)
    ap.add_argument("--result-file", help="write new=/failed= counts here for the shell wrapper")
    ap.add_argument("--newest-at-start", action="store_true",
                    help="playlist index 1 is the newest item (default: newest = highest index)")
    args = ap.parse_args()
    if not args.m3u:
        playlist_name = safe_name(args.playlist_subdir or "ytsync")
        args.m3u = str(Path(args.music_dir) / f"{playlist_name}.m3u")

    staging = Path(args.staging)
    amap = ArtistMap(Path(args.artist_map))
    db = open_db(Path(args.db))
    lyr = LyricsClient()

    infos = []
    for p in sorted(staging.glob("*.info.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            log(f"[fail] unreadable {p.name}: {e}")
            continue
        if d.get("_type") == "playlist" or not d.get("duration"):
            continue                                          # playlist-level metadata
        infos.append((d.get("playlist_index") or 0, p))
    infos.sort(key=lambda x: x[0])

    done: list[tuple[str, int, str]] = []
    failed = 0
    for _, p in infos:
        try:
            status, entry = process_one(p, args, amap, db, lyr)
            if entry:
                done.append(entry)
        except Exception as e:
            failed += 1
            log(f"[fail] {p.name}: {type(e).__name__}: {e} (left in staging; will retry next run)")

    # done is oldest -> newest if newest has the highest index; m3u wants newest first.
    entries = done if args.newest_at_start else list(reversed(done))
    if entries:
        try:
            n = prepend_m3u(Path(args.m3u), entries)
            log(f"[m3u]  prepended {n} track(s) to {args.m3u}")
        except Exception as e:
            log(f"[fail] could not update m3u: {e}")
            failed += 1

    log(f"[done] new={len(done)} failed={failed}")
    if args.result_file:
        Path(args.result_file).write_text(f"new={len(done)}\nfailed={failed}\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
