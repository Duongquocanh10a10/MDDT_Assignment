# Benchmark Case: case_010_antenna_rf_keepout_zone_violation

## Title
2.4GHz RF Keepout Perimeter Trace Intrusion & Fringing Field

## Category
`keepout_intrusion` (IPC-2221 & IPC-7351 Standards)

## Engineering Description & Root Cause
Digital SPI clock track intruded 1.8mm into ESP32 PCB inverted-F antenna keepout zone, causing dielectric detuning and parasitic radiative coupling. Transformation redirects SPI bus around antenna perimeter via Layer 4 (B.Cu) under solid ground shield.

## Verification Metrics
- **Initial DRC Violations:** 2
- **Post-Transformation Violations:** 0 (100% Convergence Verified)
- **Signal Integrity Improvement:** Validated with open-source field solver models.
