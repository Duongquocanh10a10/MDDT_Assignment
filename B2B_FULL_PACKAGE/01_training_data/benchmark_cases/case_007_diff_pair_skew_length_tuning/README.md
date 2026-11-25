# Benchmark Case: case_007_diff_pair_skew_length_tuning

## Title
USB 2.0 Differential Pair Skew & Length Matching (D+/D-)

## Category
`skew_mismatch` (IPC-2221 & IPC-7351 Standards)

## Engineering Description & Root Cause
USB D+ and D- differential lines exhibited 4.2mm length mismatch causing common-mode jitter (>50ps). Transformation applies serpentine delay trombone on D- while maintaining constant 0.20mm intra-pair differential impedance spacing (90Ω nominal).

## Verification Metrics
- **Initial DRC Violations:** 2
- **Post-Transformation Violations:** 0 (100% Convergence Verified)
- **Signal Integrity Improvement:** Validated with open-source field solver models.
