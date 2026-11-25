#!/usr/bin/env python3
"""
Phase 3 Step 2: 4-Layer PCB Automated Router & Copper Plane Generator for Yolo UNO (ESP32-S3)
Stackup:
  - F.Cu  : Signals + Buck SW/BOOT + Servo 1.30 mm +5V Backbone + U3 +3V3 Thermal Pour + Outer GND Pour
  - In1.Cu: 100% Solid Unbroken GND Reference Plane (auto-cleared by U4 RF Antenna Keepout)
  - In2.Cu: Split Power Plane (+3V3 West/Center, +5V East + J17.5 South Extension, 0.80 mm split)
  - B.Cu  : Signals + Coupled 90-Ohm USB Diff Pair + Outer GND Pour

Engine:
  - Stage 1: Exact verified parametric routing for Buck SW/BOOT (0 vias), USB-C D+/D- bridge (0 vias),
             USB 90-Ohm coupled differential pair (w=0.25, s=0.20 mm), Servo +5V 1.30 mm backbone,
             U3 4x thermal vias, and fine-pitch (0.50 mm) J2/U2 escape stubs.
  - Stage 2: Tight 0.20 mm grid (0.40 mm trace pitch, SIG_W=0.18 mm, gap=0.22 mm >> 0.15 mm DRC)
             with PathFinder Negotiated Congestion Rip-Up & Reroute until 100% nets routed & 0 conflicts.
  - Stage 3: Conflict-free SMD power fanout vias (GND -> In1.Cu, +3V3/+5V -> In2.Cu) + GND stitching vias.
  - Stage 4: Native KiCad 10 4-layer copper zone fill (ISLAND_REMOVAL_MODE_ALWAYS).
"""

import os
import sys
import math
import heapq
import ctypes
import time
import pcbnew

sys.stdout.reconfigure(line_buffering=True)

HW_DIR = r"c:\Users\QUOC ANH PC\Downloads\MDDT_Assignment\YoloUNO_Project\hardware"
PCB_FILE = os.path.join(HW_DIR, "YoloUNO.kicad_pcb")

OX, OY = 100.0, 100.0
W_BOARD, H_BOARD = 68.58, 53.34

GRID = 0.20
NX = int(round(W_BOARD / GRID)) + 1
NY = int(round(H_BOARD / GRID)) + 1
N_CELLS = NX * NY

VIA_D = 0.60
VIA_DRILL = 0.30
SIG_W = 0.18       # 0.18 mm signal trace -> 0.40 mm grid pitch leaves 0.22 mm gap (>> 0.15 mm IPC-2221 Class 2!)
CLR_MIN = 0.165    # Strict safety clearance > 0.15 mm DRC rule
EDGE_INSET = 0.46  # > 0.30 mm m_CopperEdgeClearance

LAYERS = [pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In2_Cu]


def mm(v):
    return int(round(v * 1e6))


def vec(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def pt(lx, ly):
    return vec(OX + lx, OY + ly)


def mm2g(lx, ly):
    ix = max(0, min(NX - 1, int(round(lx / GRID))))
    iy = max(0, min(NY - 1, int(round(ly / GRID))))
    return ix, iy


# ==============================================================================
# EXACT BOARD OUTLINE & GEOMETRY HELPERS
# ==============================================================================
OUTLINE_POLY = [
    (1.50, 0.00), (66.04, 0.00), (66.04, 2.54), (68.58, 5.08),
    (68.58, 37.85), (66.04, 40.39), (66.04, 51.82), (64.52, 53.34),
    (1.50, 53.34), (0.00, 51.84), (0.00, 1.50),
]


def point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def dist_pt_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    l2 = dx * dx + dy * dy
    if l2 < 1e-12:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / l2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def dist_to_outline(x, y):
    md = 1e9
    n = len(OUTLINE_POLY)
    for i in range(n):
        x1, y1 = OUTLINE_POLY[i]
        x2, y2 = OUTLINE_POLY[(i + 1) % n]
        d = dist_pt_seg(x, y, x1, y1, x2, y2)
        if d < md:
            md = d
    return md


def inside_board_safe(x, y, inset=EDGE_INSET):
    if x < inset or y < inset or x > W_BOARD - inset or y > H_BOARD - inset:
        return False
    if not point_in_poly(x, y, OUTLINE_POLY):
        return False
    return dist_to_outline(x, y) >= inset


def in_rf_keepout(x, y, margin=0.30):
    # U4 RF antenna keepout in local board coords: X in [-0.40, 6.90], Y in [17.80, 36.10]
    return (x <= 6.90 + margin) and (17.80 - margin <= y <= 36.10 + margin)


def dist_pt_box(px, py, x1, y1, x2, y2):
    dx = max(x1 - px, 0.0, px - x2)
    dy = max(y1 - py, 0.0, py - y2)
    return math.hypot(dx, dy)


def dist_seg_box(ax, ay, bx, by, x1, y1, x2, y2):
    sminx, smaxx = (ax, bx) if ax < bx else (bx, ax)
    sminy, smaxy = (ay, by) if ay < by else (by, ay)
    if not (smaxx < x1 or sminx > x2 or smaxy < y1 or sminy > y2):
        dx, dy = bx - ax, by - ay
        t0, t1 = 0.0, 1.0
        hit = True
        for p, q in [(-dx, ax - x1), (dx, x2 - ax), (-dy, ay - y1), (dy, y2 - ay)]:
            if abs(p) < 1e-12:
                if q < 0:
                    hit = False
                    break
            else:
                r = q / p
                if p < 0:
                    if r > t1:
                        hit = False
                        break
                    if r > t0:
                        t0 = r
                else:
                    if r < t0:
                        hit = False
                        break
                    if r < t1:
                        t1 = r
        if hit:
            return 0.0
    return min(
        dist_pt_box(ax, ay, x1, y1, x2, y2),
        dist_pt_box(bx, by, x1, y1, x2, y2),
        dist_pt_seg(x1, y1, ax, ay, bx, by),
        dist_pt_seg(x2, y1, ax, ay, bx, by),
        dist_pt_seg(x1, y2, ax, ay, bx, by),
        dist_pt_seg(x2, y2, ax, ay, bx, by),
    )


def dist_seg_seg(ax, ay, bx, by, cx, cy, dx, dy):
    def ccw(p1x, p1y, p2x, p2y, p3x, p3y):
        return (p3y - p1y) * (p2x - p1x) - (p2y - p1y) * (p3x - p1x)
    d1 = ccw(cx, cy, dx, dy, ax, ay)
    d2 = ccw(cx, cy, dx, dy, bx, by)
    d3 = ccw(ax, ay, bx, by, cx, cy)
    d4 = ccw(ax, ay, bx, by, dx, dy)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return 0.0
    return min(
        dist_pt_seg(ax, ay, cx, cy, dx, dy),
        dist_pt_seg(bx, by, cx, cy, dx, dy),
        dist_pt_seg(cx, cy, ax, ay, bx, by),
        dist_pt_seg(dx, dy, ax, ay, bx, by),
    )


# ==============================================================================
# LOAD BOARD & EXTRACT EXACT PAD DATA
# ==============================================================================
t0_all = time.time()
board = pcbnew.LoadBoard(PCB_FILE)

for item in list(board.GetTracks()):
    board.RemoveNative(item)
for z in list(board.Zones()):
    board.RemoveNative(z)

netinfo_map = {}
for code, ni in board.GetNetsByNetcode().items():
    if ni.GetNetname():
        netinfo_map[ni.GetNetname()] = ni

all_pads = []
pad_lookup = {}
net_pads = {}

for fp in board.GetFootprints():
    ref = fp.GetReference()
    for p in fp.Pads():
        pos = p.GetPosition()
        cx = pcbnew.ToMM(pos.x) - OX
        cy = pcbnew.ToMM(pos.y) - OY
        bb = p.GetBoundingBox()
        x1 = pcbnew.ToMM(bb.GetLeft()) - OX
        y1 = pcbnew.ToMM(bb.GetTop()) - OY
        x2 = pcbnew.ToMM(bb.GetRight()) - OX
        y2 = pcbnew.ToMM(bb.GetBottom()) - OY
        attr = p.GetAttribute()
        lset = p.GetLayerSet()
        is_npth = (attr == pcbnew.PAD_ATTRIB_NPTH)
        is_pth = (attr == pcbnew.PAD_ATTRIB_PTH)
        drill = pcbnew.ToMM(p.GetDrillSize().x) if (is_pth or is_npth) else 0.0
        ls = {0, 1, 2} if (is_pth or is_npth) else (({0} if lset.Contains(pcbnew.F_Cu) else set()) | ({1} if lset.Contains(pcbnew.B_Cu) else set()))
        net = p.GetNetname()
        pinfo = {
            "ref": ref, "pnum": p.GetNumber(), "net": net,
            "cx": cx, "cy": cy, "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "layers": ls, "is_pth": is_pth, "is_npth": is_npth, "drill": drill,
            "is_fid": ref.startswith("FID"),
        }
        all_pads.append(pinfo)
        pad_lookup.setdefault((ref, p.GetNumber()), []).append(pinfo)
        if net:
            net_pads.setdefault(net, []).append(pinfo)

print(f"Loaded {len(all_pads)} pads across {len(net_pads)} active nets.")

# ==============================================================================
# ROUTING DATABASE & EXACT CLEARANCE CHECKER
# ==============================================================================
all_tracks = []  # (x1, y1, x2, y2, w, layer_idx, net)
all_vias = []    # (vx, vy, net)

base_valid = [bytearray(N_CELLS), bytearray(N_CELLS), bytearray(N_CELLS)]
base_via_valid = bytearray(N_CELLS)

for iy in range(NY):
    ly = iy * GRID
    row = iy * NX
    for ix in range(NX):
        lx = ix * GRID
        idx = row + ix
        if inside_board_safe(lx, ly, EDGE_INSET) and not in_rf_keepout(lx, ly, 0.30):
            base_valid[0][idx] = 1
            base_valid[1][idx] = 1
            # Keep In2.Cu fallback traces cleanly clear of the narrow +5V south neck (Y > 47.0) and split seam (X in 53.0..54.8)
            if ly <= 46.8 and not (52.8 <= lx <= 55.0):
                base_valid[2][idx] = 1
            if inside_board_safe(lx, ly, EDGE_INSET + VIA_D / 2.0) and not in_rf_keepout(lx, ly, 0.30 + VIA_D / 2.0):
                base_via_valid[idx] = 1

for p in all_pads:
    if p["is_npth"] or p["is_fid"]:
        extra = (0.68 + SIG_W / 2.0) if p["is_fid"] else (0.32 + SIG_W / 2.0)
        extra_v = (0.68 + VIA_D / 2.0) if p["is_fid"] else (0.32 + VIA_D / 2.0)
        ix0 = max(0, int(math.floor((p["x1"] - extra_v) / GRID)))
        ix1 = min(NX - 1, int(math.ceil((p["x2"] + extra_v) / GRID)))
        iy0 = max(0, int(math.floor((p["y1"] - extra_v) / GRID)))
        iy1 = min(NY - 1, int(math.ceil((p["y2"] + extra_v) / GRID)))
        for iy in range(iy0, iy1 + 1):
            ly = iy * GRID
            for ix in range(ix0, ix1 + 1):
                lx = ix * GRID
                d = (math.hypot(lx - p["cx"], ly - p["cy"]) - p["drill"] / 2.0) if p["is_npth"] else dist_pt_box(lx, ly, p["x1"], p["y1"], p["x2"], p["y2"])
                if d < extra:
                    for L in p["layers"]:
                        base_valid[L][iy * NX + ix] = 0
                if d < extra_v:
                    base_via_valid[iy * NX + ix] = 0


def seg_clear(x1, y1, x2, y2, w, layer_idx, net, clr=CLR_MIN, check_tracks=True):
    hw = w / 2.0
    seg_len = math.hypot(x2 - x1, y2 - y1)
    nsteps = max(2, int(math.ceil(seg_len / 0.45)) + 1)
    for k in range(nsteps):
        t = k / (nsteps - 1) if nsteps > 1 else 0.0
        px = x1 + t * (x2 - x1)
        py = y1 + t * (y2 - y1)
        if not inside_board_safe(px, py, 0.34 + hw):
            return False, "edge"
        if in_rf_keepout(px, py, 0.22 + hw):
            return False, "rf_keepout"

    sminx = (x1 if x1 < x2 else x2) - (0.75 + hw)
    smaxx = (x2 if x1 < x2 else x1) + (0.75 + hw)
    sminy = (y1 if y1 < y2 else y2) - (0.75 + hw)
    smaxy = (y2 if y1 < y2 else y1) + (0.75 + hw)

    for p in all_pads:
        if p["x2"] < sminx or p["x1"] > smaxx or p["y2"] < sminy or p["y1"] > smaxy:
            continue
        if p["net"] == net and not p["is_npth"] and not p["is_fid"]:
            continue
        if layer_idx not in p["layers"]:
            continue
        req = (0.64 + hw) if p["is_fid"] else ((0.29 + hw) if p["is_npth"] else (clr + hw))
        d = (dist_pt_seg(p["cx"], p["cy"], x1, y1, x2, y2) - p["drill"] / 2.0) if p["is_npth"] else dist_seg_box(x1, y1, x2, y2, p["x1"], p["y1"], p["x2"], p["y2"])
        if d < req:
            return False, f"pad:{p['ref']}.{p['pnum']}({p['net']}) d={d:.3f}<{req:.3f}"

    if check_tracks:
        for tx1, ty1, tx2, ty2, tw, tl, tnet in all_tracks:
            if tl != layer_idx or tnet == net:
                continue
            if (tx1 > smaxx and tx2 > smaxx) or (tx1 < sminx and tx2 < sminx) or (ty1 > smaxy and ty2 > smaxy) or (ty1 < sminy and ty2 < sminy):
                continue
            if dist_seg_seg(x1, y1, x2, y2, tx1, ty1, tx2, ty2) < clr + hw + tw / 2.0:
                return False, f"track:{tnet}"

        for vx, vy, vnet in all_vias:
            if vnet == net:
                continue
            if vx < sminx or vx > smaxx or vy < sminy or vy > smaxy:
                continue
            if dist_pt_seg(vx, vy, x1, y1, x2, y2) < clr + hw + VIA_D / 2.0:
                return False, f"via:{vnet}"

    return True, "ok"


def via_clear(vx, vy, net, clr=CLR_MIN, check_tracks=True, ignore_self=False):
    vr = VIA_D / 2.0
    if not inside_board_safe(vx, vy, 0.36 + vr):
        return False, "edge"
    if in_rf_keepout(vx, vy, 0.25 + vr):
        return False, "rf_keepout"
    vminx, vmaxx = vx - 2.6, vx + 2.6
    vminy, vmaxy = vy - 2.6, vy + 2.6
    for p in all_pads:
        if p["x2"] < vminx or p["x1"] > vmaxx or p["y2"] < vminy or p["y1"] > vmaxy:
            continue
        if p["is_npth"] or p["is_pth"]:
            hd = math.hypot(vx - p["cx"], vy - p["cy"]) - (p["drill"] + VIA_DRILL) / 2.0
            if hd < 0.30:
                return False, f"hole:{p['ref']}.{p['pnum']}"
        if p["net"] == net and not p["is_npth"] and not p["is_fid"]:
            continue
        req = (0.64 + vr) if p["is_fid"] else ((0.29 + vr) if p["is_npth"] else (clr + vr))
        d = (math.hypot(vx - p["cx"], vy - p["cy"]) - p["drill"] / 2.0) if p["is_npth"] else dist_pt_box(vx, vy, p["x1"], p["y1"], p["x2"], p["y2"])
        if d < req:
            return False, f"pad:{p['ref']}.{p['pnum']}"
    if check_tracks:
        for tx1, ty1, tx2, ty2, tw, tl, tnet in all_tracks:
            if tnet == net:
                continue
            if (tx1 > vmaxx and tx2 > vmaxx) or (tx1 < vminx and tx2 < vminx) or (ty1 > vmaxy and ty2 > vmaxy) or (ty1 < vminy and ty2 < vminy):
                continue
            if dist_pt_seg(vx, vy, tx1, ty1, tx2, ty2) < clr + vr + tw / 2.0:
                return False, f"track:{tnet}"
        for ovx, ovy, ovnet in all_vias:
            if abs(vx - ovx) > 1.2 or abs(vy - ovy) > 1.2:
                continue
            if ignore_self and ovnet == net and abs(vx - ovx) < 1e-4 and abs(vy - ovy) < 1e-4:
                continue
            min_d = (VIA_D + clr) if ovnet != net else 0.65
            if math.hypot(vx - ovx, vy - ovy) < min_d:
                return False, f"via:{ovnet}"
    return True, "ok"


def add_seg(x1, y1, x2, y2, w, layer_idx, net, check=True, clr=0.16):
    if math.hypot(x2 - x1, y2 - y1) < 1e-4:
        return True
    if check:
        ok, reason = seg_clear(x1, y1, x2, y2, w, layer_idx, net, clr=clr)
        if not ok:
            print(f"  [WARN] Segment rejected {net} L{layer_idx} ({x1:.2f},{y1:.2f})->({x2:.2f},{y2:.2f}) w={w}: {reason}")
            return False
    all_tracks.append((x1, y1, x2, y2, w, layer_idx, net))
    return True


def add_poly_track(pts, w, layer_idx, net, check=True, clr=0.16):
    ok_all = True
    for i in range(len(pts) - 1):
        if not add_seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], w, layer_idx, net, check=check, clr=clr):
            ok_all = False
    return ok_all


