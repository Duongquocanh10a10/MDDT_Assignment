# Phase 3: 4-Layer PCB Layout, Routing & Zero-DRC Verification (`Phần B — Mục 5`)

**Project:** HCMUT CO2037 — Project 1: Redesign of Yolo UNO (`ESP32-S3-WROOM-1-N16R8`)  
**EDA Tool:** KiCad 10.0.8 (`pcbnew` + `kicad-cli` automated DRC & zone fill)  
**Board File:** `YoloUNO_Project/hardware/YoloUNO.kicad_pcb`  
**Verification Status:** **PASS — `0` DRC Violations, `0` Unconnected Items, `0` Schematic Parity / Footprint Errors (`DRC_EXIT_CODE = 0`)**

---

## 5.1 Board Dimensions, Form Factor & 4-Layer Stackup

The PCB adheres strictly to the official **Arduino UNO R3 mechanical form factor** (`68.58 × 53.34 mm` with the East mechanical notch, `R = 1.50 mm` West corner fillets, 4× M3 mounting holes `H1–H4`, and exact standard 2.54 mm female header pitch including the famous `4.06 mm` (`0.160 in`) non-standard gap between `J19` Pin 1 (`D8`) and `J20` Pin 8 (`D7`)).

### Mechanical Alignment Verification (Local Coordinates, Top-Left Origin `(0, 0)`)

| Mechanical Feature | Reference | Exact Board Coordinates `(X, Y)` mm | Verification |
| :--- | :---: | :---: | :--- |
| **Board Outline** | `Edge.Cuts` | `68.58 × 53.34 mm` (East notch `X = 66.04 ↔ 68.58`, West fillets `R = 1.50 mm`) | Exact UNO R3 spec |
| **Mounting Holes (M3, Ø3.2 mm)** | `H1, H2, H3, H4` | `H1(13.97, 50.80)`, `H2(15.24, 2.54)`, `H3(66.04, 45.72)`, `H4(66.04, 17.78)` | Exact UNO R3 spec |
| **Top Digital Header (1×10)** | `J19` (`SCL..D8`) | Pin 10 (`SCL`) `(18.80, 2.54)` → Pin 1 (`D8`) `(41.66, 2.54)` | Shield-compatible |
| **Top Digital Header (1×08)** | `J20` (`D7..D0`) | Pin 8 (`D7`) `(45.72, 2.54)` → Pin 1 (`D0/RX`) `(63.50, 2.54)` (`4.06 mm` gap to `J19`) | Shield-compatible |
| **Bottom Power Header (1×08)** | `J17` (`NC..VIN`) | Pin 1 (`NC`) `(27.94, 50.80)` → Pin 8 (`VIN`) `(45.72, 50.80)` | Shield-compatible |
| **Bottom Analog Header (1×06)** | `J18` (`A0..A5`) | Pin 1 (`A0`) `(50.80, 50.80)` → Pin 6 (`A5/SCL`) `(63.50, 50.80)` | Shield-compatible |
| **Optical Fiducials** | `FID1, FID2, FID3` | `(28.00, 7.00)`, `(65.00, 28.00)`, `(28.60, 35.20)` on `F.Cu` | SMT assembly ready |

### 4-Layer FR4 PCB Stackup (`1.60 mm` Standard Thickness, `1 oz / 35 µm` Copper)

