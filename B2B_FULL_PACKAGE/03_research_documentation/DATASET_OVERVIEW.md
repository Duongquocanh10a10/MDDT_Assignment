# 📚 PCB Design Rule Check (DRC) AI Training Dataset & Routing Algorithm Suite (v1.5)

**Framework:** Production-Grade EDA Autonomous Routing & DRC Dataset
**Standards:** IPC-2221 Class 2 & IPC-2141 Controlled Impedance
**Substrate:** 4-Layer Industrial Mixed-Signal Architecture ($52.0 \times 75.0\text{ mm}$)

---

## 1. Dataset Overview & Benchmark Breadth

This dataset captures the complete geometric and topological progression of a complex 4-layer mixed-signal PCB from 798 initial DRC violations down to 0 absolute DRC violations and 100% net connectivity.

### 12 Distinct Engineering Benchmark Cases:
1. `case_001`: VBUS 5V Power Trace to Pin 1 Dogleg Routing (Narrow corridor clearance)
2. `case_002`: MT3608 Boost Converter Inductor Clearance & S-Pad Corridor
3. `case_003`: LCD Bus 8-Pin High-Density Parallel Bus Routing (Congestion navigation)
4. `case_004`: Sensors, GPS & RTC Multi-Peripheral Layer Distribution
5. `case_005`: Isolated Ground Islands & Zone Pour Stitching (Copper balance)
6. `case_006`: Global Multi-Net Integration & Pin Congestion
7. `case_007`: USB 2.0 Differential Pair Skew Length Tuning ($90\Omega$ matching, serpentine delay)
8. `case_008`: Star Ground Kelvin Bridge Analog-Digital Domain Split (Noise immunity)
9. `case_009`: Thermal Relief Spoke Current Starvation on High-Current Rail (IPC-2221)
10. `case_010`: Antenna 2.4GHz RF Keepout Zone Copper Invasion Prevention
11. `case_011`: QFN-28 Exposed Pad Thermal Via Solder Wicking & Masking (DFM yield)
12. `case_012`: Grounded Coplanar Waveguide (GCPW) Guard Ring Crosstalk Suppression

---

## 2. Production EDA Routing & Verification Engines (`02_algorithms_and_scripts/`)

- `bentley_ottmann_drc.py`: $O((N+K)\log N)$ sweepline segment-to-segment Euclidean distance auditor.
- `ripup_reroute_engine.py`: McMurchie-Ebeling PathFinder Negotiated Congestion router with history penalty.
- `parallel_multiprocess_router.py`: Concurrent multi-core routing via `ProcessPoolExecutor`.
- `drc_solver_state_machine.py`: Deterministic FSM solver with exponential backoff and KiCad CLI subprocess IPC.
- `gnn_pcb_graph_builder.py`: Heterogeneous GNN graph tensor extractor (SMD/THT/Via nodes, Delaunay/Clearance edges).
- `train_high_speed_si_pi_model.py`: Multi-task Message Passing Neural Network (MPNN) training pipeline with saved weights.
