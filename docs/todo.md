# Project To-Do & Feature Backlog
- **Last Updated:** 14-11-2026 21:02:00
- **Related:** [[progress-state#Module 2: Samsung Galaxy M11 (DAP + 2.4GHz Homelab)]] | [[states/progress-state-m11-homelab]]

---

## Automated Wallpaper Cycler for Samsung M11
- **Problem Category:** Software / Android Automation
- **Target Device:** Samsung Galaxy M11 (rooted, Magisk v30.7, Termux + OpenSSH on `192.168.1.110:8022`)
- **Status:** Not started

### 1. Prerequisites
- Termux installed with `sshd` reachable over SSH (`[[states/progress-state-m11-homelab]]`).
- At least one image copied into the phone's `~/wall/` folder before testing step 5.

### 2. Implementation Steps
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

### 3. Test & Verify
- Manual run first: `bash ~/wallpaper-changer.sh` (wallpaper should change immediately).
- Then confirm cron is actually running: `pgrep -l crond`, and check `logcat`/output if it fires at the top of the hour.

### 4. Gotchas
- `termux-wallpaper` fails silently/with an error if the **Termux:API app** is missing — install the APK before step 2's test.
- Termux has no init system: `crond` will not be running just because `cronie` is installed. Start it manually (or via Termux:Boot) before trusting the schedule.
- Android may kill the cron process when the phone sleeps/Doze kicks in — the ACC charge-cap + 24/7 plugged-in setup helps, but a Termux wake-lock (`termux-wake-lock`) is the reliable fix.