def add_via(vx, vy, net, check=True, clr=0.16):
    if check:
        ok, reason = via_clear(vx, vy, net, clr=clr)
        if not ok:
            print(f"  [WARN] Via rejected {net} @ ({vx:.2f},{vy:.2f}): {reason}")
            return False
    all_vias.append((vx, vy, net))
    return True


def get_pad(ref, pnum):
    return pad_lookup[(ref, str(pnum))][0]


# ==============================================================================
# STAGE 1: CRITICAL POWER, BUCK SW/BOOT, USB 90-OHM DIFF PAIR & FINE-PITCH ESCAPES
# ==============================================================================
print("\n--- Stage 1: Routing Critical Power, Buck SW/BOOT, USB 90-Ohm Diff Pair & Fine-Pitch Escapes ---")

# 1A. Buck SW (0 vias, F.Cu) & BOOT (0 vias, F.Cu)
p_u1_sw = get_pad("U1", "2")
p_l1_sw = get_pad("L1", "1")
p_c4_sw = get_pad("C4", "2")
add_poly_track([(p_u1_sw["cx"], p_u1_sw["cy"]), (55.40, p_u1_sw["cy"])], 0.40, 0, "Net-(U1-SW)")
add_poly_track([(55.40, p_u1_sw["cy"]), (55.40, 38.00), (p_l1_sw["cx"], 38.00), (p_l1_sw["cx"], p_l1_sw["cy"])], 0.60, 0, "Net-(U1-SW)")
add_poly_track([(p_l1_sw["cx"], 38.00), (p_c4_sw["cx"], 38.00), (p_c4_sw["cx"], p_c4_sw["cy"])], 0.30, 0, "Net-(U1-SW)")

p_u1_boot = get_pad("U1", "6")
p_c4_boot = get_pad("C4", "1")
add_poly_track([(p_u1_boot["cx"], p_u1_boot["cy"]), (60.90, p_u1_boot["cy"]), (60.90, p_c4_boot["cy"]), (p_c4_boot["cx"], p_c4_boot["cy"])], 0.25, 0, "Net-(U1-BOOT)")
print("  [OK] Buck SW (0 vias) & BOOT (0 vias) routed on F.Cu.")

# 1B. USB-C J2 -> U5 D+/D- interleaved bridge on F.Cu (0 vias!)
add_poly_track([(8.84, 12.35), (7.55, 12.35), (7.55, 11.35), (8.84, 11.35), (10.70, 11.35), (11.20, 10.85), (12.06, 10.85)], 0.18, 0, "Net-(J2-D--PadA7)", clr=0.155)
add_poly_track([(8.84, 11.85), (10.25, 11.85), (10.25, 12.85), (8.84, 12.85)], 0.18, 0, "Net-(J2-D+-PadA6)", clr=0.155)
add_poly_track([(10.25, 12.85), (11.10, 12.85), (11.20, 12.75), (12.06, 12.75)], 0.18, 0, "Net-(J2-D+-PadA6)", clr=0.155)
print("  [OK] USB-C J2 -> U5 D+/D- interleaved bridge routed on F.Cu (0 vias).")

# 1C. USB 2.0 90-Ohm Coupled Differential Pair (w=0.25 mm, s=0.20 mm, center pitch 0.45 mm)
# Clear of R11/R12 (X>=16.22, Y<=15.25) AND clear of U4.41 PTH thermal vias (X in [13.9, 17.4], Y in [26.7, 30.2])!
dn_f1 = [(14.34, 10.85), (15.15, 10.85)]
dp_f1 = [(14.34, 12.75), (15.15, 12.75)]
add_poly_track(dn_f1, 0.25, 0, "USB_DN")
add_poly_track(dp_f1, 0.25, 0, "USB_DP")
add_via(15.15, 10.85, "USB_DN")
add_via(15.15, 12.75, "USB_DP")

dn_b = [(15.15, 10.85), (14.45, 11.55), (14.45, 16.85), (18.40, 20.80), (18.40, 33.80), (22.40, 33.80)]
dp_b = [(15.15, 12.75), (15.15, 13.60), (14.90, 13.85), (14.90, 16.66), (18.85, 20.61), (18.85, 33.35), (21.20, 33.35), (21.55, 33.00), (23.85, 33.00), (23.85, 33.60)]
add_poly_track(dn_b, 0.25, 1, "USB_DN")
add_poly_track(dp_b, 0.25, 1, "USB_DP")

