# 📚 Multi-Domain PCB DRC & High-Speed SI/PI AI Training Dataset (v2.0)

**Framework:** Enterprise EDA Autonomous Routing & Signal Integrity Dataset
**Standard:** IPC-2221 Class 2 & IPC-2141 Controlled Impedance
**Total Assets:** 371 curated files | 18 physics-grounded benchmark cases | 31 milestone PCB models | 84 KiCad DRC logs

---

## 1. Executive Summary & Domain Diversity

This enterprise training dataset provides full geometric, electrical, and topological annotations for training Graph Neural Networks (GNNs), reinforcement learning agents, and algorithmic autorouters on multi-layer PCB layout optimization.

### Multi-Domain Coverage (18 Distinct Benchmark Cases):
1. **High-Speed Signal Integrity (SI):**
   - USB 2.0 Differential Pair ($90\Omega \pm 10\%$, skew equalized with serpentine delay meanders)
   - PCIe Gen2 Differential Bus ($100\Omega$, $5	ext{ Gbps}$ phase tuning with trombone matching)
   - High-Frequency Clock Return Path Discontinuity (RPD) bridging across ground split slots
   - High-frequency 3W aggressor crosstalk suppression with GCPW via-stitched guard rings
2. **Power Integrity & Thermal Distribution (PI):**
   - 1.2V Core PDN Target Impedance ($Z_{target} \le 18	ext{ m}\Omega$) and mounting loop inductance
   - Switching inductor thermal spoke starvation prevention under 2.5A continuous DC load
   - Decoupling capacitor loop inductance hierarchy (0201 high-frequency local to bulk)
3. **Mixed-Signal & RF Isolation:**
   - 2.4GHz RF antenna keepout zone copper exclusion and ground plane perimeter edge fencing
   - Star-ground Kelvin bridge split between sensitive analog and noisy digital ground domains
4. **DFM & Assembly Yield:**
   - QFN-28 exposed center pad solder wicking prevention via micro-tented thermal vias

---

## 2. File Organization
- `01_training_data/`: 12 DRC benchmark pairs, 31 milestone progression boards, 84 DRC reports, 28 DRC JSONs.
- `02_algorithms_and_scripts/`: Multi-core parallel router, McMurchie-Ebeling Negotiated Congestion ripup-reroute, Bentley-Ottmann $O((N+K)\log N)$ clearance checker, FSM solver, 66 CAD diagnostics.
- `03_research_documentation/`: Formal topological proofs and mathematical theorems.
- `04_high_speed_si_pi_dataset/`: 6 dedicated transmission line cases, IPC-2141 physics reports, and GNN graph tensors.
