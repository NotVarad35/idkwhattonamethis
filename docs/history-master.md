# Project History, Filtered Milestones & Incident Logs
- **Last Updated:** 15-11-2026 05:54:09

## Part 1: Filtered Chronological Story (What Happened Till Now)

### 1. The Origin Idea
- Started with the concept of a tactile, offline physical media ecosystem[cite: 1]: a standalone **Minecraft Jukebox**[cite: 1, 2] (and a conceptual "Sleeper DVD Player" idea, though the Sleeper build is currently shelved/myth status because Raspberry Pi 4 and projectors are way too expensive right now).

### 2. The DAP Search & The Free Samsung M11 Pivot (Points 3 & 5)
- Initially explored building a custom Raspberry Pi Zero 2 W dual-screen DAP or hunting for a used iPod Classic / iPhone SE 1st Gen[cite: 1].
- **Current Working Idea:** Got a **Samsung Galaxy M11 (3GB RAM, 32GB storage + 64GB MicroSD card)** for free. While no plan is locked in stone until we build it, the current idea is using the M11 both as an offline FLAC music player and a lightweight 2.4GHz Wi-Fi micro-homelab running automated daily/weekly scripts.

### 3. Sourcing the Jukebox Electronics (Points 6 & 7 Combined)
- Ordered the solderless Jukebox electronics across **Robu.in** and **FlyRobo** (~₹1,026 total) alongside a **DT830D Digital Multimeter** for checking voltages and continuity[cite: 1, 2].

### 4. Breadboard Width & Audio Wiring (Points 9 & 10 Combined)
- **ESP32 Width Issue:** Discovered the 30-pin ESP32 board is too wide for a 400-point breadboard (straddling leaves pins hanging outside Row J)[cite: 7]. Kept the ESP32 off-board and bridged connections with Dupont jumper wires[cite: 2, 7].
- **Audio Wiring:** Seated the **DFPlayer Mini** across the breadboard center trench (Rows 2–9) and wired it to the **TRRS 3.5mm AUX breakout board** (Rows 27–30: `DAC_L`, `DAC_R`, `GND`)[cite: 2].

### 5. 64GB SD Card & FFmpeg Audio Pipeline (Points 11, 12, 13)
- **FAT32 Limit Bypass:** Bypassed Windows' 32GB FAT32 limit on the 64GB MicroSD card using `GUIFormat` / PowerShell `Format-Volume`[cite: 2].
- **FFmpeg Batch Conversion:** Used FFmpeg CLI in PowerShell to batch-convert 16-bit/24-bit/32-bit FLAC tracks into DFPlayer-compatible **16-bit, 44.1kHz stereo WAV** files[cite: 2, 3].
- **DFPlayer Folder Rules:** Discovered DFPlayer cannot read nested text folders (`/mp3/playlist/`) and caps numbered folders (`/01/`) at 255 tracks[cite: 3]. Standardized on `/mp3/0001.wav` through `0015.wav` for testing[cite: 2, 3].

### 6. Arduino IDE Cache Crash & USB Data Cable Fix (Points 14, 15, 16)
- **`EISDIR` Read-Only Bug:** Fixed an Arduino IDE 2.x crash where a mismatched folder/sketch name (`mcjukebox` vs `mc.ino`) created a locked temp directory[cite: 3]. Purged `$env:LOCALAPPDATA\Temp\.arduinoIDE*` and matched the folder/file names[cite: 3].
- **Charge-Only Cable Trap:** First upload failed (`No serial data received`) because the old Micro-USB cable only had power lines and `COM3` was an internal Intel port[cite: 2].
- **Clean Flash:** Bought a proper **Micro-USB data cable**, detected the ESP32's **Silicon Labs CP2102** chip on **COM4**, and flashed the board cleanly at 921600 baud[cite: 2].

### 7. The NFC Failure, Web UI Bugs & Breadboard Reboot (Points 17, 18, 19)
- **RC522 Un-Soldered Pin Failure:** The RC522 RFID reader failed to detect tags on the ESP32 because its header pins were unsoldered, causing contact bounce and unstable voltage (3.10V–3.53V)[cite: 2].
- **Web UI Bug & Pause:** Removed the RC522 wires and built a local ESP32 Wi-Fi Web UI + rotary/button setup[cite: 2]. The Web UI had a lot of bugs, which led to pausing/scrapping the build temporarily with the thought of waiting until getting a soldering iron—**but now we are reviving it on the breadboard first** and iterating step-by-step.
- **NFC Wall Poster Concept:** Tested the NTAG213 stickers with the phone's built-in NFC reader and confirmed they read/write properly. Plan to stick them onto room **album cover posters**—exact payload/action to write on the poster tags remains undecided until the physical posters arrive.

