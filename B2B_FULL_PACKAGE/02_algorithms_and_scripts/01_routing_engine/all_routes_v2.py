"""
all_routes_v2.py — Complete conflict-free routing for 52x75mm 4-layer PCB.
ALL coordinates verified against pads_summary.json and obstacle map.
"""

from router_engine import seg, via, get_pad

# ============================================================
# GROUP A: Boost Converter
# ============================================================
def get_group_a_routes():
    routes = ""
    # SW_NODE: L1.2(86.25,105.5) — U4.1(90.6375,106.45) — D1.2(94.0,105.5)
    routes += seg(90.6375, 106.45, 90.6375, 107.30, "F.Cu", "SW_NODE", 0.40)
    routes += seg(90.6375, 107.30, 86.25, 107.30, "F.Cu", "SW_NODE", 0.40)
    routes += seg(86.25, 107.30, 86.25, 105.50, "F.Cu", "SW_NODE", 0.40)
    routes += seg(90.6375, 107.30, 94.00, 107.30, "F.Cu", "SW_NODE", 0.40)
    routes += seg(94.00, 107.30, 94.00, 105.50, "F.Cu", "SW_NODE", 0.40)

    # BST_FB: U4.3(90.6375,104.55), C_FF.2(93.225,107.5)B, R_FB2.1(90.825,107.5)B, R_FB1.2(85.175,107.5)B
    # Escape NORTH on F.Cu to avoid U4.2(GND, 105.5), drop via to B.Cu at (92.5, 103.5)
    routes += seg(90.6375, 104.55, 90.6375, 103.5, "F.Cu", "BST_FB", 0.20)
    routes += seg(90.6375, 103.5, 92.5, 103.5, "F.Cu", "BST_FB", 0.20)
    routes += via(92.5, 103.5, "BST_FB")
    routes += seg(92.5, 103.5, 92.5, 106.5, "B.Cu", "BST_FB", 0.20)
    routes += seg(85.175, 106.5, 93.225, 106.5, "B.Cu", "BST_FB", 0.20)
    routes += seg(93.225, 106.5, 93.225, 107.5, "B.Cu", "BST_FB", 0.20)
    routes += seg(90.825, 106.5, 90.825, 107.5, "B.Cu", "BST_FB", 0.20)
    routes += seg(85.175, 106.5, 85.175, 107.5, "B.Cu", "BST_FB", 0.20)
    return routes

# ============================================================
# GROUP B: Battery Protection
# ============================================================
def get_group_b_routes():
    routes = ""
    # DRAIN_U3: U3.1(106.8625,97.55) to U3.6(109.1375,97.55)
    routes += seg(106.8625, 97.55, 106.8625, 96.6, "F.Cu", "DRAIN_U3", 0.35)
    routes += seg(106.8625, 96.6, 109.1375, 96.6, "F.Cu", "DRAIN_U3", 0.35)
    routes += seg(109.1375, 96.6, 109.1375, 97.55, "F.Cu", "DRAIN_U3", 0.35)

    # DW01_VDD: U2.5(101.1375,98.50) to R_VDD.2(100.825,102.0) and C_VDD.1(102.725,102.0)
    routes += seg(101.1375, 98.50, 100.2, 98.50, "F.Cu", "DW01_VDD", 0.25)
    routes += seg(100.2, 98.50, 100.2, 102.0, "F.Cu", "DW01_VDD", 0.25)
    routes += seg(100.2, 102.0, 100.825, 102.0, "F.Cu", "DW01_VDD", 0.25)
    routes += seg(100.825, 102.0, 102.725, 102.0, "F.Cu", "DW01_VDD", 0.25)

    # OD_GATE: U2.1(98.8625,97.55) to U3.5(109.1375,98.5)
    routes += seg(98.8625, 97.55, 97.5, 97.55, "F.Cu", "OD_GATE", 0.20)
    routes += via(97.5, 97.55, "OD_GATE")
    routes += seg(97.5, 97.55, 97.5, 96.0, "B.Cu", "OD_GATE", 0.20)
    routes += seg(97.5, 96.0, 110.5, 96.0, "B.Cu", "OD_GATE", 0.20)
    routes += seg(110.5, 96.0, 110.5, 98.5, "B.Cu", "OD_GATE", 0.20)
    routes += via(110.5, 98.5, "OD_GATE")
    routes += seg(110.5, 98.5, 109.1375, 98.5, "F.Cu", "OD_GATE", 0.20)

    # OC_GATE: U2.3(98.8625,99.45) to U3.4(109.1375,99.45)
    routes += seg(98.8625, 99.45, 97.5, 99.45, "F.Cu", "OC_GATE", 0.20)
    routes += via(97.5, 99.45, "OC_GATE")
    routes += seg(97.5, 99.45, 110.5, 99.45, "B.Cu", "OC_GATE", 0.20)
    routes += via(110.5, 99.45, "OC_GATE")
    routes += seg(110.5, 99.45, 109.1375, 99.45, "F.Cu", "OC_GATE", 0.20)

    # DW01_CS: U2.2(98.8625,98.5) to R_CS.2(108.825,102.0) - escaped west to X=96.3 on F.Cu
    routes += seg(98.8625, 98.5, 96.3, 98.5, "F.Cu", "DW01_CS", 0.20)
    routes += seg(96.3, 98.5, 96.3, 103.5, "F.Cu", "DW01_CS", 0.20)
    routes += seg(96.3, 103.5, 108.825, 103.5, "F.Cu", "DW01_CS", 0.20)
    routes += seg(108.825, 103.5, 108.825, 102.0, "F.Cu", "DW01_CS", 0.20)

    # B_MINUS: U2.6(101.1375,97.55), C_VDD.2(104.275,102.0), U3.3(106.8625,99.45), J_BAT.2(120.0,95.0)
    routes += seg(101.1375, 97.55, 104.275, 97.55, "F.Cu", "B_MINUS", 0.35)
    routes += seg(104.275, 97.55, 104.275, 102.0, "F.Cu", "B_MINUS", 0.35)
    routes += seg(104.275, 99.45, 106.8625, 99.45, "F.Cu", "B_MINUS", 0.35)
    routes += seg(104.275, 97.55, 104.275, 95.2, "F.Cu", "B_MINUS", 0.35)
    routes += seg(104.275, 95.2, 116.0, 95.2, "F.Cu", "B_MINUS", 0.35)
    routes += seg(116.0, 95.2, 116.0, 93.5, "F.Cu", "B_MINUS", 0.35)
    routes += seg(116.0, 93.5, 120.0, 93.5, "F.Cu", "B_MINUS", 0.35)
    routes += seg(120.0, 93.5, 120.0, 95.0, "F.Cu", "B_MINUS", 0.35)
    return routes

# ============================================================
# GROUP C: USB & Charger
# ============================================================
def get_group_c_routes():
    routes = ""
    # CHRG_ANODE: D_CHRG.2(89.7875,80.0) to R_CHRG.2(89.825,82.5)
    routes += seg(89.7875, 80.0, 89.825, 80.1, "F.Cu", "CHRG_ANODE", 0.20)
    routes += seg(89.825, 80.1, 89.825, 82.5, "F.Cu", "CHRG_ANODE", 0.20)

    # STDBY_ANODE: D_STDBY.2(93.7875,80.0) to R_STDBY.2(93.825,82.5)
    routes += seg(93.7875, 80.0, 93.825, 80.1, "F.Cu", "STDBY_ANODE", 0.20)
    routes += seg(93.825, 80.1, 93.825, 82.5, "F.Cu", "STDBY_ANODE", 0.20)

    # CHRG_LED: D_CHRG.1(88.2125,80.0) to U1.7(92.475,97.865)
    routes += seg(88.2125, 80.0, 88.2125, 78.8, "F.Cu", "CHRG_LED", 0.20)
    routes += via(88.2125, 78.8, "CHRG_LED")
    routes += seg(88.2125, 78.8, 93.8, 78.8, "B.Cu", "CHRG_LED", 0.20)
    routes += seg(93.8, 78.8, 93.8, 97.865, "B.Cu", "CHRG_LED", 0.20)
    routes += via(93.8, 97.865, "CHRG_LED")
    routes += seg(93.8, 97.865, 92.475, 97.865, "F.Cu", "CHRG_LED", 0.20)

    # STDBY_LED: D_STDBY.1(92.2125,80.0) to U1.6(92.475,99.135)
    routes += seg(92.2125, 80.0, 92.2125, 78.2, "F.Cu", "STDBY_LED", 0.20)
    routes += via(92.2125, 78.2, "STDBY_LED")
    routes += seg(92.2125, 78.2, 94.8, 78.2, "B.Cu", "STDBY_LED", 0.20)
    routes += seg(94.8, 78.2, 94.8, 99.135, "B.Cu", "STDBY_LED", 0.20)
    routes += via(94.8, 99.135, "STDBY_LED")
    routes += seg(94.8, 99.135, 92.475, 99.135, "F.Cu", "STDBY_LED", 0.20)

    # U1_PROG: U1.2(87.525,97.865) to R_PROG.1(80.675,98.5)B
    routes += seg(87.525, 97.865, 80.675, 97.865, "F.Cu", "U1_PROG", 0.20)
    routes += via(80.675, 97.865, "U1_PROG")
    routes += seg(80.675, 97.865, 80.675, 98.50, "B.Cu", "U1_PROG", 0.20)

    # CC1: J_USB.A5(80.545,90.25) to R_CC1.1(83.675,87.0)
    routes += seg(80.545, 90.25, 82.2, 90.25, "F.Cu", "CC1", 0.15)
    routes += seg(82.2, 90.25, 83.0, 87.0, "F.Cu", "CC1", 0.15)
    routes += seg(83.0, 87.0, 83.675, 87.0, "F.Cu", "CC1", 0.15)

    # CC2: J_USB.B5(80.545,93.25) to R_CC2.1(83.675,96.0)
    routes += seg(80.545, 93.25, 82.2, 93.25, "F.Cu", "CC2", 0.15)
    routes += seg(82.2, 93.25, 83.0, 96.0, "F.Cu", "CC2", 0.15)
    routes += seg(83.0, 96.0, 83.675, 96.0, "F.Cu", "CC2", 0.15)

    # USB_D+: 100% on F.Cu!
    routes += seg(80.545, 91.25, 81.6, 91.25, "F.Cu", "USB_D+", 0.15)
    routes += seg(81.6, 91.25, 82.2, 91.35, "F.Cu", "USB_D+", 0.15)
    routes += seg(82.2, 91.35, 83.0, 91.35, "F.Cu", "USB_D+", 0.15)
    routes += seg(83.0, 91.35, 83.8, 90.5, "F.Cu", "USB_D+", 0.15)
    routes += seg(83.8, 90.5, 94.5, 90.5, "F.Cu", "USB_D+", 0.15)
    routes += seg(94.5, 90.5, 95.0, 91.0, "F.Cu", "USB_D+", 0.15)
    routes += seg(95.0, 91.0, 96.55, 91.0, "F.Cu", "USB_D+", 0.15)
    # B6 branch
    routes += seg(80.545, 92.25, 81.6, 92.25, "F.Cu", "USB_D+", 0.15)
    routes += seg(81.6, 92.25, 82.5, 92.8, "F.Cu", "USB_D+", 0.15)
    routes += seg(82.5, 92.8, 85.0, 92.8, "F.Cu", "USB_D+", 0.15)
    routes += seg(85.0, 92.8, 85.8, 90.5, "F.Cu", "USB_D+", 0.15)

    # USB_D-:
    routes += seg(80.545, 90.75, 82.5, 90.75, "F.Cu", "USB_D-", 0.15)
    routes += via(82.5, 90.75, "USB_D-")
    routes += seg(80.545, 91.75, 84.5, 91.75, "F.Cu", "USB_D-", 0.15)
    routes += via(84.5, 91.75, "USB_D-")
    routes += seg(82.5, 90.75, 84.5, 91.75, "B.Cu", "USB_D-", 0.15)
    routes += seg(84.5, 91.75, 91.5, 91.75, "B.Cu", "USB_D-", 0.15)
    routes += via(91.5, 91.75, "USB_D-")
    routes += seg(91.5, 91.75, 95.0, 91.5, "F.Cu", "USB_D-", 0.15)
    routes += seg(95.0, 91.5, 96.55, 91.5, "F.Cu", "USB_D-", 0.15)

    # CP_RST: U8.9(98.0,93.45) to R_CP_RST.2(104.825,88.5)
    routes += seg(98.0, 93.45, 98.0, 94.8, "F.Cu", "CP_RST", 0.20)
    routes += via(98.0, 94.8, "CP_RST")
    routes += seg(98.0, 94.8, 106.2, 94.8, "B.Cu", "CP_RST", 0.20)
    routes += seg(106.2, 94.8, 106.2, 88.5, "B.Cu", "CP_RST", 0.20)
    routes += via(106.2, 88.5, "CP_RST")
    routes += seg(106.2, 88.5, 104.825, 88.5, "F.Cu", "CP_RST", 0.20)

    # CP_VDD: U8.6(96.55,92.0), C_CP_VDD.1(93.225,92.5), C_CP_DEC.1(103.225,92.5), R_CP_RST.1(103.175,88.5)
    routes += seg(96.55, 92.0, 95.8, 92.0, "F.Cu", "CP_VDD", 0.20)
    routes += seg(95.8, 92.0, 95.8, 93.6, "F.Cu", "CP_VDD", 0.20)
    routes += seg(95.8, 93.6, 93.225, 93.6, "F.Cu", "CP_VDD", 0.20)
    routes += seg(93.225, 93.6, 93.225, 92.5, "F.Cu", "CP_VDD", 0.20)
    routes += via(95.8, 93.6, "CP_VDD")
    routes += seg(95.8, 93.6, 103.225, 93.6, "B.Cu", "CP_VDD", 0.20)
    routes += via(103.225, 93.6, "CP_VDD")
    routes += seg(103.225, 93.6, 103.225, 92.5, "F.Cu", "CP_VDD", 0.20)
    routes += seg(103.225, 92.5, 103.175, 88.5, "F.Cu", "CP_VDD", 0.20)
    return routes

