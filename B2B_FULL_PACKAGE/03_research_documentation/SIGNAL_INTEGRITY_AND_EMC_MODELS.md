# Transmission Line & Signal Integrity Formal Guidelines

## 1. High-Speed Differential Microstrip Impedance & Skew
For USB 2.0 (D+/D-) differential transmission lines on 4-layer FR4 ($arepsilon_r = 4.4$, $h = 0.2	ext{ mm}$ to reference ground plane In1.Cu):
$$Z_{diff} pprox 2 Z_0 \left(1 - 0.48 e^{-0.96 rac{s}{h}}ight) = 90.0\ \Omega \pm 10\%$$
Where:
- Trace width $w = 0.25	ext{ mm}$
- Intra-pair clearance $s = 0.20	ext{ mm}$
- Maximum permissible intra-pair skew $\Delta t_{skew} \le 50	ext{ ps}$ (equivalent to $\Delta L \le 7.5	ext{ mm}$).

## 2. Coplanar Ground Shielding for High-Impedance Analog Lines
High-impedance sensor nets ($R_{in} > 10^{11}\ \Omega$, e.g. glass electrode pH probe) require Grounded Coplanar Waveguide (GCPW) shielding with continuous guard rings:
$$C_{coupling} = rac{arepsilon_0 arepsilon_{eff} K(k')}{K(k)}$$
Periodic ground stitching vias must be placed at intervals $\lambda / 20 \le 5.0	ext{ mm}$ to suppress RF resonance and prevent return path inductive ground bounce.
