# Master Project Router (`idkwhattonamethis`)
- **Last Updated:** 15-11-2026 19:10:38
- **Master Inventory:** [[inventory-bom]]
- **Master To-Do:** [[Todo]]
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
- **CRITICAL LOCK:** NEVER touch or delete **Samsung Settings** (`com.android.settings`) or **Device Drivers**. Also keep: Magisk, ACC, Termux, OpenSSH, Linux Deploy, and `mpv` (CLI audio; no VLC). The One UI core (launcher, SystemUI, telephony, providers) stays; only apps are stripped.
- **Browser:** Firefox (armeabi-v7a APK) installed via ADB on 14-11-2026; Chrome removal only after that.
- **Completed:** Unlocked bootloader, wiped device, flashed Magisk v30.7 via Odin, bypassed setup screen, verified root, and turned off auto-updates.
- **Currently doing:** Re-establishing base infrastructure: Re-debloating One UI and managing the 24/7 battery charge limit via the ACC Magisk module.
- **Left to do:** 
  1. ~~Re-run ADB debloat pass~~ — done 14-11-2026 21:26:16, 325 -> 166 packages (details in [[states/progress-state-m11-debloat]]).
  2. Install ACC module for battery hard-cap.
  3. Re-install Termux and OpenSSH (Port 8022).
  4. Spin up native Debian via Linux Deploy.
  5. Seed initial FLAC library (Yorushika album + singles) over SCP.
  6. Implement Automated Wallpaper Cycler via Termux:API and cron (Details in [[Todo#Automated Wallpaper Cycler for Samsung M11]]).

## Module 3: ESP32 + I2S Network Jukebox (M11 as Audio Host)
- **Linked State File:** [[states/progress-state-jukebox-esp32]]
- **Architecture (pivot 15-11-2026):** **NO MicroSD card on the jukebox.** The Samsung M11 is the sole storage hub and wireless audio host; the ESP32 streams the library over 2.4GHz Wi-Fi and outputs I2S to a DAC.
- **Active parts:** I2S DAC module (GY-PCM5102A or UDA1334A) + 2.0-inch square IPS LCD (ST7789V, SPI) for album art.
- **Deprecated:** DFPlayer Mini for standalone playback — it is an SD-card-only decoder and cannot stream.
- **Enclosure:** **16 cm x 16 cm x 16 cm** cube — 1:1 Minecraft pixel ratio (**1 px = 1 cm**).
- **Supposed to do:** Build a network-attached jukebox on the breadboard: ESP32 pulls audio from the M11 (Navidrome), decodes it to I2S, and renders album art on the ST7789V.
- **Completed:** Verified CP2102 COM4 serial connection; benched the unsoldered RC522; locked the network-audio architecture, the new parts list, and the 16 cm cube enclosure.
- **Currently doing:** On hold awaiting the I2S DAC and ST7789V display before any rewiring.
- **Left to do:** Wire I2S DAC → TRRS breakout, bring up the ST7789V over SPI, write the streaming client, then add encoder/button controls and cut the cube.

## Module 4: NFC Album Wall Posters
- **Supposed to do:** Repurpose NTAG213 stickers onto room album posters to trigger playback when scanned by a primary smartphone.
- **Completed:** Verified NTAG213 read/write capability.
- **Currently doing:** On hold until physical posters are acquired.