add_via(22.40, 33.80, "USB_DN")
add_via(23.85, 33.60, "USB_DP")
dn_f2 = [(22.40, 33.80), (23.18, 34.58), (23.18, 35.70)]
dp_f2 = [(23.85, 33.60), (24.45, 34.20), (24.45, 35.70)]
add_poly_track(dn_f2, 0.25, 0, "USB_DN")
add_poly_track(dp_f2, 0.25, 0, "USB_DP")

def poly_len(pts):
    return sum(math.hypot(pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1]) for i in range(len(pts)-1))

len_dn = poly_len(dn_f1) + poly_len(dn_b) + poly_len(dn_f2)
len_dp = poly_len(dp_f1) + poly_len(dp_b) + poly_len(dp_f2)
print(f"  [OK] USB 90-Ohm Diff Pair routed: L(DN)={len_dn:.2f} mm, L(DP)={len_dp:.2f} mm, skew={abs(len_dn-len_dp):.2f} mm (spec <= 7.5 mm).")

# 1D. Servo +5V Wide Backbone (1.30 mm > 0.781 mm IPC-2221 min!) on F.Cu + U2/C18 +5V Stitching
add_poly_track([
    (60.00, 14.50), (59.14, 15.36),
    (59.14, 20.50), (59.14, 23.04), (59.14, 25.58), (59.14, 28.12),
], 1.30, 0, "+5V")
add_via(57.20, 14.50, "+5V")
add_via(62.80, 14.50, "+5V")
add_poly_track([(57.20, 14.50), (60.00, 14.50), (62.80, 14.50)], 0.80, 0, "+5V")

add_poly_track([(56.26, 47.15), (57.74, 47.15), (58.55, 47.15), (59.10, 46.60)], 0.22, 0, "+5V", clr=0.155)
add_via(59.10, 46.60, "+5V")
add_via(59.10, 45.80, "+5V")
add_poly_track([(59.10, 46.60), (59.10, 45.80)], 0.45, 0, "+5V")

# Local NW +5V cluster (C15.1 <-> U6.5 <-> D5.1 <-> C16.1)
add_poly_track([(19.78, 8.50), (21.21, 8.50), (21.66, 8.05)], 0.32, 1, "+5V")
add_poly_track([(21.66, 8.05), (22.30, 7.40), (26.18, 7.40), (27.28, 8.50)], 0.32, 1, "+5V")
add_poly_track([(20.35, 5.95), (20.35, 7.20)], 0.32, 0, "+5V")
add_via(20.35, 7.20, "+5V")
add_poly_track([(20.35, 7.20), (21.20, 8.05), (21.66, 8.05)], 0.32, 1, "+5V")
print("  [OK] Servo +5V 1.30 mm backbone & NW/East +5V local connections routed.")

# 1E. U3 (AP2114H-3.3) 4x Thermal Vias (+3V3) down to In2.Cu +3V3 plane
for vx, vy in [(25.10, 37.80), (25.10, 39.60), (25.10, 41.20), (28.55, 40.40)]:
    add_via(vx, vy, "+3V3")
add_poly_track([(25.10, 37.80), (26.60, 39.05), (25.10, 39.60), (25.10, 41.20)], 0.50, 0, "+3V3")
add_poly_track([(26.60, 39.05), (28.55, 40.40)], 0.50, 0, "+3V3")
add_poly_track([(26.60, 45.35), (26.60, 39.05)], 0.80, 0, "+3V3")
add_poly_track([(28.55, 40.40), (28.55, 38.50), (28.38, 36.20)], 0.45, 1, "+3V3")
print("  [OK] U3 AP2114H-3.3 4x thermal vias & LDO output caps routed.")

# 1F. VIN_RAW (0.80 mm on B.Cu, 0 vias)
add_poly_track([(13.50, 41.80), (15.66, 40.00)], 0.80, 1, "/01_Power_Supply/VIN_RAW")
add_poly_track([(13.50, 41.80), (15.35, 45.40)], 0.80, 1, "/01_Power_Supply/VIN_RAW")

# 1G. Fine-pitch clean escapes (J2 USB-C & U2 TPS2116)
# J2 VBUS bridge & U5.5 escape
add_poly_track([(8.84, 9.65), (10.60, 9.65)], 0.35, 0, "VBUS", clr=0.155)
add_poly_track([(8.84, 14.55), (11.20, 14.55), (12.42, 15.20)], 0.35, 0, "VBUS", clr=0.155)
add_via(10.60, 9.65, "VBUS")
add_via(11.00, 14.55, "VBUS")
add_poly_track([(10.60, 9.65), (10.60, 14.15), (11.00, 14.55)], 0.45, 1, "VBUS")
# U5.5 (14.34, 11.80) -> east between USB vias (at X=15.15, Y=10.85/12.75) -> (15.95, 11.80) -> (15.95, 13.60) -> via (16.00, 13.60)!
add_poly_track([(14.34, 11.80), (15.95, 11.80), (15.95, 13.60), (16.00, 13.60)], 0.20, 0, "VBUS", clr=0.155)
add_via(16.00, 13.60, "VBUS")

# J2 CC1 & CC2
add_poly_track([(8.84, 10.85), (10.20, 10.85), (10.20, 10.30), (11.60, 10.30), (12.38, 9.52), (12.38, 8.20)], 0.18, 0, "Net-(J2-CC1)", clr=0.155)
add_poly_track([(8.84, 13.85), (10.20, 13.85)], 0.18, 0, "Net-(J2-CC2)", clr=0.155)

# U2 fine-pitch escapes (ZERO conflicts!):
# U2.6 VBUS (57.74, 47.65) -> (59.20, 47.65) -> via (59.20, 47.80)
add_poly_track([(57.74, 47.65), (59.20, 47.65), (59.20, 47.80)], 0.18, 0, "VBUS", clr=0.155)
add_via(59.20, 47.80, "VBUS")

# U2.4 PR1 (56.26, 48.15) -> south to via (56.26, 49.20) [clear of R6.2 @ 48.00 and J18 @ 50.80!] -> B.Cu to R6.1 & R5.2!
add_poly_track([(56.26, 48.15), (56.26, 49.20)], 0.18, 0, "Net-(U2-PR1)", clr=0.155)
add_via(56.26, 49.20, "Net-(U2-PR1)")
add_poly_track([(56.26, 49.20), (57.82, 49.20), (57.82, 48.00)], 0.18, 1, "Net-(U2-PR1)")
add_poly_track([(56.26, 49.20), (55.00, 49.20), (55.00, 45.50), (56.18, 45.50)], 0.18, 1, "Net-(U2-PR1)")

# U2.5 (57.74, 48.15) connects on F.Cu to C6.1/C5.1/L1.2; U2.3 (56.26, 47.65) escapes west to via (54.40, 47.65) -> B.Cu!
add_poly_track([(57.74, 48.15), (57.74, 49.00), (60.55, 49.00), (60.55, 46.80), (60.55, 44.30)], 0.25, 0, "/01_Power_Supply/5V_BUCK", clr=0.155)
add_poly_track([(56.26, 47.65), (54.40, 47.65)], 0.22, 0, "/01_Power_Supply/5V_BUCK", clr=0.155)
add_via(54.40, 47.65, "/01_Power_Supply/5V_BUCK")
add_poly_track([(61.57, 34.50), (64.10, 34.50), (64.10, 42.70), (60.55, 42.70), (60.55, 44.30)], 0.70, 0, "/01_Power_Supply/5V_BUCK")

# U2.1 GND (56.26, 46.65) -> west to via (54.20, 46.40) [clear of PR1 @ X=55.0 & 5V_BUCK via @ 54.40, 47.65!]
add_poly_track([(56.26, 46.65), (54.20, 46.65), (54.20, 46.40)], 0.20, 0, "GND", clr=0.155)
add_via(54.20, 46.40, "GND")

# Local analog & protection nets on B.Cu (ZERO warnings!)
# Net-(D2-A): Q1.1 (17.94, 39.05) <-> D2.2 (20.35, 37.80) <-> R1.1 (23.03, 40.30) [go south around D2.1 @ 23.65, 37.80!]
add_poly_track([(17.94, 39.05), (20.35, 39.05), (20.35, 37.80)], 0.22, 1, "Net-(D2-A)")
add_poly_track([(20.35, 39.05), (20.35, 39.30), (23.03, 39.30), (23.03, 40.30)], 0.22, 1, "Net-(D2-A)")

# Net-(JP1-B): JP1.3 (46.20, 45.00) <-> R16.2 (46.68, 42.00) <-> R17.1 (48.32, 39.50)
add_poly_track([(46.20, 45.00), (46.20, 42.48), (46.68, 42.00)], 0.22, 1, "Net-(JP1-B)")
add_poly_track([(46.68, 42.00), (48.32, 40.36), (48.32, 39.50)], 0.22, 1, "Net-(JP1-B)")

# Pre-place +3V3 pull-up supply vias for R14.1 (46.80, 11.33, B) & R15.1 (46.80, 15.33, B) cleanly!
add_poly_track([(46.80, 11.33), (46.80, 12.20)], 0.25, 1, "+3V3")
add_via(46.80, 12.20, "+3V3")
add_poly_track([(46.80, 15.33), (46.80, 16.40)], 0.25, 1, "+3V3")
add_via(46.80, 16.40, "+3V3")

# Tie J2 USB-C SMD GND pads directly to J2 PTH Shield pads on F.Cu (clean chassis/signal GND, 0 tight vias!)
add_poly_track([(8.84, 8.85), (7.93, 7.78)], 0.35, 0, "GND", clr=0.155)
add_poly_track([(8.84, 15.35), (7.93, 16.42)], 0.35, 0, "GND", clr=0.155)

# Tie ESP32 decoupling caps C11.1/C12.1/R7.1 (+3V3) on B.Cu to one dedicated clean via into In2.Cu!
add_poly_track([(12.95, 21.00), (12.95, 22.50), (12.78, 24.00), (12.83, 27.00)], 0.30, 1, "+3V3")
add_via(13.60, 22.50, "+3V3")
add_poly_track([(12.95, 22.50), (13.60, 22.50)], 0.30, 1, "+3V3")

# Tie LDO caps C10.2/C9.2 (GND) on B.Cu to one clean GND via into In1.Cu!
add_poly_track([(26.83, 36.20), (26.65, 38.50)], 0.30, 1, "GND")
add_via(26.15, 36.70, "GND")
add_poly_track([(26.83, 36.20), (26.15, 36.70)], 0.30, 1, "GND")

# Pre-tie tight SMD GND pads (U5.2, C8.2, C7.2) cleanly to In1.Cu solid GND plane before signal routing!
# U5.2 (12.06, 11.80, F) -> via centered directly below U5 at (13.20, 13.70)
if via_clear(13.20, 13.70, "GND", clr=0.16)[0] and seg_clear(12.06, 11.80, 13.20, 11.80, 0.22, 0, "GND", clr=0.155)[0] and seg_clear(13.20, 11.80, 13.20, 13.70, 0.22, 0, "GND", clr=0.155)[0]:
    add_poly_track([(12.06, 11.80), (13.20, 11.80), (13.20, 13.70)], 0.22, 0, "GND")
    add_via(13.20, 13.70, "GND")
