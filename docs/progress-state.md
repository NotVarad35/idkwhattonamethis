# Master Project Router (`idkwhattonamethis`)
- **Last Updated:** 06-11-2026 08:20:00
- **Master Inventory:** [[inventory-bom]]
- **Chronological History:** [[history-master]]

---

## Module 1: Workspace & Multi-Agent System (Antigravity + OpenCode)
- **Supposed to do:** Set up `D:\project\idkwhattonamethis`, VS Code Antigravity, OpenCode UI, private GitHub repo (`NotVarad35/idkwhattonamethis`), and Obsidian-linked modular `.md` tracking.
- **Completed:** Migrated to Antigravity, created `.gemini/styleguide.md`[cite: 1], pushed initial commit to GitHub, designed `opencode.json` multi-agent config.
- **Currently doing:** Configuring OpenCode UI and linking per-chat state files in `docs/states/`[cite: 1].
- **Left to do:** Switch GitHub repo visibility to Private and test first `@architect` -> `@coder` handoff.

## Module 2: Samsung Galaxy M11 (DAP + 2.4GHz Homelab)
- **Linked State File:** [[states/progress-state-m11-homelab]]
- **Specs:** 3GB RAM | 32GB Internal ([Pending verification - run `df -h /data`]; see [[inventory-bom#Compute & Devices]]) | 64GB MicroSD (`43CC-5E0C`) symlinked at `~/sdcard` | 2.4GHz Wi-Fi (static `192.168.1.110`, SSH on `:8022`) | 3.5mm Jack.
- **CRITICAL LOCK:** NEVER touch or delete **Samsung Settings** or **Device Drivers**.
- **Supposed to do:** Factory reset phone, debloat via ADB (remove Montray too), keep core apps (`Samsung Settings`, `Device Drivers`, `CX File Explorer`, `YouTube ReVanced`, `VLC`, `Gboard`), install `Termux`, and configure `OpenSSH` (`:8022`) for PC control.
- **Completed:** Clean reset, account-free setup, deep ADB debloat, OpenSSH configured on port 8022 (`u0_a253@192.168.1.110`), and SD card filesystem symlinked (`~/sdcard`).
- **Currently doing:** Finalizing SD card storage structure (`~/sdcard/Music/FLAC`) and checking internal storage recovery.
- **Left to do:** Audit final free internal storage space and write first lightweight media/status script.

## Module 3: ESP32 + DFPlayer Physical Jukebox
- **Linked State File:** [[states/progress-state-jukebox-esp32]]
- **Hardware Note:** Currently has NO MicroSD card (the single 64GB card is in the M11; see [[inventory-bom#Storage]]).
- **Supposed to do:** Build standalone offline Jukebox on breadboard.
- **Completed:** Verified CP2102 COM4 flashing[cite: 3] and removed unsoldered RC522 NFC module[cite: 3].
- **Currently doing:** **Scrapped previous buggy Web UI & wiring — redoing all the work from scratch on the breadboard.**
- **Left to do:** Decide SD card allocation for DFPlayer Mini, re-verify clean breadboard wiring from zero, and write fresh modular C++ code step-by-step.

## Module 4: NFC Album Wall Posters
- **Supposed to do:** Repurpose 5x NTAG213 stickers onto room album posters to trigger playback when scanned by Nothing Phone (2a)[cite: 2, 3].
- **Completed:** Verified NTAG213 read/write works using phone NFC scanner.
- **Currently doing:** On hold until physical album posters are purchased.