# ============================================================
# GROUP D: Programming & Reset (VERIFIED: 0 DRC, 0 Unconnected)
# ============================================================
def get_group_d_routes():
    routes = ""
    # N_Q4_B: Q4.1(97.5625,82.55) to R_RTS.2(99.325,86.5)
    # Stays 100% on F.Cu at X=100.5
    routes += seg(97.5625, 82.55, 97.5625, 81.5, "F.Cu", "N_Q4_B", 0.15)
    routes += seg(97.5625, 81.5, 100.5, 81.5, "F.Cu", "N_Q4_B", 0.15)
    routes += seg(100.5, 81.5, 100.5, 86.5, "F.Cu", "N_Q4_B", 0.15)
    routes += seg(100.5, 86.5, 99.325, 86.5, "F.Cu", "N_Q4_B", 0.15)

    # N_Q3_B: Q3.1(103.5625,82.55) to R_DTR.2(105.325,86.5)
    # Stays 100% on F.Cu wrapping east of Q3 at X=107.0
    routes += seg(103.5625, 82.55, 103.5625, 81.5, "F.Cu", "N_Q3_B", 0.15)
    routes += seg(103.5625, 81.5, 107.0, 81.5, "F.Cu", "N_Q3_B", 0.15)
    routes += seg(107.0, 81.5, 107.0, 86.5, "F.Cu", "N_Q3_B", 0.15)
    routes += seg(107.0, 86.5, 105.325, 86.5, "F.Cu", "N_Q3_B", 0.15)

    # CP_DTR: U8.28(97.5,88.55), Q4.2(97.5625,84.45), R_DTR.1(103.675,86.5)
    # Escape U8.28 on F.Cu west to 95.5, up to Q4.2
    routes += seg(97.5, 88.55, 95.5, 88.55, "F.Cu", "CP_DTR", 0.20)
    routes += seg(95.5, 88.55, 95.5, 84.45, "F.Cu", "CP_DTR", 0.20)
    routes += seg(95.5, 84.45, 97.5625, 84.45, "F.Cu", "CP_DTR", 0.20)
    # To R_DTR.1 via B.Cu: via at (95.5, 84.45), east to 103.675 at Y=87.5
    routes += via(95.5, 84.45, "CP_DTR")
    routes += seg(95.5, 84.45, 95.5, 87.5, "B.Cu", "CP_DTR", 0.20)
    routes += seg(95.5, 87.5, 103.675, 87.5, "B.Cu", "CP_DTR", 0.20)
    routes += seg(103.675, 87.5, 103.675, 86.5, "B.Cu", "CP_DTR", 0.20)
    routes += via(103.675, 87.5, "CP_DTR")
    routes += seg(103.675, 87.5, 103.675, 86.5, "F.Cu", "CP_DTR", 0.20)

    # CP_RTS: U8.24(99.5,88.55), R_RTS.1(97.675,86.5), Q3.2(103.5625,84.45)
    routes += seg(99.5, 88.55, 99.5, 87.85, "F.Cu", "CP_RTS", 0.15)
    routes += seg(99.5, 87.85, 102.3, 87.85, "F.Cu", "CP_RTS", 0.15)
    routes += seg(102.3, 87.85, 102.3, 84.45, "F.Cu", "CP_RTS", 0.15)
    routes += seg(102.3, 84.45, 103.5625, 84.45, "F.Cu", "CP_RTS", 0.15)
    # Branch to R_RTS.1 via B.Cu: via at (102.3, 86.2)
    routes += seg(102.3, 84.45, 102.3, 86.2, "F.Cu", "CP_RTS", 0.15)
    routes += via(102.3, 86.2, "CP_RTS")
    routes += seg(102.3, 86.2, 97.675, 86.2, "B.Cu", "CP_RTS", 0.20)
    routes += via(97.675, 86.2, "CP_RTS")
    routes += seg(97.675, 86.2, 97.675, 86.5, "F.Cu", "CP_RTS", 0.20)

    # IO0: U6.25(108.75,74.26), Q3.3(105.4375,83.5), R_IO0.1(113.175,80.26), SW_BOOT.1(118.8,87.5), J_BOOT.5(121.0,79.66)
    routes += seg(108.75, 74.26, 110.0, 74.26, "F.Cu", "IO0", 0.20)
    routes += seg(110.0, 74.26, 110.0, 77.0, "F.Cu", "IO0", 0.20)
    # Branch to Q3.3 via B.Cu hop under N_Q3_B
    routes += seg(110.0, 77.0, 108.0, 77.0, "F.Cu", "IO0", 0.20)
    routes += seg(108.0, 77.0, 108.0, 83.50, "F.Cu", "IO0", 0.20)
    routes += via(108.0, 83.50, "IO0")
    routes += seg(108.0, 83.50, 105.4375, 83.50, "B.Cu", "IO0", 0.20)
    routes += via(105.4375, 83.50, "IO0")
    # Branch to R_IO0.1 on F.Cu
    routes += seg(110.0, 77.0, 113.175, 77.0, "F.Cu", "IO0", 0.20)
    routes += seg(113.175, 77.0, 113.175, 80.26, "F.Cu", "IO0", 0.20)
    # Branch to J_BOOT.5 and SW_BOOT.1 on F.Cu
    routes += seg(113.175, 78.5, 121.0, 78.5, "F.Cu", "IO0", 0.20)
    routes += seg(121.0, 78.5, 121.0, 79.66, "F.Cu", "IO0", 0.20)
    routes += seg(118.8, 78.5, 118.8, 87.5, "F.Cu", "IO0", 0.20)

    # CHIP_PU: U6.3(91.25,60.29), SW_EN.1(77.8,83.5), C_EN.1(81.725,80.0), R_EN.1(81.675,76.0), Q4.3(99.4375,83.5), J_BOOT.6(121.0,82.2)
    routes += seg(91.25, 60.29, 89.8, 60.29, "F.Cu", "CHIP_PU", 0.20)
    routes += via(89.8, 60.29, "CHIP_PU")
    routes += seg(89.8, 60.29, 89.8, 65.5, "B.Cu", "CHIP_PU", 0.20)
    routes += seg(89.8, 65.5, 76.0, 65.5, "B.Cu", "CHIP_PU", 0.20)
    routes += via(76.0, 65.5, "CHIP_PU")
    routes += seg(76.0, 65.5, 76.0, 83.5, "F.Cu", "CHIP_PU", 0.20)
    routes += seg(76.0, 76.0, 81.675, 76.0, "F.Cu", "CHIP_PU", 0.20)
    routes += seg(76.0, 80.0, 81.725, 80.0, "F.Cu", "CHIP_PU", 0.20)
    routes += seg(76.0, 83.5, 77.8, 83.5, "F.Cu", "CHIP_PU", 0.20)
    # Cross board on F.Cu at Y=77.0 north of LEDs to clear CHRG_LED/STDBY_LED/ANODEs
    routes += seg(81.675, 76.0, 81.675, 77.0, "F.Cu", "CHIP_PU", 0.20)
    routes += seg(81.675, 77.0, 96.5, 77.0, "F.Cu", "CHIP_PU", 0.20)
    routes += seg(96.5, 77.0, 96.5, 81.25, "F.Cu", "CHIP_PU", 0.20)
    routes += via(96.5, 81.25, "CHIP_PU")
    routes += seg(96.5, 81.25, 99.4375, 81.25, "B.Cu", "CHIP_PU", 0.20)
    # Branch to Q4.3 on B.Cu down to 84.5, via to F.Cu, up to 83.50
    routes += seg(99.4375, 81.25, 99.4375, 84.5, "B.Cu", "CHIP_PU", 0.20)
    routes += via(99.4375, 84.5, "CHIP_PU")
    routes += seg(99.4375, 84.5, 99.4375, 83.50, "F.Cu", "CHIP_PU", 0.20)
    # Continue east on B.Cu to J_BOOT.6
    routes += seg(99.4375, 81.25, 119.5, 81.25, "B.Cu", "CHIP_PU", 0.20)
    routes += seg(119.5, 81.25, 119.5, 82.20, "B.Cu", "CHIP_PU", 0.20)
    routes += seg(119.5, 82.20, 121.0, 82.20, "B.Cu", "CHIP_PU", 0.20)

    # TX0: U8.25(99.0,88.55), U6.35(108.75,61.56), J_BOOT.3(121.0,74.58)
    routes += seg(99.0, 88.55, 99.0, 87.55, "F.Cu", "TX0", 0.15)
    routes += seg(99.0, 87.55, 101.7, 87.55, "F.Cu", "TX0", 0.15)
    routes += seg(101.7, 87.55, 101.7, 79.75, "F.Cu", "TX0", 0.15)
    routes += via(101.7, 79.75, "TX0")
    routes += seg(101.7, 79.75, 116.2, 79.75, "B.Cu", "TX0", 0.20)
    routes += seg(116.2, 79.75, 116.2, 74.58, "B.Cu", "TX0", 0.20)
    routes += seg(116.2, 74.58, 121.0, 74.58, "B.Cu", "TX0", 0.20)
    routes += seg(116.2, 74.58, 116.2, 61.56, "B.Cu", "TX0", 0.20)
    routes += seg(116.2, 61.56, 111.0, 61.56, "B.Cu", "TX0", 0.20)
    routes += via(111.0, 61.56, "TX0")
    routes += seg(111.0, 61.56, 108.75, 61.56, "F.Cu", "TX0", 0.20)

    # RX0: U8.26(98.5,88.55), U6.34(108.75,62.83), J_BOOT.4(121.0,77.12)
    routes += seg(98.5, 88.55, 98.5, 87.25, "F.Cu", "RX0", 0.15)
    routes += seg(98.5, 87.25, 101.1, 87.25, "F.Cu", "RX0", 0.15)
    routes += seg(101.1, 87.25, 101.1, 78.9, "F.Cu", "RX0", 0.15)
    routes += via(101.1, 78.9, "RX0")
    routes += seg(101.1, 78.9, 115.0, 78.9, "B.Cu", "RX0", 0.20)
    routes += seg(115.0, 78.9, 115.0, 77.12, "B.Cu", "RX0", 0.20)
    # J_BOOT.4 branch on F.Cu
    routes += via(115.0, 77.12, "RX0")
    routes += seg(115.0, 77.12, 121.0, 77.12, "F.Cu", "RX0", 0.20)
    # Continue north on B.Cu to U6.34
    routes += seg(115.0, 77.12, 115.0, 62.83, "B.Cu", "RX0", 0.20)
    routes += seg(115.0, 62.83, 112.5, 62.83, "B.Cu", "RX0", 0.20)
    routes += via(112.5, 62.83, "RX0")
    routes += seg(112.5, 62.83, 108.75, 62.83, "F.Cu", "RX0", 0.20)

    return routes