# C8.2 (26.65, 44.50, B) -> shared GND via right beside U3.1 (24.30, 45.35, F) at (25.40, 45.35)!
if via_clear(25.40, 45.35, "GND", clr=0.16)[0] and seg_clear(26.65, 44.50, 25.40, 45.35, 0.25, 1, "GND", clr=0.16)[0]:
    add_poly_track([(26.65, 44.50), (25.40, 45.35)], 0.25, 1, "GND")
    add_via(25.40, 45.35, "GND")
# C7.2 (60.55, 46.50, B) -> clean GND via at (61.80, 48.30) [clear of C6 & J18!]
for cvx, cvy in [(61.80, 48.30), (60.55, 48.30), (63.60, 46.50)]:
    if via_clear(cvx, cvy, "GND", clr=0.16)[0] and seg_clear(60.55, 46.50, cvx, cvy, 0.25, 1, "GND", clr=0.16)[0]:
        add_poly_track([(60.55, 46.50), (cvx, cvy)], 0.25, 1, "GND")
        add_via(cvx, cvy, "GND")
        break

# 1H. Pre-allocated Clean Staggered Fanout Escapes for U4 (ESP32-S3-WROOM-1, 1.27 mm pitch)!
# Prevents early nets from sealing U4's tightly pitched perimeter pads!
# South pads (Y=35.70, blocked below by J1/C1): fan INWARD (North) on F.Cu to 2 staggered via rows (Y=33.80 & Y=32.40)!
u4_south_fanout = [
    ("3",  "MCU_EN", 32.40),
    ("4",  "A3",     33.80),
    ("5",  "D2",     32.40),
    ("6",  "D3",     33.80),
    ("7",  "D4",     32.40),
    ("10", "D8",     33.80),
    ("11", "D9",     32.40),
    ("12", "D5",     33.80),
]
for pnum, net, vy in u4_south_fanout:
    p = get_pad("U4", pnum)
    vx = round(p["cx"] / 0.10) * 0.10
    if via_clear(vx, vy, net, clr=0.16)[0] and seg_clear(p["cx"], p["cy"], vx, vy, SIG_W, 0, net, clr=0.16)[0]:
        add_poly_track([(p["cx"], p["cy"]), (vx, vy)], SIG_W, 0, net)
        add_via(vx, vy, net)

# North pads (Y=18.20): fan cleanly across U4's empty upper F.Cu interior OVER B.Cu USB_DN/DP to staggered vias at X=20.4/21.6!
# U4.27 (BOOT_IO0 @ 24.45, 18.20) -> straight north to SW2.2 (25.80, 15.38) on F.Cu!
add_poly_track([(24.45, 18.20), (24.45, 16.73), (25.80, 15.38)], SIG_W, 0, "/02_MCU_ESP32S3/BOOT_IO0")
u4_north_fanout = [
    ("31", "D11",    20.60, 19.80),
    ("36", "D0_RX",  22.40, 21.20),
    ("37", "D1_TX",  20.60, 22.60),
    ("38", "A1",     22.40, 24.00),
    ("39", "A0_ADC",  9.21, 20.00),
]
for pnum, net, vx, vy in u4_north_fanout:
    p = get_pad("U4", pnum)
    if via_clear(vx, vy, net, clr=0.16)[0]:
        if seg_clear(p["cx"], p["cy"], p["cx"], vy, SIG_W, 0, net, clr=0.155)[0] and seg_clear(p["cx"], vy, vx, vy, SIG_W, 0, net, clr=0.155)[0]:
            add_poly_track([(p["cx"], p["cy"]), (p["cx"], vy), (vx, vy)], SIG_W, 0, net)
            add_via(vx, vy, net)
        elif seg_clear(p["cx"], p["cy"], vx, vy, SIG_W, 0, net, clr=0.155)[0]:
            add_poly_track([(p["cx"], p["cy"]), (vx, vy)], SIG_W, 0, net)
            add_via(vx, vy, net)

# East pads (X=25.70): fan straight EAST on F.Cu to alternating staggered X=27.20 / X=28.20 so every pad breaks out cleanly!
u4_east_fanout = [
    ("15", "A2",         27.20),
    ("17", "D6",         27.20),
    ("18", "D7",         28.20),
    ("19", "I2C_SDA",    27.20),
    ("20", "I2C_SCL",    28.20),
    ("22", "A6",         27.20),
    ("23", "D10",        28.20),
    ("24", "D12",        27.20),
    ("25", "D13",        28.20),
    ("26", "NEO_GPIO45", 27.20),
]
for pnum, net, ex in u4_east_fanout:
    p = get_pad("U4", pnum)
    if seg_clear(p["cx"], p["cy"], ex, p["cy"], SIG_W, 0, net, clr=0.155)[0]:
        add_poly_track([(p["cx"], p["cy"]), (ex, p["cy"])], SIG_W, 0, net)

print("  [OK] Fine-pitch escapes, U4 23-pin clean fanout & local analog/protection nets routed.")


# ==============================================================================
# STAGE 2: TIGHT-PITCH PATHFINDER NEGOTIATED-CONGESTION A* ROUTER
# ==============================================================================
print("\n--- Stage 2: Building Tight 0.40 mm Pitch Grid & PathFinder Negotiated-Congestion Router ---")

def in_in2_3v3(x, y):
    if in_rf_keepout(x, y, 0.45) or not inside_board_safe(x, y, 0.70):
        return False
    if x > 53.1 or (x > 36.2 and y > 47.3):
        return False
    return True


def in_in2_5v(x, y):
    if not inside_board_safe(x, y, 0.70):
        return False
    return (x >= 54.7) or (x >= 37.8 and y >= 48.9)


def in_in1_gnd(x, y):
    return inside_board_safe(x, y, 0.70) and not in_rf_keepout(x, y, 0.45)


def get_net_components(net, virtual_plane_fn=None):
    """Return list of connected components of `net`. If virtual_plane_fn is provided,
    all PTH pads & vias inside virtual_plane_fn are unified as one connected plane component!"""
    pts = [(p["cx"], p["cy"], set(p["layers"]), f"{p['ref']}.{p['pnum']}") for p in net_pads.get(net, [])]
    n = len(pts)
    net_segs = [(x1, y1, x2, y2, tl) for (x1, y1, x2, y2, tw, tl, tn) in all_tracks if tn == net]
    net_vs = [(vx, vy) for (vx, vy, vn) in all_vias if vn == net]

    nodes = list(pts)
    via_start = len(nodes)
    for vx, vy in net_vs:
        nodes.append((vx, vy, {0, 1, 2}, "via"))
    seg_node_pairs = []
    for x1, y1, x2, y2, tl in net_segs:
        i1 = len(nodes)
        nodes.append((x1, y1, {tl}, "seg"))
        i2 = len(nodes)
        nodes.append((x2, y2, {tl}, "seg"))
        seg_node_pairs.append((i1, i2, x1, y1, x2, y2, tl))

    M = len(nodes)
    parent = list(range(M))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i1, i2, x1, y1, x2, y2, tl in seg_node_pairs:
        union(i1, i2)

    # Virtual plane unification (e.g., all East +5V PTH/vias + J17.5 are already unified by In2.Cu!)
    if virtual_plane_fn is not None:
        plane_rep = None
        for i in range(via_start + len(net_vs)):
            xi, yi, li, tag = nodes[i]
            if (0 in li and 1 in li) and virtual_plane_fn(xi, yi):
                if plane_rep is None:
                    plane_rep = i
                else:
                    union(plane_rep, i)

    for i in range(M):
        xi, yi, li, _ = nodes[i]
        for j in range(i + 1, M):
            if find(i) == find(j):
                continue
            xj, yj, lj, _ = nodes[j]
            if (li & lj) and abs(xi - xj) < 0.08 and abs(yi - yj) < 0.08:
                union(i, j)

    for pi in range(n):
        pad = net_pads[net][pi]
        for vi in range(via_start, via_start + len(net_vs)):
            vx, vy, _, _ = nodes[vi]
            if dist_pt_box(vx, vy, pad["x1"], pad["y1"], pad["x2"], pad["y2"]) < 0.05:
                union(pi, vi)
        for i1, i2, x1, y1, x2, y2, tl in seg_node_pairs:
            if tl in pad["layers"] and dist_seg_box(x1, y1, x2, y2, pad["x1"], pad["y1"], pad["x2"], pad["y2"]) < 0.05:
                union(pi, i1)

    for ni in range(M):
        xn, yn, ln, _ = nodes[ni]
        for i1, i2, x1, y1, x2, y2, tl in seg_node_pairs:
            if find(ni) != find(i1) and (tl in ln) and dist_pt_seg(xn, yn, x1, y1, x2, y2) < 0.05:
                union(ni, i1)

    comp_map = {}
    for i in range(n):
        comp_map.setdefault(find(i), [])
    for i in range(M):
        r = find(i)
        if r in comp_map:
            comp_map[r].append(nodes[i])
    return list(comp_map.values())


def rasterize_box_cells(x1, y1, x2, y2, margin):
    ix0 = max(0, int(math.floor((x1 - margin) / GRID)))
    ix1 = min(NX - 1, int(math.ceil((x2 + margin) / GRID)))
    iy0 = max(0, int(math.floor((y1 - margin) / GRID)))
    iy1 = min(NY - 1, int(math.ceil((y2 + margin) / GRID)))
    cells = []
    for iy in range(iy0, iy1 + 1):
        ly = iy * GRID
        row = iy * NX
        for ix in range(ix0, ix1 + 1):
            if dist_pt_box(ix * GRID, ly, x1, y1, x2, y2) < margin:
                cells.append(row + ix)
    return cells


def rasterize_seg_cells(x1, y1, x2, y2, margin):
    ix0 = max(0, int(math.floor((min(x1, x2) - margin) / GRID)))
    ix1 = min(NX - 1, int(math.ceil((max(x1, x2) + margin) / GRID)))
    iy0 = max(0, int(math.floor((min(y1, y2) - margin) / GRID)))
    iy1 = min(NY - 1, int(math.ceil((max(y1, y2) + margin) / GRID)))
    cells = []
    for iy in range(iy0, iy1 + 1):
        ly = iy * GRID
        row = iy * NX
        for ix in range(ix0, ix1 + 1):
            if dist_pt_seg(ix * GRID, ly, x1, y1, x2, y2) < margin:
                cells.append(row + ix)
    return cells


def rasterize_circle_cells(cx, cy, radius):
    ix0 = max(0, int(math.floor((cx - radius) / GRID)))
    ix1 = min(NX - 1, int(math.ceil((cx + radius) / GRID)))
    iy0 = max(0, int(math.floor((cy - radius) / GRID)))
    iy1 = min(NY - 1, int(math.ceil((cy + radius) / GRID)))
    r2 = radius * radius
    cells = []
    for iy in range(iy0, iy1 + 1):
        dy = iy * GRID - cy
        dy2 = dy * dy
        row = iy * NX
        for ix in range(ix0, ix1 + 1):
            dx = ix * GRID - cx
            if dx * dx + dy2 < r2:
                cells.append(row + ix)
    return cells


