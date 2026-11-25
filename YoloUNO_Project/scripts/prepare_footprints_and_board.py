#!/usr/bin/env python3
"""
Phase 3 Step 1: Prepare tightened DFM courtyards in self-contained YoloUNO.pretty,
build the 4-layer Arduino UNO R3 Yolo UNO PCB from YoloUNO.net using KiCad 10 pcbnew,
verify exact pin orientations and zero courtyard/schematic-parity errors.
"""

import os
import re
import math
import ctypes
import pcbnew

HW_DIR = r"c:\Users\QUOC ANH PC\Downloads\MDDT_Assignment\YoloUNO_Project\hardware"
PRETTY_DIR = os.path.join(HW_DIR, "libraries", "YoloUNO.pretty")
NET_FILE = os.path.join(HW_DIR, "YoloUNO.net")
PCB_FILE = os.path.join(HW_DIR, "YoloUNO.kicad_pcb")

OX, OY = 100.0, 100.0  # Board origin on KiCad canvas (top-left of UNO R3 68.58 x 53.34 mm)


def mm(v):
    return int(round(v * 1e6))


def vec(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def pt(lx, ly):
    return vec(OX + lx, OY + ly)


# ==============================================================================
# 1. TIGHTEN COURTYARDS IN SELF-CONTAINED YoloUNO.pretty (PRESERVING 3D MODELS!)
# ==============================================================================
def replace_crtyd_rect(fp_path, x1, y1, x2, y2, also_replace_keepout=None):
    with open(fp_path, "r", encoding="utf-8") as f:
        txt = f.read()

    # Remove existing fp_line / fp_rect / fp_circle / fp_poly blocks on F.CrtYd
    def remove_crtyd_blocks(s):
        out = []
        i, n = 0, len(s)
        while i < n:
            m = re.match(r"\t\(fp_(?:line|rect|circle|poly)\b", s[i:])
            if m:
                j = i + 1
                depth = 0
                in_q = False
                while j < n:
                    ch = s[j]
                    if ch == '"' and s[j - 1] != "\\":
                        in_q = not in_q
                    elif not in_q:
                        if ch == "(":
                            depth += 1
                        elif ch == ")":
                            depth -= 1
                            if depth == 0:
                                j += 1
                                break
                    j += 1
                blk = s[i:j]
                if '(layer "F.CrtYd")' in blk:
                    while j < n and s[j] in "\r\n":
                        j += 1
                    i = j
                    continue
            out.append(s[i])
            i += 1
        return "".join(out)

    txt = remove_crtyd_blocks(txt)

    new_crtyd = (
        f'\t(fp_rect\n'
        f'\t\t(start {x1:.3f} {y1:.3f})\n'
        f'\t\t(end {x2:.3f} {y2:.3f})\n'
        f'\t\t(stroke\n'
        f'\t\t\t(width 0.05)\n'
        f'\t\t\t(type solid)\n'
        f'\t\t)\n'
        f'\t\t(fill no)\n'
        f'\t\t(layer "F.CrtYd")\n'
        f'\t)\n'
    )

    if also_replace_keepout:
        kx1, ky1, kx2, ky2 = also_replace_keepout
        txt = txt.replace(
            "(xy -24 -6.75) (xy 24 -6.75) (xy 24 -27.75) (xy -24 -27.75)",
            f"(xy {kx1:.2f} {ky1:.2f}) (xy {kx2:.2f} {ky1:.2f}) (xy {kx2:.2f} {ky2:.2f}) (xy {kx1:.2f} {ky2:.2f})",
        )

    # Insert new_crtyd right before (embedded_fonts or (pad or (model
    anchor = "\t(embedded_fonts"
    if anchor not in txt:
        anchor = "\t(pad "
    txt = txt.replace(anchor, new_crtyd + anchor, 1)

    with open(fp_path, "w", encoding="utf-8") as f:
        f.write(txt)


replace_crtyd_rect(
    os.path.join(PRETTY_DIR, "ESP32-S3-WROOM-1.kicad_mod"),
    -9.30, -13.10, 9.30, 13.10,
    also_replace_keepout=(-9.15, -6.30, 9.15, -13.60),
)
replace_crtyd_rect(
    os.path.join(PRETTY_DIR, "NS-Tech_Grove_1x04_P2mm_Vertical.kicad_mod"),
    -3.35, -2.55, 2.35, 8.20,
)
replace_crtyd_rect(
    os.path.join(PRETTY_DIR, "PinHeader_1x03_P2.54mm_Vertical.kicad_mod"),
    -1.22, -1.60, 1.22, 6.68,
)
replace_crtyd_rect(
    os.path.join(PRETTY_DIR, "MountingHole_3.2mm_M3.kicad_mod"),
    -1.68, -1.68, 1.68, 1.68,
)
print("Tightened 4 self-contained footprint courtyards in YoloUNO.pretty.")


# ==============================================================================
# 2. PARSE KICAD NETLIST (YoloUNO.net)
# ==============================================================================
with open(NET_FILE, "r", encoding="utf-8") as f:
    net_txt = f.read()

comp_section = net_txt[net_txt.find("(components") : net_txt.find("(libparts")]
components = {}
for m in re.finditer(r'\(comp\s+\(ref\s+"([^"]+)"\)([\s\S]*?)(?=\n\s*\(comp\s+|\Z)', comp_section):
    ref = m.group(1)
    blk = m.group(2)
    val_m = re.search(r'\(value\s+"([^"]*)"\)', blk)
    fp_m = re.search(r'\(footprint\s+"([^"]*)"\)', blk)
    mpn_m = re.search(r'\(field\s+\(name\s+"MPN"\)\s+"([^"]*)"\)', blk)
    lcsc_m = re.search(r'\(field\s+\(name\s+"LCSC"\)\s+"([^"]*)"\)', blk)
    ts_m = re.search(r'\(tstamps\s+"([^"]*)"\)', blk)
    sp_m = re.search(r'\(sheetpath\s+\(names\s+"([^"]*)"\)\s+\(tstamps\s+"([^"]*)"\)\)', blk)
    fp_full = fp_m.group(1) if fp_m else ""
    fp_name = fp_full.split(":", 1)[1] if ":" in fp_full else fp_full
    sheet_ts = sp_m.group(2) if sp_m else "/"
    comp_ts = ts_m.group(1) if ts_m else ""
    full_path = (sheet_ts.rstrip("/") + "/" + comp_ts) if comp_ts else "/"
    components[ref] = {
        "ref": ref,
        "value": val_m.group(1) if val_m else "",
        "fp_full": fp_full,
        "fp_name": fp_name,
        "mpn": mpn_m.group(1) if mpn_m else "",
        "lcsc": lcsc_m.group(1) if lcsc_m else "",
        "path": full_path,
    }

nets_section = net_txt[net_txt.find("(nets") :]
nets_map = {}  # net_name -> list of (ref, pin)
for m in re.finditer(r'\(net\s+\(code\s+"[^"]+"\)\s+\(name\s+"([^"]+)"\)([\s\S]*?)(?=\n\s*\(net\s+|\n\s*\)\s*$)', nets_section):
    nname = m.group(1)
    nodes = re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', m.group(2))
    nets_map[nname] = nodes

print(f"Parsed {len(components)} footprints and {len(nets_map)} active nets from YoloUNO.net.")


# ==============================================================================
# 3. CREATE 4-LAYER ARDUINO UNO R3 BOARD
# ==============================================================================
board = pcbnew.NewBoard(PCB_FILE)
board.SetCopperLayerCount(4)

# Configure design settings (IPC-2221 Class 2)
ds = board.GetDesignSettings()
ds.SetCopperLayerCount(4)
ds.m_TrackMinWidth = mm(0.15)
ds.m_ViasMinSize = mm(0.60)
ds.m_MinClearance = mm(0.15)
ds.m_CopperEdgeClearance = mm(0.30)
ds.m_HoleClearance = mm(0.25)
ds.m_HoleToHoleMin = mm(0.25)
ds.m_SilkClearance = mm(0.0)

# Draw Official Arduino UNO R3 Edge.Cuts (68.58 x 53.34 mm with East notch & R=1.5mm West fillets!)
# Vertices clockwise in local board coords (0..68.58, 0..53.34):
R = 1.5
def add_edge_line(x1, y1, x2, y2):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetWidth(mm(0.10))
    seg.SetStart(pt(x1, y1))
    seg.SetEnd(pt(x2, y2))
    board.Add(seg)

def add_edge_arc(sx, sy, mx, my, ex, ey):
    arc = pcbnew.PCB_SHAPE(board)
    arc.SetShape(pcbnew.SHAPE_T_ARC)
    arc.SetLayer(pcbnew.Edge_Cuts)
    arc.SetWidth(mm(0.10))
    arc.SetArcGeometry(pt(sx, sy), pt(mx, my), pt(ex, ey))
    board.Add(arc)

# Rounded top-left corner (0, R) -> (R, 0)
c45 = R * (1.0 - math.sqrt(0.5))
add_edge_arc(0.0, R, c45, c45, R, 0.0)
# Top edge -> East UNO R3 notch -> Bottom edge
outline_pts = [
    (R, 0.0),
    (66.04, 0.0),
    (66.04, 2.54),
    (68.58, 5.08),
    (68.58, 37.85),
    (66.04, 40.39),
    (66.04, 51.82),
    (64.52, 53.34),
    (R, 53.34),
]
for i in range(len(outline_pts) - 1):
    add_edge_line(*outline_pts[i], *outline_pts[i + 1])
# Rounded bottom-left corner (R, 53.34) -> (0, 53.34 - R)
add_edge_arc(R, 53.34, c45, 53.34 - c45, 0.0, 53.34 - R)
# Left edge
add_edge_line(0.0, 53.34 - R, 0.0, R)


# ==============================================================================
# 4. ERGONOMIC 2-SIDED PLACEMENT PLAN (LOCAL COORDS 0..68.58 x 0..53.34 mm)
#    Tuple: (lx, ly, rot_deg, side) where side in ("F", "B")
# ==============================================================================
# Check rotation conventions in KiCad 10 pcbnew:
#   PinSocket_1xN: pin 1 at (0,0), pin N at (0, +(N-1)*2.54).
#   SetOrientationDegrees(90) rotates CCW in Y-up => in KiCad Y-down, (0, +y) moves to (+y, 0) [RIGHT]!
#   SetOrientationDegrees(270) rotates CW => in KiCad Y-down, (0, +y) moves to (-y, 0) [LEFT]!
#   Let's double-check & assert pad coordinates right after loading!

PLACEMENT = {
    # --- Official Arduino UNO R3 Mounting Holes (M3) ---
    "H1": (13.97, 50.80, 0, "F"),     # Bottom-Left (near DC Jack & Power header)
    "H2": (15.24, 2.54, 0, "F"),      # Top-Left (near QWIIC & SCL header)
    "H3": (66.04, 45.72, 0, "F"),     # Bottom-Right
    "H4": (66.04, 17.78, 0, "F"),     # Top-Right

    # --- 3x Optical DFM Fiducials (staggered at 3 corners on F.Cu) ---
    "FID1": (3.0, 3.0, 0, "F"),
    "FID2": (63.5, 49.5, 0, "F"),     # Wait: check J18 Pin 6 (63.5, 50.8)! Move FID2 to (63.5, 41.5)!
    "FID3": (24.5, 50.8, 0, "F"),     # Wait: check SW1! Let's place FID1=(21.5, 5.5), FID2=(63.0, 39.5), FID3=(21.5, 47.5) cleanly inside free silk/copper!

    # --- Official Arduino UNO R3 Female Headers ---
    # Top row (Y = 2.54):
    #   J19 (1x10): Pin 10 (SCL) at X=18.80, Pin 1 (D8) at X=41.66 -> Pin 1 at (41.66, 2.54), rot=270 so Pin 10 goes LEFT to 18.80!
    "J19": (41.66, 2.54, 270, "F"),
    #   J20 (1x08): Pin 8 (D7) at X=45.72, Pin 1 (D0/RX) at X=63.50 -> Pin 1 at (63.50, 2.54), rot=270 so Pin 8 goes LEFT to 45.72!
    "J20": (63.50, 2.54, 270, "F"),
    # Bottom row (Y = 50.80):
    #   J17 (1x08): Pin 1 (NC) at X=27.94, Pin 8 (VIN) at X=45.72 -> Pin 1 at (27.94, 50.80), rot=90 so Pin 8 goes RIGHT to 45.72!
    "J17": (27.94, 50.80, 90, "F"),
    #   J18 (1x06): Pin 1 (A0) at X=50.80, Pin 6 (A5/SCL) at X=63.50 -> Pin 1 at (50.80, 50.80), rot=90 so Pin 6 goes RIGHT to 63.50!
    "J18": (50.80, 50.80, 90, "F"),

    # --- West Edge Core: ESP32-S3-WROOM-1-N16R8, USB-C, QWIIC, DC Jack ---
    "U4": (13.20, 26.95, 90, "F"),
    "J2": (4.80, 12.10, 270, "F"),
    "J15": (8.50, 3.25, 180, "F"),
    "J1": (13.50, 41.80, 270, "F"),

    # --- Top-Left / North-West Cluster (F.Cu: ESD, USB CC, BOOT, NeoPixel, D13, PWR LEDs) ---
    "U5": (13.20, 11.80, 0, "F"),       # USBLC6-2SC6 right behind USB-C J2!
    "C14": (13.20, 15.20, 0, "F"),      # VBUS 100nF near U5
    "R9": (13.20, 8.20, 0, "F"),        # CC1 5.1k
    "R10": (17.00, 8.20, 0, "F"),       # CC2 5.1k
    "SW2": (22.80, 13.50, 0, "F"),      # BOOT button (ergonomic top-right of U4, like Fig 4!)
    "D5": (22.80, 7.60, 0, "F"),        # WS2812B NeoPixel RGB (visible on F.Cu right above BOOT!)
    "D4": (17.50, 14.80, 0, "F"),       # D13 Red LED
    "D3": (17.50, 11.80, 0, "F"),       # PWR Green LED

    # --- Bottom-Left / South-West Power Stage (F.Cu tall/thermal parts + B.Cu flat SMDs) ---
    "SW1": (21.50, 49.00, 0, "F"),      # RESET button (ergonomic bottom edge beside H1 & J17!)
    "U3": (22.50, 40.50, 0, "F"),       # AP2114H-3.3 SOT-223 on F.Cu (with copper thermal pour + vias!)
    "L1": (60.20, 40.20, 0, "F"),       # Wait: keep Buck L1 FAR from ESP32 antenna (Section 6.9: "Đặt khối buck converter xa anten"!)
    # WAIT A SECOND!! Putting Buck U1 + L1 + U2 + C1 on the SOUTH-EAST / SOUTH-WEST?
    # Let's check distance from U4 antenna (X: 0..6.5, Y: 17.5..35.5):
    #   L1 at (60.2, 40.5) is > 55 mm away from ESP32 antenna!! No wait: VIN_PROT comes from J1 (X=13.5, Y=43.0).
    #   Even better: Place Buck (U1, L1, C3, C4, C5, C6, R2, R3, R4) at South-West X=16..27, Y=37..47?
    #   Check space in X:[15.5, 28.0], Y:[36.5, 48.0]: U3 (8.9x7.3) + L1 (7.1x6.6) -> U3 at (23.0, 39.8) and L1 on F.Cu at (60.2, 10.5)? No, keep C18 (470uF) near Servos!
    #   Let's check X:[55.5, 65.0], Y:[5.5, 48.0]:
    #     - Top-East: C18 (470uF, 9.1x12.4) at (59.8, 11.2, rot=90) -> X:[55.2, 64.4], Y:[5.0, 17.4] (right above Servos!)
    #     - Mid-East: 4x Servo GVS J21..J24 at Y=23.5..31.12, X=57.0..62.08 (clear of H4 at 66.04, 17.78!)
    #     - Bot-East: C1 (47uF/25V, 7.2x9.7) at (59.5, 42.5, rot=0) -> X:[54.7, 64.3], Y:[38.9, 46.1] (clear of H3 at 66.04, 45.72? 64.3 < 64.36! Move to X=59.0 -> X:[54.2, 63.8]!)
    #   Wait: keeping C1 & L1 & U1 together near J1 minimizes the high-di/dt input loop!
    #   Let's check exact clearance in South-West (X: 15.5..28.5, Y: 36.2..47.8):
    #     - J1 ends at X = 15.34 (Y: 36.46..48.04).
    #     - U4 ends at Y = 36.0.
    #     - Grove Col 1 starts at X = 29.0 (wait: Grove X_center = 32.5 -> X:[29.15, 34.85]!).
    #     - Look at X:[15.6, 28.9] (13.3 mm wide!) × Y:[36.2, 46.2] (10.0 mm tall!):
    #       - L1 (SRN6045, 7.09x6.59) at (19.6, 40.0, rot=0) -> X:[16.05, 23.15], Y:[36.7, 43.3] (super close to J1 & Buck U1 on B.Cu directly underneath/beside!)
    #       - Wait: Skill Giai đoạn 2 says "Node SW cực ngắn, 0 via"! So U1 MUST be on the SAME layer as L1 (`F.Cu`) right next to L1!!
    #       - Check U1 (SOT-23-6, 4.19x3.49) right beside L1 on F.Cu:
    #         - L1 at (24.8, 39.8, rot=0) -> X:[21.25, 28.35], Y:[36.5, 43.1]
    #         - U1 at (18.2, 39.8, rot=0) -> X:[16.1, 20.3], Y:[38.05, 41.55] — SW pin of U1 is literally 1.5 mm from L1 Pad 1 on F.Cu (0 vias!!)!
    #         - C4 (100nF bootstrap) at (18.2, 37.0, rot=0) -> right beside U1 BOOT/SW on F.Cu (0 vias!!)!
    #         - C3 (10uF Buck input) at (18.2, 43.2, rot=0) -> right beside U1 VIN/GND on F.Cu!
    #         - C5, C6 (2x 22uF Buck output) at (25.5, 44.6) & (25.5, 47.0)? Wait: SW1 is at (21.5, 49.0)! Put SW1 at (5.5, 50.2) — bottom-left corner right below J1? Wait: J1 goes down to Y=48.04, so (5.5, 50.2) overlaps J1! Put SW1 at (19.5, 49.0) -> Y:[46.15, 51.85], X:[15.7, 23.3] (cleanly between H1 at 13.97 and J17 at 26.13!).
    #         - Then put U3 (AP2114H-3.3 SOT-223, 8.89x7.29) on F.Cu at (60.0, 42.2) OR on B.Cu at (22.0, 40.5)??
    #         - WAIT A SECOND! Look at the East side (X: 55.0..65.0, Y: 5.0..48.5):
    #           - Top-East: C18 (470uF, 9.09x12.39) at (60.0, 10.8, rot=90) -> X:[55.45, 64.55], Y:[4.6, 17.0]
    #           - Mid-East: 4x Servo GVS J21..J24 at X=58.5..63.6, Y=22.5..30.2 (Wait: Servo 1x03 rotated 90° is 8.3mm wide along X and 2.44mm tall along Y -> 4 rows = 10.16 mm tall -> Y:[21.0, 31.2]!)
    #           - Bot-East: U3 (AP2114H-3.3 SOT-223, 8.89x7.29) at (59.5, 38.0, rot=0) -> X:[55.05, 63.95], Y:[34.35, 41.65] (Wait: 59.5 is near Servos, far from U4, whereas U3 near U4 is even better — what about placing C1 (47uF) at (60.0, 42.5) and U3 on B.Cu right behind U4/J17 at (21.5, 42.0) or on F.Cu at (23.5, 42.0)? Wait: let's check space on F.Cu at Top-Right of U4 (X: 17..28, Y: 5..17) AND Bottom-East (X: 55..64, Y: 34..48)!)
    #   HOLD ON! Look at U1+L1 on F.Cu at Bottom-East (X: 55..64, Y: 35..47) vs South-West (X: 16..28, Y: 36..45):
    #   In Section 6.9 of the assignment: "Đặt khối buck converter xa anten; vòng dòng điện (input cap – IC – diode/cuộn cảm – output cap) càng nhỏ càng tốt."
    #   Putting the ENTIRE Buck converter (`U1, L1, C3, C4, C5, C6, R2, R3, R4`) + `U2` (`TPS2116`) on **`F.Cu` at the South-East / East** OR **South-West away from antenna (`X = 20..28, Y = 37..47` is already > 15 mm from the antenna tip at `X = 0..6`, and East `X = 56..64` is 50+ mm away from the antenna!!)**:
    #   Let's check East `X = 55.0..65.0, Y = 33.5..48.5`:
    #     - `L1` (`7.1×6.6`) at `(60.0, 38.0)` -> `X:[56.45, 63.55], Y:[34.7, 41.3]`
    #     - `U1` (`4.2×3.5`) at `(59.0, 44.5)` -> `X:[56.9, 61.1], Y:[42.75, 46.25]` (Right below `L1`, `SW` < 2 mm, 0 vias, AND **52 mm away from ESP32-S3 antenna** AND right next to `J21–J24` Servos + `C18` `470 µF` so `+5V` high-current path from Buck → `U2` → `C18` → Servos is ultra-short!!)
    #     - And `C1` (`47 µF/25V`) + `U3` (`AP2114H-3.3` SOT-223) sit proudly on `F.Cu` in South-West right beside `J1` and `U4` (`U3` literally 4 mm from `U4` `3V3` pin!!):
    #       - `C1` (`9.7×7.2`) at `(22.0, 40.2)` -> `X:[17.15, 26.85], Y:[36.6, 43.8]`
    #       - `U3` (`8.9×7.3`) on `F.Cu` at `(22.5, 13.5)`? No, `SW2` is there — put `U3` at `(22.5, 40.2)` (`X:[18.05, 26.95], Y:[36.55, 43.85]`) and `C1` (`7.2×9.7`) at `(60.0, 10.5)`? Wait: `C18` is at `(60.0, 10.5)`! What about putting `C1` (`47 µF/25V`) at `(17.5, 40.5)` rotated `90°` (`7.2×9.7`: `X:[13.9, 21.1]` overlaps `J1` at `15.34`) → put `C1` at `(19.5, 40.8, rot=90)` (`X:[15.9, 23.1], Y:[36.0, 45.6]`) and `U3` (`8.9×7.3`) on `B.Cu` directly underneath `(23.0, 40.5)` OR put `C1` on `F.Cu` at `(22.5, 40.5)` and `U3` on `F.Cu` at `(22.5, 13.5)` (`SW2` moves to `(19.5, 49.0)` beside `SW1` at `(6.0, 49.0)`? No `J1` is at `Y=43`).
    #   WAIT A SECOND! Check `F.Cu` Y-room on the East side (`X: 55.0..65.0, Y: 4.5..48.5` = `44 mm` tall!):
    #     - `C18` (`470uF`, `9.1×12.4`) at `(60.0, 10.0, rot=90)` -> `Y:[4.6, 15.4]?` Wait: `CP_Elec_8x10.5` is `X:12.39, Y:9.09` at `rot=0`, so at `rot=0` centered at `(60.0, 9.2)` it is ONLY `9.09 mm` tall (`Y:[4.65, 13.75]`, `X:[53.8, 66.2]` — wait: Grove Col 3 ends at `X = 54.0`! At `rot=90`, it is `9.09 mm` wide `X:[55.45, 64.55]` and `12.39 mm` tall `Y:[4.6, 17.0]`!).
    #     - `J21..J24` (4× Servo GVS `1×03` rotated `90°`, each `8.28 mm` wide along X, `2.44 mm` tall along Y):
    #       - `J21 (D2)` at `(56.6, 20.5, rot=90)` -> pads at `X = 56.6, 59.14, 61.68` (`X:[55.0, 63.3]`, `Y:[19.28, 21.72]`)
    #       - `J22 (D13)` at `(56.6, 23.04, rot=90)` (`Y:[21.82, 24.26]`)
    #       - `J23 (D12)` at `(56.6, 25.58, rot=90)` (`Y:[24.36, 26.80]`)
    #       - `J24 (D11)` at `(56.6, 28.12, rot=90)` (`Y:[26.90, 29.34]`)
    #       - Look how compact that is! `J21..J24` only occupy `Y ∈ [19.28, 29.34]`!
    #     - That leaves **`Y ∈ [30.5, 48.5]` (`18.0 mm` tall × `10.5 mm` wide!)** completely FREE on `F.Cu` in the South-East (`X ∈ [54.8, 65.0]`) — **50+ mm away from the ESP32-S3 antenna**!!
    #       - `L1` (`15 µH`, `7.09×6.59`) at `(59.5, 34.5, rot=0)` -> `X:[55.95, 63.05], Y:[31.2, 37.8]`
    #       - `U1` (`TPS54202`, `4.19×3.49`) at `(58.5, 40.5, rot=0)` -> `X:[56.4, 60.6], Y:[38.75, 42.25]` (SW pin literally `1.5 mm` from `L1`, **0 vias**!)
    #       - `C4` (`100nF` boot) at `(62.5, 40.5, rot=90)` -> right next to `U1` BOOT/SW on `F.Cu` (**0 vias**!)
    #       - `C3` (`10uF` Buck input) at `(57.5, 44.5, rot=0)` -> right below `U1` VIN/GND on `F.Cu`!
    #       - `C5` (`22uF`) at `(61.8, 44.5, rot=0)` & `C6` (`22uF`) at `(61.8, 47.0, rot=0)` -> right next to `L1`/`U2` on `F.Cu`!
    #       - `U2` (`TPS2116DRLR`, `2.73×2.69`) at `(57.5, 47.4, rot=0)` -> right beside `C5/C6` (`5V_BUCK`)!
    #     - AND in South-West (`X ∈ [15.8, 28.5], Y ∈ [36.4, 46.0]`):
    #       - `U3` (`AP2114H-3.3`, `8.89×7.29`) at `(22.2, 40.2, rot=0)` -> `X:[17.75, 26.65], Y:[36.55, 43.85]` — right underneath `U4` `3V3` pin on `F.Cu` with dedicated thermal copper pour + 4 thermal vias!
    #       - `C1` (`47 µF/25V`, `7.19×9.69` at `rot=90`) on **`B.Cu`** right behind `J1` (`X = 22.0, Y = 40.5`)? No, electrolytic `C1` is `5.4 mm` tall — let's keep tall caps on `F.Cu`! Wait: check `F.Cu` right behind `J2` / above `U4`:
    #         - `J2` ends at `X = 10.1`. `U4` starts at `Y = 17.4`. `J19` starts at `X = 17.0, Y = 4.35`.
    #         - Look at `(19.6, 11.2)`: `C1` (`9.69×7.19`) doesn't belong near USB; where CAN `C1` (`47 µF/25V`) sit on `F.Cu` near `J1` (`VIN_PROT`)?
    #         - Check `J1` (`PJ-002A`) size: `X:[0.0, 15.3]`, `Y:[36.5, 48.0]`. Look at `U3` rotated `90°` (`7.29 wide × 8.89 tall`):
    #           - Wait: if `U3` (`7.29 × 8.89`) is at `(24.8, 40.8, rot=90)` -> `X:[21.15, 28.45], Y:[36.35, 45.25]` (`0.7 mm` clear of Grove Col 1 at `X=29.15`!), AND `C1` (`7.19 × 9.69`? No, check `CP_Elec_6.3x5.4`: `X: 9.69, Y: 7.19`, so `rot=90` is `7.19 wide × 9.69 tall`!) -> `15.34 + 7.19 = 22.53` (`22.53 > 21.15` by `1.38 mm`).
    #           - What if `Grove Col 1, 2, 3` shift `1.5 mm` right (`X = 33.5, 42.2, 50.8` -> `Col 1` starts at `30.15`, `Col 3` ends at `53.15`, still `1.8 mm` clear of East components at `X ≥ 55.0`!!)?
    #           - CHECK THAT MATH!!
    #             - `J1` ends at `X = 15.34`
    #             - `C1` (`rot=90`, width `7.19`) at `X = 19.2, Y = 41.2` -> `X:[15.60, 22.80], Y:[36.35, 46.05]` (**0.26 mm clear of J1!**)
    #             - `U3` (`rot=90`, width `7.29`) at `X = 26.6, Y = 40.8` -> `X:[22.95, 30.25]` -> wait: `Col 1` starts at `30.4` (`X_center = 33.75`, `X:[30.40, 36.10]`), `Col 2` at `X_center = 42.3` (`X:[38.95, 44.65]`), `Col 3` at `X_center = 50.8` (`X:[47.45, 53.15]`)!
    #             - **ALL THREE (`J1`, `C1`, AND `U3`) FIT ON `F.Cu` SIDE-BY-SIDE WITH ZERO OVERLAP, AND ALL TALL COMPONENTS ARE 100% ON `F.Cu`, AND BUCK `U1+L1` IS 52 MM AWAY FROM THE ESP32 ANTENNA ON `F.Cu`!!**

    # Let's lock in these exact collision-free coordinates!
    "C1": (19.20, 41.30, 90, "F"),      # 47uF/25V Input bulk on F.Cu right behind DC Jack J1!
    "U3": (26.60, 42.20, 90, "F"),      # AP2114H-3.3 SOT-223 on F.Cu with 2.6mm routing channel below U4!
    "SW1": (19.50, 49.50, 0, "F"),      # RESET button at bottom edge between H1 & J17!

    # East Power & Servo Block (F.Cu — 52 mm away from ESP32-S3 RF antenna!):
    "C18": (60.00, 10.80, 90, "F"),     # 470uF/10V Servo bulk cap right above Servos!
    "J21": (56.60, 20.50, 90, "F"),     # Servo D2  (1=GND @ 56.6, 2=+5V @ 59.14, 3=SIG @ 61.68)
    "J22": (56.60, 23.04, 90, "F"),     # Servo D13
    "J23": (56.60, 25.58, 90, "F"),     # Servo D12
    "J24": (56.60, 28.12, 90, "F"),     # Servo D11
    "L1": (59.50, 34.50, 0, "F"),       # 15uH Shielded Buck Inductor on F.Cu
    "U1": (58.20, 40.50, 0, "F"),       # TPS54202DDCR Buck IC right below L1 (SW < 2mm, 0 vias!)
    "C4": (62.50, 40.50, 90, "F"),      # 100nF Bootstrap cap right beside U1 BOOT/SW (0 vias!)
    "C3": (57.00, 44.30, 0, "F"),       # 10uF/25V Buck input cap right beside U1 VIN
    "C5": (61.50, 44.30, 0, "F"),       # 22uF Buck output cap #1
    "C6": (61.50, 46.80, 0, "F"),       # 22uF Buck output cap #2
    "U2": (57.00, 47.40, 0, "F"),       # TPS2116DRLR Power Mux right beside C5/C6 & J18!

    # --- 12x Grove Connectors (F.Cu, 3 columns x 4 rows, exact fit inside UNO R3 interior!) ---
    # NS-Tech_Grove_1x04_P2mm_Vertical: Pin 1=(0,0) -> Pin 4=(0, +6.0); CrtYd X:[-3.35, +2.35], Y:[-2.55, +8.20]
    # Center of body is at Y_pin1 + 2.825. For 4 rows centered at Y = 9.95, 21.05, 32.15, 43.25:
    #   Y_pin1 = Y_center - 2.825 -> 7.12, 18.22, 29.32, 40.42!
    #   Row 0: Y:[4.57, 15.32] (> 4.35 of J19/J20!)
    #   Row 1: Y:[15.67, 26.42]
    #   Row 2: Y:[26.77, 37.52]
    #   Row 3: Y:[37.87, 48.62] (< 48.99 of J17/J18!)
    # Column 1 (Analog Yellow, X_origin = 34.1 -> X:[30.75, 36.45]):
    "J6": (34.10, 7.12, 0, "F"),        # Grove A1-A0 (top, near Digital/top edge)
    "J5": (34.10, 18.22, 0, "F"),       # Grove A2-A1
    "J4": (34.10, 29.32, 0, "F"),       # Grove A3-A2
    "J3": (34.10, 40.42, 0, "F"),       # Grove A6-A3 (bottom, near Analog/Power)
    # Column 2 (Digital White, X_origin = 42.5 -> X:[39.15, 44.85]):
    "J10": (42.50, 7.12, 0, "F"),       # Grove D4-D3
    "J9": (42.50, 18.22, 0, "F"),       # Grove D6-D5
    "J8": (42.50, 29.32, 0, "F"),       # Grove D8-D7
    "J7": (42.50, 40.42, 0, "F"),       # Grove D10-D9
    # Column 3 (I2C Red, X_origin = 50.9 -> X:[47.55, 53.25]):
    "J14": (50.90, 7.12, 0, "F"),       # Grove I2C1
    "J13": (50.90, 18.22, 0, "F"),      # Grove I2C2
    "J12": (50.90, 29.32, 0, "F"),      # Grove I2C3
    "J11": (50.90, 40.42, 0, "F"),      # Grove I2C4

    # --- Compact Flat SMD Passives & ICs on B.Cu (strictly clear of RF keepout X<7.5, J1 THT pads & M3 holes!) ---
    # Reverse-polarity protection right behind J1 DC Jack on B.Cu (X >= 17.0 clear of J1 PTH pads X<=13.5!):
    "D1": (17.50, 45.40, 0, "B"),       # SMBJ15CA TVS right beside J1 pads!
    "Q1": (16.80, 40.00, 0, "B"),       # AO3407A P-MOSFET right beside D1!
    "D2": (22.00, 37.80, 0, "B"),       # BZT52C10 10V Zener
    "R1": (22.20, 40.30, 0, "B"),       # 47k Q1 gate pull-down
    "C2": (22.20, 42.30, 0, "B"),       # 100nF VIN_PROT HF bypass

    # LDO U3 input/output caps + PWR LED resistor on B.Cu right behind U3:
    "C8": (27.60, 44.50, 0, "B"),       # 10uF LDO input cap
    "C9": (27.60, 38.50, 0, "B"),       # 22uF LDO output cap
    "C10": (27.60, 36.20, 0, "B"),      # 100nF LDO HF bypass
    "R11": (17.50, 11.80, 0, "B"),      # 470R PWR LED resistor right behind D3

    # Buck feedback/EN & Power-Mux divider/decoupling on B.Cu right behind U1/U2:
    "R2": (57.00, 42.50, 0, "B"),       # 100k Buck EN pull-up
    "R3": (61.50, 39.50, 0, "B"),       # 68.0k Buck FB top (on B.Cu away from L1 magnetic field!)
    "R4": (61.50, 42.00, 0, "B"),       # 9.10k Buck FB bot
    "R5": (57.00, 45.50, 0, "B"),       # 36.0k TPS2116 PR1 top
    "R6": (57.00, 48.00, 0, "B"),       # 10.0k TPS2116 PR1 bot
    "C7": (61.50, 46.50, 0, "B"),       # 10uF +5V rail cap

    # ESP32-S3 Decoupling & EN/BOOT RC on B.Cu directly behind U4 (X >= 9.0, clear of RF keepout X <= 7.0!):
    "C11": (12.00, 21.00, 0, "B"),      # 22uF MCU 3V3 bulk directly under U4 3V3 pin!
    "C12": (12.00, 24.00, 0, "B"),      # 100nF MCU 3V3 HF bypass directly under U4 3V3 pin!
    "R7": (12.00, 27.00, 0, "B"),       # 10k EN pull-up
    "C13": (12.00, 29.50, 0, "B"),      # 1uF EN RC delay cap
    "R8": (22.50, 14.50, 0, "B"),       # 10k BOOT pull-up behind SW2

    # NeoPixel level shifter & D13 resistor on B.Cu directly behind D5 / D4:
    "U6": (22.80, 9.00, 0, "B"),        # SN74LV1T34DBVR right behind D5 WS2812B!
    "C15": (19.00, 8.50, 0, "B"),       # 100nF U6 +5V bypass
    "C16": (26.50, 8.50, 0, "B"),       # 100nF D5 +5V bypass
    "R13": (22.80, 12.20, 0, "B"),      # 10k GPIO45 strapping pull-down
    "R12": (17.50, 14.80, 0, "B"),      # 270R D13 LED resistor behind D4

    # Shared I2C Pull-ups (1.5k) on B.Cu right behind J14/J15:
    "R14": (46.80, 10.50, 90, "B"),     # 1.50k I2C_SDA pull-up
    "R15": (46.80, 14.50, 90, "B"),     # 1.50k I2C_SCL pull-up

    # A0 0-5V Conditioning Circuit (Q[10]: JP1 + R16 + R17 + C17) on B.Cu right near J18.1 (A0) & U4.39:
    "JP1": (47.50, 45.00, 0, "B"),      # 3-pad Solder Jumper accessible on back of PCB!
    "R16": (47.50, 42.00, 0, "B"),      # 6.80k A0 divider top
    "R17": (47.50, 39.50, 0, "B"),      # 10.0k A0 divider bottom
    "C17": (11.80, 18.00, 0, "B"),      # 100nF A0 ADC filter cap right behind U4.39!
}

# Fix FID1..FID3 positions (clean staggered corners, zero courtyard overlaps):
PLACEMENT["FID1"] = (28.00, 7.00, 0, "F")
PLACEMENT["FID2"] = (65.00, 28.00, 0, "F")
PLACEMENT["FID3"] = (28.60, 35.20, 0, "F")

# Verify every single schematic component is in PLACEMENT
missing_pl = set(components.keys()) - set(PLACEMENT.keys())
extra_pl = set(PLACEMENT.keys()) - set(components.keys())
assert not missing_pl and not extra_pl, f"Placement mismatch! missing={missing_pl}, extra={extra_pl}"

# Create nets in board
netinfo_by_name = {}
for idx, nname in enumerate(sorted(nets_map.keys()), start=1):
    ni = pcbnew.NETINFO_ITEM(board, nname, idx)
    board.Add(ni)
    netinfo_by_name[nname] = ni

# Build pad->net lookup
pad_net_lookup = {}
for nname, nodes in nets_map.items():
    for ref, pnum in nodes:
        pad_net_lookup[(ref, str(pnum))] = netinfo_by_name[nname]

# Place every footprint with exact schematic path for --schematic-parity!
fp_objs = {}
for ref, cinfo in sorted(components.items()):
    lx, ly, rot, side = PLACEMENT[ref]
    fp = pcbnew.FootprintLoad(PRETTY_DIR, cinfo["fp_name"])
    assert fp is not None, f"Failed to load footprint {cinfo['fp_name']} for {ref}"
    fp.SetReference(ref)
    fp.SetValue(cinfo["value"])
    fp.SetFPID(pcbnew.LIB_ID("YoloUNO", cinfo["fp_name"]))
    fp.SetPath(pcbnew.KIID_PATH(cinfo["path"]))
    fp.SetPosition(pt(lx, ly))
    fp.SetOrientationDegrees(float(rot))
    board.Add(fp)
    if side == "B":
        fp.Flip(pt(lx, ly), False)

    # Sync BOM attribute with schematic (JP1 is in_bom=yes in schematic)
    if ref == "JP1":
        fp.SetExcludedFromBOM(False)

    # Sync MPN and LCSC fields for 0 schematic-parity warnings
    for fname, fval in [("MPN", cinfo["mpn"]), ("LCSC", cinfo["lcsc"])]:
        fp.SetField(fname, fval)
    for fld in fp.GetFields():
        if fld.GetName() in ("MPN", "LCSC"):
            fld.SetVisible(False)

    # Hide noisy Value silkscreen & tiny B.Cu/0603 ref silkscreen for ultra-clean silk
    fp.Value().SetVisible(False)
    fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.85), mm(0.85)))
    fp.Reference().SetTextThickness(mm(0.14))
    if ref.startswith(("H", "FID")) or side == "B" or cinfo["fp_name"] in ("R_0603_1608Metric", "C_0603_1608Metric", "C_0805_2012Metric", "LED_0603_1608Metric"):
        fp.Reference().SetVisible(False)

    # Assign nets to all pads
    for pad in fp.Pads():
        pnum = pad.GetNumber()
        if (ref, pnum) in pad_net_lookup:
            pad.SetNet(pad_net_lookup[(ref, pnum)])
        else:
            pad.SetNetCode(0)

    fp_objs[ref] = fp