# ============================================================
# GROUP E: Analog pH & TDS
# ============================================================
def get_group_e_routes():
    routes = ""
    # LM358B_OUT: U9.6(88.475,115.635), U9.7(88.475,114.365)
    routes += seg(88.475, 115.635, 88.475, 114.365, "F.Cu", "LM358B_OUT", 0.25)

    # PH_AMP_OUT: U9.1(83.525,113.095), U9.2(83.525,114.365), R_PH_FILT.1(84.175,122.0)B
    routes += seg(83.525, 113.095, 83.525, 114.365, "F.Cu", "PH_AMP_OUT", 0.25)
    routes += seg(83.525, 113.095, 83.525, 111.50, "F.Cu", "PH_AMP_OUT", 0.20)
    routes += via(83.525, 111.50, "PH_AMP_OUT")
    routes += seg(83.525, 111.50, 82.50, 111.50, "B.Cu", "PH_AMP_OUT", 0.20)
    routes += seg(82.50, 111.50, 82.50, 122.00, "B.Cu", "PH_AMP_OUT", 0.20)
    routes += seg(82.50, 122.00, 84.175, 122.00, "B.Cu", "PH_AMP_OUT", 0.20)

    # PH_SIGNAL: U9.3(83.525,115.635), R_PH_BIAS.2(84.175,119.5)B, J_BNC.1(90.0,120.5)
    # Connect J_BNC.1 to R_PH_BIAS.2 on B.Cu at Y=120.50
    routes += seg(90.00, 120.50, 84.175, 120.50, "B.Cu", "PH_SIGNAL", 0.25)
    routes += seg(84.175, 120.50, 84.175, 119.50, "B.Cu", "PH_SIGNAL", 0.20)
    # Via to F.Cu at (84.175, 118.50) to reach U9.3 on F.Cu (stays west of X=86.0)
    routes += seg(84.175, 119.50, 84.175, 118.50, "B.Cu", "PH_SIGNAL", 0.20)
    routes += via(84.175, 118.50, "PH_SIGNAL")
    routes += seg(84.175, 118.50, 86.00, 118.50, "F.Cu", "PH_SIGNAL", 0.20)
    routes += seg(86.00, 118.50, 86.00, 115.635, "F.Cu", "PH_SIGNAL", 0.20)
    routes += seg(86.00, 115.635, 83.525, 115.635, "F.Cu", "PH_SIGNAL", 0.20)

    # PH_OFFSET: J_BNC.2 shell (84.92, 95.08 at 125.58, 92.54 at 120.50), R_PH_BIAS.1(85.825,119.5)B, RV1.2(97.66,114.0)
    routes += seg(84.92, 125.58, 95.08, 125.58, "F.Cu", "PH_OFFSET", 0.40)
    routes += seg(95.08, 125.58, 92.54, 120.50, "F.Cu", "PH_OFFSET", 0.30)
    routes += seg(97.66, 114.00, 97.66, 120.50, "F.Cu", "PH_OFFSET", 0.25)
    routes += seg(97.66, 120.50, 92.54, 120.50, "F.Cu", "PH_OFFSET", 0.25)
    routes += seg(85.825, 119.50, 85.825, 118.00, "B.Cu", "PH_OFFSET", 0.20)
    routes += seg(85.825, 118.00, 92.54, 118.00, "B.Cu", "PH_OFFSET", 0.20)
    routes += seg(92.54, 118.00, 92.54, 120.50, "B.Cu", "PH_OFFSET", 0.20)

    # PH_ADC: U6.6(91.25,64.10), C_PH_FILT.1(84.225,113.0)B, R_PH_FILT.2(85.825,122.0)B
    # Highway West on F.Cu to Y=122.00, then east to X=87.20 on F.Cu
    routes += seg(91.25, 64.10, 90.00, 64.75, "F.Cu", "PH_ADC", 0.15)
    routes += seg(90.00, 64.75, 74.20, 64.75, "F.Cu", "PH_ADC", 0.15)
    routes += seg(74.20, 64.75, 74.20, 122.00, "F.Cu", "PH_ADC", 0.20)
    routes += seg(74.20, 122.00, 87.20, 122.00, "F.Cu", "PH_ADC", 0.20)
    # Branch 1: R_PH_FILT.2 via at (87.20, 122.00) to B.Cu
    routes += via(87.20, 122.00, "PH_ADC")
    routes += seg(87.20, 122.00, 85.825, 122.00, "B.Cu", "PH_ADC", 0.20)
    # Branch 2: C_PH_FILT.1 via F.Cu north along X=87.20 (hops over PH_OFFSET on B.Cu!)
    routes += seg(87.20, 122.00, 87.20, 111.00, "F.Cu", "PH_ADC", 0.20)
    routes += via(87.20, 111.00, "PH_ADC")
    routes += seg(87.20, 111.00, 84.225, 111.00, "B.Cu", "PH_ADC", 0.20)
    routes += seg(84.225, 111.00, 84.225, 113.00, "B.Cu", "PH_ADC", 0.20)

    # TDS_PROBE_DRIVE: Q1.3(106.4375,114.5) to J_TDS.1(101.5,123.5)
    routes += seg(106.4375, 114.50, 106.4375, 112.00, "F.Cu", "TDS_PROBE_DRIVE", 0.20)
    routes += seg(106.4375, 112.00, 101.50, 112.00, "F.Cu", "TDS_PROBE_DRIVE", 0.20)
    routes += seg(101.50, 112.00, 101.50, 123.50, "F.Cu", "TDS_PROBE_DRIVE", 0.25)

    # TDS_GATE: Q1.1(104.5625,113.55), R_TDS_PD.1(105.325,117.2), R_TDS_GATE.2(108.325,119.4)
    routes += seg(104.5625, 113.55, 102.70, 113.55, "F.Cu", "TDS_GATE", 0.15)
    routes += seg(102.70, 113.55, 102.70, 118.20, "F.Cu", "TDS_GATE", 0.15)
    routes += seg(102.70, 118.20, 105.325, 118.20, "F.Cu", "TDS_GATE", 0.15)
    routes += seg(105.325, 118.20, 105.325, 117.20, "F.Cu", "TDS_GATE", 0.15)
    routes += seg(105.325, 118.20, 108.325, 118.20, "F.Cu", "TDS_GATE", 0.15)
    routes += seg(108.325, 118.20, 108.325, 119.40, "F.Cu", "TDS_GATE", 0.15)

    # TDS_SENSE: R_TDS_REF.1(108.5875,114.5), R_TDS_FILT.1(109.675,117.2), J_TDS.2(104.0,123.5)
    routes += seg(108.5875, 114.50, 108.5875, 116.00, "F.Cu", "TDS_SENSE", 0.20)
    routes += seg(108.5875, 116.00, 109.675, 116.00, "F.Cu", "TDS_SENSE", 0.20)
    routes += seg(109.675, 116.00, 109.675, 117.20, "F.Cu", "TDS_SENSE", 0.20)
    routes += seg(109.675, 117.20, 109.675, 121.60, "F.Cu", "TDS_SENSE", 0.20)
    routes += via(109.675, 121.60, "TDS_SENSE")
    routes += seg(109.675, 121.60, 104.00, 121.60, "B.Cu", "TDS_SENSE", 0.20)
    routes += seg(104.00, 121.60, 104.00, 123.50, "B.Cu", "TDS_SENSE", 0.25)

    # TDS_ADC: U6.7(91.25,65.37), R_TDS_FILT.2(111.325,117.2), C_TDS_FILT.1(112.725,119.4)
    # Escape east under U6 shield to drop via to B.Cu, then north to 57.0, bypass H2 via Y=55.0
    routes += seg(91.25, 65.37, 93.00, 65.37, "F.Cu", "TDS_ADC", 0.20)
    routes += via(93.00, 65.37, "TDS_ADC")
    routes += seg(93.00, 65.37, 93.00, 57.00, "B.Cu", "TDS_ADC", 0.20)
    routes += seg(93.00, 57.00, 117.00, 57.00, "B.Cu", "TDS_ADC", 0.20)
    routes += seg(117.00, 57.00, 117.00, 55.00, "B.Cu", "TDS_ADC", 0.20)
    routes += seg(117.00, 55.00, 123.80, 55.00, "B.Cu", "TDS_ADC", 0.20)
    routes += seg(123.80, 55.00, 123.80, 120.50, "B.Cu", "TDS_ADC", 0.20)
    routes += seg(123.80, 120.50, 111.325, 120.50, "B.Cu", "TDS_ADC", 0.20)
    routes += via(111.325, 120.50, "TDS_ADC")
    routes += seg(111.325, 120.50, 111.325, 117.20, "F.Cu", "TDS_ADC", 0.20)
    routes += seg(111.325, 119.40, 112.725, 119.40, "F.Cu", "TDS_ADC", 0.20)

    # TDS_PWR_CTRL: U6.11(91.25,70.45), R_TDS_GATE.1(106.675,119.4)
    # Via at (89.50, 72.00) to B.Cu, Highway West on B.Cu, shift east to X=107.80 on B.Cu to clear +3V3 via
    routes += seg(91.25, 70.45, 89.50, 70.45, "F.Cu", "TDS_PWR_CTRL", 0.20)
    routes += seg(89.50, 70.45, 89.50, 72.00, "F.Cu", "TDS_PWR_CTRL", 0.20)
    routes += via(89.50, 72.00, "TDS_PWR_CTRL")
    routes += seg(89.50, 72.00, 73.70, 72.00, "B.Cu", "TDS_PWR_CTRL", 0.20)
    routes += seg(73.70, 72.00, 73.70, 100.00, "B.Cu", "TDS_PWR_CTRL", 0.20)
    routes += seg(73.70, 100.00, 74.80, 100.00, "B.Cu", "TDS_PWR_CTRL", 0.20)
    routes += via(74.80, 100.00, "TDS_PWR_CTRL")
    routes += seg(74.80, 100.00, 80.20, 100.00, "F.Cu", "TDS_PWR_CTRL", 0.20)
    routes += via(80.20, 100.00, "TDS_PWR_CTRL")
    routes += seg(80.20, 100.00, 107.80, 100.00, "B.Cu", "TDS_PWR_CTRL", 0.20)
    routes += seg(107.80, 100.00, 107.80, 120.50, "B.Cu", "TDS_PWR_CTRL", 0.20)
    routes += seg(107.80, 120.50, 106.675, 120.50, "B.Cu", "TDS_PWR_CTRL", 0.20)
    routes += via(106.675, 120.50, "TDS_PWR_CTRL")
    routes += seg(106.675, 120.50, 106.675, 119.40, "F.Cu", "TDS_PWR_CTRL", 0.20)

    return routes