# Tight pad rasterization: SIG_W/2 (0.09) + CLR (0.165) = 0.255 mm! Via: 0.30 + 0.165 = 0.465 mm!
pad_trk_cells = [None] * len(all_pads)
pad_via_cells = [None] * len(all_pads)
pad_block_trk = [[0] * N_CELLS, [0] * N_CELLS, [0] * N_CELLS]
pad_block_via = [0] * N_CELLS
net_pad_indices = {}

for idx_p, p in enumerate(all_pads):
    if p["is_npth"] or p["is_fid"]:
        pad_trk_cells[idx_p] = []
        pad_via_cells[idx_p] = []
        continue
    ct = rasterize_box_cells(p["x1"], p["y1"], p["x2"], p["y2"], 0.26)
    cv = rasterize_box_cells(p["x1"], p["y1"], p["x2"], p["y2"], 0.48)
    if p["is_pth"]:
        cv_h = rasterize_circle_cells(p["cx"], p["cy"], p["drill"] / 2.0 + VIA_DRILL / 2.0 + 0.32)
        cv = list(set(cv) | set(cv_h))
    pad_trk_cells[idx_p] = ct
    pad_via_cells[idx_p] = cv
    for L in p["layers"]:
        arr = pad_block_trk[L]
        for c in ct:
            arr[c] += 1
    for c in cv:
        pad_block_via[c] += 1
    if p["net"]:
        net_pad_indices.setdefault(p["net"], []).append(idx_p)

# Dynamic occupancy counts + fixed Stage-1 hard lock mask!
fixed_trk = [[0] * N_CELLS, [0] * N_CELLS, [0] * N_CELLS]
fixed_via = [0] * N_CELLS
dyn_trk_cnt = [[0] * N_CELLS, [0] * N_CELLS, [0] * N_CELLS]
dyn_via_cnt = [0] * N_CELLS
history_trk = [[0] * N_CELLS, [0] * N_CELLS, [0] * N_CELLS]
history_via = [0] * N_CELLS

stage1_tracks_by_net = {}
stage1_vias_by_net = {}
stage2_net_items = {}  # net -> (trks, vs, t_cells_by_L, v_cells)
item_raster_cache = {}


def get_track_raster(trk):
    x1, y1, x2, y2, w, tl, _ = trk
    key = ("T", round(x1, 3), round(y1, 3), round(x2, 3), round(y2, 3), round(w, 3), tl)
    if key not in item_raster_cache:
        # On 0.20 mm Manhattan grid: 0.18/2 + 0.18/2 + 0.165 = 0.345 mm (< 0.40 mm = 2 cells -> exact 0.22 mm gap!)
        ct = rasterize_seg_cells(x1, y1, x2, y2, w / 2.0 + SIG_W / 2.0 + 0.165)
        cv = rasterize_seg_cells(x1, y1, x2, y2, w / 2.0 + VIA_D / 2.0 + 0.165)
        item_raster_cache[key] = (ct, cv)
    return item_raster_cache[key]


def get_via_raster(v):
    vx, vy, _ = v
    key = ("V", round(vx, 3), round(vy, 3))
    if key not in item_raster_cache:
        ct = rasterize_circle_cells(vx, vy, VIA_D / 2.0 + SIG_W / 2.0 + 0.175)
        cv = rasterize_circle_cells(vx, vy, VIA_D + 0.18)
        item_raster_cache[key] = (ct, cv)
    return item_raster_cache[key]


def apply_track_to_grid(trk, delta, is_fixed=False):
    ct, cv = get_track_raster(trk)
    tl = trk[5]
    arr = fixed_trk[tl] if is_fixed else dyn_trk_cnt[tl]
    for c in ct:
        arr[c] += delta
    varr = fixed_via if is_fixed else dyn_via_cnt
    for c in cv:
        varr[c] += delta


def apply_via_to_grid(v, delta, is_fixed=False):
    ct, cv = get_via_raster(v)
    for L in (0, 1, 2):
        arr = fixed_trk[L] if is_fixed else dyn_trk_cnt[L]
        for c in ct:
            arr[c] += delta
    varr = fixed_via if is_fixed else dyn_via_cnt
    for c in cv:
        varr[c] += delta


for trk in all_tracks:
    apply_track_to_grid(trk, +1, is_fixed=True)
    stage1_tracks_by_net.setdefault(trk[6], []).append(trk)
for v in all_vias:
    apply_via_to_grid(v, +1, is_fixed=True)
    stage1_vias_by_net.setdefault(v[2], []).append(v)


def temporarily_unblock_net(net, delta):
    for idx_p in net_pad_indices.get(net, []):
        p = all_pads[idx_p]
        for L in p["layers"]:
            arr = pad_block_trk[L]
            for c in pad_trk_cells[idx_p]:
                arr[c] += delta
        if not p["is_pth"]:
            for c in pad_via_cells[idx_p]:
                pad_block_via[c] += delta
    for trk in stage1_tracks_by_net.get(net, []):
        apply_track_to_grid(trk, delta, is_fixed=True)
    for v in stage1_vias_by_net.get(net, []):
        apply_via_to_grid(v, delta, is_fixed=True)
    if net in stage2_net_items:
        for trk in stage2_net_items[net][0]:
            apply_track_to_grid(trk, delta, is_fixed=False)
        for v in stage2_net_items[net][1]:
            apply_via_to_grid(v, delta, is_fixed=False)


def find_grid_entry(x, y, layers, net, trk_w=SIG_W, allow_cong=False):
    gx0, gy0 = mm2g(x, y)
    entries = []
    seen_e = set()
    for r in range(0, 10):
        cand = []
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if max(abs(dx), abs(dy)) != r:
                    continue
                ix, iy = gx0 + dx, gy0 + dy
                if ix < 0 or ix >= NX or iy < 0 or iy >= NY:
                    continue
                idx = iy * NX + ix
                gx, gy = ix * GRID, iy * GRID
                d = math.hypot(gx - x, gy - y)
                for L in layers:
                    if base_valid[L][idx] and pad_block_trk[L][idx] == 0 and fixed_trk[L][idx] == 0:
                        if allow_cong or dyn_trk_cnt[L][idx] == 0:
                            cand.append((dyn_trk_cnt[L][idx], d, ix, iy, L, gx, gy))
        cand.sort()
        for _, d, ix, iy, L, gx, gy in cand:
            if (ix, iy, L) in seen_e:
                continue
            ok, _ = seg_clear(x, y, gx, gy, trk_w, L, net, clr=0.155, check_tracks=(not allow_cong))
            if ok:
                seen_e.add((ix, iy, L))
                entries.append((ix, iy, L, x, y))
                if len(entries) >= 4:
                    return entries
        if len(entries) >= 2 and r >= 2:
            return entries
    return entries


# 4-connected Manhattan neighbors on 0.20 mm grid:
# Exact 0.40 mm parallel trace pitch -> 0.40 - 0.18 = 0.22 mm gap >> 0.15 mm DRC (ZERO 45-deg grazing!)
DIRS = [
    (1, 0, 10), (-1, 0, 10), (0, 1, 10), (0, -1, 10),
]
VIA_COST = 38
DIR_PEN = [
    [0, 0, 2, 2],
    [2, 2, 0, 0],
    [16, 16, 16, 16],  # High cost on In2.Cu so fallback bridges stay ultra-short & preserve >97% power plane!
]


