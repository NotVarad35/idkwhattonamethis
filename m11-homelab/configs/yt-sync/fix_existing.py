#!/usr/bin/env python3
"""fix_existing.py - one-shot migration for tracks downloaded by the old yt-sync layout.

No network, no re-downloading. Reads yt-sync.db, then for every tracked .m4a/.opus:
  1. extracts the embedded cover art and crops it to true 1:1 with ffmpeg if needed;
  2. moves the audio (and .lrc sidecar, if any) flat into
     MUSIC_DIR/<PLAYLIST_SUBDIR>/;
  3. updates tracks.path / tracks.lrc_path / tracks.art in the database;
  4. rewrites the old paths in every existing .m3u (new default and legacy);
  5. removes only now-empty old artist / Various Artists folders.

Dependencies: stdlib + mutagen + ffmpeg (the same ones process_track.py uses).
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import shlex
import shutil
import sqlite3
import struct
import subprocess
import sys
import time
from pathlib import Path

from mutagen.flac import Picture
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggopus import OggOpus

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

_WIN_BAD = {"/": "／", "\\": "＼", ":": "：", "*": "＊", "?": "？", '"': "＂",
            "<": "＜", ">": "＞", "|": "｜"}


def log(msg: str) -> None:
    print(msg, flush=True)


def safe_name(s: str) -> str:
    """Same path-component sanitising as process_track.py."""
    s = "".join(_WIN_BAD.get(ch, ch) for ch in s)
    s = "".join(ch for ch in s if ch >= " " and ch != "\x7f")
    s = re.sub(r"\s+", " ", s).strip().rstrip(". ")
    return s or "_"


def load_env_file(path: Path) -> None:
    """Load KEY=value lines from yt-sync.env without executing shell code."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2)
        try:
            parts = shlex.split(value, comments=True, posix=True)
            value = parts[0] if parts else ""
        except ValueError:
            value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, os.path.expandvars(value))


def abspath(value: str | Path) -> Path:
    return Path(os.path.abspath(os.path.expandvars(str(value))))


def sniff_image(data: bytes) -> tuple[str, int, int] | None:
    """Return (mime, width, height) for JPEG/PNG, else None."""
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


def convert_to_jpeg(data: bytes) -> bytes | None:
    """ffmpeg conversion for webp and other formats mutagen cannot describe."""
    import tempfile

    with tempfile.TemporaryDirectory(prefix="yt-sync-art-") as td:
        src, dst = Path(td) / "in", Path(td) / "out.jpg"
        try:
            src.write_bytes(data)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                            "-frames:v", "1", "-q:v", "2", str(dst)],
                           check=True, timeout=120)
            return dst.read_bytes()
        except Exception:
            return None


def extract_cover(path: Path) -> tuple[bytes, str, int, int] | None:
    """Return (data, mime, width, height) for the first embedded picture."""
    try:
        ext = path.suffix.lower()
        if ext == ".m4a":
            a = MP4(str(path))
            covers = list((a.tags or {}).get("covr") or [])
            if not covers:
                return None
            data = bytes(covers[0])
            meta = sniff_image(data)
            if meta is None:
                converted = convert_to_jpeg(data)
                if converted:
                    data = converted
                    meta = sniff_image(data)
            mime, w, h = meta if meta else ("image/jpeg", 0, 0)
            return data, mime, w, h

        if ext == ".opus":
            a = OggOpus(str(path))
            blocks = list(a.get("metadata_block_picture") or [])
            if not blocks:
                return None
            pic = Picture(base64.b64decode(blocks[0]))
            data = pic.data
            meta = sniff_image(data)
            mime = pic.mime or (meta[0] if meta else "image/jpeg")
            w = pic.width or (meta[1] if meta else 0)
            h = pic.height or (meta[2] if meta else 0)
            return data, mime, w, h
    except Exception as e:
        log(f"    [art] cannot read embedded cover: {type(e).__name__}: {e}")
    return None


def crop_square(data: bytes, w: int, h: int) -> bytes | None:
    """Crop to 1:1. hqdefault 480x360 gets 270:270 to drop its black bars."""
    import tempfile

    vf = "crop=270:270" if (w == 480 and h == 360) else "crop='min(iw,ih)':'min(iw,ih)'"
    with tempfile.TemporaryDirectory(prefix="yt-sync-crop-") as td:
        src, dst = Path(td) / "in", Path(td) / "out.jpg"
        try:
            src.write_bytes(data)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                            "-vf", vf, "-frames:v", "1", "-q:v", "2", str(dst)],
                           check=True, timeout=120)
            out = dst.read_bytes()
            meta = sniff_image(out)
            if meta and meta[1] == meta[2] and meta[1] > 0:
                return out
            log(f"    [art] ffmpeg did not produce a square image with {vf}")
        except Exception as e:
            log(f"    [art] crop failed ({vf}): {e}")
        return None