# ============================================================
# GROUP F: LCD signals
# Strategy: Direct B.Cu termination to J_LCD pins (no F.Cu stubs near J_LCD)
# ============================================================
def get_group_f_routes():
    routes = (

        # 1. LCD_BL_SINK
        seg(114.4375, 114.50, 116.5875, 114.50, 'F.Cu', 'LCD_BL_SINK', 0.25) +
        # 2. LCD_GATE
        seg(112.5625, 113.55, 112.5625, 112.60, 'F.Cu', 'LCD_GATE', 0.15) +
        via(112.5625, 112.60, 'LCD_GATE') +
        seg(112.5625, 112.60, 117.3250, 112.60, 'B.Cu', 'LCD_GATE', 0.15) +
        seg(117.3250, 112.60, 117.3250, 116.00, 'B.Cu', 'LCD_GATE', 0.15) +
        via(117.3250, 116.00, 'LCD_GATE') +
        seg(117.3250, 116.00, 117.3250, 117.20, 'F.Cu', 'LCD_GATE', 0.15) +
        seg(117.3250, 117.20, 118.6750, 117.20, 'F.Cu', 'LCD_GATE', 0.15) +
        seg(118.6750, 117.20, 118.6750, 119.40, 'F.Cu', 'LCD_GATE', 0.15) +
        # 3. LCD_BL_PWM
        seg(91.25, 66.64, 93.80, 66.64, 'F.Cu', 'LCD_BL_PWM', 0.15) +
        seg(93.80, 66.64, 93.80, 56.60, 'F.Cu', 'LCD_BL_PWM', 0.15) +
        seg(93.80, 56.60, 112.00, 56.60, 'F.Cu', 'LCD_BL_PWM', 0.15) +
        seg(112.00, 56.60, 112.00, 54.50, 'F.Cu', 'LCD_BL_PWM', 0.15) +
        seg(112.00, 54.50, 117.20, 54.50, 'F.Cu', 'LCD_BL_PWM', 0.15) +
        seg(117.20, 54.50, 117.20, 62.50, 'F.Cu', 'LCD_BL_PWM', 0.15) +
        via(117.20, 62.50, 'LCD_BL_PWM') +
        seg(117.20, 62.50, 122.70, 62.50, 'B.Cu', 'LCD_BL_PWM', 0.15) +
        seg(122.70, 62.50, 122.70, 118.50, 'B.Cu', 'LCD_BL_PWM', 0.15) +
        seg(122.70, 118.50, 115.675, 118.50, 'B.Cu', 'LCD_BL_PWM', 0.15) +
        via(115.675, 118.50, 'LCD_BL_PWM') +
        seg(115.675, 118.50, 115.675, 117.20, 'F.Cu', 'LCD_BL_PWM', 0.15) +
        # 4. LCD_LED_K
        seg(118.4125, 114.50, 118.4125, 115.50, 'F.Cu', 'LCD_LED_K', 0.15) +
        seg(118.4125, 115.50, 121.2000, 115.50, 'F.Cu', 'LCD_LED_K', 0.15) +
        seg(121.2000, 115.50, 121.2000, 121.50, 'F.Cu', 'LCD_LED_K', 0.15) +
        seg(121.2000, 121.50, 118.0000, 121.50, 'F.Cu', 'LCD_LED_K', 0.15) +
        seg(118.0000, 121.50, 118.0000, 123.00, 'F.Cu', 'LCD_LED_K', 0.15) +
        via(118.0000, 123.00, 'LCD_LED_K') +
        seg(118.0000, 123.00, 118.0000, 127.45, 'B.Cu', 'LCD_LED_K', 0.15) +
        seg(118.0000, 127.45, 76.2000, 127.45, 'B.Cu', 'LCD_LED_K', 0.15) +
        seg(76.2000, 127.45, 76.2000, 119.28, 'B.Cu', 'LCD_LED_K', 0.15) +
        seg(76.2000, 119.28, 76.5000, 119.28, 'B.Cu', 'LCD_LED_K', 0.25) +
        # 5. SPI_SCK: via at (93.30, 72.30)
        seg(108.75, 67.91, 93.30, 67.91, 'F.Cu', 'SPI_SCK', 0.15) +
        seg(93.30, 67.91, 93.30, 72.30, 'F.Cu', 'SPI_SCK', 0.15) +
        via(93.30, 72.30, 'SPI_SCK') +
        seg(93.30, 72.30, 92.50, 72.30, 'B.Cu', 'SPI_SCK', 0.15) +
        seg(92.50, 72.30, 92.20, 72.60, 'B.Cu', 'SPI_SCK', 0.15) +
        seg(92.20, 72.60, 76.80, 72.60, 'B.Cu', 'SPI_SCK', 0.15) +
        seg(76.80, 72.60, 76.80, 98.80, 'B.Cu', 'SPI_SCK', 0.15) +
        seg(76.80, 98.80, 77.80, 98.80, 'B.Cu', 'SPI_SCK', 0.15) +
        seg(77.80, 98.80, 77.80, 106.58, 'B.Cu', 'SPI_SCK', 0.15) +
        seg(77.80, 106.58, 76.50, 106.58, 'B.Cu', 'SPI_SCK', 0.25) +
        # 6. SPI_MOSI (bypassing GPS_ANT via X=90.10 and returning at 71.80)
        seg(108.75, 59.02, 94.60, 59.02, 'F.Cu', 'SPI_MOSI', 0.15) +
        via(94.60, 59.02, 'SPI_MOSI') +
        seg(94.60, 59.02, 93.85, 59.02, 'B.Cu', 'SPI_MOSI', 0.15) +
        seg(93.85, 59.02, 93.85, 66.20, 'B.Cu', 'SPI_MOSI', 0.15) +
        seg(93.85, 66.20, 90.10, 66.20, 'B.Cu', 'SPI_MOSI', 0.15) +
        seg(90.10, 66.20, 90.10, 71.70, 'B.Cu', 'SPI_MOSI', 0.15) +
        seg(90.10, 71.70, 93.85, 71.70, 'B.Cu', 'SPI_MOSI', 0.15) +
        seg(93.85, 71.70, 93.85, 72.92, 'B.Cu', 'SPI_MOSI', 0.15) +
        seg(93.85, 72.92, 77.15, 72.92, 'B.Cu', 'SPI_MOSI', 0.15) +
        seg(77.15, 72.92, 77.15, 98.40, 'B.Cu', 'SPI_MOSI', 0.15) +
        seg(77.15, 98.40, 78.15, 98.40, 'B.Cu', 'SPI_MOSI', 0.15) +
        seg(78.15, 98.40, 78.15, 109.12, 'B.Cu', 'SPI_MOSI', 0.15) +
        seg(78.15, 109.12, 76.50, 109.12, 'B.Cu', 'SPI_MOSI', 0.25) +
        # 7. LCD_RST (offset to 70.85 to clear LCD_CS via)
        seg(108.75, 70.45, 107.50, 70.45, 'F.Cu', 'LCD_RST', 0.15) +
        seg(107.50, 70.45, 107.10, 70.85, 'F.Cu', 'LCD_RST', 0.15) +
        seg(107.10, 70.85, 94.40, 70.85, 'F.Cu', 'LCD_RST', 0.15) +
        via(94.40, 70.85, 'LCD_RST') +
        seg(94.40, 70.85, 94.40, 73.24, 'B.Cu', 'LCD_RST', 0.15) +
        seg(94.40, 73.24, 77.50, 73.24, 'B.Cu', 'LCD_RST', 0.15) +
        seg(77.50, 73.24, 77.50, 98.00, 'B.Cu', 'LCD_RST', 0.15) +
        seg(77.50, 98.00, 78.50, 98.00, 'B.Cu', 'LCD_RST', 0.15) +
        seg(78.50, 98.00, 78.50, 111.66, 'B.Cu', 'LCD_RST', 0.15) +
        seg(78.50, 111.66, 76.50, 111.66, 'B.Cu', 'LCD_RST', 0.25) +
        # 8. LCD_DC (original)
        seg(108.75, 71.72, 94.95, 71.72, 'F.Cu', 'LCD_DC', 0.15) +
        via(94.95, 71.72, 'LCD_DC') +
        seg(94.95, 71.72, 94.95, 73.56, 'B.Cu', 'LCD_DC', 0.15) +
        seg(94.95, 73.56, 77.85, 73.56, 'B.Cu', 'LCD_DC', 0.15) +
        seg(77.85, 73.56, 77.85, 97.60, 'B.Cu', 'LCD_DC', 0.15) +
        seg(77.85, 97.60, 78.85, 97.60, 'B.Cu', 'LCD_DC', 0.15) +
        seg(78.85, 97.60, 78.85, 114.20, 'B.Cu', 'LCD_DC', 0.15) +
        seg(78.85, 114.20, 76.50, 114.20, 'B.Cu', 'LCD_DC', 0.25) +
        # 9. LCD_CS (step south on F.Cu to 70.05 to clear GPS_ANT on B.Cu)
        seg(108.75, 69.18, 95.50, 69.18, 'F.Cu', 'LCD_CS', 0.15) +
        seg(95.50, 69.18, 95.50, 70.05, 'F.Cu', 'LCD_CS', 0.15) +
        via(95.50, 70.05, 'LCD_CS') +
        seg(95.50, 70.05, 95.50, 73.88, 'B.Cu', 'LCD_CS', 0.15) +
        seg(95.50, 73.88, 78.20, 73.88, 'B.Cu', 'LCD_CS', 0.15) +
        seg(78.20, 73.88, 78.20, 97.20, 'B.Cu', 'LCD_CS', 0.15) +
        seg(78.20, 97.20, 79.20, 97.20, 'B.Cu', 'LCD_CS', 0.15) +
        seg(79.20, 97.20, 79.20, 116.74, 'B.Cu', 'LCD_CS', 0.15) +
        seg(79.20, 116.74, 76.50, 116.74, 'B.Cu', 'LCD_CS', 0.25)

    )
    return routes

