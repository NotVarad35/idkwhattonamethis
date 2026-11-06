# State Tracker: Samsung M11 DAP & Homelab
- **Problem Category:** Software / Homelab / Android ADB & Termux
- **Created / Last Updated:** 06-11-2026 08:20:00
- **Related Links:** [[progress-state#Module 2: Samsung Galaxy M11 (DAP + 2.4GHz Homelab)]] | [[inventory-bom#Compute & Devices]]

## 1. What Happened / Context
- Repurposed a free Samsung Galaxy M11 (3GB/32GB) with our single 64GB MicroSD card (`/storage/43CC-5E0C`) as an offline FLAC player and lightweight 2.4GHz Wi-Fi Linux homelab.
- **Storage Reality Check:** `df -h /data` showed only 2.6 GB free because the phone was never factory reset, leaving old user data/cache intact.
- **Decision:** Perform a full factory reset first, then re-run the clean ADB debloat pass and reinstall Termux + OpenSSH.
- **Fresh Reset:** Completed fresh factory data reset without adding Google/Samsung accounts.
- **Deep Debloat:** Executed deep debloat purge using `pm clear` and `pm uninstall --user 0`.
- **Static IP:** Locked static IP to `192.168.1.110` via router DHCP reservation using the device's Phone MAC address.
- **32-bit APKs:** Installed 32-bit standalone packages: `Gboard` (nodpi arm-v7a), `Termux` (arm-v7a), and `CX File Explorer`.
- **Hard Rule:** Never touch or remove **Samsung Settings** or **Device Drivers**. Montray was also deleted.

## 2. Tracker
- **Supposed to do:** Debloat One UI via ADB, set up Termux + OpenSSH (`:8022`), and test local FLAC playback.
- **What we actually did:** Ran clean reset, stripped bloat, locked static IP `192.168.1.110`, verified user `u0_a253`, started `sshd` auto-start on port `8022`, rebuilt storage access via `termux-setup-storage`, and created `~/sdcard` symlink pointing to external MicroSD.
- **Currently doing:** Verifying `df -h /data` internal storage recovery and organizing `~/sdcard/Music/FLAC` directory structure.
- **Left to do:** 
  1. Record exact free internal storage GBs in [[inventory-bom]].
  2. Transfer test FLAC album to `~/sdcard/Music/FLAC` via SCP/CX File Explorer.
  3. Configure Termux `cron` (`crond` via `cronie`) once automation scripts are written.

## 3. Unexpected Roadblocks & Fixes Employed
- **Unexpected:** Cloudflare blocked PowerShell `Invoke-WebRequest` APK downloads; Windows SCP threw colon/space path errors (`E:\`).
- **Fix:** Downloaded APKs manually via browser; `cd`-ed into source folder and wrapped filenames in single quotes (`'...'`) for SCP.
- **Unexpected:** `ls -l /storage` failed with `Permission denied`, and 64-bit APKs failed with `INSTALL_FAILED_NO_MATCHING_ABIS`.
- **Fix:** Switched to 32-bit `arm-v7a` standalone APKs; ran `termux-setup-storage` and mapped storage via `~/storage/external-1` (`/storage/43CC-5E0C`).