---

## Part 2: Incident Recovery Report — Restoring `.gemini` & Migrating to Antigravity

### 1. What Happened
- During initial workspace setup for `minecraft-audio-ecosystem`, the PowerShell script created `docs`, `jukebox-esp32`, and `m11-homelab`, but omitted `.gemini/styleguide.md`.
- Attempting to use the legacy *Gemini Code Assist* VS Code extension threw a deprecation notice (*"This client is no longer supported for Gemini Code Assist for individuals"*).

### 2. Resolution Employed
- Uninstalled legacy *Gemini Code Assist* and installed the **Antigravity** developer suite extension, authenticating with the Google AI Pro account.
- Created `.gemini\styleguide.md` using `-Force` flags in PowerShell and applied the multi-chat Shared Brain Sync rules.

---

## Part 3: Samsung Galaxy M11 DAP & Homelab Setup Log

### 1. What We Did
- **Targeted ADB Debloat (`user 0`):** Removed One UI telemetry, Bixby, GOS (Game Optimization Service), Samsung/Google keyboards, Samsung Messages, Google Search/Drive, My Files, Theme Center, and Montray.
- **Core App Stack:** Kept essential settings and installed `CX File Explorer`, `Gboard`, `VLC`, and `YouTube ReVanced`.
- **Linux Terminal & SSH Server:** Installed Termux, configured OpenSSH (`sshd`) on port `8022` with password auth, and added `sshd` to `~/.bashrc` for auto-start.
- **Storage Mapping:** Granted storage permissions and mapped the 64GB MicroSD card at `/storage/43CC-5E0C`.
- **CLI Audio Verification:** Transferred FLAC tracks from laptop via SCP and verified playback using `mpv` inside Termux.

### 2. Unexpected Roadblocks & Solutions
- **Cloudflare Bot Walls:** PowerShell `Invoke-WebRequest` pulls from APKPure hit Cloudflare JS challenges -> Bypassed via direct browser/mirror downloads.
- **PowerShell SCP Colon/Space Errors:** OpenSSH treated `E:\` as a remote host delimiter (`Could not resolve hostname e`) -> Fixed by `cd`-ing directly into the target directory and wrapping filenames in single quotes (`'...'`).

### 3. Scope Adjustments
- Stripped additional system apps (Messages, Keyboard, My Files, Drive) for maximum RAM savings on the 3GB M11.
- Deferred Tailscale setup in favor of local 2.4GHz Wi-Fi SSH and zero-latency USB port forwarding (`adb forward tcp:8022 tcp:8022`).
- **Future Addition Queued:** Automated daily/weekly background scripts running on the M11 via Termux cron/job scheduler.

---

## Part 4: Root, Deep Debloat & the Network-Audio Pivot (14-11-2026 → 15-11-2026)

### 1. M11 Rooted — and Wiped
- Standard Termux on the unrooted One UI kernel blocks the cgroups/namespaces Docker needs, so the M11 was rooted to enable Linux Deploy (chroot).
- Unlocking the bootloader forced a mandatory `/data` wipe and tripped Knox (`0x1`), destroying the working unrooted Termux/SSH baseline. Magisk v30.7 was flashed via Odin and root verified (`uid=0`); auto-updates were disabled to protect the patched boot image.

### 2. Post-Root Debloat Round 2
- Package count went **325 → 166** via `pm uninstall -k --user 0`. Removed Samsung/Google bloat, telemetry, Play Store, Gallery/My Files, Edge panels, and all wallpaper packages. Kept the hard locks (Samsung Settings, device drivers, telephony core) plus Magisk, Termux, Firefox, and the launcher (freezing it broke Recents).
- Details: [[states/progress-state-m11-debloat]].

### 3. Jukebox Architecture Pivot (15-11-2026)
- **No MicroSD card on the jukebox.** The ESP32 is now a Wi-Fi audio client; the M11 is the sole storage hub and wireless audio host (Navidrome at `192.168.1.110`).
- **DFPlayer Mini deprecated** for playback (SD-card-only decoder, cannot stream). Replaced by an I2S DAC module (GY-PCM5102A or UDA1334A), with a 2.0-inch ST7789V IPS display for album art.
- Enclosure fixed at a **16 cm x 16 cm x 16 cm** cube — 1:1 Minecraft pixel ratio (1 px = 1 cm). See [[inventory-bom#3. Enclosure Spec (Target)]].