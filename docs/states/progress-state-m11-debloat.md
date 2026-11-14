# State Tracker: Samsung M11 Post-Root ADB Debloat
- **Problem Category:** Software / Homelab / Android Debloat
- **Created / Last Updated:** 14-11-2026 21:26:16
- **Related Links:** [[progress-state#Module 2: Samsung Galaxy M11 (DAP + 2.4GHz Homelab)]] | [[progress-state-m11-homelab#2. Tracker]] | [[inventory-bom#Compute & Devices]]

## 1. What Happened / Context
- The factory reset (needed for the bootloader unlock) restored all Samsung/Google bloat, so the round-1 list in [[setup-log]] had to be redone. Everything below was removed over ADB with `pm uninstall -k --user 0` (reversible with `adb shell cmd package install-existing <pkg>`), after the list was shown and approved.
- Package count on the M11 (SM-M115F, serial `R9ZN603V3GF`): **325 -> 166**.
- Hard locks respected: Samsung Settings, device drivers (Qualcomm/QTI/fingerprint/providers), Magisk, Termux, CX File Explorer, Firefox, Gboard, Knox/MDM bits, telephony core.
- The temporary `debloat-round2.ps1` was deleted once the run was done. The removed packages are logged below instead.

## 2. Tracker
- **Supposed to do:** Strip all bloat, ads and telemetry from One UI Core to free RAM for 24/7 homelab use, without touching the locked packages.
- **What we actually did:**
  - Installed Firefox (`fire.apk`, armeabi-v7a) and Olauncher (`Olauncher.apk`); set Olauncher as default Home.
  - Removed Facebook, Netflix, OneDrive, Samsung Galaxy Club/Shop/Free/Video/Finder/Quick Share/Weather/Calendar, Bixby leftovers, Edge panels, Samsung Cloud/Find My Mobile, Galaxy Store, Smart Switch, AR/stickers, Josh, Hiya, Chrome, Samsung My Files, Gallery, stock YouTube, Samsung account, Samsung push/OTA updaters, Knox license agent.
  - Removed Google apps: Photos, Maps, Gmail, Videos, YouTube Music, Duo/Meet, Android Auto, Device Health, TTS, Google app, Drive/Docs, and later the Play Store.
  - Removed telemetry/ads: `rubin`, `dqagent`, `diagmonagent`, `cidmanager`, `attribution`, `discover`, `cmh`, `crane`, Google mainline telemetry, Dynamic Lock Screen (Glance), `wsomacp`.
  - Removed Game Launcher/GOS, Phone app, Contacts app, Clock, Messages, SIM calling/IMS/RCS/Wi-Fi-calling/SIM-toolkit packages, TalkBack, face unlock, Google contacts/calendar sync, Secure Folder, service-mode apps, test/diagnostic apps, backup helpers, cutout overlays.
  - Removed all wallpaper packages (`wallpaper.res`, `livepicker`, `wallpapercropper`, `wallpapermulti`, `dressroom`).
- **Currently doing:** Verifying the phone after reboot (Home, Recents, Wi-Fi, Firefox).
- **Left to do:**
  1. Optional: enable Gboard and then remove Samsung's keyboard (`com.samsung.android.honeyboard`).
  2. Optional: remove the stock launcher only if Recents isn't needed (it is currently enabled because freezing it broke Recents).
  3. Optional: Google Play services (`com.google.android.gms`) still carries the advertising ID; reset it in Settings, or accept breakage if removed.
  4. Continue with ACC charge cap, Termux/OpenSSH (`:8022`), Linux Deploy, and the SCP music seed in [[progress-state-m11-homelab#2. Tracker]].

## 3. Unexpected Roadblocks & Fixes Employed
- **Unexpected:** Freezing the stock launcher (`com.sec.android.app.launcher`) broke the Recents screen, since One UI runs Recents inside it.
- **Fix:** Re-enabled the stock launcher; Olauncher stays the default Home app.
- **Unexpected:** `com.samsung.android.themecenter` refused removal (`DELETE_FAILED_INTERNAL_ERROR`) and `game.gos` reappeared after the first uninstall.
- **Fix:** Left `themecenter` in place (harmless); re-ran the `game.gos` uninstall, which succeeded.
- **Unexpected:** Earlier note that Gboard was missing was wrong; it is installed as `com.google.android.inputmethod.latin` but not the active keyboard.
- **Fix:** Kept Samsung's keyboard until Gboard is enabled.