def normalize_cover(path: Path, current_kind: str | None) -> tuple[bool, str | None]:
    """Return (success, art_kind). success=False means the file must not be moved."""
    cover = extract_cover(path)
    if cover is None:
        log("    [art] no embedded cover; leaving art tag as-is")
        return True, current_kind

    data, mime, w, h = cover
    if not w or not h:
        converted = convert_to_jpeg(data)
        if converted:
            data = converted
            meta = sniff_image(data)
            mime, w, h = meta if meta else ("image/jpeg", 0, 0)
    if not w or not h:
        log("    [art] cannot determine cover dimensions; skipping this track")
        return False, None

    if w == h:
        log(f"    [art] already {w}x{h}")
        set_cover(path, data, mime, w, h)
        return True, "1:1"

    log(f"    [art] {w}x{h} -> 1:1")
    squared = crop_square(data, w, h)
    if squared is None:
        return False, None
    meta = sniff_image(squared) or ("image/jpeg", 0, 0)
    set_cover(path, squared, "image/jpeg", meta[1], meta[2])
    return True, "1:1-crop"


def set_cover(path: Path, data: bytes, mime: str, w: int, h: int) -> None:
    """Replace the first embedded picture while keeping every other tag."""
    ext = path.suffix.lower()
    if ext == ".m4a":
        a = MP4(str(path))
        if a.tags is None:
            a.add_tags()
        fmt = MP4Cover.FORMAT_PNG if mime == "image/png" else MP4Cover.FORMAT_JPEG
        covers = list(a.tags.get("covr") or [])
        new_cover = MP4Cover(data, imageformat=fmt)
        if covers:
            covers[0] = new_cover
        else:
            covers = [new_cover]
        a.tags["covr"] = covers
        a.save()
        return

    if ext == ".opus":
        a = OggOpus(str(path))
        blocks = list(a.get("metadata_block_picture") or [])
        pic = Picture()
        pic.type = 3                      # front cover
        pic.mime = mime
        pic.data = data
        pic.width, pic.height = w, h
        pic.depth = 24
        encoded = base64.b64encode(pic.write()).decode("ascii")
        if blocks:
            blocks[0] = encoded
        else:
            blocks = [encoded]
        a["metadata_block_picture"] = blocks
        a.save()
        return

    raise ValueError(f"unsupported audio type {ext}")


def m3u_path_for(path: Path, music_dir: Path, navidrome_dir: Path | None) -> str:
    """Render a DB (real) path the way the m3u expects it."""
    if not navidrome_dir:
        return str(path)
    try:
        return str(navidrome_dir / path.relative_to(music_dir))
    except ValueError:
        return str(path)


def rewrite_m3u(path: Path, replacements: dict[str, str]) -> int:
    """Replace exact path lines. Returns the number of lines changed."""
    if not path.is_file():
        log(f"    [m3u] not found, skipped: {path}")
        return 0
    before = path.read_text(encoding="utf-8").splitlines()
    after: list[str] = []
    changed = 0
    for line in before:
        stripped = line.strip()
        new_line = line
        for old, new in replacements.items():
            if stripped == old:
                new_line = line.replace(old, new)
                changed += 1
                break
        after.append(new_line)
    if changed:
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text("\n".join(after) + "\n", encoding="utf-8")
        os.replace(tmp, path)
    return changed


