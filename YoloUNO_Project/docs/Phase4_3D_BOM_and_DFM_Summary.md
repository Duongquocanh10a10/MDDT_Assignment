# Phase 4: 3D Renders, Final Production BOM & Gerber/Drill DFM Package

**Project:** HCMUT CO2037 — Project 1: Redesign of Yolo UNO (`ESP32-S3-WROOM-1-N16R8`)  
**Status:** **COMPLETE — All 3D renders visually verified, 100% BOM parity asserted, 4-layer Gerber/Excellon DFM package generated & audited**

---

## 4.1 High-Resolution 3D Raytraced Renders (`2400 × 1800 px`, KiCad 10 Raytracer)

All `81` footprints (`74` placed electrical parts + `4× M3` mounting holes + `3×` fiducials) are accurately rendered in 3D with verified mechanical alignment on both sides:

| Render View | File | Resolution | Key Verified Visual Features |
| :--- | :--- | :---: | :--- |
| **Top View** | `outputs/3d_renders/YoloUNO_3D_Top.png` | `2400 × 1800` | 12× Grove matrix (`3×4`), ESP32-S3 antenna overhang, USB-C (`J2`), DC Jack (`J1`), QWIIC (`J15`), `SW1`/`SW2`, `WS2812B` (`D5`), `C18` + 4× Servo GVS, `L1`/`U1`/`U2`, UNO R3 headers (`J17–J20`) |
| **Bottom View** | `outputs/3d_renders/YoloUNO_3D_Bottom.png` | `2400 × 1800` | Gold ENIG pads, `"YOLO UNO v1.0 / ESP32-S3 CO2037 HCMUT"`, `JP1` (`A0: 1-2=3V3 2-3=5V`), copper-free RF keepout window, `D1`/`Q1`/`D2` protection behind `J1`, `U6` buffer, `90 Ω` USB pair |
| **Isometric (Front-Right)** | `outputs/3d_renders/YoloUNO_3D_Isometric.png` | `2400 × 1800` | 3D component clearances, tall connectors (`J1`, `J2`, `C18`, 12× Grove, UNO sockets, Servo headers), zero collisions |
| **Isometric (West Ports)** | `outputs/3d_renders/YoloUNO_3D_Isometric_WestPorts.png` | `2400 × 1800` | Flush West-edge access for DC 6–12 V barrel jack, ESP32-S3 PCB antenna, USB-C receptacle, and QWIIC JST-SH |
| **Isometric (Bottom)** | `outputs/3d_renders/YoloUNO_3D_Isometric_Bottom.png` | `2400 × 1800` | Bottom SMD layout, solder jumper accessibility, clean mirrored silkscreen |
| **3D CAD Assembly** | `outputs/YoloUNO_3D_Assembly.step` | `6.88 MB` STEP | Full mechanical STEP model for 3D enclosure/case integration |

---

## 4.2 Final Production BOM & Pick-and-Place CPL

Verified **100% 1-to-1 designator parity** between `YoloUNO.kicad_sch` (`YoloUNO_KiCad_BOM.csv`), `YoloUNO.kicad_pcb`, and the final BOM:

- **CSV BOM:** `outputs/bom/YoloUNO_BOM_Final.csv` (`57` functional rows across Blocks `4.1–4.8`)
- **Multi-Sheet Styled Excel BOM:** `outputs/bom/YoloUNO_BOM_Final.xlsx`
  - Sheet 1 (`BOM_By_Block`): Complete functional block breakdown with live Excel `SUM` formulas
  - Sheet 2 (`BOM_Consolidated_MPN`): Consolidated by unique MPN (`43` unique procurement line items, `74` total placed electrical parts, **Estimated Prototype BOM Cost: \$11.30 USD/board** excluding PCB fabrication)
  - Sheet 3 (`PCB_DFM_Summary`): Mechanical, stackup, ERC/DRC, and SI/PI summary
- **SMT Pick-and-Place CPL:** `outputs/bom/YoloUNO_CPL_Pos.csv` (`76` placed entries, both sides, mm)

---

## 4.3 4-Layer Manufacturing Gerber & Excellon Drill Package

Packaged ready for fabrication (JLCPCB / PCBWay 4-layer `1.60 mm` FR4, `1 oz` copper, ENIG/HASL):
- **Ready-to-Fabricate ZIP:** `outputs/YoloUNO_Gerbers_4Layer.zip` (`434.5 KB`)
- **11 RS-274X Gerber Layers + Job File (`outputs/gerbers/`):**
  - Copper: `YoloUNO-F_Cu.gtl`, `YoloUNO-In1_Cu.g1` (Solid GND), `YoloUNO-In2_Cu.g2` (Split `+3V3`/`+5V`), `YoloUNO-B_Cu.gbl`
  - Solder Mask: `YoloUNO-F_Mask.gts`, `YoloUNO-B_Mask.gbs`
  - Silkscreen (mask-subtracted): `YoloUNO-F_Silkscreen.gto`, `YoloUNO-B_Silkscreen.gbo`
  - Solder Paste Stencil: `YoloUNO-F_Paste.gtp`, `YoloUNO-B_Paste.gbp`
  - Board Outline: `YoloUNO-Edge_Cuts.gm1`
  - Gerber Job Metadata: `YoloUNO-job.gbrjob` (`4` layers, `1.60 mm` FR4, `68.58 × 53.34 mm` UNO R3 outline)
- **Excellon Drill Files & Drill Maps:**
  - `YoloUNO-PTH.drl` + `YoloUNO-PTH-drl_map.pdf`: `340` plated holes across `6` drill diameters (`0.200, 0.300, 0.600, 0.762, 1.000, 1.600 mm`)
  - `YoloUNO-NPTH.drl` + `YoloUNO-NPTH-drl_map.pdf`: `6` non-plated holes across `2` drill diameters (`0.650 mm` USB-C pegs, `3.200 mm` M3 mounting holes `H1–H4`)