def get_group_g_routes():
    routes = ""
    # GPS_ANT: J_ANT.1(91.5,69.25) to U_GPS.4(97.1,69.25) on B.Cu
    routes += seg(91.5000, 69.2500, 97.1000, 69.2500, "B.Cu", "GPS_ANT", 0.40)

    # GPS_TX: U6.16(95.56,75.51) to U_GPS.21(108.9,69.25) via (103.50,74.00)
    routes += seg(95.56, 75.51, 95.56, 74.00, "F.Cu", "GPS_TX", 0.15)
    routes += seg(95.56, 74.00, 103.50, 74.00, "F.Cu", "GPS_TX", 0.15)
    routes += via(103.50, 74.00, "GPS_TX")
    routes += seg(103.50, 74.00, 103.50, 69.25, "B.Cu", "GPS_TX", 0.15)
    routes += seg(103.50, 69.25, 108.90, 69.25, "B.Cu", "GPS_TX", 0.15)

    # GPS_RX: U6.13(91.25,72.99) to U_GPS.20(108.9,70.35) via (105.50,73.10)
    routes += seg(91.25, 72.99, 105.50, 72.99, "F.Cu", "GPS_RX", 0.15)
    routes += seg(105.50, 72.99, 105.50, 73.10, "F.Cu", "GPS_RX", 0.15)
    routes += via(105.50, 73.10, "GPS_RX")
    routes += seg(105.50, 73.10, 105.50, 70.35, "B.Cu", "GPS_RX", 0.15)
    routes += seg(105.50, 70.35, 108.90, 70.35, "B.Cu", "GPS_RX", 0.15)

    # VBAT_RTC: BT1.1(85.35,94.50) to U7.14(114.15,114.405)
    routes += seg(85.35, 94.50, 84.00, 94.50, "B.Cu", "VBAT_RTC", 0.15)
    routes += seg(84.00, 94.50, 84.00, 98.80, "B.Cu", "VBAT_RTC", 0.15)
    routes += via(84.00, 98.80, "VBAT_RTC")
    routes += seg(84.00, 98.80, 84.00, 101.80, "F.Cu", "VBAT_RTC", 0.15)
    routes += via(84.00, 101.80, "VBAT_RTC")
    routes += seg(84.00, 101.80, 106.50, 101.80, "B.Cu", "VBAT_RTC", 0.15)
    routes += seg(106.50, 101.80, 106.50, 110.00, "B.Cu", "VBAT_RTC", 0.15)
    routes += via(106.50, 110.00, "VBAT_RTC")
    routes += seg(106.50, 110.00, 109.20, 110.00, "F.Cu", "VBAT_RTC", 0.15)
    routes += via(109.20, 110.00, "VBAT_RTC")
    routes += seg(109.20, 110.00, 109.20, 114.405, "B.Cu", "VBAT_RTC", 0.15)
    routes += seg(109.20, 114.405, 114.15, 114.405, "B.Cu", "VBAT_RTC", 0.15)

    # I2C_SCL: U6.36(108.75,60.29), R_SCL_PU.1(113.175,66.29), U7.16(114.15,116.945)
    routes += seg(108.75, 60.29, 113.175, 60.29, "F.Cu", "I2C_SCL", 0.15)
    routes += seg(113.175, 60.29, 113.175, 66.29, "F.Cu", "I2C_SCL", 0.15)
    routes += seg(113.175, 65.00, 124.20, 65.00, "F.Cu", "I2C_SCL", 0.15)
    routes += seg(124.20, 65.00, 124.20, 113.00, "F.Cu", "I2C_SCL", 0.15)
    routes += seg(124.20, 113.00, 120.50, 113.00, "F.Cu", "I2C_SCL", 0.15)
    routes += via(120.50, 113.00, "I2C_SCL")
    routes += seg(120.50, 113.00, 120.50, 116.945, "B.Cu", "I2C_SCL", 0.15)
    routes += seg(120.50, 116.945, 114.15, 116.945, "B.Cu", "I2C_SCL", 0.15)

    # I2C_SDA: U6.33(108.75,64.10), R_SDA_PU.1(113.175,70.10), U7.15(114.15,115.675)
    routes += seg(108.75, 64.10, 111.50, 64.10, "F.Cu", "I2C_SDA", 0.15)
    routes += seg(111.50, 64.10, 111.50, 70.10, "F.Cu", "I2C_SDA", 0.15)
    routes += seg(111.50, 70.10, 113.175, 70.10, "F.Cu", "I2C_SDA", 0.15)
    routes += seg(113.175, 70.10, 113.175, 70.80, "F.Cu", "I2C_SDA", 0.15)
    routes += seg(113.175, 70.80, 123.60, 70.80, "F.Cu", "I2C_SDA", 0.15)
    routes += seg(123.60, 70.80, 123.60, 112.00, "F.Cu", "I2C_SDA", 0.15)
    routes += seg(123.60, 112.00, 121.50, 112.00, "F.Cu", "I2C_SDA", 0.15)
    routes += via(121.50, 112.00, "I2C_SDA")
    routes += seg(121.50, 112.00, 121.50, 117.80, "B.Cu", "I2C_SDA", 0.15)
    routes += seg(121.50, 117.80, 112.00, 117.80, "B.Cu", "I2C_SDA", 0.15)
    routes += seg(112.00, 117.80, 112.00, 115.675, "B.Cu", "I2C_SDA", 0.15)
    routes += seg(112.00, 115.675, 114.15, 115.675, "B.Cu", "I2C_SDA", 0.15)

    # ONEWIRE_TEMP: U6.26(108.75,72.99), R_DS_PU.1(114.175,111.5)F, J_TEMP.2(112.5,123.5)
    routes += seg(108.75, 72.99, 117.00, 72.99, "F.Cu", "ONEWIRE_TEMP", 0.15)
    routes += seg(117.00, 72.99, 117.50, 73.31, "F.Cu", "ONEWIRE_TEMP", 0.15)
    routes += seg(117.50, 73.31, 123.00, 73.31, "F.Cu", "ONEWIRE_TEMP", 0.15)
    routes += seg(123.00, 73.31, 123.00, 109.70, "F.Cu", "ONEWIRE_TEMP", 0.15)
    routes += seg(123.00, 109.70, 114.175, 109.70, "F.Cu", "ONEWIRE_TEMP", 0.15)
    routes += seg(114.175, 109.70, 114.175, 111.50, "F.Cu", "ONEWIRE_TEMP", 0.15)
    routes += seg(114.175, 109.70, 110.00, 109.70, "F.Cu", "ONEWIRE_TEMP", 0.15)
    routes += seg(110.00, 109.70, 110.00, 110.80, "F.Cu", "ONEWIRE_TEMP", 0.15)
    routes += seg(110.00, 110.80, 99.00, 110.80, "F.Cu", "ONEWIRE_TEMP", 0.15)
    routes += via(99.00, 110.80, "ONEWIRE_TEMP")
    routes += seg(99.00, 110.80, 99.00, 125.50, "B.Cu", "ONEWIRE_TEMP", 0.15)
    routes += seg(99.00, 125.50, 112.50, 125.50, "B.Cu", "ONEWIRE_TEMP", 0.15)
    routes += seg(112.50, 125.50, 112.50, 123.50, "B.Cu", "ONEWIRE_TEMP", 0.15)

    # RTC_INT: U6.9(91.25,67.91), R_RTC_PU.1(88.825,67.91), U7.3(104.85,114.405)B
    # 1. From U6.9 to R_RTC_PU.1
    routes += seg(91.25, 67.91, 88.825, 67.91, "F.Cu", "RTC_INT", 0.15)
    # 2. Jog west to corridor X=88.0
    routes += seg(88.825, 67.91, 88.00, 67.91, "F.Cu", "RTC_INT", 0.15)
    # 3. Descend south on F.Cu along X=88.0 to Y=75.5
    routes += seg(88.00, 67.91, 88.00, 75.50, "F.Cu", "RTC_INT", 0.15)
    # 4. Via to B.Cu at (88.0, 75.5)
    routes += via(88.00, 75.50, "RTC_INT")
    # 5. Jog to X=87.5 on B.Cu
    routes += seg(88.00, 75.50, 87.50, 76.50, "B.Cu", "RTC_INT", 0.15)
    # 6. Descend south on B.Cu along X=87.5 to Y=89.8
    routes += seg(87.50, 76.50, 87.50, 89.80, "B.Cu", "RTC_INT", 0.15)
    # 7. Jog east on B.Cu to X=92.5 at Y=89.8
    routes += seg(87.50, 89.80, 92.50, 89.80, "B.Cu", "RTC_INT", 0.15)
    # 8. Descend south on B.Cu along X=92.5 to Y=98.8
    routes += seg(92.50, 89.80, 92.50, 98.80, "B.Cu", "RTC_INT", 0.15)
    # 9. Jog west on B.Cu to X=85.5 at Y=98.8
    routes += seg(92.50, 98.80, 85.50, 98.80, "B.Cu", "RTC_INT", 0.15)
    # 10. Via north to F.Cu at (85.5, 98.8)
    routes += via(85.50, 98.80, "RTC_INT")
    # 11. Hop over TDS_PWR_CTRL on F.Cu
    routes += seg(85.50, 98.80, 85.50, 101.00, "F.Cu", "RTC_INT", 0.15)
    # 12. Via south to B.Cu at (85.5, 101.0)
    routes += via(85.50, 101.00, "RTC_INT")
    # 13. Run east on B.Cu at Y=101.0 to X=107.2 (parallel to VBAT_RTC, clr=0.65mm)
    routes += seg(85.50, 101.00, 107.20, 101.00, "B.Cu", "RTC_INT", 0.15)
    # 14. Descend south on B.Cu along X=107.2 to Y=114.405 (parallel to VBAT_RTC, clr=0.55mm)
    routes += seg(107.20, 101.00, 107.20, 114.405, "B.Cu", "RTC_INT", 0.15)
    # 15. Jog west into U7.3 (104.85, 114.405)
    routes += seg(107.20, 114.405, 104.85, 114.405, "B.Cu", "RTC_INT", 0.15)
    return routes