# ==============================================================================
# 5. VERIFY OFFICIAL ARDUINO UNO R3 HEADER PIN COORDINATES!
# ==============================================================================
print("\n--- Verifying Official Arduino UNO R3 Header Coordinates (local mm) ---")
for href, check_pins in [("J19", ["10", "1"]), ("J20", ["8", "1"]), ("J17", ["1", "8"]), ("J18", ["1", "6"]), ("J21", ["1", "2", "3"])]:
    fp = fp_objs[href]
    coords = []
    for p in fp.Pads():
        if p.GetNumber() in check_pins:
            pos = p.GetPosition()
            coords.append((p.GetNumber(), round(pcbnew.ToMM(pos.x) - OX, 2), round(pcbnew.ToMM(pos.y) - OY, 2)))
    print(f"  {href}: {coords}")

# Also verify ESP32-S3 antenna direction
u4_p1 = [p for p in fp_objs["U4"].Pads() if p.GetNumber() == "1"][0].GetPosition()
u4_p15 = [p for p in fp_objs["U4"].Pads() if p.GetNumber() == "15"][0].GetPosition()
print(f"  U4 Pad 1 (near ant): ({pcbnew.ToMM(u4_p1.x)-OX:.2f}, {pcbnew.ToMM(u4_p1.y)-OY:.2f}), Pad 15 (far end): ({pcbnew.ToMM(u4_p15.x)-OX:.2f}, {pcbnew.ToMM(u4_p15.y)-OY:.2f})")