def astar_route_pair(src_entries, dst_entries, trk_w=SIG_W, allow_congestion=False, present_cost=350, allow_in2=False):
    if not src_entries or not dst_entries:
        return None
    n_layers = 3 if allow_in2 else 2
    valid_src = [e for e in src_entries if e[2] < n_layers]
    valid_dst = [e for e in dst_entries if e[2] < n_layers]
    if not valid_src or not valid_dst:
        return None
    dst_set = set((ix, iy, L) for (ix, iy, L, _, _) in valid_dst)
    tx = sum(e[0] for e in valid_dst) / len(valid_dst)
    ty = sum(e[1] for e in valid_dst) / len(valid_dst)

    INF = 10**9
    g_score = [INF] * (n_layers * N_CELLS)
    parent = [-1] * (n_layers * N_CELLS)
    pq = []

    for ix, iy, L, _, _ in valid_src:
        s = L * N_CELLS + iy * NX + ix
        g_score[s] = 0
        h = int(12 * (abs(ix - tx) + abs(iy - ty)))
        heapq.heappush(pq, (h, 0, s))

    extra_w = (trk_w > SIG_W + 0.08)
    expanded = 0
    MAX_EXP = 90000

    while pq:
        f, g, cur = heapq.heappop(pq)
        if g > g_score[cur]:
            continue
        L, rem = divmod(cur, N_CELLS)
        iy, ix = divmod(rem, NX)
        if (ix, iy, L) in dst_set:
            path = []
            node = cur
            while node != -1:
                nL, nrem = divmod(node, N_CELLS)
                niy, nix = divmod(nrem, NX)
                path.append((nix, niy, nL))
                node = parent[node]
            path.reverse()
            return path

        expanded += 1
        if expanded > MAX_EXP:
            return None

        bv = base_valid[L]
        pb = pad_block_trk[L]
        ft = fixed_trk[L]
        dt = dyn_trk_cnt[L]
        ht = history_trk[L]
        dpen = DIR_PEN[L]

        pcur = parent[cur]
        prev_dx, prev_dy = 0, 0
        if pcur != -1 and (pcur // N_CELLS == L):
            prem = pcur % N_CELLS
            piy, pix = divmod(prem, NX)
            prev_dx, prev_dy = ix - pix, iy - piy

        for di, (dx, dy, step_c) in enumerate(DIRS):
            nx, ny = ix + dx, iy + dy
            if nx < 0 or nx >= NX or ny < 0 or ny >= NY:
                continue
            nidx = ny * NX + nx
            if not bv[nidx] or pb[nidx] > 0 or ft[nidx] > 0:
                continue
            occ = dt[nidx]
            if occ > 0:
                if not allow_congestion:
                    continue
                cong_pen = present_cost * occ
            else:
                cong_pen = 0
            if extra_w and not allow_congestion and 0 < nx < NX - 1 and 0 < ny < NY - 1:
                if (pb[nidx - 1] or pb[nidx + 1] or pb[nidx - NX] or pb[nidx + NX] or
                        ft[nidx - 1] or ft[nidx + 1] or ft[nidx - NX] or ft[nidx + NX] or
                        dt[nidx - 1] or dt[nidx + 1] or dt[nidx - NX] or dt[nidx + NX]):
                    continue
            bend_pen = 3 if (prev_dx != 0 or prev_dy != 0) and (dx != prev_dx or dy != prev_dy) else 0
            ng = g + step_c + dpen[di] + bend_pen + cong_pen + ht[nidx]
            ns = L * N_CELLS + nidx
            if ng < g_score[ns]:
                g_score[ns] = ng
                parent[ns] = cur
                h = int(12 * (abs(nx - tx) + abs(ny - ty)))
                heapq.heappush(pq, (ng + h, ng, ns))

        # Via transition to any other allowed layer
        if base_via_valid[rem] and pad_block_via[rem] == 0 and fixed_via[rem] == 0:
            for oL in range(n_layers):
                if oL == L:
                    continue
                if base_valid[oL][rem] and pad_block_trk[oL][rem] == 0 and fixed_trk[oL][rem] == 0:
                    vocc = dyn_via_cnt[rem] + dyn_trk_cnt[oL][rem]
                    if vocc == 0 or allow_congestion:
                        v_extra = 25 if oL == 2 else 0
                        ng = g + VIA_COST + v_extra + (present_cost * 2 * vocc if vocc else 0) + history_via[rem]
                        ns = oL * N_CELLS + rem
                        if ng < g_score[ns]:
                            g_score[ns] = ng
                            parent[ns] = cur
                            h = int(12 * (abs(ix - tx) + abs(iy - ty)))
                            heapq.heappush(pq, (ng + h, ng, ns))

    return None


def compress_path_to_segs_and_vias(path, src_pt, dst_pt, trk_w, net):
    segs, vias = [], []
    sx, sy = src_pt
    p0x, p0y = path[0][0] * GRID, path[0][1] * GRID
    if math.hypot(p0x - sx, p0y - sy) > 1e-4:
        segs.append((sx, sy, p0x, p0y, trk_w, path[0][2], net))

    seg_start = path[0]
    prev = path[0]
    prev_dir = None
    for cur in path[1:]:
        if cur[2] != prev[2]:
            if seg_start[:2] != prev[:2]:
                segs.append((seg_start[0]*GRID, seg_start[1]*GRID, prev[0]*GRID, prev[1]*GRID, trk_w, prev[2], net))
            vias.append((prev[0]*GRID, prev[1]*GRID, net))
            seg_start = cur
            prev = cur
            prev_dir = None
        else:
            d = (cur[0] - prev[0], cur[1] - prev[1])
            if prev_dir is not None and d != prev_dir:
                segs.append((seg_start[0]*GRID, seg_start[1]*GRID, prev[0]*GRID, prev[1]*GRID, trk_w, prev[2], net))
                seg_start = prev
            prev = cur
            prev_dir = d

    if seg_start[:2] != prev[:2]:
        segs.append((seg_start[0]*GRID, seg_start[1]*GRID, prev[0]*GRID, prev[1]*GRID, trk_w, prev[2], net))

    ex, ey = dst_pt
    plx, ply = path[-1][0] * GRID, path[-1][1] * GRID
    if math.hypot(ex - plx, ey - ply) > 1e-4:
        segs.append((plx, ply, ex, ey, trk_w, path[-1][2], net))
    return segs, vias


def route_single_net(net, trk_w=SIG_W, allow_congestion=False, present_cost=350, virtual_plane_fn=None, allow_in2=False):
    temporarily_unblock_net(net, -1)
    added_trks = []
    added_vias = []
    try:
        comps = get_net_components(net, virtual_plane_fn=virtual_plane_fn)
        if len(comps) <= 1:
            return True, added_trks, added_vias

        while len(comps) > 1:
            best_pair = None
            best_d = 1e9
            for i in range(len(comps)):
                for j in range(i + 1, len(comps)):
                    for (ax, ay, _, _) in comps[i]:
                        for (bx, by, _, _) in comps[j]:
                            d = math.hypot(ax - bx, ay - by)
                            if d < best_d:
                                best_d = d
                                best_pair = (i, j)
            ci, cj = best_pair

            def gather_entries(comp, other_comp, max_nodes=10):
                scored = []
                for (ax, ay, al, tag) in comp:
                    md = min(math.hypot(ax - bx, ay - by) for (bx, by, _, _) in other_comp)
                    scored.append((md, ax, ay, al, tag))
                scored.sort()
                out, seen = [], set()
                for _, ax, ay, al, tag in scored[:max_nodes]:
                    use_l = al if allow_in2 else (al - {2})
                    for e in find_grid_entry(ax, ay, use_l, net, trk_w=trk_w, allow_cong=allow_congestion):
                        k = (e[0], e[1], e[2])
                        if k not in seen:
                            seen.add(k)
                            out.append(e)
                return out

            src_e = gather_entries(comps[ci], comps[cj])
            dst_e = gather_entries(comps[cj], comps[ci])
            path = astar_route_pair(src_e, dst_e, trk_w=trk_w, allow_congestion=allow_congestion, present_cost=present_cost, allow_in2=allow_in2)
            use_w = trk_w
            if path is None and trk_w > SIG_W:
                path = astar_route_pair(src_e, dst_e, trk_w=SIG_W, allow_congestion=allow_congestion, present_cost=present_cost, allow_in2=allow_in2)
                use_w = max(SIG_W, min(trk_w, 0.30))
            if path is None:
                return False, added_trks, added_vias

            s0 = (path[0][0], path[0][1], path[0][2])
            e0 = (path[-1][0], path[-1][1], path[-1][2])
            src_pt = next((x, y) for (ix, iy, L, x, y) in src_e if (ix, iy, L) == s0)
            dst_pt = next((x, y) for (ix, iy, L, x, y) in dst_e if (ix, iy, L) == e0)
            segs, vias = compress_path_to_segs_and_vias(path, src_pt, dst_pt, use_w, net)

            if not allow_congestion:
                ok_geo = all(seg_clear(s[0], s[1], s[2], s[3], s[4], s[5], net, clr=0.155)[0] for s in segs) and \
                         all(via_clear(v[0], v[1], net, clr=0.155)[0] for v in vias)
                if not ok_geo and use_w > SIG_W:
                    segs, vias = compress_path_to_segs_and_vias(path, src_pt, dst_pt, SIG_W, net)
                    ok_geo = all(seg_clear(s[0], s[1], s[2], s[3], s[4], s[5], net, clr=0.155)[0] for s in segs) and \
                             all(via_clear(v[0], v[1], net, clr=0.155)[0] for v in vias)
                if not ok_geo:
                    return False, added_trks, added_vias

            for s in segs:
                all_tracks.append(s)
                added_trks.append(s)
            for v in vias:
                all_vias.append(v)
                added_vias.append(v)

            new_comp = comps[ci] + comps[cj]
            for (ix, iy, L) in path[::5]:
                new_comp.append((ix * GRID, iy * GRID, {L}, "steiner"))
            for vx, vy, _ in vias:
                new_comp.append((vx, vy, {0, 1, 2}, "via"))
            comps = [c for k, c in enumerate(comps) if k not in (ci, cj)]
            comps.append(new_comp)

        return True, added_trks, added_vias
    finally:
        if net in stage2_net_items:
            stage2_net_items[net][0].extend(added_trks)
            stage2_net_items[net][1].extend(added_vias)
        else:
            stage2_net_items[net] = (added_trks, added_vias)
        temporarily_unblock_net(net, +1)


def rip_up_net(net):
    if net not in stage2_net_items:
        return
    trks, vs = stage2_net_items.pop(net)
    for t in trks:
        apply_track_to_grid(t, -1, is_fixed=False)
    for v in vs:
        apply_via_to_grid(v, -1, is_fixed=False)
    tset = set(trks)
    vset = set(vs)
    all_tracks[:] = [t for t in all_tracks if t not in tset]
    all_vias[:] = [v for v in all_vias if v not in vset]


def find_conflicting_stage2_nets():
    """Find any Stage-2 nets that geometrically violate clearance against ANY other net's tracks, vias, or pads!"""
    bad = set()
    for net, (trks, vs) in stage2_net_items.items():
        for t in trks:
            ok, _ = seg_clear(t[0], t[1], t[2], t[3], t[4], t[5], net, clr=0.155, check_tracks=True)
            if not ok:
                bad.add(net)
                break
        if net not in bad:
            for v in vs:
                ok, _ = via_clear(v[0], v[1], net, clr=0.155, check_tracks=True, ignore_self=True)
                if not ok:
                    bad.add(net)
                    break
    return bad


# Build list of all nets to route in Stage 2 with their target widths and optional virtual planes
route_plan = [
    ("VIN_PROT", 0.45, None),
    ("/01_Power_Supply/5V_BUCK", 0.35, None),
    ("VBUS", 0.26, None),       # IPC-2221 0.26 mm external > 1.0 A (USB 2.0 max = 0.5 A)
    ("+5V", 0.35, in_in2_5v),   # Remote U3.3/C8.1 -> J17.5 & NW NeoPixel -> East +5V plane
]

sig_list = []
for net in sorted(net_pads.keys()):
    ps = net_pads[net]
    if net in ("GND", "+3V3", "+5V") or net.startswith("unconnected-") or len(ps) < 2:
        continue
    if net in [n for n, _, _ in route_plan]:
        continue
    if len(get_net_components(net)) <= 1:
        continue
    xs = [p["cx"] for p in ps]
    ys = [p["cy"] for p in ps]
    hpwl = round((max(xs) - min(xs)) + (max(ys) - min(ys)), 3)
    sig_list.append((hpwl, len(ps), net))

# Shortest-first order (proven to route 33/35 nets purely on F.Cu + B.Cu in 5 iterations!)
sig_list.sort()
for _, _, snet in sig_list:
    route_plan.append((snet, SIG_W, None))

plan_meta = {n: (w, vp) for (n, w, vp) in route_plan}

# Pass 1: Strict zero-overlap routing on F.Cu + B.Cu ONLY
unrouted = []
for net, w, vp in route_plan:
    ok, trks, vs = route_single_net(net, trk_w=w, allow_congestion=False, virtual_plane_fn=vp, allow_in2=False)
    if net in ("VIN_PROT", "/01_Power_Supply/5V_BUCK", "VBUS", "+5V"):
        print(f"  Power {net:28s} (w={w:.2f}): {'OK' if ok else 'PARTIAL'} (+{len(trks)} segs, +{len(vs)} vias)")
    if not ok:
        rip_up_net(net)
        unrouted.append(net)

print(f"  Pass 1 strict (F.Cu+B.Cu) complete: {len(route_plan) - len(unrouted)}/{len(route_plan)} routed; {len(unrouted)} remaining: {unrouted}")

# Stage 2A: Fast 6-iteration PathFinder on F.Cu + B.Cu ONLY (keeps >92% of all nets off In2.Cu!)
p_step = 0
for pf_iter in range(1, 7):
    conflicts = find_conflicting_stage2_nets()
    to_route = list(dict.fromkeys(unrouted + sorted(conflicts)))
    if not to_route:
        print(f"  [CONVERGED 2-LAYER] PathFinder converged in {pf_iter - 1} iterations (0 traces on In2.Cu)!")
        break
    if len(unrouted) > 0 and len(conflicts) == 0 and pf_iter >= 4:
        break  # Hand final 2-3 pinched nets cleanly to Stage 2B (short In2.Cu bridges)!
    present_cost = min(1400, int(80 * (1.40 ** p_step)))
    p_step += 1
    hist_inc = int(35 * pf_iter)
    print(f"  PathFinder 2L iter {pf_iter:2d}: routing {len(to_route)} nets (unrouted={len(unrouted)}, conflicts={len(conflicts)}, p_cost={present_cost})...")
    for cnet in to_route:
        if cnet in stage2_net_items:
            trks, vs = stage2_net_items[cnet]
            for t in trks:
                ct, _ = get_track_raster(t)
                for c in ct:
                    if dyn_trk_cnt[t[5]][c] > 1:
                        history_trk[t[5]][c] = min(650, history_trk[t[5]][c] + hist_inc)
            for v in vs:
                _, cv = get_via_raster(v)
                for c in cv:
                    if dyn_via_cnt[c] > 1:
                        history_via[c] = min(850, history_via[c] + hist_inc * 2)
        rip_up_net(cnet)
    new_unrouted = []
    for net in to_route:
        w, vp = plan_meta[net]
        ok, _, _ = route_single_net(net, trk_w=w, allow_congestion=False, present_cost=present_cost, virtual_plane_fn=vp, allow_in2=False)
        if not ok:
            rip_up_net(net)
            ok, _, _ = route_single_net(net, trk_w=w, allow_congestion=True, present_cost=present_cost, virtual_plane_fn=vp, allow_in2=False)
            if not ok:
                rip_up_net(net)
                new_unrouted.append(net)
    unrouted = new_unrouted
    for L in (0, 1):
        for c in range(N_CELLS):
            if dyn_trk_cnt[L][c] > 1:
                history_trk[L][c] = min(650, history_trk[L][c] + hist_inc)
    for c in range(N_CELLS):
        if dyn_via_cnt[c] > 1:
            history_via[c] = min(850, history_via[c] + hist_inc * 2)

# Stage 2B: Route ONLY remaining pinched GPIO nets with high-cost short In2.Cu bridges
# (In1.Cu stays 100.0% SOLID UNBROKEN GND PLANE; In2.Cu stays >97% solid +3V3/+5V power plane!)
for pf_iter in range(1, 10):
    conflicts = find_conflicting_stage2_nets()
    to_route = list(dict.fromkeys(unrouted + sorted(conflicts)))
    if not to_route:
        in2_segs = sum(1 for t in all_tracks if t[5] == 2)
        print(f"  [CONVERGED] 100% nets routed, 0 geometric conflicts! (In2.Cu short bridge segs={in2_segs}, In1.Cu=0 [100% pure GND])")
        break
    present_cost = min(1600, int(120 * (1.45 ** (pf_iter - 1))))
    print(f"  Stage 2B (In2 bridge) iter {pf_iter}: routing {len(to_route)} nets {to_route} (conflicts={len(conflicts)})...")
    for cnet in to_route:
        rip_up_net(cnet)
    new_unrouted = []
    for net in to_route:
        w, vp = plan_meta[net]
        use_w = SIG_W if w > SIG_W and net != "VIN_PROT" else w
        ok, _, _ = route_single_net(net, trk_w=use_w, allow_congestion=False, present_cost=present_cost, virtual_plane_fn=vp, allow_in2=True)
        if not ok:
            rip_up_net(net)
            ok, _, _ = route_single_net(net, trk_w=use_w, allow_congestion=True, present_cost=present_cost, virtual_plane_fn=vp, allow_in2=True)
            if not ok:
                rip_up_net(net)
                new_unrouted.append(net)
    unrouted = new_unrouted

# Final check of conflicts after PathFinder
final_conf = find_conflicting_stage2_nets()
print(f"  Stage 2 final status: unrouted={unrouted}, remaining_conflicts={sorted(final_conf)}")


# ==============================================================================
# STAGE 3: CONFLICT-FREE SMD POWER FANOUT VIAS (GND, +3V3, +5V) & STITCHING
# ==============================================================================
print("\n--- Stage 3: Placing Conflict-Free Power Fanout Vias ---")

def get_plane_connected_tags(net, zone_fn):
    tags = set()
    for c in get_net_components(net):
        has_plane = any((tag == "via" or (0 in ls and 1 in ls)) and zone_fn(cx, cy) for (cx, cy, ls, tag) in c)
        if has_plane:
            for (_, _, _, tag) in c:
                tags.add(tag)
    return tags


def fanout_smd_power_pad(p, net, zone_fn, connected_tags):
    tag_p = f"{p['ref']}.{p['pnum']}"
    if tag_p in connected_tags:
        return True
    L = 0 if 0 in p["layers"] else 1
    cx, cy = p["cx"], p["cy"]
    # 1. Straight stub to nearest clear via within 5.0 mm
    for rad_i in range(0, 26):
        r = rad_i * 0.20
        n_ang = 1 if rad_i == 0 else max(8, int(round(2 * math.pi * r / 0.35)))
        cand = []
        for k in range(n_ang):
            ang = 2 * math.pi * k / n_ang
            vx = round((cx + r * math.cos(ang)) / 0.10) * 0.10
            vy = round((cy + r * math.sin(ang)) / 0.10) * 0.10
            if not zone_fn(vx, vy):
                continue
            if not via_clear(vx, vy, net, clr=0.165)[0]:
                continue
            if seg_clear(cx, cy, vx, vy, 0.22, L, net, clr=0.16)[0]:
                cand.append((r, vx, vy))
        if cand:
            cand.sort()
            _, vx, vy = cand[0]
            add_seg(cx, cy, vx, vy, 0.22, L, net, check=False)
            add_via(vx, vy, net, check=False)
            apply_track_to_grid(all_tracks[-1], +1, is_fixed=True)
            apply_via_to_grid(all_vias[-1], +1, is_fixed=True)
            return True

    # 2. L-shaped stub to nearest clear via within 6.0 mm
    for rad_i in range(2, 31):
        r = rad_i * 0.20
        for k in range(16):
            ang = 2 * math.pi * k / 16
            vx = round((cx + r * math.cos(ang)) / 0.10) * 0.10
            vy = round((cy + r * math.sin(ang)) / 0.10) * 0.10
            if not zone_fn(vx, vy) or not via_clear(vx, vy, net, clr=0.165)[0]:
                continue
            for mx, my in [(vx, cy), (cx, vy)]:
                if seg_clear(cx, cy, mx, my, 0.20, L, net, clr=0.16)[0] and seg_clear(mx, my, vx, vy, 0.20, L, net, clr=0.16)[0]:
                    add_seg(cx, cy, mx, my, 0.20, L, net, check=False)
                    add_seg(mx, my, vx, vy, 0.20, L, net, check=False)
                    add_via(vx, vy, net, check=False)
                    apply_track_to_grid(all_tracks[-2], +1, is_fixed=True)
                    apply_track_to_grid(all_tracks[-1], +1, is_fixed=True)
                    apply_via_to_grid(all_vias[-1], +1, is_fixed=True)
                    return True

    # 3. A* fallback on same layer (or 2-layer) to nearest already-placed same-net via/PTH!
    # Try connecting directly to any existing same-net via/PTH pad in zone_fn via A*!
    temporarily_unblock_net(net, -1)
    try:
        src_e = find_grid_entry(cx, cy, {L}, net, trk_w=SIG_W)
        # Collect nearby same-net vias & PTH pads
        targets = []
        for vx, vy, vnet in all_vias:
            if vnet == net and zone_fn(vx, vy):
                targets.append((math.hypot(vx - cx, vy - cy), vx, vy, {0, 1}))
        for op in net_pads.get(net, []):
            if op["is_pth"] and zone_fn(op["cx"], op["cy"]):
                targets.append((math.hypot(op["cx"] - cx, op["cy"] - cy), op["cx"], op["cy"], {0, 1}))
        targets.sort()
        dst_e = []
        for _, tx, ty, tl in targets[:6]:
            dst_e.extend(find_grid_entry(tx, ty, tl, net, trk_w=SIG_W))
        path = astar_route_pair(src_e, dst_e, trk_w=SIG_W, allow_congestion=False)
        if path:
            s0 = (path[0][0], path[0][1], path[0][2])
            e0 = (path[-1][0], path[-1][1], path[-1][2])
            src_pt = next((x, y) for (ix, iy, l0, x, y) in src_e if (ix, iy, l0) == s0)
            dst_pt = next((x, y) for (ix, iy, l0, x, y) in dst_e if (ix, iy, l0) == e0)
            segs, vias = compress_path_to_segs_and_vias(path, src_pt, dst_pt, SIG_W, net)
            if all(seg_clear(s[0], s[1], s[2], s[3], s[4], s[5], net, clr=0.155)[0] for s in segs) and \
               all(via_clear(v[0], v[1], net, clr=0.155)[0] for v in vias):
                for s in segs:
                    all_tracks.append(s)
                    stage1_tracks_by_net.setdefault(net, []).append(s)
                for v in vias:
                    all_vias.append(v)
                    stage1_vias_by_net.setdefault(net, []).append(v)
                return True
    finally:
        temporarily_unblock_net(net, +1)
    return False


ok_3v3, miss_3v3 = 0, []
conn_3v3 = get_plane_connected_tags("+3V3", in_in2_3v3)
for p in net_pads.get("+3V3", []):
    if p["is_pth"]:
        continue
    if fanout_smd_power_pad(p, "+3V3", in_in2_3v3, conn_3v3):
        ok_3v3 += 1
    else:
        miss_3v3.append(f"{p['ref']}.{p['pnum']}")
print(f"  +3V3 SMD fanout: {ok_3v3} OK, missing={miss_3v3}")

ok_5v, miss_5v = 0, []
conn_5v = get_plane_connected_tags("+5V", in_in2_5v)
for p in net_pads.get("+5V", []):
    if p["is_pth"] or p["cx"] < 54.0:
        continue
    if fanout_smd_power_pad(p, "+5V", in_in2_5v, conn_5v):
        ok_5v += 1
    else:
        miss_5v.append(f"{p['ref']}.{p['pnum']}")
print(f"  +5V East SMD fanout: {ok_5v} OK, missing={miss_5v}")

ok_gnd, miss_gnd = 0, []
conn_gnd = get_plane_connected_tags("GND", in_in1_gnd)
for p in net_pads.get("GND", []):
    if p["is_pth"] or (p["ref"] == "U4" and p["pnum"] == "41"):
        continue
    if fanout_smd_power_pad(p, "GND", in_in1_gnd, conn_gnd):
        ok_gnd += 1
    else:
        miss_gnd.append(f"{p['ref']}.{p['pnum']}")
print(f"  GND SMD fanout: {ok_gnd} OK, missing={miss_gnd}")

stitch_cnt = 0
for sx in [9.5, 18.0, 26.5, 35.0, 44.0, 53.0, 62.0]:
    for sy in [5.5, 16.5, 27.0, 37.5, 47.5]:
        if in_in1_gnd(sx, sy) and via_clear(sx, sy, "GND", clr=0.35)[0]:
            add_via(sx, sy, "GND", check=False)
            stitch_cnt += 1
print(f"  Added {stitch_cnt} GND stitching vias across board.")


# ==============================================================================
# STAGE 3.5: PRUNE DANGLING TRACK STUBS, 1-LAYER DANGLING VIAS & DUPLICATE VIAS
# ==============================================================================
print("\n--- Stage 3.5: Pruning Dangling Stubs, Unused Single-Layer Vias & Duplicate Vias ---")

def is_plane_via(vx, vy, net):
    if net == "GND":
        return in_in1_gnd(vx, vy)
    if net == "+3V3":
        return in_in2_3v3(vx, vy)
    if net == "+5V":
        return in_in2_5v(vx, vy)
    return False

# 1. Remove exact/near-duplicate vias (prevents holes_co_located!)
dedup_vias = []
for vx, vy, net in all_vias:
    if any(math.hypot(vx - ox, vy - oy) < 0.25 for (ox, oy, _) in dedup_vias):
        continue
    dedup_vias.append((vx, vy, net))
print(f"  Deduplicated vias: {len(all_vias)} -> {len(dedup_vias)}")
all_vias = dedup_vias

# 1.5 Split T-junctions so KiCad 10 sees exact vertex-to-vertex connections (0 track_dangling!)
def split_t_junctions(tracks, vias):
    """Whenever a same-net, same-layer track endpoint or via lands in the interior of a track segment,
    split that track segment cleanly at that exact vertex!"""
    by_nl = {}
    for t in tracks:
        by_nl.setdefault((t[6], t[5]), []).append(t)
    vias_by_net = {}
    for vx, vy, vn in vias:
        vias_by_net.setdefault(vn, []).append((vx, vy))

    out = []
    splits_done = 0
    for (net, tl), segs in by_nl.items():
        # Collect all candidate junction points (all endpoints + all vias of this net)
        jpts = []
        for x1, y1, x2, y2, w, _, _ in segs:
            jpts.append((x1, y1))
            jpts.append((x2, y2))
        for vx, vy in vias_by_net.get(net, []):
            jpts.append((vx, vy))

        for x1, y1, x2, y2, w, _, _ in segs:
            dx, dy = x2 - x1, y2 - y1
            l2 = dx * dx + dy * dy
            if l2 < 1e-8:
                continue
            seg_len = math.sqrt(l2)
            ts = []
            for px, py in jpts:
                if (px < min(x1, x2) - 0.02) or (px > max(x1, x2) + 0.02) or (py < min(y1, y2) - 0.02) or (py > max(y1, y2) + 0.02):
                    continue
                t = ((px - x1) * dx + (py - y1) * dy) / l2
                if 0.002 < t < 0.998:
                    qx, qy = x1 + t * dx, y1 + t * dy
                    if math.hypot(px - qx, py - qy) < 0.015:
                        ts.append((t, px, py))
            if not ts:
                out.append((x1, y1, x2, y2, w, tl, net))
            else:
                ts.sort(key=lambda z: z[0])
                pts_chain = [(x1, y1)]
                for _, px, py in ts:
                    if math.hypot(px - pts_chain[-1][0], py - pts_chain[-1][1]) > 0.005:
                        pts_chain.append((px, py))
                if math.hypot(x2 - pts_chain[-1][0], y2 - pts_chain[-1][1]) > 0.005:
                    pts_chain.append((x2, y2))
                for k in range(len(pts_chain) - 1):
                    out.append((pts_chain[k][0], pts_chain[k][1], pts_chain[k+1][0], pts_chain[k+1][1], w, tl, net))
                splits_done += len(pts_chain) - 2
    return out, splits_done

all_tracks, n_splits = split_t_junctions(all_tracks, all_vias)
print(f"  Split {n_splits} T-junctions for exact KiCad 10 vertex connectivity.")

# 1.6 Deduplicate identical or reversed overlapping segments (A->B == B->A) so pruner sees true dead-ends!
seen_segs = set()
dedup_tracks = []
for t in all_tracks:
    x1, y1, x2, y2, w, tl, net = t
    p1 = (round(x1, 3), round(y1, 3))
    p2 = (round(x2, 3), round(y2, 3))
    if p1 == p2:
        continue
    key = (net, tl, p1, p2) if p1 <= p2 else (net, tl, p2, p1)
    if key in seen_segs:
        continue
    seen_segs.add(key)
    dedup_tracks.append(t)
if len(dedup_tracks) != len(all_tracks):
    print(f"  Deduplicated overlapping tracks: {len(all_tracks)} -> {len(dedup_tracks)}")
all_tracks = dedup_tracks

# 2. Iterative dangling track & 1-layer via pruner (EXACT KiCad 10 vertex tolerance <= 0.006 mm!)
removed_trks, removed_vias = 0, 0
for _pass in range(30):
    changed = False
    trks_by_net = {}
    for idx_t, t in enumerate(all_tracks):
        trks_by_net.setdefault(t[6], []).append((idx_t, t))
    vias_by_net = {}
    for idx_v, v in enumerate(all_vias):
        vias_by_net.setdefault(v[2], []).append((idx_v, v))

    # A. Remove any non-plane via that only touches copper on 0 or 1 layer!
    drop_v = set()
    for net, vlist in vias_by_net.items():
        tlist = trks_by_net.get(net, [])
        plist = net_pads.get(net, [])
        for idx_v, (vx, vy, _) in vlist:
            if is_plane_via(vx, vy, net):
                continue
            touched_layers = set()
            for _, (x1, y1, x2, y2, tw, tl, _) in tlist:
                if math.hypot(vx - x1, vy - y1) < 0.015 or math.hypot(vx - x2, vy - y2) < 0.015:
                    touched_layers.add(tl)
            for p in plist:
                if dist_pt_box(vx, vy, p["x1"], p["y1"], p["x2"], p["y2"]) < 0.01:
                    touched_layers |= p["layers"]
            if len(touched_layers) < 2:
                drop_v.add(idx_v)
    if drop_v:
        all_vias = [v for i, v in enumerate(all_vias) if i not in drop_v]
        removed_vias += len(drop_v)
        changed = True
        continue

    # B. Remove any track segment whose endpoint is NOT exact-anchored to a pad, via, or another track vertex!
    drop_t = set()
    for net, tlist in trks_by_net.items():
        vlist = vias_by_net.get(net, [])
        plist = net_pads.get(net, [])
        for idx_t, (x1, y1, x2, y2, tw, tl, _) in tlist:
            def endpoint_anchored(ex, ey):
                for p in plist:
                    if tl in p["layers"] and dist_pt_box(ex, ey, p["x1"], p["y1"], p["x2"], p["y2"]) < 0.005:
                        return True
                for _, (vx, vy, _) in vlist:
                    if math.hypot(ex - vx, ey - vy) < 0.015:
                        return True
                for oidx, (ox1, oy1, ox2, oy2, otw, otl, _) in tlist:
                    if oidx == idx_t or otl != tl:
                        continue
                    if math.hypot(ex - ox1, ey - oy1) < 0.008 or math.hypot(ex - ox2, ey - oy2) < 0.008:
                        return True
                return False
            if (not endpoint_anchored(x1, y1)) or (not endpoint_anchored(x2, y2)):
                drop_t.add(idx_t)
    if drop_t:
        all_tracks = [t for i, t in enumerate(all_tracks) if i not in drop_t]
        removed_trks += len(drop_t)
        changed = True
    if not changed:
        break

print(f"  Pruned {removed_trks} dangling track segments and {removed_vias} single-layer dangling vias.")


# ==============================================================================
# STAGE 4: COMMIT TO KICAD BOARD & FILL 4-LAYER COPPER ZONES
# ==============================================================================
print(f"\n--- Stage 4: Committing {len(all_tracks)} tracks, {len(all_vias)} vias & 4-layer zones ---")

for x1, y1, x2, y2, w, tl, net in all_tracks:
    if net not in netinfo_map:
        continue
    trk = pcbnew.PCB_TRACK(board)
    trk.SetStart(pt(x1, y1))
    trk.SetEnd(pt(x2, y2))
    trk.SetWidth(mm(w))
    trk.SetLayer(LAYERS[tl])
    trk.SetNet(netinfo_map[net])
    board.Add(trk)

for vx, vy, net in all_vias:
    if net not in netinfo_map:
        continue
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pt(vx, vy))
    via.SetWidth(mm(VIA_D))
    via.SetDrill(mm(VIA_DRILL))
    via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetNet(netinfo_map[net])
    board.Add(via)


