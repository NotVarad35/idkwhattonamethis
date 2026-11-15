# State Tracker: Jukebox ESP32 (Network Audio Reboot)
- **Problem Category:** Hardware / Electronics / Embedded C++
- **Created / Last Updated:** 15-11-2026 05:54:09
- **Related Links:** [[progress-state#Module 3: ESP32 + I2S Network Jukebox (M11 as Audio Host)]] | [[inventory-bom#Audio & Inputs]] | [[progress-state-m11-homelab]]

## 1. What Happened / Context
- **Architecture Pivot (15-11-2026):** The jukebox will NOT have a MicroSD card. The project owns exactly one 64GB card (`43CC-5E0C`) and it stays in the Samsung M11, which is now the **sole storage hub and wireless audio host** (Navidrome on the 2.4GHz network at `192.168.1.110`).
- **DFPlayer Mini deprecated for standalone playback:** it is an SD-card-only MP3 decoder and cannot read from the network or a shared card, so it was dropped from the active build and kept only as a spare.
- **New active hardware:** an **I2S DAC module** (GY-PCM5102A or UDA1334A) to convert the ESP32's I2S output to line-level audio, plus a **2.0-inch square IPS LCD (ST7789V, SPI)** for album art.
- **Enclosure:** **16 cm x 16 cm x 16 cm** cube — a 1:1 Minecraft pixel ratio where **1 px = 1 cm**.
- **History:** the earlier Web UI build was scrapped for instability, and the RC522 NFC module was benched (unsoldered header pins, unstable 3.10V–3.53V).

## 2. Tracker
- **Supposed to do:** Build a network-attached jukebox: the ESP32 pulls audio from the M11 over Wi-Fi, decodes it to I2S for the DAC, and renders album art on the ST7789V, driven by the rotary encoder and buttons.
- **What we actually did:** Locked the new architecture (M11 = storage + audio host, no SD card on the jukebox), selected the I2S DAC and ST7789V display, and fixed the 16 cm cube enclosure spec.
- **Currently doing:** On hold until the I2S DAC and the ST7789V display arrive; no meaningful wiring can start without them.
- **Left to do:** 
  1. Confirm which DAC board actually arrives (PCM5102A vs UDA1334A) and wire I2S: `BCK`/`LRCK`/`DIN` + `3V3`/`GND`, with DAC line-out into the TRRS 3.5mm breakout.
  2. Bring up the ST7789V over SPI (`CS`/`DC`/`RST`/`BLK`) and draw one static album-art bitmap before integrating anything.
  3. Write the streaming client against the M11's Navidrome HTTP endpoint with a small ring buffer; verify one track plays start-to-finish.
  4. Add the rotary encoder (volume) and a single play/pause button only after audio is clean.
  5. Cut the 16 cm cube enclosure once the breadboard circuit is final.

## 3. Unexpected Roadblocks & Fixes Employed
- **Unexpected:** The "one card for everything" plan was physically impossible — the DFPlayer Mini is a local-SD-only decoder, so sharing the single 64GB card would have meant unplugging it from the M11 for every jukebox session.
- **Fix:** Deprecated the DFPlayer for playback and pivoted to an I2S DAC fed by the ESP32, with the M11 streaming the library over Wi-Fi.
- **Unexpected:** Web UI instability and RC522 unsoldered pin drop (3.10V–3.53V)[cite: 3].
- **Fix:** Benched the RC522[cite: 3] and wiped the buggy Web UI to rebuild modularly.