# ============================================================
# FANOUT: Power via connections
# ============================================================
def get_fanout_routes():
    routes = ""

    # +3V3 U6.2 fanout via
    p_u6_2 = get_pad('+3V3', 'U6', '2')
    routes += seg(p_u6_2['x'], p_u6_2['y'], 89.8, p_u6_2['y'], "F.Cu", "+3V3", 0.30)
    routes += via(89.8, p_u6_2['y'], "+3V3")

    # +3V3: R_EN.2(83.325,76.0) local via to In2.Cu
    p_ren = get_pad('+3V3', 'R_EN', '2')
    routes += seg(p_ren['x'], p_ren['y'], p_ren['x'], 74.5, "F.Cu", "+3V3", 0.25)
    routes += via(p_ren['x'], 74.5, "+3V3")

    # +3V3: C_MCU_BULK.1(86.05,60.5) local via to In2.Cu
    p_mb = get_pad('+3V3', 'C_MCU_BULK', '1')
    routes += via(p_mb['x'], p_mb['y'], "+3V3")

    # +3V3: C_MCU_DEC.1(86.225,63.5) via
    p_md = get_pad('+3V3', 'C_MCU_DEC', '1')
    routes += via(p_md['x'], p_md['y'], "+3V3")

    # +3V3: R_RTC_PU.2(87.175,67.91) via to In2.Cu
    p_rpu = get_pad('+3V3', 'R_RTC_PU', '2')
    routes += via(p_rpu['x'], p_rpu['y'], "+3V3")

    # +3V3: R_IO0.2(114.825,80.26)
    p_rio = get_pad('+3V3', 'R_IO0', '2')
    routes += seg(p_rio['x'], p_rio['y'], p_rio['x'], 84.5, "F.Cu", "+3V3", 0.25)
    routes += via(p_rio['x'], 84.5, "+3V3")

    # +3V3: I2C pullups R_SCL_PU.2 and R_SDA_PU.2
    p_scl_pu = get_pad('+3V3', 'R_SCL_PU', '2')
    p_sda_pu = get_pad('+3V3', 'R_SDA_PU', '2')
    routes += seg(p_scl_pu['x'], p_scl_pu['y'], 117.5, p_scl_pu['y'], "F.Cu", "+3V3", 0.25)
    routes += seg(117.5, p_scl_pu['y'], 117.5, p_sda_pu['y'], "F.Cu", "+3V3", 0.25)
    routes += seg(p_sda_pu['x'], p_sda_pu['y'], 117.5, p_sda_pu['y'], "F.Cu", "+3V3", 0.25)
    routes += via(117.5, 68.2, "+3V3")

    # +3V3: GPS U_GPS.22/23 (via into open space under ESP32 at 105.0, 65.0)
    p_g22 = get_pad('+3V3', 'U_GPS', '22')
    p_g23 = get_pad('+3V3', 'U_GPS', '23')
    routes += seg(p_g22['x'], p_g22['y'], p_g23['x'], p_g23['y'], "B.Cu", "+3V3", 0.30)
    routes += seg(p_g23['x'], p_g23['y'], 105.0, p_g23['y'], "B.Cu", "+3V3", 0.30)
    routes += seg(105.0, p_g23['y'], 105.0, 65.0, "B.Cu", "+3V3", 0.30)
    routes += via(105.0, 65.0, "+3V3")

    # +3V3: GPS caps
    p_cg1 = get_pad('+3V3', 'C_GPS1', '1')
    p_cg2 = get_pad('+3V3', 'C_GPS2', '1')
    routes += seg(p_cg1['x'], p_cg1['y'], 102.22, 60.2, "B.Cu", "+3V3", 0.25)
    routes += via(102.22, 60.2, "+3V3")
    routes += seg(p_cg2['x'], p_cg2['y'], 98.05, 60.2, "B.Cu", "+3V3", 0.25)
    routes += via(98.05, 60.2, "+3V3")

    # +3V3: U5.2(111.85,105.0) — LDO output
    routes += seg(111.85, 105.0, 114.5, 105.0, "F.Cu", "+3V3", 0.40)
    routes += via(114.5, 105.0, "+3V3")

    # +3V3: C_LDO_OUT
    p_clo = get_pad('+3V3', 'C_LDO_OUT', '1')
    routes += seg(p_clo['x'], p_clo['y'], 120.7, p_clo['y'], "B.Cu", "+3V3", 0.35)
    routes += via(120.7, p_clo['y'], "+3V3")

    # +3V3: C_LDO_DEC
    p_cld = get_pad('+3V3', 'C_LDO_DEC', '1')
    routes += seg(p_cld['x'], p_cld['y'], 120.7, p_cld['y'], "B.Cu", "+3V3", 0.35)
    routes += via(120.7, p_cld['y'], "+3V3")

    # +3V3: U7.5(104.85,115.675)B
    routes += seg(104.85, 115.675, 107.0, 115.675, "B.Cu", "+3V3", 0.25)
    routes += via(107.0, 115.675, "+3V3")

    # +3V3: C_RTC_VCC
    p_crtc = get_pad('+3V3', 'C_RTC_VCC', '1')
    routes += seg(p_crtc['x'], p_crtc['y'], 116.5, p_crtc['y'], "B.Cu", "+3V3", 0.25)
    routes += via(116.5, p_crtc['y'], "+3V3")

    # +3V3: R_DS_PU.2 and C_DS_VCC.1
    p_cds = get_pad('+3V3', 'C_DS_VCC', '1')
    p_rds = get_pad('+3V3', 'R_DS_PU', '2')
    routes += seg(p_rds['x'], p_rds['y'], p_rds['x'], 110.5, "F.Cu", "+3V3", 0.25)
    routes += seg(p_rds['x'], 110.5, p_cds['x'], 110.5, "F.Cu", "+3V3", 0.25)
    routes += seg(p_cds['x'], 110.5, p_cds['x'], p_cds['y'], "F.Cu", "+3V3", 0.25)
    routes += via(p_cds['x'], 110.5, "+3V3")

    # +3V3: R_TDS_REF.2
    p_rtds = get_pad('+3V3', 'R_TDS_REF', '2')
    routes += seg(p_rtds['x'], p_rtds['y'], 110.41, 113.3, "F.Cu", "+3V3", 0.25)
    routes += via(110.41, 113.3, "+3V3")

    # +3V3: C_LCD_VCC
    p_clcd = get_pad('+3V3', 'C_LCD_VCC', '1')
    routes += seg(p_clcd['x'], p_clcd['y'], 119.5, p_clcd['y'], "F.Cu", "+3V3", 0.25)
    routes += via(119.5, p_clcd['y'], "+3V3")

    # GND: U6.15 fanout via
    p_u6_15 = get_pad('GND', 'U6', '15')
    routes += seg(p_u6_15['x'], p_u6_15['y'], 93.69, 75.71, "F.Cu", "GND", 0.25)
    routes += via(93.69, 75.71, "GND")

    # GND: R_PROG.2 fanout via
    p_rprog_2 = get_pad('GND', 'R_PROG', '2')
    routes += seg(p_rprog_2['x'], p_rprog_2['y'], 82.40, 99.15, "B.Cu", "GND", 0.25)
    routes += via(82.40, 99.15, "GND")

    # +5V POWER TRUNK
    p_d1_1 = get_pad('+5V', 'D1', '1')
    p_cldo_in = get_pad('+5V', 'C_LDO_IN', '1')
    p_u5_3 = get_pad('+5V', 'U5', '3')
    p_cbo2 = get_pad('+5V', 'C_BST_OUT2', '1')
    p_cbo1 = get_pad('+5V', 'C_BST_OUT1', '1')
    p_cff_1 = get_pad('+5V', 'C_FF', '1')
    p_rfb1_1 = get_pad('+5V', 'R_FB1', '1')

    routes += seg(p_d1_1['x'], p_d1_1['y'], p_d1_1['x'], 108.0, "F.Cu", "+5V", 0.40)
    routes += seg(p_d1_1['x'], 108.0, p_cldo_in['x'], 108.0, "F.Cu", "+5V", 0.40)
    routes += seg(p_cldo_in['x'], 108.0, p_cldo_in['x'], p_cldo_in['y'], "F.Cu", "+5V", 0.40)
    routes += seg(p_cldo_in['x'], 108.0, p_u5_3['x'], 108.0, "F.Cu", "+5V", 0.40)
    routes += seg(p_u5_3['x'], 108.0, p_u5_3['x'], p_u5_3['y'], "F.Cu", "+5V", 0.40)
    routes += seg(p_d1_1['x'], 108.0, p_cbo2['x'], 108.0, "F.Cu", "+5V", 0.40)
    routes += seg(p_cbo2['x'], 108.0, p_cbo2['x'], p_cbo2['y'], "F.Cu", "+5V", 0.40)
    routes += seg(p_cbo2['x'], 108.0, p_cbo1['x'], 108.0, "F.Cu", "+5V", 0.40)
    routes += seg(p_cbo1['x'], 108.0, p_cbo1['x'], p_cbo1['y'], "F.Cu", "+5V", 0.40)
    routes += seg(p_cbo1['x'], 108.0, 79.7125, 108.0, "F.Cu", "+5V", 0.40)
    routes += seg(79.7125, 108.0, 79.7125, 114.5, "F.Cu", "+5V", 0.40)
    # B.Cu +5V feed at Y=108.5 (orthogonal routing to avoid C_FF.2)
    routes += seg(91.775, 108.0, 91.775, 108.5, "F.Cu", "+5V", 0.40)
    routes += via(91.775, 108.5, "+5V")
    routes += seg(91.775, 108.5, p_cff_1['x'], 108.5, "B.Cu", "+5V", 0.25)
    routes += seg(p_cff_1['x'], 108.5, p_cff_1['x'], p_cff_1['y'], "B.Cu", "+5V", 0.25)
    # Direct +5V via for R_FB1.1 to preserve B.Cu GND zone corridor for R_FB2.2
    routes += via(p_rfb1_1['x'], 108.0, "+5V")
    routes += seg(p_rfb1_1['x'], p_rfb1_1['y'], p_rfb1_1['x'], 108.0, "B.Cu", "+5V", 0.25)
    return routes


