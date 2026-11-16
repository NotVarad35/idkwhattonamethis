# yt-sync — J-Pop YouTube playlist → Navidrome (Samsung M11 / Termux)

## Files

| File | Role |
|---|---|
| `yt-sync.sh` | Wrapper: lock, yt-dlp + archive, calls the processor, Navidrome rescan, log |
| `process_track.py` | Tag, name, route, lyrics (LRCLIB), cover art, `yt-sync.m3u` |
| `artist_map.json` | Canonical artist spelling (`ヨルシカ`, `Eve`, …) + per-video `overrides` |
| `yt-sync.env.example` | Copy to `yt-sync.env` (git-ignored) and fill in playlist URL + Navidrome login |

## Where things go

In the repo: `m11-homelab/configs/yt-sync/` (this folder). On the phone, mirror it:

```
~/m11-homelab/configs/yt-sync/
    yt-sync.sh  process_track.py  artist_map.json  yt-sync.env
~/.local/share/yt-sync/          # created automatically
    archive.txt   yt-sync.db   yt-sync.log   staging/
/storage/43CC-5E0C/Music/        # your library (MUSIC_DIR)
    <Artist>/…  Various Artists/…  yt-sync.m3u
```

## One-time setup

From the laptop (PowerShell, repo root):

```bash
ssh -p 8022 user@192.168.1.110 'mkdir -p ~/m11-homelab/configs'
scp -P 8022 -r m11-homelab/configs/yt-sync user@192.168.1.110:~/m11-homelab/configs/
```

On the M11 (SSH):

```bash
pkg update && pkg install python ffmpeg curl nodejs cronie termux-api -y
pip install -U "yt-dlp[default]" mutagen
cd ~/m11-homelab/configs/yt-sync
sed -i 's/\r$//' yt-sync.sh process_track.py     # in case Windows added CRLF
chmod +x yt-sync.sh
cp yt-sync.env.example yt-sync.env && chmod 600 yt-sync.env && nano yt-sync.env
./yt-sync.sh --dry-run      # lists what would be downloaded, changes nothing
./yt-sync.sh                # real run
```

## Running it

| How | Command |
|---|---|
| SSH / manual | `~/m11-homelab/configs/yt-sync/yt-sync.sh` |
| Android launcher (Termux:Widget app) | `mkdir -p ~/.shortcuts/tasks && ln -s ~/m11-homelab/configs/yt-sync/yt-sync.sh ~/.shortcuts/tasks/yt-sync.sh` |
| Weekly (Sun 04:00) | `crontab -e` → `0 4 * * 0 $HOME/m11-homelab/configs/yt-sync/yt-sync.sh >/dev/null 2>&1` |

`crond` is not started by installing cronie, and Android may kill it in Doze — see the pitfalls in `docs/Todo.md` §4. The script takes a `termux-wake-lock` itself while it runs.

Flags: `--dry-run`, `--process-only` (retry what is stuck in staging), `--no-rescan`. Env: `FORCE_RESCAN=1`.

## Rules the processor applies

- **Title**: version descriptors are kept as `[MV]`, `[Live]`, `[Cover]`, `[THE FIRST TAKE]`, `[Lyric Video]`, `[Acoustic]`. Noise (`Official Audio`, `HD`, `4K`, `/ alt romaji`) is dropped. Non-descriptor brackets such as `(feat. X)` stay.
- **Route**: any of `MV`, `Live`, `Cover`, `THE FIRST TAKE` → `Various Artists/`. Everything else → `Artist/` (flat, no album folder). Change `VARIOUS_LABELS` at the top of `process_track.py` to adjust.
- **Artist**: YouTube music metadata (`artist` on Topic/auto-generated uploads) first, then the title (`Artist - Song`, `Song / Artist`, `Artist「Song」`; `artist_map.json` decides which side is the artist), then the channel. **Covers use the channel name.** The result goes through `artist_map.json`.
- **File name**: `{title incl. [MV]} - {artist} [{VideoID}].{m4a|opus}`; characters FAT/exFAT forbid become full-width look-alikes (`/`→`／`), and the name is cut to 240 bytes.
- **Album tag** = the title (each track is its own single, so every track keeps its own cover art for the jukebox display). `AlbumArtist` = `Various Artists` + compilation flag on that route.
- **Cover art**: a square (1:1) thumbnail ≥ 500 px if YouTube lists one in the metadata (mostly Topic/auto-generated uploads); otherwise the 16:9 thumbnail.
- **Lyrics**: LRCLIB synced lyrics, embedded (`©lyr` / `LYRICS`). If embedding fails the file gets a same-name `.lrc` sidecar and the path is stored in `yt-sync.db` (`tracks.lrc_path`, `lyrics_status` = `embedded|sidecar|missing|error`).
- **Playlist**: new tracks are inserted at the top of `yt-sync.m3u`, newest first. By default the newest playlist item is the one with the highest index (YouTube appends); if your playlist adds new videos at the top, set `NEWEST_AT_START=1` in `yt-sync.env`.

## Maintaining `artist_map.json`

Every run logs `[map?] unmapped artist 'X' (channel 'Y', id Z)` for names it doesn't know:

```bash
grep 'map?' ~/.local/share/yt-sync/yt-sync.log | sort -u
```

Add `"Canonical": ["alias", …]` entries. For a single video that is mis-parsed, add an override:

```json
"overrides": { "VIDEOID123": { "artist": "ヨルシカ", "title": "Song [Live]", "route": "various" } }
```

Already-routed files are not moved when you change the map; delete the file and its line in `archive.txt` (and the `tracks` row) to re-fetch it.

## Things to know

- **Navidrome playlists**: it imports `*.m3u` from the library (default `PlaylistsPath`) during a scan. If Navidrome runs inside a Linux Deploy chroot and sees the SD card at another path, set `NAVIDROME_MUSIC_DIR` so the m3u paths match what it sees.
- **Rescan** uses the Subsonic `startScan` call with salted-token auth (your password is never sent); a normal Navidrome user is enough.
- **YouTube changes**: if yt-dlp reports missing formats / "n challenge" errors, update it (`pip install -U "yt-dlp[default]"`) and keep `nodejs` installed — the wrapper passes `--js-runtimes node` when `deno` is absent.
- **Failures are retried**: anything that fails processing stays in `staging/` and is picked up on the next run (`--process-only` to retry now).