| Layer | Function | Copper Fill Area | Routing Usage | SI / EMC Role |
| :---: | :--- | :---: | :---: | :--- |
| **L1 (`F.Cu`)** | Top Signal, High-Current Power Trunks, `U3` Thermal Pad + Outer `GND` Pour | `1,654.0 mm²` (`GND`) + `20.4 mm²` (`U3 +3V3`) | `491` track segments | Buck `SW`/`BOOT` (0 vias), USB-C `D+/D-` bridge (0 vias), `1.30 mm` Servo `+5V` bus, top component fanout |
| **L2 (`In1.Cu`)** | **100% Solid Unbroken `GND` Reference Plane** | **`2,852.3 mm²`** (1 single polygon) | **`0` tracks** | Unbroken low-inductance return path for `F.Cu` signals, EMI shielding, auto-cleared under `U4` antenna |
| **L3 (`In2.Cu`)** | **100% Pure Split Power Plane (`+3V3` & `+5V`)** | **`2,135.5 mm²` (`+3V3`)** + **`623.5 mm²` (`+5V`)** | **`0` tracks** | `0.80 mm` clean split seam; unbroken low-impedance PDN for MCU/12× Grove (`+3V3`) & 4× Servo/Buck (`+5V`) |
| **L4 (`B.Cu`)** | Bottom Signal, `90 Ω` Coupled USB Diff Pair + Outer `GND` Pour | `1,789.8 mm²` (`GND`) | `541` track segments | Coupled `USB_DN`/`USB_DP` pair (`w = 0.25, s = 0.20 mm`), compact `0603/0805` decoupling & protection passives |

---

## 5.2 Design Rules & Manufacturing Constraints (IPC-2221 Class 2)

Configured in `YoloUNO.kicad_pro` and enforced by `kicad-cli pcb drc --severity-all --refill-zones --schematic-parity`:

| Parameter | Design Rule (Minimum) | Implemented Value | Standard / Reference |
| :--- | :---: | :---: | :--- |
| **Min Track Width (Signals)** | `0.15 mm` (`6 mil`) | `0.18 mm` (general GPIO / I²C) | IPC-2221 Class 2 / JLCPCB 4L |
| **Min Copper Clearance** | `0.15 mm` (`6 mil`) | `≥ 0.165 mm` (trace-to-trace pitch `0.40 mm` → `0.22 mm` gap) | IPC-2221 Class 2 |
| **Via Size / Drill** | `0.60 / 0.30 mm` | `0.60 mm` pad / `0.30 mm` drill (`0.15 mm` annular ring) | Standard 4-layer DFM |
| **Copper-to-Board-Edge Clearance** | `0.30 mm` | `≥ 0.45 mm` (zones & tracks) | Safe V-score / routing margin |
| **Hole-to-Hole & Hole-to-Copper** | `0.25 mm` | `≥ 0.30 mm` | Zero drill-breakout risk |
| **Zone Thermal Relief** | `0.22–0.25 mm` gap | `0.35 mm` spokes (`0.40 mm` solid on `U3` thermal pad) | Solderability + low thermal R |
| **USB 2.0 Differential Pair** | `90 Ω ±10%`, skew `≤ 7.5 mm` | `w = 0.25 mm`, `s = 0.20 mm`, **skew = `0.67 mm`** | `B2B_FULL_PACKAGE` SI model |
| **Servo `+5V` Trace Width (`2 A`)** | `≥ 0.781 mm` (IPC-2221 Q[13]) | **`1.30 mm`** `F.Cu` backbone **+** `623.5 mm²` `In2.Cu` `+5V` plane | IPC-2221 (`1 oz`, `ΔT = 10 °C`) |

---

## 5.3 Ergonomic 2-Sided Placement Strategy & EMI/RF Isolation

All `81` footprints (`100%` matched with schematic) were partitioned strategically across `F.Cu` and `B.Cu` to satisfy Section 6.9 of the assignment:

1. **ESP32-S3 RF Antenna Isolation (`U4`):**
   - `ESP32-S3-WROOM-1-N16R8` (`U4`) sits along the **West board edge (`X = 0`)** with its PCB meander antenna pointing directly outward into free space.
   - An embedded 4-layer **RF keepout zone** (`X ∈ [0, 6.90]`, `Y ∈ [17.80, 36.10]`) guarantees **zero copper, zero tracks, zero vias, and zero ground/power pours** on all 4 layers beneath the antenna.
