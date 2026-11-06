# State Tracker: Jukebox ESP32 Breadboard Reboot
- **Problem Category:** Hardware / Electronics / Embedded C++
- **Created / Last Updated:** 06-11-2026
- **Related Links:** [[progress-state#Module 3: ESP32 + DFPlayer Physical Jukebox]] | [[inventory-bom#Audio, Inputs & Breadboard Gear]]

## 1. What Happened / Context
- Earlier Web UI code had too many bugs, and the single 64GB MicroSD card was moved into the Samsung M11 (`[[progress-state-m11-homelab]]`).
- **Decision:** Scrapped the buggy Web UI and previous setup. Redoing all the ESP32 + DFPlayer work cleanly from scratch on the breadboard before buying any wood enclosure parts.

## 2. Tracker
- **Supposed to do:** Build a rock-solid, bug-free breadboard prototype for the ESP32 + DFPlayer Mini[cite: 3].
- **What we actually did:** Verified ESP32 CP2102 flashes cleanly on COM4 with the new Micro-USB data cable[cite: 3]; benched the unsoldered RC522 module[cite: 3]; scrapped the buggy Web UI sketch.
- **Currently doing:** Scrapped and redoing all the work from zero.
- **Left to do:** 
  1. Sort out a small MicroSD card (or partition/spare card) for the DFPlayer Mini since the 64GB card is in the M11.
  2. Wire ONLY the bare minimum audio circuit first and test 1 button in C++ before adding rotary encoders or Wi-Fi.

## 3. Unexpected Roadblocks & Fixes Employed
- **Unexpected:** Web UI instability and RC522 unsoldered pin drop (3.10V–3.53V)[cite: 3].
- **Fix:** Benched RC522[cite: 3] and wiped the buggy Web UI to rebuild modularly.