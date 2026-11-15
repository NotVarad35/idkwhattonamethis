# Master To-Do List (`idkwhattonamethis`)
- **Last Updated:** 15-11-2026 05:54:09
- **Related:** [[progress-state]] | [[inventory-bom]]

---

## 1. High Priority (Active — Samsung M11 & Navidrome)
- [ ] **Navidrome Music Library Setup:** Organize `/storage/43CC-5E0C/Music` into `Artist/Album` folders, verify FLAC tags (`AlbumArtist`, `TrackNumber`), and drop `cover.jpg` files.
- [ ] **Navidrome Tuning:** Configure `navidrome.toml` preferences (transcoding cache limits for 3GB RAM, scan schedule, UI theme/language).
- [ ] **M11 Storage & Cron Automation:** Check post-debloat free internal storage (`df -h /data`) to update [[inventory-bom#Compute & Devices]] and set up Termux `crond` scripts.

## 2. On Hold / Blocked (Pending Hardware Parts)
- [ ] **ESP32 Jukebox Breadboard ([[states/progress-state-jukebox-esp32]]):** Not ready — paused while waiting for the I2S DAC and ST7789V display to arrive before rebuilding the bare-minimum audio circuit.
- [ ] **Jukebox Enclosure:** Blocked until breadboard hardware is finalized (target: 16 cm x 16 cm x 16 cm cube, 1 px = 1 cm).
- [ ] **NFC Wall Posters ([[progress-state#Module 4: NFC Album Wall Posters]]):** Waiting on physical album posters to mount NTAG213 stickers.

## 3. Backlog (Future)
- [ ] **NFC Poster Automation:** Connect phone NFC tag scans to M11 Navidrome playback via webhook/intent.
- [ ] **Automated Wallpaper Cycler for Samsung M11:** Termux:API + cron job that rotates the wallpaper hourly (full steps in §4 below).

---

## 4. Automated Wallpaper Cycler for Samsung M11
- **Problem Category:** Software / Android Automation
- **Target Device:** Samsung Galaxy M11 (rooted, Magisk v30.7, Termux + OpenSSH on `192.168.1.110:8022`)
- **Status:** Not started

### Prerequisites
- Termux installed with `sshd` reachable over SSH ([[states/progress-state-m11-homelab]]).
- At least one image copied into the phone's `~/wall/` folder before testing step 5.

### Implementation Steps
1. **Install the F-Droid Termux:API app** on the phone (this is the companion APK, not the `termux-api` package — the package alone will not work).
2. **Install the packages** inside Termux over SSH:
   ```bash
   pkg install termux-api cronie -y
   ```
3. **Create the image folder:**
   ```bash
   mkdir ~/wall
   ```
4. **Write the script `~/wallpaper-changer.sh`:**
   ```bash
   #!/data/data/com.termux/files/usr/bin/bash
   PIC=$(ls ~/wall/* | shuf -n 1)
   termux-wallpaper -f "$PIC"
   ```
   ```bash
   chmod +x ~/wallpaper-changer.sh
   ```
5. **Add the cron job:**
   ```bash
   crontab -e
   ```
   Add this line:
   ```cron
   0 * * * * bash ~/wallpaper-changer.sh
   ```

### Test & Verify
- Manual run first: `bash ~/wallpaper-changer.sh` (wallpaper should change immediately).
- Then confirm cron is actually running: `pgrep -l crond`, and check `logcat`/output if it fires at the top of the hour.

### Gotchas
- `termux-wallpaper` fails silently/with an error if the **Termux:API app** is missing — install the APK before step 2's test.
- Termux has no init system: `crond` will not be running just because `cronie` is installed. Start it manually (or via Termux:Boot) before trusting the schedule.
- Android may kill the cron process when the phone sleeps/Doze kicks in — the ACC charge-cap + 24/7 plugged-in setup helps, but a Termux wake-lock (`termux-wake-lock`) is the reliable fix.