2. **Switching Buck Converter Isolation (`U1`, `L1`, `C3–C6`):**
   - Placed in the **South-East quadrant (`X ≈ 56–64 mm`, `Y ≈ 31–48 mm`)** — more than **`52 mm` away from the ESP32-S3 RF antenna** — preventing `500 kHz` switching harmonics from coupling into the `2.4 GHz` Wi-Fi/BLE front-end.
   - The high-`di/dt` switching node `SW` (`U1.2 ↔ L1.1 ↔ C4.2`) and bootstrap node `BOOT` (`U1.6 ↔ C4.1`) are routed **100% on `F.Cu` with `0` vias** (`L(SW) = 16.49 mm`, `0.60 mm` main trunk; `L(BOOT) = 4.89 mm`).
   - Feedback divider resistors `R3` (`68.0 kΩ`) and `R4` (`9.10 kΩ`) sit directly behind `U1` on `B.Cu`, shielded from `L1`'s magnetic flux by the solid `In1.Cu` GND plane.
3. **Ergonomic Peripheral & Power Access (All Tall Connectors on `F.Cu`):**
   - **West Edge:** `J1` DC Barrel Jack (`6–12 V`, South-West), `U4` ESP32-S3 (Center-West), `J2` USB-C (North-West), `J15` QWIIC (North-West corner).
   - **North-West UX Zone:** `U5` (`USBLC6-2SC6` ESD directly behind `J2`), `D5` (`WS2812B` NeoPixel), `SW2` (`BOOT`), `D3` (`PWR` green LED), `D4` (`D13` red LED); `SW1` (`RESET`) at South-West edge beside `H1`.
   - **Center Grove Matrix (12× Vertical Grove, `3 cols × 4 rows`):**
     - Col 1 (Analog): `J6 (A1-A0)`, `J5 (A2-A1)`, `J4 (A3-A2)`, `J3 (A6-A3)`
     - Col 2 (Digital): `J10 (D4-D3)`, `J9 (D6-D5)`, `J8 (D8-D7)`, `J7 (D10-D9)`
     - Col 3 (I²C): `J14 (I2C1)`, `J13 (I2C2)`, `J12 (I2C3)`, `J11 (I2C4)`
   - **East Servo Power Block:** `C18` (`470 µF / 10 V`) immediately north of the 4× Servo GVS headers `J21–J24` (`D2, D13, D12, D11`) and directly above Buck `L1`/`U1`/`U2` (`TPS2116`), minimizing the `2 A` Servo current loop.
4. **Compact Flat SMDs on `B.Cu`:**
   - Reverse-polarity & surge protection (`D1`, `Q1`, `D2`, `R1`, `C2`) directly behind `J1` (`VIN_RAW` routed at `0.80 mm`, `6.86 mm` total length, `0` vias).
   - MCU decoupling (`C11 = 22 µF`, `C12 = 100 nF`, `R7`, `C13`, `C17 = 100 nF` A0 filter) directly underneath `U4`'s `3V3`/`EN`/`A0` pins (strictly outside `X ≤ 7.0` RF keepout).
   - `JP1` 3-pad `0–5 V` A0 conditioning solder jumper + `R16`/`R17` accessible cleanly on the bottom silkscreen (`A0: 1-2=3V3 2-3=5V`).

---

## 5.4 Critical Net Metrics, Thermal Management & Plane Integrity

