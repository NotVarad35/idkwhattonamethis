# State Tracker: Samsung M11 DAP & Homelab
- **Problem Category:** Software / Homelab / Android Root & Linux Deploy
- **Created / Last Updated:** 14-11-2026 19:55:15
- **Related Links:** [[progress-state#Module 2: Samsung Galaxy M11 (DAP + 2.4GHz Homelab)]] | [[inventory-bom#Compute & Devices]]

## 1. What Happened / Context
- **The Pivot to Root:** Standard Termux on an unrooted Samsung One UI kernel blocks the Linux namespaces and cgroups required for Docker. To get bare-metal containerized freedom for our automation scripts and music server, we decided to root the device.
- **The Factory Reset:** Unlocking the bootloader to flash Magisk forced a mandatory hardware wipe of the `/data` partition. All previous Termux, SSH, and ADB debloat configurations were erased. Knox is permanently tripped (`0x1`).
- **Root Achieved:** Successfully flashed a Magisk-patched AP file via Odin. Magisk v30.7 is installed with Ramdisk active.
- **Prior Baseline (pre-root, now erased):** Unrooted setup had reached 20 GB free on `/data`, static IP `192.168.1.110`, `sshd` on `:8022` as user `u0_a253`, plus 32-bit `arm-v7a` APKs and a `~/sdcard` symlink to the 64GB card. All of it is gone post-wipe; only the router's DHCP reservation (Phone MAC) survives.
- **Hard Rule:** Never touch or remove **Samsung Settings** or **Device Drivers**. Montray was also deleted.

## 2. Tracker
- **Supposed to do:** Rebuild the homelab environment from scratch, this time utilizing root access for kernel-level battery management and a true Debian chroot (Linux Deploy) instead of standard Termux.
- **What we actually did:** Unlocked bootloader, wiped device, flashed Magisk v30.7 via Odin, bypassed setup screen, verified root (`uid=0(root)`), and turned off auto-updates to protect the patched boot image.
- **Currently doing:** Re-establishing base infrastructure: re-debloating One UI and managing the 24/7 charge limit via the ACC Magisk module (or the native One UI 85% cap).
- **Left to do:** 
  1. Re-run ADB debloat script to free up RAM on the 3GB device.
  2. Implement kernel-level charge limit (ACC) so the phone can stay plugged in safely 24/7.
  3. Re-install F-Droid, Termux (root shell), and OpenSSH (Port `8022`).
  4. Spin up a native Debian environment via Linux Deploy (chroot) to host Navidrome and the `yt-dlp` cron automation scripts.

## 3. Unexpected Roadblocks & Fixes Employed
- **Unexpected:** Bootloader unlock silently forced a full `/data` wipe and tripped Knox (`0x1`), destroying the working unrooted Termux/SSH baseline.
- **Fix:** Accepted the wipe as the cost of root; rebuilding in a fixed order (debloat → ACC charge cap → SSH → Linux Deploy) so no step depends on lost state.
- **Unexpected:** Standard Termux could not provide Docker's namespaces/cgroups on the stock Samsung kernel.
- **Fix:** Rooted the device (Magisk v30.7) and pivoted to a Linux Deploy Debian chroot.
- **Unexpected:** `ls -l /storage` failed with `Permission denied`, and 64-bit APKs failed with `INSTALL_FAILED_NO_MATCHING_ABIS` (pre-root baseline).
- **Fix:** Switched to 32-bit `arm-v7a` standalone APKs; ran `termux-setup-storage` and mapped storage via `~/storage/external-1` (`/storage/43CC-5E0C`). To be re-applied post-root.
