# Project Ecosystem: Active Progress State

## System Rule for AI Agents
Every specialized chat MUST read this file first and update its respective module block below upon completing any step.

---

## Module 1: Workspace & AI Environment
- **Supposed to do:** Set up local monorepo, VS Code + Antigravity, private GitHub repo, and multi-chat `.md` tracking.
- **Completed:** Designed directory structure and agent sync rules.
- **Currently doing:** Initializing Git repo and pasting baseline `.md` files.
- **Left to do:** First `git push` to private GitHub repository.

## Module 2: Samsung Galaxy M11 (DAP + 2.4GHz Homelab)
- **Specs:** 3GB RAM | 23GB/32GB Internal Used | 64GB MicroSD Installed | One UI (Android) | 2.4GHz Wi-Fi.
- **Supposed to do:** Debloat via ADB, keep core apps (Settings, CX File Explorer, Montray/SpotiFLAC, YouTube ReVanced, Tailscale), install Linux terminal (Termux), and configure OpenSSH Server for PC control.
for now delete Montray also. THINGS NOT TO DELETE NO MATTER WHAT IS samsung Settings and Device Drivers.
- **Completed:** Initial Google/Samsung system app removal via ADB; core media apps installed.
- **Currently doing:** Installing F-Droid Termux, configuring `sshd` on Port 8022, and mapping 64GB SD card permissions.
- **Left to do:** Connect via PowerShell SSH from laptop and lock in One UI background battery exemptions.

## Module 3: ESP32 + DFPlayer Physical Jukebox
- **Supposed to do:** Build standalone offline Jukebox with tactile buttons and local Web UI.
- **Completed:** 
  - Formatted 64GB SD card to FAT32; converted 15 test tracks via FFmpeg to 16-bit 44.1kHz WAV in `/mp3/0001.wav`–`0015.wav`.
  - Wired DFPlayer Mini (`VIN`, `GND`, `TX2/GPIO17`, `RX2/GPIO16`) and TRRS 3.5mm breakout (`DAC_L`, `DAC_R`, `GND`).
  - Solved CP2102 COM4 driver and Micro-USB data cable upload.
  - Removed unsoldered RC522 NFC module.
- **Currently doing:** Wiring 3 tactile push buttons (`GPIO 25, 26, 27` -> `GND`) and flashing hybrid Web UI + Button C++ firmware.
- **Left to do:** Wire KY-040 rotary encoder, test 18650 battery + TP4056 + 5V boost chain.

## Module 4: NFC Album Wall Posters
- **Supposed to do:** Repurpose NTAG213 stickers onto room album posters to trigger playback when scanned by phone.
- **Completed:** Verified NTAG213 read/write works using daily phone's NFC scanner.
- **Currently doing:** Planning webhook/playback trigger between phone scanner and M11/Jukebox.
- **Left to do:** Buy album posters, stick tags, map UIDs/URLs.