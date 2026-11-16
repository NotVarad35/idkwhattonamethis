# Termux Core Packages (Samsung M11)
- **Created / Last Updated:** 16-11-2026 02:59:05
- **Device:** Samsung Galaxy M11 (SM-M115F), rooted — Magisk v30.7, Knox `0x1`
- **Related:** [[progress-state-m11-homelab]] | [[inventory-bom#Compute & Devices]]

## Installed Packages
| Package | Purpose |
|---|---|
| `openssh` | `sshd` on port `8022` for laptop → phone control |
| `termux-tools` | Core Termux utilities (`termux-*` helpers) |
| `termux-services` | Service supervision for long-running daemons |
| `tmux` | Persistent terminal sessions that survive SSH drops |
| `navidrome` | Music server / streaming backend for the jukebox |
| `ffmpeg` | FLAC ↔ WAV conversion and metadata work |
| `wget` | Direct downloads (APKs, release tarballs, mirrors) |
| `tar` | Archive extraction for releases and backups |
| `nano` | Simple on-device text editor |

## Install Command
```bash
pkg update -y && pkg install openssh termux-tools termux-services tmux navidrome ffmpeg wget tar nano -y
```

## Notes
- Keep this list in sync with `pkg list-installed` on the device.
- Nothing here replaces the hard locks: **Samsung Settings** and **Device Drivers** are never touched by package operations.