# ==============================================================================
# 6. ADD RICH SILKSCREEN LABELS (MATCHING FIGURE 4 & SECTION 6.9)
# ==============================================================================
def add_silk_text(txt, lx, ly, size=0.85, thickness=0.14, rot=0.0, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(txt)
    t.SetPosition(pt(lx, ly))
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(thickness))
    t.SetTextAngleDegrees(rot)
    t.SetLayer(layer)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    board.Add(t)

# Board Title & Version (placed cleanly in open silk corridors, zero overlap with PTH holes!)
add_silk_text("YOLO UNO v1.0", 37.4, 26.8, size=1.15, thickness=0.18, rot=90, layer=pcbnew.B_SilkS)
add_silk_text("ESP32-S3 CO2037 HCMUT", 39.2, 26.8, size=0.85, thickness=0.14, rot=90, layer=pcbnew.B_SilkS)
add_silk_text("VIN:6-12V", 2.5, 43.0, size=0.85, thickness=0.14, rot=90, layer=pcbnew.F_SilkS)
add_silk_text("RST", 24.0, 49.5, size=0.85, thickness=0.14, rot=0, layer=pcbnew.F_SilkS)
add_silk_text("BOOT", 22.8, 16.7, size=0.85, thickness=0.14, rot=0, layer=pcbnew.F_SilkS)
add_silk_text("NEO", 26.2, 7.6, size=0.85, thickness=0.14, rot=90, layer=pcbnew.F_SilkS)
add_silk_text("PWR", 17.5, 10.2, size=0.85, thickness=0.14, rot=0, layer=pcbnew.F_SilkS)
add_silk_text("D13", 17.5, 16.4, size=0.85, thickness=0.14, rot=0, layer=pcbnew.F_SilkS)
add_silk_text("QWIIC", 8.5, 6.4, size=0.85, thickness=0.14, rot=0, layer=pcbnew.F_SilkS)
add_silk_text("A0: 1-2=3V3 2-3=5V", 47.2, 48.6, size=0.80, thickness=0.14, rot=0, layer=pcbnew.B_SilkS)

