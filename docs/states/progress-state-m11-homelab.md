# Samsung Galaxy M11 DAP & Homelab Setup Log

## 1. What We Did
* **Targeted Debloat:** Removed One UI telemetry, Bixby, GOS (Game Optimization Service), Samsung/Google keyboards, Samsung Messages, Google Search/Drive, My Files, Theme Center, and Montray via ADB (`user 0`).
* **Core App Installation:** Retained essential utilities and installed replacements (`CX File Explorer`, `Gboard`, `VLC`, `YouTube ReVanced`).
* **Linux Terminal & SSH Server:** Installed Termux, configured OpenSSH on port `8022`, set up password authentication, and added `sshd` to `.bashrc` for auto-start on boot.
* **Storage Mapping:** Granted Termux storage permissions and mapped the 64GB MicroSD card root volume (`/storage/43CC-5E0C`).
* **Audio Testing:** Transferred FLAC tracks from the laptop via SCP and verified command-line playback using `mpv` inside Termux.

## 2. What Went Unexpected
* **Cloudflare Bot Challenges:** Attempting to download APKs via PowerShell `Invoke-WebRequest` from APKPure triggered JavaScript verification walls, breaking automated pulls.
* **PowerShell SCP Parsing Errors:** Windows PowerShell misinterpreted drive letter colons (`E:\`) as remote host delimiters, and unescaped spaces in file paths caused OpenSSH to throw `Could not resolve hostname e` errors.

## 3. What Solutions We Employed
* **Direct Mirroring / Manual Pulls:** Bypassed Cloudflare blocks by sourcing clean APKs directly or downloading them via browser manually.
* **Path Quoting & Working Directory Switch:** Resolved SCP syntax errors by wrapping local file paths in single quotes (`'...'`) and changing the active PowerShell directory (`cd`) directly into the target folder before executing transfers.

## 4. What Went Out of Plan
* **Scope Adjustments:** Expanded the initial debloat list mid-stream to strip out Samsung Messages, Samsung Keyboard, My Files, and Google Drive based on your lean-setup preference.
* **Deferred Tailscale:** Decided to omit Tailscale configuration for now, relying instead on local Wi-Fi and ultra-fast USB port forwarding (`adb forward`) for control and file management.
