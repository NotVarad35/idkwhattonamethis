# State Tracker: Samsung M11 DAP & Homelab
- **Problem Category:** Software / Homelab / Android Root & Storage
- **Created / Last Updated:** 15-11-2026 05:54:09
- **Related Links:** [[progress-state#Module 2: Samsung Galaxy M11 (DAP + 2.4GHz Homelab)]] | [[inventory-bom#Compute & Devices]]

## 1. What Happened / Context
- Repurposed a Samsung Galaxy M11 (3GB/32GB) with our single 64GB MicroSD card (`43CC-5E0C`) as an offline FLAC player and 2.4GHz Wi-Fi micro-homelab (`192.168.1.110`).
- **The Pivot to Root:** Standard Termux on an unrooted Samsung kernel blocks Docker's required namespaces. We pivoted to root to unlock Linux Deploy (chroot). Note that the bootloader unlock forced a mandatory `/data` wipe (Knox 0x1), erasing previous Termux/SSH setups. Magisk v30.7 is now active.
- **File Organization Strategy:** Building a clean FLAC library from scratch on the 64GB MicroSD.
- **Role Change (15-11-2026):** This M11 is now the project's **sole storage hub and wireless audio host** for the jukebox — the ESP32 has no SD card and streams the library from here over Wi-Fi (see [[progress-state-jukebox-esp32]]).

## 2. Tracker
- **Supposed to do:** Rebuild the homelab environment from scratch (this time utilizing root access for kernel-level battery management and a true Debian chroot) and seed the initial music library.
- **What we actually did:** Unlocked bootloader, wiped device, flashed Magisk v30.7 via Odin, bypassed setup screen, verified root, and turned off auto-updates. Instructed Claude Code to audit the One UI OS for a deeper debloat pass.
- **Currently doing:** Re-establishing base infrastructure: Re-debloating One UI, managing the 24/7 battery charge limit via the ACC Magisk module, and preparing the first SCP music transfer.
- **Left to do:** 
  1. Approve Claude's deep ADB debloat list and execute.
  2. Install ACC module for battery hard-cap. 
  3. Re-install Termux and OpenSSH (Port 8022). 
  4. Manually seed the library via SCP: Yorushika's debut album (`夏草が邪魔をする`) and 5 singles (`思想犯`, `春泥棒`, `晴る`, `忘れてください`, `アポリア`).
  5. Spin up native Debian via Linux Deploy.
  6. Implement Automated Wallpaper Cycler via Termux:API and cron (Details in [[Todo#Automated Wallpaper Cycler for Samsung M11]]).
