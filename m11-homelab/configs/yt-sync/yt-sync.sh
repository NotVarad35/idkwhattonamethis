#!/data/data/com.termux/files/usr/bin/bash
# yt-sync.sh - sync a J-Pop YouTube playlist into Navidrome (Termux on the M11).
#
#   yt-sync.sh              download new tracks, tag/route them, update m3u, rescan Navidrome
#   yt-sync.sh --dry-run    only list what yt-dlp WOULD download (archive untouched)
#   yt-sync.sh --process-only   skip yt-dlp; just (re)process whatever is in staging
#   yt-sync.sh --no-rescan  do everything except the Navidrome rescan ping
#
# Config comes from yt-sync.env next to this script (or $YT_SYNC_CONF). See yt-sync.env.example.
set -uo pipefail

SELF="$(readlink -f "${BASH_SOURCE[0]}")"       # works through a ~/.shortcuts symlink
SCRIPT_DIR="$(dirname "$SELF")"

DRY_RUN=0; PROCESS_ONLY=0; DO_RESCAN=1
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --process-only) PROCESS_ONLY=1 ;;
    --no-rescan) DO_RESCAN=0 ;;
    -h|--help) sed -n '2,10p' "$SELF" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

# ---- config ---------------------------------------------------------------
CONF="${YT_SYNC_CONF:-$SCRIPT_DIR/yt-sync.env}"
# shellcheck disable=SC1090
[ -f "$CONF" ] && . "$CONF"

: "${PLAYLIST_URL:?set PLAYLIST_URL in $CONF}"
MUSIC_DIR="${MUSIC_DIR:-/storage/43CC-5E0C/Music}"
NAVIDROME_MUSIC_DIR="${NAVIDROME_MUSIC_DIR:-$MUSIC_DIR}"   # path as Navidrome sees it
NAVIDROME_URL="${NAVIDROME_URL:-http://127.0.0.1:4533}"
STATE_DIR="${STATE_DIR:-$HOME/.local/share/yt-sync}"
ARTIST_MAP="${ARTIST_MAP:-$SCRIPT_DIR/artist_map.json}"
M3U_FILE="${M3U_FILE:-$MUSIC_DIR/yt-sync.m3u}"
PYTHON="${PYTHON:-python}"

ARCHIVE="$STATE_DIR/archive.txt"
STAGING="$STATE_DIR/staging"
DB="$STATE_DIR/yt-sync.db"
LOG="$STATE_DIR/yt-sync.log"
LOCK="$STATE_DIR/run.lock"
PROCESSOR="$SCRIPT_DIR/process_track.py"

mkdir -p "$STATE_DIR" "$STAGING"

# ---- logging (everything below goes to the terminal AND the log file) --------
if [ -f "$LOG" ] && [ "$(stat -c %s "$LOG" 2>/dev/null || echo 0)" -gt 1048576 ]; then
  mv -f "$LOG" "$LOG.1"
fi
exec > >(tee -a "$LOG") 2>&1
log()  { printf '%s %s\n' "$(date '+%F %T')" "$*"; }
die()  { log "ERROR: $*"; exit 1; }

# ---- single instance + keep CPU awake -----------------------------------------
if ! mkdir "$LOCK" 2>/dev/null; then
  oldpid="$(cat "$LOCK/pid" 2>/dev/null || true)"
  if [ -n "$oldpid" ] && kill -0 "$oldpid" 2>/dev/null; then
    die "already running (pid $oldpid)"
  fi
  log "removing stale lock"; rm -rf "$LOCK"; mkdir "$LOCK" || die "cannot take lock"
fi
echo $$ > "$LOCK/pid"
HAVE_WAKELOCK=0
if command -v termux-wake-lock >/dev/null 2>&1; then termux-wake-lock && HAVE_WAKELOCK=1; fi
RESULT_FILE="$(mktemp "$STATE_DIR/result.XXXXXX")"
cleanup() {
  rm -f "$RESULT_FILE"; rm -rf "$LOCK"
  [ "$HAVE_WAKELOCK" = 1 ] && termux-wake-unlock
  return 0
}
trap cleanup EXIT

# ---- preflight ---------------------------------------------------------------
for c in yt-dlp ffmpeg curl md5sum "$PYTHON"; do
  command -v "$c" >/dev/null 2>&1 || die "missing command: $c (see README: pkg install ...)"
done
"$PYTHON" -c 'import mutagen' 2>/dev/null || die "mutagen missing: pip install mutagen"
[ -f "$PROCESSOR" ] || die "missing $PROCESSOR"
[ -d "$MUSIC_DIR" ] && [ -w "$MUSIC_DIR" ] || die "MUSIC_DIR not writable: $MUSIC_DIR (run termux-setup-storage / check SD mount)"

log "=== yt-sync start (dry_run=$DRY_RUN process_only=$PROCESS_ONLY) ==="