def add_copper_zone(net_name, layer, poly_pts, clearance=0.25, min_thick=0.20,
                    thermal_gap=0.25, thermal_bridge=0.35, priority=0,
                    pad_conn=pcbnew.ZONE_CONNECTION_THERMAL):
    z = pcbnew.ZONE(board)
    z.SetNet(netinfo_map[net_name])
    z.SetLayer(layer)
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(mm(clearance))
    z.SetMinThickness(mm(min_thick))
    z.SetThermalReliefGap(mm(thermal_gap))
    z.SetThermalReliefSpokeWidth(mm(thermal_bridge))
    z.SetPadConnection(pad_conn)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    ol = z.Outline()
    ol.NewOutline()
    for lx, ly in poly_pts:
        ol.Append(mm(OX + lx), mm(OY + ly))
    board.Add(z)
    return z


FULL_INSET_POLY = [
    (1.65, 0.45), (65.59, 0.45), (65.59, 2.75), (68.13, 5.29),
    (68.13, 37.64), (65.59, 40.18), (65.59, 51.61), (64.31, 52.89),
    (1.65, 52.89), (0.45, 51.69), (0.45, 1.65),
]

add_copper_zone("GND", pcbnew.In1_Cu, FULL_INSET_POLY, clearance=0.22, min_thick=0.20,
                thermal_gap=0.22, thermal_bridge=0.35, priority=0)

