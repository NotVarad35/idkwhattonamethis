# Samsung Galaxy M11 — Setup Log
- **Last Updated:** 06-11-2026 06:46:33
- **Related Links:** [[progress-state-m11-homelab]] | [[inventory-bom#Compute & Devices]]

---

## 1. ADB Debloat (User 0)

### Removed Packages
```bash
# One UI Telemetry & Bloat
adb shell pm uninstall -k --user 0 com.samsung.android.visionintelligence
adb shell pm uninstall -k --user 0 com.samsung.android.app.spage
adb shell pm uninstall -k --user 0 com.samsung.android.bixby.agent
adb shell pm uninstall -k --user 0 com.samsung.android.bixby.service
adb shell pm uninstall -k --user 0 com.samsung.android.game.gamehome
adb shell pm uninstall -k --user 0 com.samsung.android.game.gametools
adb shell pm uninstall -k --user 0 com.samsung.android.game.gos

# Samsung Apps
adb shell pm uninstall -k --user 0 com.samsung.android.messaging
adb shell pm uninstall -k --user 0 com.samsung.android.themestore
adb shell pm uninstall -k --user 0 com.samsung.android.themecenter
adb shell pm uninstall -k --user 0 com.samsung.android.myfiles
adb shell pm uninstall -k --user 0 com.sec.android.inputmethod

# Google Apps
adb shell pm uninstall -k --user 0 com.google.android.googlequicksearchbox
adb shell pm uninstall -k --user 0 com.google.android.apps.docs
adb shell pm uninstall -k --user 0 com.google.android.inputmethod.latin

# Montray
adb shell pm uninstall -k --user 0 com.samsung.android.montray
```

### CRITICAL — Never Remove
- `com.android.settings` (Samsung Settings)
- Device Drivers (system-level)

### Kept / Installed Apps
| App | Purpose |
|---|---|
| **Samsung Settings** | System settings (LOCKED — never remove) |
| **Device Drivers** | System drivers (LOCKED — never remove) |
| **CX File Explorer** | File management |
| **Gboard** | Keyboard (replaced Samsung & Google keyboards) |
| **VLC** | Media playback |
| **YouTube ReVanced** | Ad-free YouTube |

---

## 2. Termux & OpenSSH Configuration

### Installation
```bash
# After installing Termux (F-Droid / GitHub release):
pkg update && pkg upgrade
pkg install openssh
```

### SSH Server Setup
```bash
# Start SSH server on port 8022
sshd

# Auto-start sshd on every Termux launch
echo "sshd" >> ~/.bashrc
```

### Connection Methods
| Method | Command |
|---|---|
| **Wi-Fi (2.4GHz LAN)** | `ssh user@<M11_IP> -p 8022` |
| **USB (zero-latency)** | `adb forward tcp:8022 tcp:8022` then `ssh localhost -p 8022` |

- **Port:** `8022`
- **Auth:** Password-based

---

## 3. Storage Mapping

```bash
# Grant Termux access to shared storage & SD card
termux-setup-storage
```

| Mount Point | What |
|---|---|
| `~/storage/shared` | Internal shared storage |
| `/storage/43CC-5E0C` | 64GB MicroSD card |

---

## 4. CLI Audio Verification

```bash
# Install mpv
pkg install mpv

# Transfer FLAC from laptop via SCP
# (run from laptop PowerShell — cd into the source folder first)
scp -P 8022 'track.flac' user@<M11_IP>:~/music/

# Play FLAC on M11
mpv ~/music/track.flac
```
- ✅ Verified: FLAC playback works via `mpv` inside Termux.

---

## 5. Roadblocks & Workarounds

| Issue | Cause | Fix |
|---|---|---|
| PowerShell APK downloads blocked | Cloudflare JS challenges on APKPure | Downloaded APKs via browser/mirror directly |
| SCP path errors on Windows | OpenSSH treated `E:\` colon as remote host delimiter | `cd` into source dir, wrap filenames in `'...'` |