# ---- 1. download new tracks -----------------------------------------------------
if [ "$PROCESS_ONLY" = 0 ]; then
  YTDLP_ARGS=(
    --ignore-errors
    --download-archive "$ARCHIVE"
    --format bestaudio                      # best stream: Opus (~130-160k) or AAC/m4a (~128k), no re-encode
    --extract-audio --audio-format best     # keep codec; remux to .opus or .m4a so tags work
    --write-info-json --no-write-playlist-metafiles
    --write-thumbnail --convert-thumbnails jpg
    --output "$STAGING/%(id)s.%(ext)s"
    --retries 5 --fragment-retries 5
    --sleep-requests 1 --sleep-interval 2 --max-sleep-interval 6
    --no-mtime --no-progress
  )
  # Recent YouTube extraction needs a JS runtime; use node if there is no deno.
  if yt-dlp --help 2>/dev/null | grep -q -- '--js-runtimes' && ! command -v deno >/dev/null 2>&1 \
     && command -v node >/dev/null 2>&1; then
    YTDLP_ARGS+=(--js-runtimes node)
  fi
  [ -n "${YTDLP_COOKIES:-}" ] && YTDLP_ARGS+=(--cookies "$YTDLP_COOKIES")
  if [ -n "${YTDLP_EXTRA_ARGS:-}" ]; then
    read -r -a _extra <<< "$YTDLP_EXTRA_ARGS"; YTDLP_ARGS+=("${_extra[@]}")
  fi

  if [ "$DRY_RUN" = 1 ]; then
    log "dry run: items yt-dlp would download"
    yt-dlp --simulate --print "  %(id)s  %(title)s" "${YTDLP_ARGS[@]}" "$PLAYLIST_URL"
    exit $?
  fi

  log "yt-dlp: checking playlist against $ARCHIVE"
  yt-dlp "${YTDLP_ARGS[@]}" "$PLAYLIST_URL"
  rc=$?
  # 1 = some videos failed (private/deleted): carry on. >=2 = bad options/crash.
  [ "$rc" -ge 2 ] && die "yt-dlp failed hard (exit $rc)"
  [ "$rc" -eq 1 ] && log "yt-dlp reported errors for some items (exit 1); continuing"
fi

# ---- 2-6. tag, route, lyrics, m3u (all in process_track.py) ----------------------
NEW=0; FAILED=0
PROC_EXTRA=()
[ "${NEWEST_AT_START:-0}" = 1 ] && PROC_EXTRA+=(--newest-at-start)
"$PYTHON" "$PROCESSOR" \
  --staging "$STAGING" --music-dir "$MUSIC_DIR" --navidrome-music-dir "$NAVIDROME_MUSIC_DIR" \
  --artist-map "$ARTIST_MAP" --m3u "$M3U_FILE" --db "$DB" --result-file "$RESULT_FILE" \
  "${PROC_EXTRA[@]}"
PY_RC=$?
# shellcheck disable=SC1090
[ -s "$RESULT_FILE" ] && . "$RESULT_FILE"      # sets new= / failed=
NEW="${new:-0}"; FAILED="${failed:-0}"

# ---- 7. Navidrome rescan -----------------------------------------------------------
rescan_navidrome() {
  if [ -z "${ND_USER:-}" ] || [ -z "${ND_PASS:-}" ]; then
    log "ND_USER/ND_PASS not set; skipping Navidrome rescan"; return 0
  fi
  local salt token resp
  salt="$(head -c 8 /dev/urandom | od -An -tx1 | tr -d ' \n')"
  token="$(printf '%s%s' "$ND_PASS" "$salt" | md5sum | cut -d' ' -f1)"   # Subsonic token auth
  resp="$(curl -fsS -G --max-time 20 "$NAVIDROME_URL/rest/startScan" \
            --data-urlencode "u=$ND_USER" --data-urlencode "t=$token" --data-urlencode "s=$salt" \
            --data-urlencode "v=1.16.1" --data-urlencode "c=yt-sync" --data-urlencode "f=json")" \
    || { log "WARN: could not reach Navidrome at $NAVIDROME_URL"; return 1; }
  if printf '%s' "$resp" | grep -Eq '"status": ?"ok"'; then
    log "Navidrome rescan triggered"
  else
    log "WARN: Navidrome rejected the scan request: $resp"; return 1
  fi
}

if [ "$DO_RESCAN" = 1 ] && { [ "$NEW" -gt 0 ] || [ "${FORCE_RESCAN:-0}" = 1 ]; }; then
  rescan_navidrome
else
  log "rescan skipped (new=$NEW, --no-rescan=$((1-DO_RESCAN)))"
fi

log "=== yt-sync done: new=$NEW failed=$FAILED ==="
[ "$PY_RC" -eq 0 ] || exit 1