def backup_file(path: Path) -> None:
    if not path.is_file():
        return
    stamp = time.strftime("%Y%m%d-%H%M%S")
    bak = path.with_name(f"{path.name}.{stamp}.bak")
    shutil.copy2(path, bak)
    log(f"[backup] {bak}")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> int:
    script_dir = Path(__file__).resolve().parent
    load_env_file(Path(os.environ.get("YT_SYNC_CONF") or script_dir / "yt-sync.env"))
    env = os.environ.get

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=env("DB"), help="yt-sync.db (default: $STATE_DIR/yt-sync.db)")
    ap.add_argument("--state-dir", default=env("STATE_DIR", str(Path.home() / ".local/share/yt-sync")))
    ap.add_argument("--music-dir", default=env("MUSIC_DIR", "/storage/43CC-5E0C/Music"))
    ap.add_argument("--playlist-subdir", default=env("PLAYLIST_SUBDIR", "ytsync") or "ytsync")
    ap.add_argument("--navidrome-music-dir", default=env("NAVIDROME_MUSIC_DIR"))
    ap.add_argument("--m3u", action="append",
                    help="m3u to rewrite; repeatable. Default: M3U_FILE, new <subdir>.m3u and legacy yt-sync.m3u")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        log("ERROR: ffmpeg is required to crop cover art")
        return 2

    music_dir = abspath(args.music_dir)
    navidrome_dir = abspath(args.navidrome_music_dir) if args.navidrome_music_dir else None
    target_dir = music_dir / safe_name(args.playlist_subdir)
    db_path = abspath(args.db or (Path(args.state_dir) / "yt-sync.db"))

    if not db_path.is_file():
        log(f"ERROR: database not found: {db_path}")
        return 2
    if not music_dir.is_dir():
        log(f"ERROR: MUSIC_DIR not found: {music_dir}")
        return 2

    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    try:
        rows = db.execute("SELECT * FROM tracks").fetchall()
    except sqlite3.Error as e:
        log(f"ERROR: cannot read tracks table: {e}")
        return 2
    if not rows:
        log("No tracks in the database; nothing to do.")
        return 0

    m3u_files: list[Path] = []
    if args.m3u:
        m3u_files = [abspath(p) for p in args.m3u]
    else:
        if env("M3U_FILE"):
            m3u_files.append(abspath(env("M3U_FILE")))
        m3u_files.append(music_dir / f"{safe_name(args.playlist_subdir)}.m3u")
        m3u_files.append(music_dir / "yt-sync.m3u")
    m3u_files = list(dict.fromkeys(m3u_files))

    backed_up: set[Path] = set()
    changed_rows = 0
    failed = 0
    old_dirs: set[Path] = set()
    replacements: dict[str, str] = {}

    log(f"=== fix_existing: db={db_path} music_dir={music_dir} target={target_dir} ===")
    for row in rows:
        vid = row["video_id"]
        raw_path = row["path"]
        if not raw_path:
            log(f"[skip] {vid}: no path in db")
            continue

        source = abspath(raw_path)
        work = source if source.exists() else target_dir / source.name

        if not work.exists():
            log(f"[fail] {vid}: neither {source} nor {work} exists")
            failed += 1
            continue
        if work.suffix.lower() not in {".m4a", ".opus"}:
            log(f"[skip] {vid}: unsupported file {work}")
            continue

        log(f"[track] {vid}: {work.name}")
        ok, art_kind = normalize_cover(work, row["art"] if "art" in row.keys() else None)
        if not ok:
            log(f"[fail] {vid}: cover art could not be fixed; left in place")
            failed += 1
            continue

        dest = target_dir / work.name
        if work != dest:
            if dest.exists():
                try:
                    if os.path.samefile(work, dest):
                        work = dest
                    else:
                        log(f"[fail] {vid}: destination already exists: {dest}")
                        failed += 1
                        continue
                except OSError:
                    log(f"[fail] {vid}: destination already exists: {dest}")
                    failed += 1
                    continue
            if work != dest:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(work), str(dest))
                log(f"    [move] {work} -> {dest}")
            work = dest

        if source.parent != target_dir:
            old_dirs.add(source.parent)

        # Lyrics sidecar: trust the DB first, then the usual same-stem file.
        lrc_candidates: list[Path] = []
        db_lrc = row["lrc_path"] if "lrc_path" in row.keys() else None
        if db_lrc:
            lrc_candidates.append(abspath(db_lrc))
        lrc_candidates.append(source.with_suffix(".lrc"))
        lrc_candidates.append(dest.with_suffix(".lrc"))
        old_lrc = next((p for p in lrc_candidates if p.exists()), None)
        new_lrc: str | None = None
        if old_lrc:
            lrc_dest = dest.with_suffix(".lrc")
            if old_lrc != lrc_dest:
                if lrc_dest.exists() and not os.path.samefile(old_lrc, lrc_dest):
                    log(f"    [warn] lrc destination exists, keeping both: {lrc_dest}")
                    new_lrc = str(lrc_dest)
                else:
                    lrc_dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(old_lrc), str(lrc_dest))
                    log(f"    [move] {old_lrc} -> {lrc_dest}")
            new_lrc = str(lrc_dest)

        if db_path not in backed_up:
            backup_file(db_path)
            backed_up.add(db_path)
        db.execute(
            "UPDATE tracks SET path=?, lrc_path=?, art=? WHERE video_id=?",
            (str(dest), new_lrc, art_kind, vid),
        )
        changed_rows += 1

        old_m3u = m3u_path_for(source, music_dir, navidrome_dir)
        new_m3u = m3u_path_for(dest, music_dir, navidrome_dir)
        if old_m3u != new_m3u:
            replacements[old_m3u] = new_m3u
        if str(source) != old_m3u:
            replacements[str(source)] = new_m3u

    db.commit()
    db.close()

    m3u_changes = 0
    for m3u in m3u_files:
        if not m3u.is_file():
            continue
        if m3u not in backed_up:
            backup_file(m3u)
            backed_up.add(m3u)
        n = rewrite_m3u(m3u, replacements)
        m3u_changes += n
        log(f"[m3u] {m3u}: {n} line(s) rewritten")

    # Only empty parents of files we actually moved are candidates. os.rmdir
    # refuses to remove anything non-empty, so unrelated folders are safe.
    for d in sorted(old_dirs, key=lambda p: len(p.parts), reverse=True):
        cursor = d
        while cursor != music_dir and music_dir in cursor.parents:
            if cursor == target_dir:          # never remove the playlist folder itself
                break
            if cursor.is_symlink() or not cursor.is_dir():
                break
            try:
                cursor.rmdir()
                log(f"[prune] removed empty folder: {cursor}")
            except OSError:
                break
            cursor = cursor.parent

    log(f"=== fix_existing done: tracks={changed_rows} failed={failed} m3u_lines={m3u_changes} ===")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
