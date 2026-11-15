# Hardware Inventory & Bill of Materials (BOM)
- **Last Updated:** 15-11-2026 19:10:38

## 1. Active Bench Hardware (In-Hand)
### Compute & Devices
- [x] **Samsung Galaxy M11 (Free | Snapdragon 450, 3GB RAM, 32GB Internal [run `df -h /data` post-debloat], 2.4GHz Wi-Fi, 3.5mm Jack)** — Rooted (Magisk v30.7, Knox `0x1`), static IP `192.168.1.110`, debloated 325 → 166 packages. **Sole storage hub and wireless audio host** for the jukebox (see [[states/progress-state-m11-homelab]]).
- [x] **ESP32 Dev Board (30-Pin ESP-WROOM-32, CP2102 on COM4)** — Jukebox MCU; now acts as a Wi-Fi audio client feeding an I2S DAC[cite: 2].
- [x] **Nothing Phone (2a)** — Daily phone & NFC reader/writer[cite: 1].

### Storage
- [x] **64GB MicroSD Card (`/storage/43CC-5E0C`)** — The only card in the project; mounted in the Samsung M11. **No card is allocated to the jukebox** (network-attached architecture).
- [x] **Dedicated Jukebox MicroSD — CANCELLED** — The jukebox streams from the M11 over Wi-Fi instead of reading local media (see [[states/progress-state-jukebox-esp32]]).

### Audio & Inputs
- [x] **CJMCU-TRRS 3.5mm Female Audio Breakout** — Voice of the audio chain; I2S DAC line-out feeds it[cite: 2].
- [x] **KY-040 Rotary Encoder Module** — Volume & push-button dial[cite: 1, 2].
- [x] **10x Tactile Momentary Push Buttons (6x6x5mm, 4-Pin)**[cite: 1, 2].
- [x] **SPST Mini Rocker Switch (KCD11)**[cite: 2].

### Network Audio Upgrade (Active Build — Awaiting Delivery)
- [ ] **I2S DAC Module (GY-PCM5102A or UDA1334A)** — Converts the ESP32's I2S stream to line-level stereo audio for the TRRS breakout. Confirm the exact board on delivery before wiring.
- [ ] **2.0-inch Square IPS LCD (ST7789V, SPI)** — Album-art display for the jukebox face; driven over SPI (`CS`/`DC`/`RST`/`BLK`).

### Deprecated / Retired From Active Build
- [x] **DFPlayer Mini (MP3-TF-16P)** — **DEPRECATED for playback** (SD-card-only decoder; cannot stream). Kept in the parts drawer as a spare. Was seated on breadboard Rows 2–9[cite: 2].

### Power Chain (On Hold Until Breadboard Logic is Finalized)
- [x] **DMEGC 18650 2600mAh 3.7V Li-ion Cell + Holder**[cite: 1, 2].
- [x] **TP4056 Type-C Charger Module**[cite: 1, 2].
- [x] **Mini 5V DC-DC Step-Up Boost Module (Solder-pad version)**[cite: 1].

### NFC
- [x] **5x NTAG213 13.56MHz Round NFC Adhesive Stickers** — Allocated to Album Wall Posters (posters are not yet bought)
- [x] **RC522 13.56MHz RFID Module** — Currently benched (unsoldered header pins)

## 2. General Prototyping, Wiring & Tools
- [x] **400-Point Solderless Breadboard**[cite: 1, 2]
- [x] **400-Point Half-Size Solderless Breadboard**
- [x] **40x Male-to-Male Dupont Jumper Wires (20cm)**[cite: 1, 2]
- [x] **40x Male-to-Female Dupont Jumper Wires (20cm)**[cite: 1, 2]
- [x] **Verified Micro-USB Data Cable**[cite: 2]
- [x] **3.5mm Male-to-Male AUX Cable**
- [x] **DT830D Digital Multimeter**[cite: 1, 2]

## 3. Enclosure Spec (Target)
- **Dimensions:** **16 cm x 16 cm x 16 cm** cube.
- **Pixel ratio:** 1:1 with Minecraft's block grid — **1 px = 1 cm** (16 px per face).
- **Materials:** 3x Basswood Plywood + 3x Sunboard sheets (still to be bought; blocked until the breadboard circuit is final)[cite: 1].

---

## 4. Pending Purchases (Only When Ready)
- [ ] **Enclosure Panels — 16 cm x 16 cm x 16 cm cube:** 3x Basswood Plywood + 3x Sunboard sheets (on hold until breadboard electronics & code are 100% stable)[cite: 1].
- [ ] **I2S DAC + ST7789V Display:** Ordered/awaited as part of the network-audio pivot; see [[states/progress-state-jukebox-esp32]].
- [ ] **Room Album Cover Posters:** For attaching the NTAG213 stickers.