| Critical Net / Feature | Measured Length | Width(s) | Vias | Engineering Requirement Check |
| :--- | :---: | :---: | :---: | :--- |
| **`USB_DN` / `USB_DP` (`90 Ω` Diff Pair)** | `31.91 mm` / `31.24 mm` | `0.25 mm` (`s = 0.20 mm`) | `2` / `2` (symmetric) | **Skew = `0.67 mm`** (`≪ 7.5 mm` spec); continuous reference plane |
| **`J2 → U5` USB-C `D-`/`D+` Bridge** | `7.01 mm` / `5.67 mm` | `0.18 mm` | **`0` / `0`** | Interleaved `0.50 mm`-pitch bridge on `F.Cu` with zero vias |
| **Buck `SW` (`Net-(U1-SW)`)** | `16.49 mm` | `0.30 / 0.40 / 0.60 mm` | **`0`** | Ultra-short switching node on `F.Cu`, `> 52 mm` from antenna |
| **Buck `BOOT` (`Net-(U1-BOOT)`)** | `4.89 mm` | `0.25 mm` | **`0`** | Direct `F.Cu` strap between `U1.6` and `C4.1` |
| **Servo `+5V` Backbone (`Q[13]`)** | `96.59 mm` total | **`1.30 mm`** (`F.Cu` bus) + `In2.Cu` plane | `8` (stitching) | Exceeds `0.781 mm` IPC-2221 min by **`1.66×`** + parallel `623.5 mm²` plane |
| **`VIN_RAW` (DC Protection Loop)** | `6.86 mm` | **`0.80 mm`** | **`0`** | Direct `B.Cu` `J1.1 → Q1.3 & D1.2` |
| **`VIN_PROT` / `5V_BUCK`** | `73.38 mm` / `45.47 mm` | `0.45 mm` / `0.70 mm` main | `6` / `3` | Wide low-drop power delivery |
| **`U3` (`AP2114H-3.3`) Thermal Path (`Q[2]`)** | `20.4 mm²` top pour + `2,135.5 mm²` `In2.Cu` | Solid tab connection | **4× thermal vias** | Achieves `R_θJA,eff ≈ 65 °C/W` (`T_J,peak ≈ 106.3 °C < 125 °C`) |
| **`In1.Cu` Solid `GND` Plane** | `2,852.3 mm²` (`1` polygon) | Unbroken plane | `47` GND vias | `0` tracks on `In1.Cu` & `0` tracks on `In2.Cu`; `0` isolated islands |
| **Total Board Routing** | `2,513.5 mm` (`1,032` tracks) | `0.18–1.30 mm` | `229` vias | `F.Cu: 491`, `B.Cu: 541`, `In1.Cu: 0`, `In2.Cu: 0` (100% pure inner planes!) |

---

## 5.5 KiCad 10 DRC Verification Result (Absolute Zero-DRC)

Executed via:
```powershell
kicad-cli pcb drc --severity-all --refill-zones --schematic-parity --exit-code-violations `
  -o YoloUNO_Project/outputs/drc_report.rpt YoloUNO_Project/hardware/YoloUNO.kicad_pcb
```

**Verified Output (`DRC_EXIT_CODE = 0`):**
- **Total DRC Violations (Errors & Warnings):** **`0`** (`0` shorts, `0` clearance violations, `0` edge clearance violations, `0` RF keepout violations, `0` hole/annular-ring errors, `0` courtyard overlaps, `0` isolated copper islands, `0` dangling tracks/vias)
- **Total Unconnected Items:** **`0`** (all `319` pads across all `65` nets 100% routed and plane-connected)
- **Total Schematic Parity / Footprint Errors:** **`0`** (1-to-1 match with Phase 2 schematic, netlist, MPN/LCSC fields, and BOM attributes)

### Generated Phase 3 Artifacts
- Routed 4-layer PCB: `YoloUNO_Project/hardware/YoloUNO.kicad_pcb`
- Automation Scripts: `YoloUNO_Project/scripts/prepare_footprints_and_board.py`, `YoloUNO_Project/scripts/route_yolouno_4layer.py`
- DRC Reports: `YoloUNO_Project/outputs/drc_report.rpt`, `YoloUNO_Project/outputs/drc_report.json`
- 2D Copper & Silkscreen Exports:
  - Multi-page layer PDF: `YoloUNO_Project/outputs/YoloUNO_PCB_2D_Layers.pdf`
  - Composite Top/Bottom PDFs: `YoloUNO_Project/outputs/pcb_2d/01_Top_Composite.pdf`, `YoloUNO_Project/outputs/pcb_2d/04_Bot_Composite_Mirrored.pdf`
  - Individual layer SVGs: `YoloUNO_Project/outputs/pcb_2d/01_Top_FCu_Silk.svg`, `02_In1_GND.svg`, `03_In2_Power.svg`, `04_Bot_BCu_Silk.svg`