# ============================================================
# GROUP H: Final Discrete Nets (+5V_ANA, BAT_MONITOR, VBAT_RAW, VBAT_SW, VBUS)
# ============================================================
def get_group_h_routes():
    routes = ""
    routes += """	(segment (start 81.2875 114.5000) (end 80.5000 114.5000) (width 0.25) (layer "F.Cu") (net "+5V_ANA"))
	(segment (start 80.5000 114.5000) (end 80.5000 117.5500) (width 0.25) (layer "F.Cu") (net "+5V_ANA"))
	(segment (start 81.2875 114.5000) (end 81.0000 114.5000) (width 0.25) (layer "F.Cu") (net "+5V_ANA"))
	(segment (start 81.0000 114.5000) (end 81.0000 112.5000) (width 0.25) (layer "F.Cu") (net "+5V_ANA"))
	(via (at 81.0000 112.5000) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "+5V_ANA"))
	(segment (start 81.0000 112.5000) (end 81.0000 109.7000) (width 0.25) (layer "B.Cu") (net "+5V_ANA"))
	(segment (start 81.0000 109.7000) (end 92.4000 109.7000) (width 0.25) (layer "B.Cu") (net "+5V_ANA"))
	(segment (start 92.4000 109.7000) (end 92.4000 112.5000) (width 0.25) (layer "B.Cu") (net "+5V_ANA"))
	(via (at 92.4000 112.5000) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "+5V_ANA"))
	(segment (start 92.4000 112.5000) (end 92.4000 113.0950) (width 0.2) (layer "F.Cu") (net "+5V_ANA"))
	(segment (start 92.4000 113.0950) (end 88.4750 113.0950) (width 0.2) (layer "F.Cu") (net "+5V_ANA"))
	(segment (start 90.8000 113.0950) (end 90.8000 113.7750) (width 0.2) (layer "F.Cu") (net "+5V_ANA"))
	(segment (start 92.4000 112.5000) (end 100.2000 112.5000) (width 0.2) (layer "F.Cu") (net "+5V_ANA"))
	(segment (start 100.2000 112.5000) (end 100.2000 114.0000) (width 0.2) (layer "F.Cu") (net "+5V_ANA"))
"""
    routes += """	(segment (start 91.2500 62.8300) (end 88.8000 62.8300) (width 0.15) (layer "F.Cu") (net "BAT_MONITOR"))
	(segment (start 88.8000 62.8300) (end 88.8000 62.2000) (width 0.15) (layer "F.Cu") (net "BAT_MONITOR"))
	(via (at 88.8000 62.2000) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "BAT_MONITOR"))
	(segment (start 88.8000 62.2000) (end 88.8000 56.5500) (width 0.15) (layer "B.Cu") (net "BAT_MONITOR"))
	(segment (start 88.8000 56.5500) (end 112.5000 56.5500) (width 0.15) (layer "B.Cu") (net "BAT_MONITOR"))
	(segment (start 112.5000 56.5500) (end 112.5000 54.0000) (width 0.15) (layer "B.Cu") (net "BAT_MONITOR"))
	(segment (start 112.5000 54.0000) (end 113.5000 54.0000) (width 0.15) (layer "B.Cu") (net "BAT_MONITOR"))
	(segment (start 113.5000 54.0000) (end 113.5000 56.0000) (width 0.15) (layer "B.Cu") (net "BAT_MONITOR"))
	(via (at 113.5000 56.0000) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "BAT_MONITOR"))
	(segment (start 113.5000 56.0000) (end 113.5000 64.0000) (width 0.15) (layer "F.Cu") (net "BAT_MONITOR"))
	(segment (start 113.5000 64.0000) (end 114.0000 64.0000) (width 0.15) (layer "F.Cu") (net "BAT_MONITOR"))
	(via (at 114.0000 64.0000) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "BAT_MONITOR"))
	(segment (start 114.0000 64.0000) (end 114.0000 78.0000) (width 0.15) (layer "B.Cu") (net "BAT_MONITOR"))
	(segment (start 114.0000 78.0000) (end 112.5000 78.0000) (width 0.15) (layer "B.Cu") (net "BAT_MONITOR"))
	(via (at 112.5000 78.0000) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "BAT_MONITOR"))
	(segment (start 112.5000 78.0000) (end 112.2500 78.0000) (width 0.15) (layer "F.Cu") (net "BAT_MONITOR"))
	(segment (start 112.2500 78.0000) (end 112.2500 83.0000) (width 0.15) (layer "F.Cu") (net "BAT_MONITOR"))
	(segment (start 112.2500 83.0000) (end 114.0000 83.0000) (width 0.15) (layer "F.Cu") (net "BAT_MONITOR"))
	(via (at 114.0000 83.0000) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "BAT_MONITOR"))
	(segment (start 114.0000 83.0000) (end 114.5000 83.0000) (width 0.15) (layer "B.Cu") (net "BAT_MONITOR"))
	(segment (start 114.5000 83.0000) (end 114.5000 82.0000) (width 0.15) (layer "B.Cu") (net "BAT_MONITOR"))
	(segment (start 114.5000 82.0000) (end 115.3250 82.0000) (width 0.15) (layer "B.Cu") (net "BAT_MONITOR"))
	(segment (start 115.3250 82.0000) (end 117.1750 82.0000) (width 0.2) (layer "B.Cu") (net "BAT_MONITOR"))
	(segment (start 117.1750 82.0000) (end 117.1750 83.3000) (width 0.2) (layer "B.Cu") (net "BAT_MONITOR"))
	(segment (start 117.1750 83.3000) (end 120.2750 83.3000) (width 0.2) (layer "B.Cu") (net "BAT_MONITOR"))
	(segment (start 120.2750 83.3000) (end 120.2750 84.5000) (width 0.2) (layer "B.Cu") (net "BAT_MONITOR"))
"""
    routes += """	(segment (start 117.5000 95.0000) (end 116.7500 95.0000) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(segment (start 116.7500 95.0000) (end 116.7500 96.2500) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(segment (start 116.7500 96.2500) (end 111.2500 96.2500) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(segment (start 111.2500 96.2500) (end 111.2500 100.0000) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(segment (start 111.2500 100.0000) (end 110.7500 100.0000) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(segment (start 110.7500 100.0000) (end 110.7500 100.2500) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(segment (start 110.7500 100.2500) (end 108.5000 100.2500) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(via (at 108.5000 100.2500) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBAT_RAW"))
	(segment (start 108.5000 100.2500) (end 108.5000 100.2500) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 108.5000 100.2500) (end 105.2500 100.2500) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 105.2500 100.2500) (end 105.2500 102.7500) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 105.2500 102.7500) (end 105.0000 102.7500) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 105.0000 102.7500) (end 105.0000 103.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 105.0000 103.0000) (end 99.7500 103.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 99.7500 103.0000) (end 99.7500 102.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 99.7500 102.5000) (end 99.5000 102.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 99.5000 102.5000) (end 99.5000 102.2500) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 99.5000 102.2500) (end 99.2500 102.2500) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 99.2500 102.2500) (end 99.1750 102.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 99.1750 102.0000) (end 96.9200 102.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 96.9200 102.0000) (end 96.9200 102.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(via (at 96.9200 102.5000) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBAT_RAW"))
	(segment (start 96.9200 102.5000) (end 96.9200 102.5000) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(segment (start 96.9200 102.5000) (end 93.9200 102.5000) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(via (at 93.9200 102.5000) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBAT_RAW"))
	(segment (start 93.9200 102.5000) (end 93.9200 102.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 93.9200 102.5000) (end 93.9200 102.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 93.9200 102.0000) (end 93.4200 102.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 93.4200 102.0000) (end 93.4200 101.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 93.4200 101.5000) (end 93.1700 101.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 93.1700 101.5000) (end 93.1700 101.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 93.1700 101.0000) (end 92.6700 101.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 92.6700 101.0000) (end 92.6700 100.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 92.6700 100.5000) (end 92.4750 100.4050) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 92.4750 100.4050) (end 91.9700 100.4100) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 91.9700 100.4100) (end 91.4700 100.4100) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 91.4700 100.4100) (end 91.4700 100.6600) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 91.4700 100.6600) (end 90.2200 100.6600) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 90.2200 100.6600) (end 90.2200 100.9100) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 90.2200 100.9100) (end 89.9700 100.9100) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 89.9700 100.9100) (end 89.9700 101.4100) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 89.9700 101.4100) (end 89.7200 101.4100) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 89.7200 101.4100) (end 89.7200 101.6600) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 89.7200 101.6600) (end 89.4700 101.6600) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 89.4700 101.6600) (end 89.4700 102.1600) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 89.4700 102.1600) (end 89.2200 102.1600) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 89.2200 102.1600) (end 89.2200 102.4100) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 89.2200 102.4100) (end 89.0500 102.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 89.0500 102.5000) (end 83.5500 102.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 83.5500 102.5000) (end 83.5500 102.2500) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 83.5500 102.2500) (end 83.3000 102.2500) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 83.3000 102.2500) (end 83.3000 98.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(via (at 83.3000 98.5000) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBAT_RAW"))
	(segment (start 83.3000 98.5000) (end 83.3000 98.5000) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(segment (start 83.3000 98.5000) (end 83.3000 96.0000) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(segment (start 83.3000 96.0000) (end 83.0500 96.0000) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(segment (start 83.0500 96.0000) (end 83.0500 91.5000) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(segment (start 83.0500 91.5000) (end 82.0500 91.5000) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(segment (start 82.0500 91.5000) (end 82.0500 91.2500) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(segment (start 82.0500 91.2500) (end 81.8000 91.2500) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(segment (start 81.8000 91.2500) (end 81.8000 74.5000) (width 0.25) (layer "B.Cu") (net "VBAT_RAW"))
	(via (at 81.8000 74.5000) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBAT_RAW"))
	(segment (start 81.8000 74.5000) (end 81.8000 74.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 81.8000 74.5000) (end 81.8000 73.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 81.8000 73.5000) (end 81.5500 73.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 81.5500 73.5000) (end 81.5500 73.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 81.5500 73.0000) (end 81.3000 73.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 81.3000 73.0000) (end 81.3000 72.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 81.3000 72.5000) (end 80.8000 72.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 80.8000 72.5000) (end 80.8000 72.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 80.8000 72.0000) (end 80.5500 72.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 80.5500 72.0000) (end 80.5500 71.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 80.5500 71.5000) (end 80.3000 71.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 80.3000 71.5000) (end 80.3000 71.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 80.3000 71.0000) (end 79.8000 71.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 79.8000 71.0000) (end 79.8000 70.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 79.8000 70.5000) (end 79.5500 70.5000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 79.5500 70.5000) (end 79.5500 70.0000) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
	(segment (start 79.5500 70.0000) (end 79.2500 69.9300) (width 0.25) (layer "F.Cu") (net "VBAT_RAW"))
"""
    routes += """	(segment (start 80.7500 69.9300) (end 80.7500 70.9300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 80.7500 70.9300) (end 81.0000 70.9300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 81.0000 70.9300) (end 81.0000 71.4300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 81.0000 71.4300) (end 81.2500 71.4300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 81.2500 71.4300) (end 81.2500 71.9300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 81.2500 71.9300) (end 81.7500 71.9300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 81.7500 71.9300) (end 81.7500 72.4300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 81.7500 72.4300) (end 82.0000 72.4300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 82.0000 72.4300) (end 82.0000 72.9300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 82.0000 72.9300) (end 82.2500 72.9300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 82.2500 72.9300) (end 82.2500 73.9300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 82.2500 73.9300) (end 82.5000 73.9300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 82.5000 73.9300) (end 82.5000 75.1800) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 82.5000 75.1800) (end 81.0000 75.1800) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 81.0000 75.1800) (end 81.0000 75.4300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 81.0000 75.4300) (end 80.7500 75.4300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(via (at 80.7500 75.4300) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBAT_SW"))
	(segment (start 80.7500 75.4300) (end 80.7500 75.4300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 80.7500 75.4300) (end 80.7500 86.1800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 80.7500 86.1800) (end 81.0000 86.1800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 81.0000 86.1800) (end 81.0000 97.1800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 81.0000 97.1800) (end 81.2500 97.1800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 81.2500 97.1800) (end 81.2500 97.6800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 81.2500 97.6800) (end 81.5000 97.6800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 81.5000 97.6800) (end 81.5000 99.4300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(via (at 81.5000 99.4300) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBAT_SW"))
	(segment (start 81.5000 99.4300) (end 81.5000 99.4300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 81.5000 99.4300) (end 81.5000 104.6800) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 81.5000 104.6800) (end 81.2500 104.6800) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 81.2500 104.6800) (end 81.2500 104.9300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 81.2500 104.9300) (end 81.0000 104.9300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 81.0000 104.9300) (end 81.0000 105.4300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 81.0000 105.4300) (end 80.7500 105.5000) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 80.7500 105.5000) (end 85.0000 105.5000) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 85.0000 105.5000) (end 85.0000 104.0000) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 85.0000 104.0000) (end 87.5000 104.0000) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 87.5000 104.0000) (end 87.5000 105.0000) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 87.5000 105.0000) (end 87.7500 105.0000) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 87.7500 105.0000) (end 87.7500 105.2500) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 87.7500 105.2500) (end 88.2500 105.2500) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 88.2500 105.2500) (end 88.3625 105.5000) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 88.3625 105.5000) (end 88.3600 105.0000) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 88.3600 105.0000) (end 88.3600 104.7500) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 88.3600 104.7500) (end 88.3625 104.5500) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 80.7500 105.5000) (end 80.7500 107.2500) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(via (at 80.7500 107.2500) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBAT_SW"))
	(segment (start 80.7500 107.2500) (end 80.7500 107.2500) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 80.7500 107.2500) (end 80.7500 108.7500) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 80.7500 108.7500) (end 81.0000 108.7500) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 81.0000 108.7500) (end 81.0000 109.0000) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 81.0000 109.0000) (end 82.0000 109.0000) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(via (at 82.0000 109.0000) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBAT_SW"))
	(segment (start 82.0000 109.0000) (end 82.0000 109.0000) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 82.0000 109.0000) (end 82.0000 109.7500) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 82.0000 109.7500) (end 82.5000 109.7500) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 82.5000 109.7500) (end 82.5500 110.0000) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 80.7500 69.9300) (end 83.0000 69.9300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 83.0000 69.9300) (end 83.0000 70.9300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 83.0000 70.9300) (end 83.2500 70.9300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 83.2500 70.9300) (end 83.2500 71.1800) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 83.2500 71.1800) (end 87.2500 71.1800) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(segment (start 87.2500 71.1800) (end 87.2500 74.4300) (width 0.25) (layer "F.Cu") (net "VBAT_SW"))
	(via (at 87.2500 74.4300) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBAT_SW"))
	(segment (start 87.2500 74.4300) (end 87.2500 74.4300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 87.2500 74.4300) (end 95.7500 74.4300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 95.7500 74.4300) (end 95.7500 81.6800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 95.7500 81.6800) (end 96.0000 81.6800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 96.0000 81.6800) (end 96.0000 81.9300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 96.0000 81.9300) (end 98.7500 81.9300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 98.7500 81.9300) (end 98.7500 84.9300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 98.7500 84.9300) (end 99.0000 84.9300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 99.0000 84.9300) (end 99.0000 85.1800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 99.0000 85.1800) (end 109.2500 85.1800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 109.2500 85.1800) (end 109.2500 84.9300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 109.2500 84.9300) (end 109.5000 84.9300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 109.5000 84.9300) (end 109.5000 84.6800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 109.5000 84.6800) (end 110.0000 84.6800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 110.0000 84.6800) (end 110.0000 84.4300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 110.0000 84.4300) (end 110.2500 84.4300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 110.2500 84.4300) (end 110.2500 84.1800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 110.2500 84.1800) (end 110.7500 84.1800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 110.7500 84.1800) (end 110.7500 83.9300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 110.7500 83.9300) (end 111.0000 83.9300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 111.0000 83.9300) (end 111.0000 83.6800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 111.0000 83.6800) (end 111.5000 83.6800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 111.5000 83.6800) (end 111.5000 83.4300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 111.5000 83.4300) (end 111.7500 83.4300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 111.7500 83.4300) (end 111.7500 83.1800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 111.7500 83.1800) (end 112.2500 83.1800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 112.2500 83.1800) (end 112.2500 82.9300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 112.2500 82.9300) (end 112.5000 82.9300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 112.5000 82.9300) (end 112.5000 82.6800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 112.5000 82.6800) (end 113.0000 82.6800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 113.0000 82.6800) (end 113.0000 82.4300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 113.0000 82.4300) (end 113.2500 82.4300) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 113.2500 82.4300) (end 113.2500 82.1800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 113.2500 82.1800) (end 113.5000 82.1800) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
	(segment (start 113.5000 82.1800) (end 113.6750 82.0000) (width 0.25) (layer "B.Cu") (net "VBAT_SW"))
"""
    routes += """	(segment (start 80.5450 89.0500) (end 80.5500 89.3000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 80.5500 89.3000) (end 79.3000 89.3000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 79.3000 89.3000) (end 79.3000 93.5500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 79.3000 93.5500) (end 79.5500 93.5500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 79.5500 93.5500) (end 79.5500 93.8000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 79.5500 93.8000) (end 80.3000 93.8000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 80.3000 93.8000) (end 80.5450 93.9500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 80.5450 89.0500) (end 79.8000 89.0500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 79.8000 89.0500) (end 79.8000 89.3000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 79.8000 89.3000) (end 79.3000 89.3000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 79.3000 89.3000) (end 79.3000 93.5500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 79.3000 93.5500) (end 79.5500 93.5500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 79.5500 93.5500) (end 79.5500 93.8000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 79.5500 93.8000) (end 81.8000 93.8000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 81.8000 93.8000) (end 81.8000 96.8000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 81.8000 96.8000) (end 84.5500 96.8000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 84.5500 96.8000) (end 84.5500 93.3000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 84.5500 93.3000) (end 85.3000 93.3000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 85.3000 93.3000) (end 85.3000 93.0500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 85.3000 93.0500) (end 85.5500 93.0500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 85.5500 93.0500) (end 85.5500 92.5500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 85.5500 92.5500) (end 85.8000 92.5500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 85.8000 92.5500) (end 85.8000 92.0500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 85.8000 92.0500) (end 86.0500 92.0500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.0500 92.0500) (end 86.0500 91.8000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.0500 91.8000) (end 86.3000 91.8000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.3000 91.8000) (end 86.3000 91.5500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.3000 91.5500) (end 86.5500 91.5000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.5500 91.5000) (end 86.5500 96.0000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.5500 96.0000) (end 86.0500 96.0000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.0500 96.0000) (end 86.0500 97.0000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(via (at 86.0500 97.0000) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBUS"))
	(segment (start 86.0500 97.0000) (end 86.0500 97.0000) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 86.0500 97.0000) (end 84.8000 97.0000) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 84.8000 97.0000) (end 84.8000 99.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(via (at 84.8000 99.2500) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBUS"))
	(segment (start 84.8000 99.2500) (end 84.8000 99.2500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 84.8000 99.2500) (end 84.8000 101.5000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 84.8000 101.5000) (end 85.0500 101.5000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 85.0500 101.5000) (end 85.0500 101.7500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 85.0500 101.7500) (end 86.0500 101.7500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.0500 101.7500) (end 86.0500 101.2500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.0500 101.2500) (end 86.5500 101.2500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.5500 101.2500) (end 86.5500 101.0000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.5500 101.0000) (end 86.8000 101.0000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.8000 101.0000) (end 86.8000 100.7500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.8000 100.7500) (end 87.3000 100.7500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 87.3000 100.7500) (end 87.3000 100.5000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 87.3000 100.5000) (end 87.5250 100.4050) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 87.5250 100.4050) (end 87.0300 100.4100) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 87.0300 100.4100) (end 86.2800 100.4100) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.2800 100.4100) (end 86.2800 101.4100) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.2800 101.4100) (end 86.0300 101.4100) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.0300 101.4100) (end 86.0300 101.6600) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.0300 101.6600) (end 84.8000 101.6600) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 84.8000 101.6600) (end 84.8000 99.2500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 84.8000 99.2500) (end 84.8000 98.4100) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 84.7800 98.4100) (end 85.0300 98.4100) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 85.0300 98.4100) (end 85.0300 98.1600) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 85.0300 98.1600) (end 90.2800 98.1600) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 90.2800 98.1600) (end 90.2800 97.9100) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 90.2800 97.9100) (end 90.7800 97.9100) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 90.7800 97.9100) (end 90.7800 97.6600) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 90.7800 97.6600) (end 91.0300 97.6600) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 91.0300 97.6600) (end 91.0300 97.4100) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 91.0300 97.4100) (end 91.5300 97.4100) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 91.5300 97.4100) (end 91.5300 97.1600) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 91.5300 97.1600) (end 91.7800 97.1600) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 91.7800 97.1600) (end 91.7800 96.9100) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(via (at 91.7800 96.9100) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBUS"))
	(segment (start 91.7800 96.9100) (end 91.7800 96.9100) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 91.7800 96.9100) (end 92.2800 96.9100) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 92.2800 96.9100) (end 92.2800 96.6600) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 92.2800 96.6600) (end 92.4750 96.5950) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.5500 91.5000) (end 86.5500 94.2500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 86.5500 94.2500) (end 93.0500 94.2500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(via (at 93.0500 94.2500) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBUS"))
	(segment (start 93.0500 94.2500) (end 93.0500 94.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 93.0500 94.2500) (end 93.0500 89.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 93.0500 89.2500) (end 92.5500 89.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 92.5500 89.2500) (end 92.5500 88.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 92.5500 88.7500) (end 92.3000 88.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 92.3000 88.7500) (end 92.3000 88.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 92.3000 88.2500) (end 92.0500 88.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 92.0500 88.2500) (end 92.0500 87.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 92.0500 87.7500) (end 91.5500 87.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 91.5500 87.7500) (end 91.5500 87.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 91.5500 87.2500) (end 91.3000 87.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 91.3000 87.2500) (end 91.3000 86.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 91.3000 86.7500) (end 91.0500 86.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 91.0500 86.7500) (end 91.0500 86.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 91.0500 86.2500) (end 90.5500 86.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 90.5500 86.2500) (end 90.5500 85.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 90.5500 85.7500) (end 90.3000 85.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 90.3000 85.7500) (end 90.3000 85.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 90.3000 85.2500) (end 90.0500 85.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 90.0500 85.2500) (end 90.0500 84.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 90.0500 84.7500) (end 89.5500 84.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 89.5500 84.7500) (end 89.5500 84.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 89.5500 84.2500) (end 89.3000 84.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 89.3000 84.2500) (end 89.3000 83.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 89.3000 83.7500) (end 89.0500 83.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 89.0500 83.7500) (end 89.0500 83.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 89.0500 83.2500) (end 88.5500 83.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 88.5500 83.2500) (end 88.5500 82.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 88.5500 82.7500) (end 88.3000 82.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(via (at 88.3000 82.7500) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBUS"))
	(segment (start 88.3000 82.7500) (end 88.3000 82.7500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 88.3000 82.7500) (end 88.1750 82.5000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 88.1750 82.5000) (end 88.9200 82.5000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 88.9200 82.5000) (end 88.9200 83.2500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 88.9200 83.2500) (end 91.1700 83.2500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 91.1700 83.2500) (end 91.1700 83.0000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 91.1700 83.0000) (end 91.6700 83.0000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 91.6700 83.0000) (end 91.6700 82.7500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 91.6700 82.7500) (end 92.1700 82.7500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 92.1700 82.7500) (end 92.1750 82.5000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 92.1750 82.5000) (end 92.1700 83.0000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 92.1700 83.0000) (end 92.1700 87.7500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 92.1700 87.7500) (end 92.4200 87.7500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 92.4200 87.7500) (end 92.4200 88.0000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 92.4200 88.0000) (end 92.6700 88.0000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 92.6700 88.0000) (end 92.6700 88.2500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 92.6700 88.2500) (end 93.1700 88.2500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 93.1700 88.2500) (end 93.2250 88.5000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 93.2250 88.5000) (end 93.2200 88.7500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 93.2200 88.7500) (end 93.2200 90.0000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 93.2200 90.0000) (end 94.9700 90.0000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 94.9700 90.0000) (end 94.9700 90.2500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 94.9700 90.2500) (end 95.4700 90.2500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(via (at 95.4700 90.2500) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBUS"))
	(segment (start 95.4700 90.2500) (end 95.4700 90.2500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 95.4700 90.2500) (end 95.4700 91.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 95.4700 91.7500) (end 95.7200 91.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 95.7200 91.7500) (end 95.7200 92.0000) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 95.7200 92.0000) (end 95.9700 92.0000) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 95.9700 92.0000) (end 95.9700 92.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(segment (start 95.9700 92.7500) (end 96.4700 92.7500) (width 0.25) (layer "B.Cu") (net "VBUS"))
	(via (at 96.4700 92.7500) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VBUS"))
	(segment (start 96.4700 92.7500) (end 96.4700 92.7500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 96.4700 92.7500) (end 96.5500 92.5000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 96.5500 92.5000) (end 96.5500 93.0000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 96.5500 93.0000) (end 97.0500 93.0000) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 97.0500 93.0000) (end 97.0500 93.2500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 97.0500 93.2500) (end 97.3000 93.2500) (width 0.25) (layer "F.Cu") (net "VBUS"))
	(segment (start 97.3000 93.2500) (end 97.5000 93.4500) (width 0.25) (layer "F.Cu") (net "VBUS"))
"""
    return routes


def get_all_routes():
    return (
        get_fanout_routes() +
        get_group_a_routes() +
        get_group_b_routes() +
        get_group_c_routes() +
        get_group_d_routes() +
        get_group_e_routes() +
        get_group_f_routes() +
        get_group_g_routes() +
        get_group_h_routes()
    )
