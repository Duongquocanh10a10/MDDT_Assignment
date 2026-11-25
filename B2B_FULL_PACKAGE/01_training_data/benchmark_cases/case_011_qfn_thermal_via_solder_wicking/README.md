# Benchmark Case: case_011_qfn_thermal_via_solder_wicking

## Title
QFN-28 Exposed Pad Thermal Via Solder Theft & Paste Windowing

## Category
`solder_mask_tenting` (IPC-2221 & IPC-7351 Standards)

## Engineering Description & Root Cause
CP2102N 5x5mm exposed thermal pad contained 9 open 0.3mm vias without solder mask tenting or paste aperture windowing (50% rule), causing solder starvation on peripheral signal pins. Transformation applies backside tenting and segmented 4-window solder paste matrix.

## Verification Metrics
- **Initial DRC Violations:** 2
- **Post-Transformation Violations:** 0 (100% Convergence Verified)
- **Signal Integrity Improvement:** Validated with open-source field solver models.
