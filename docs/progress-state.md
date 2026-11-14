# Master Project Router (`idkwhattonamethis`)
- **Last Updated:** 14-11-2026 19:55:15
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
- **Hardware Profile:** 3GB RAM | 32GB Internal | 64GB MicroSD (`43CC-5E0C`) | 2.4GHz Wi-Fi (static `192.168.1.110` via DHCP reservation) | 3.5mm Audio Jack.
- **State Change (ROOTED):** Device was wiped to unlock bootloader. Magisk v30.7 is active. Knox is `0x1`. Previous un-rooted environment is gone.
- **CRITICAL LOCK:** NEVER touch or delete **Samsung Settings** or **Device Drivers**.
- **Supposed to do:** Rebuild the homelab from scratch on root: kernel-level battery management plus a true Debian chroot (Linux Deploy) instead of standard Termux.
- **Completed:** Bootloader unlock, Odin Magisk v30.7 AP flash, setup-screen bypass, root verification (`uid=0`), and OS auto-updates disabled.
- **Currently doing:** Rebuilding baseline: re-debloating One UI and implementing a root-level charge limit (ACC Magisk module or native 85% cap) for 24/7 operation.
- **Left to do:** Re-run ADB debloat, install ACC charge cap, restore OpenSSH (`:8022`) and SD card mapping, then build a Linux Deploy Debian chroot for Navidrome and the `yt-dlp` cron scripts.

## Module 3: ESP32 + DFPlayer Physical Jukebox
- **Linked State File:** [[states/progress-state-jukebox-esp32]]
- **Hardware Note:** Currently has NO MicroSD card (the single 64GB card is in the M11; see [[inventory-bom#Storage]]).
- **Supposed to do:** Build standalone offline Jukebox on breadboard.
- **Completed:** Verified CP2102 COM4 flashing[cite: 3] and removed unsoldered RC522 NFC module[cite: 3].
- **Currently doing:** **Scrapped previous buggy Web UI & wiring — redoing all the work from scratch on the breadboard, on hold while the M11 root/Linux Deploy rebuild lands first.**
- **Left to do:** Decide SD card allocation for DFPlayer Mini, re-verify clean breadboard wiring from zero, and write fresh modular C++ code step-by-step.

## Module 4: NFC Album Wall Posters
- **Supposed to do:** Repurpose 5x NTAG213 stickers onto room album posters to trigger playback when scanned by Nothing Phone (2a)[cite: 2, 3].
- **Completed:** Verified NTAG213 read/write works using phone NFC scanner.
- **Currently doing:** On hold until physical album posters are purchased.