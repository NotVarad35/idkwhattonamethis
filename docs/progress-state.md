# Master Project Router (`idkwhattonamethis`)
- **Last Updated:** 06-11-2026
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
- **Specs:** 3GB RAM | 32GB Internal (9GB free pre-debloat; update bracket post-debloat in [[inventory-bom#Compute & Phones]]) | 64GB MicroSD (`43CC-5E0C`) installed | 2.4GHz Wi-Fi | 3.5mm Jack.
- **CRITICAL LOCK:** NEVER touch or delete **Samsung Settings** or **Device Drivers**.
- **Supposed to do:** Debloat via ADB (removed Montray too), keep core apps (`Samsung Settings`, `Device Drivers`, `CX File Explorer`, `YouTube ReVanced`, `VLC`, `Gboard`), install `Termux`, and configure `OpenSSH` (`:8022`) for PC control.
- **Completed:** ADB debloat pass, Termux + OpenSSH running on port 8022, 64GB SD card mapped, verified CLI FLAC playback via `mpv`.
- **Currently doing:** Checking post-debloat free internal storage space and planning automated weekly/daily Termux scripts.
- **Left to do:** Configure Termux `crond` task scheduler for automated scripts.

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