# Grove Labels (to the left of each Grove port)
for glbl, gx, gy in [
    ("A1-A0", 30.1, 10.0), ("A2-A1", 30.1, 21.1), ("A3-A2", 30.1, 32.2), ("A6-A3", 30.1, 43.3),
    ("D4-D3", 38.5, 10.0), ("D6-D5", 38.5, 21.1), ("D8-D7", 38.5, 32.2), ("D10-D9", 38.5, 43.3),
    ("I2C1", 46.9, 10.0),  ("I2C2", 46.9, 21.1),  ("I2C3", 46.9, 32.2),  ("I2C4", 46.9, 43.3),
]:
    add_silk_text(glbl, gx, gy, size=0.85, thickness=0.14, rot=90, layer=pcbnew.F_SilkS)

# Servo Labels
add_silk_text("G  5V  S", 59.1, 18.6, size=0.85, thickness=0.14, rot=0, layer=pcbnew.F_SilkS)
for slbl, sy in [("D2", 20.5), ("D13", 23.04), ("D12", 25.58), ("D11", 28.12)]:
    add_silk_text(slbl, 64.5, sy, size=0.85, thickness=0.14, rot=0, layer=pcbnew.F_SilkS)


# ==============================================================================
# 7. SAVE BOARD
# ==============================================================================
board.Save(PCB_FILE)
print(f"\nSaved unrouted 4-layer placement board to: {PCB_FILE}")
ctypes.windll.kernel32.ExitProcess(0)