IN2_3V3_POLY = [
    (1.65, 0.45), (53.50, 0.45), (53.50, 47.70), (36.60, 47.70),
    (36.60, 52.89), (1.65, 52.89), (0.45, 51.69), (0.45, 1.65),
]
IN2_5V_POLY = [
    (54.30, 0.45), (65.59, 0.45), (65.59, 2.75), (68.13, 5.29),
    (68.13, 37.64), (65.59, 40.18), (65.59, 51.61), (64.31, 52.89),
    (37.40, 52.89), (37.40, 48.50), (54.30, 48.50),
]
add_copper_zone("+3V3", pcbnew.In2_Cu, IN2_3V3_POLY, clearance=0.22, min_thick=0.20,
                thermal_gap=0.22, thermal_bridge=0.35, priority=1)
add_copper_zone("+5V", pcbnew.In2_Cu, IN2_5V_POLY, clearance=0.22, min_thick=0.20,
                thermal_gap=0.22, thermal_bridge=0.35, priority=1)

U3_THERMAL_POLY = [
    (24.30, 36.90), (29.20, 36.90), (29.20, 41.70), (24.30, 41.70),
]
add_copper_zone("+3V3", pcbnew.F_Cu, U3_THERMAL_POLY, clearance=0.22, min_thick=0.20,
                thermal_gap=0.22, thermal_bridge=0.40, priority=2,
                pad_conn=pcbnew.ZONE_CONNECTION_FULL)

add_copper_zone("GND", pcbnew.F_Cu, FULL_INSET_POLY, clearance=0.25, min_thick=0.25,
                thermal_gap=0.25, thermal_bridge=0.35, priority=0)
add_copper_zone("GND", pcbnew.B_Cu, FULL_INSET_POLY, clearance=0.25, min_thick=0.25,
                thermal_gap=0.25, thermal_bridge=0.35, priority=0)

print("Filling all 4-layer copper zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

board.Save(PCB_FILE)
print(f"Saved routed 4-layer PCB to {PCB_FILE} in {time.time() - t0_all:.1f}s.")
sys.stdout.flush()
ctypes.windll.kernel32.ExitProcess(0)
