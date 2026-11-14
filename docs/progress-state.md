# Master Project Router (`idkwhattonamethis`)
- **Last Updated:** 14-11-2026 20:07:00
- **Master Inventory:** [[inventory-bom]]
- **Chronological History:** [[history-master]]

---

## Module 1: Workspace & Multi-Agent System (Antigravity + OpenCode)
- **Supposed to do:** Set up local monorepo, VS Code Antigravity, OpenCode UI, private GitHub repo (`NotVarad35/idkwhattonamethis`), and Obsidian-linked modular `.md` tracking.
- **Completed:** Initialized repository, configured agent guidelines (`.gemini/styleguide.md` and `opencode.json`), and enforced strict `DD-MM-YYYY HH:mm:ss` timestamp standards.
- **Currently doing:** Managing task handoffs between Antigravity (`@architect`) and OpenCode (`@coder`).
- **Left to do:** Test multi-agent command execution.

## Module 2: Samsung Galaxy M11 (DAP + 2.4GHz Homelab)
- **Linked State File:** [[states/progress-state-m11-homelab]]
- **Hardware Profile:** Snapdragon 450, 3GB RAM, 32GB Internal ROM, 64GB MicroSD (`43CC-5E0C`), 2.4GHz Wi-Fi (`192.168.1.110`), 3.5mm Headphone Jack.
- **State Change (ROOTED):** Device was wiped to unlock bootloader. Magisk v30.7 is active. Knox is 0x1. Previous un-rooted environment is gone.
- **CRITICAL LOCK:** NEVER touch or delete **Samsung Settings** (`com.android.settings`) or **Device Drivers**.
- **Completed:** Unlocked bootloader, wiped device, flashed Magisk v30.7 via Odin, bypassed setup screen, verified root, and turned off auto-updates.
- **Currently doing:** Re-establishing base infrastructure: Re-debloating One UI and managing the 24/7 battery charge limit via the ACC Magisk module.
- **Left to do:** 
  1. Re-run ADB debloat pass.
  2. Install ACC module for battery hard-cap.
  3. Re-install Termux and OpenSSH (Port 8022).
  4. Spin up native Debian via Linux Deploy.
  5. Seed initial FLAC library (Yorushika album + singles) over SCP.

## Module 3: ESP32 + DFPlayer Physical Jukebox
- **Linked State File:** [[states/progress-state-jukebox-esp32]]
- **Hardware Note:** Currently has NO MicroSD card inserted (the single 64GB card is active in the Samsung M11).
- **Supposed to do:** Build a standalone, offline hardware jukebox on a breadboard.
- **Completed:** Verified CP2102 COM4 serial connection and benched unsoldered RC522 NFC module.
- **Currently doing:** On hold while M11 storage and Linux Deploy rebuilding are completed.
- **Left to do:** Source a dedicated MicroSD card for the DFPlayer Mini and rebuild breadboard wiring from zero.

## Module 4: NFC Album Wall Posters
- **Supposed to do:** Repurpose NTAG213 stickers onto room album posters to trigger playback when scanned by a primary smartphone.
- **Completed:** Verified NTAG213 read/write capability.
- **Currently doing:** On hold until physical posters are acquired.
