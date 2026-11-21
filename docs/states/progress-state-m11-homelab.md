# State Tracker: Samsung M11 DAP & Homelab
- **Problem Category:** Software / Homelab / Android Root & Storage
- **Created / Last Updated:** 16-11-2026 03:42:09
- **Related Links:** [[progress-state#Module 2: Samsung Galaxy M11 (DAP + 2.4GHz Homelab)]] | [[inventory-bom#Compute & Devices]]

## 1. What Happened / Context
- Repurposed a Samsung Galaxy M11 (3GB/32GB) with our single 64GB MicroSD card (`43CC-5E0C`) as an offline FLAC player and 2.4GHz Wi-Fi micro-homelab (`192.168.1.110`).
- **The Pivot to Root:** Standard Termux on an unrooted Samsung kernel blocks Docker's required namespaces. We pivoted to root to unlock Linux Deploy (chroot). Note that the bootloader unlock forced a mandatory `/data` wipe (Knox 0x1), erasing previous Termux/SSH setups. Magisk v30.7 is now active.
- **File Organization Strategy:** Building a clean FLAC library from scratch on the 64GB MicroSD.
- **Role Change (15-11-2026):** This M11 is now the project's **sole storage hub and wireless audio host** for the jukebox — the ESP32 has no SD card and streams the library from here over Wi-Fi (see [[progress-state-jukebox-esp32]]).

## 2. Tracker
- **Last tracker update:** 20-11-2026 21:56:04 (user clock; derived from machine time with established -47810 s offset)
- **Supposed to do:** Rebuild the homelab environment from scratch (root access for kernel-level battery management and a true Debian chroot), seed the initial music library, and keep the `yt-sync` J-Pop → Navidrome pipeline clean.
- **What we actually did:** Unlocked bootloader, wiped device, flashed Magisk v30.7 via Odin, bypassed setup screen, verified root, and turned off auto-updates. Re-ran the ADB debloat pass (325 → 166 packages, 14-11-2026 21:26:16; see [[states/progress-state-m11-debloat]]). Ran `yt-sync` on the M11 and hit per-artist folders plus 16:9 cover art; on `feat/yt-sync-navidrome` the pipeline now writes every track flat to `MUSIC_DIR/<PLAYLIST_SUBDIR>/`, always embeds 1:1 art (native square or ffmpeg crop, including 480x360 hqdefault → 270x270), and ships `fix_existing.py` to migrate already-downloaded tracks without re-downloading.
- **Currently doing:** Deploying the updated `yt-sync` scripts to the M11 and preparing the one-shot `fix_existing.py` migration against the existing `yt-sync.db` / `.m3u`.
- **Supposed to do:** Rebuild the homelab environment from scratch (this time utilizing root access for kernel-level battery management and a true Debian chroot) and seed the initial music library.
- **What we actually did:** Unlocked bootloader, wiped device, flashed Magisk v30.7 via Odin, bypassed setup screen, verified root, and turned off auto-updates. Instructed Claude Code to audit the One UI OS for a deeper debloat pass.
- **Completed:** Generated the **yt-sync pipeline** — bash wrapper (`yt-sync.sh`), Python processor (`process_track.py`), canonical artist map (`artist_map.json`), plus `yt-sync.env.example` and `README.md` — and merged it into `m11-homelab/configs/yt-sync/` (PR #1, merge `fe9e9d5`).
- **Currently doing:** Deploying scripts to M11 via SSH and testing the first yt-dlp run.
- **Configs Backed Up Locally:** The Termux package list ([[termux-packages]]), the Navidrome config ([[navidrome.toml]]), and the placeholder automation script ([[debloat-and-setup.sh]]) are now versioned in `m11-homelab/configs/`, so a future wipe or re-flash can be rebuilt from the repo instead of memory.
- **Left to do:** 
  1. Install ACC module for battery hard-cap.
  2. Re-install Termux and OpenSSH (Port 8022).
  3. Spin up native Debian via Linux Deploy.
  4. Seed initial FLAC library via SCP: Yorushika's debut album (`夏草が邪魔をする`) and 5 singles (`思想犯`, `春泥棒`, `晴る`, `忘れてください`, `アポリア`).
  5. Deploy updated `yt-sync` scripts and run `fix_existing.py` once on the M11, then verify Navidrome art/layout.
  6. Implement Automated Wallpaper Cycler via Termux:API and cron (Details in [[Todo#Automated Wallpaper Cycler for Samsung M11]]).
