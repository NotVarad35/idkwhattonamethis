# State Tracker: Samsung M11 DAP & Homelab
- **Problem Category:** Software / Homelab / Android ADB & Termux
- **Created / Last Updated:** 06-11-2026 08:37:07
- **Related Links:** [[progress-state#Module 2: Samsung Galaxy M11 (DAP + 2.4GHz Homelab)]] | [[inventory-bom#Compute & Devices]]

## 1. What Happened / Context
- Repurposed a free Samsung Galaxy M11 (3GB/32GB) with our single 64GB MicroSD card (`/storage/43CC-5E0C`) as an offline FLAC player and lightweight 2.4GHz Wi-Fi Linux homelab.
- **Storage Reality Check & Recovery:** Initial check showed only 2.6 GB free due to pre-existing user data. After factory data reset and deep debloat pass, `df -h /data` confirmed **20 GB free** (3.0 GB used out of 23 GB total partition, 14% use).
- **Fresh Reset:** Completed fresh factory data reset without adding Google/Samsung accounts.
- **Deep Debloat:** Executed deep debloat purge using `pm clear` and `pm uninstall --user 0`.
- **Static IP:** Locked static IP to `192.168.1.110` via router DHCP reservation using the device's Phone MAC address.
- **32-bit APKs:** Installed 32-bit standalone packages: `Gboard` (nodpi arm-v7a), `Termux` (arm-v7a), and `CX File Explorer`.
- **Hard Rule:** Never touch or remove **Samsung Settings** or **Device Drivers**. Montray was also deleted.

## 2. Tracker
- **Supposed to do:** Debloat One UI via ADB, set up Termux + OpenSSH (`:8022`), and test local FLAC playback.
- **What we actually did:** Ran clean reset, stripped bloat, locked static IP `192.168.1.110`, verified user `u0_a253`, started `sshd` auto-start on port `8022`, rebuilt storage access via `termux-setup-storage`, created `~/sdcard` symlink pointing to external MicroSD, and verified internal storage recovery at 20 GB free.
- **Currently doing:** Organizing `~/sdcard/Music/FLAC` directory structure and preparing FLAC album transfer.
- **Left to do:** 
  1. Transfer test FLAC album to `~/sdcard/Music/FLAC` via SCP/CX File Explorer.
  2. Verify CLI audio playback via `mpv`.
  3. Configure Termux `cron` (`crond` via `cronie`) once automation scripts are written.

## 3. Unexpected Roadblocks & Fixes Employed
- **Unexpected:** Cloudflare blocked PowerShell `Invoke-WebRequest` APK downloads; Windows SCP threw colon/space path errors (`E:\`).
- **Fix:** Downloaded APKs manually via browser; `cd`-ed into source folder and wrapped filenames in single quotes (`'...'`) for SCP.
- **Unexpected:** `ls -l /storage` failed with `Permission denied`, and 64-bit APKs failed with `INSTALL_FAILED_NO_MATCHING_ABIS`.
- **Fix:** Switched to 32-bit `arm-v7a` standalone APKs; ran `termux-setup-storage` and mapped storage via `~/storage/external-1` (`/storage/43CC-5E0C`).