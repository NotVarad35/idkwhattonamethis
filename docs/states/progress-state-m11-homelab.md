# State Tracker: Samsung M11 DAP & Homelab
- **Problem Category:** Software / Homelab / Android ADB & Termux
- **Created / Last Updated:** 06-11-2026 06:31:07
- **Related Links:** [[progress-state#Module 2: Samsung Galaxy M11 (DAP + 2.4GHz Homelab)]] | [[inventory-bom#Compute & Devices]]

## 1. What Happened / Context
- Repurposed a free Samsung Galaxy M11 (3GB/32GB) with our single 64GB MicroSD card (`/storage/43CC-5E0C`) as an offline FLAC player and lightweight 2.4GHz Wi-Fi Linux homelab.
- **Hard Rule:** Never touch or remove **Samsung Settings** or **Device Drivers**. Montray was also deleted.

## 2. Tracker
- **Supposed to do:** Debloat One UI via ADB, set up Termux + OpenSSH (`:8022`), and test local FLAC playback.
- **What we actually did:** Completed ADB debloat (including Montray removal while keeping Samsung Settings & Device Drivers safe), installed `CX File Explorer`, `Gboard`, `VLC`, `YouTube ReVanced`, `Termux`, configured `sshd` auto-start, and played FLAC via `mpv`.
- **Currently doing:** Checking updated free storage space on internal 32GB ROM (to update `[[inventory-bom]]` bracket) and planning automated daily/weekly scripts.
- **Left to do:** Set up `cron` (`crond` via `cronie`) in Termux for scheduled scripts.

## 3. Unexpected Roadblocks & Fixes Employed
- **Unexpected:** Cloudflare blocked PowerShell `Invoke-WebRequest` APK downloads; Windows SCP threw colon/space path errors (`E:\`).
- **Fix:** Downloaded APKs manually via browser; `cd`-ed into source folder and wrapped filenames in single quotes (`'...'`) for SCP.