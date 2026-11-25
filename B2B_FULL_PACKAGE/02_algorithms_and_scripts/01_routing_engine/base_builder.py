"""
Module to generate the baseline 52x75mm compact board with 4-layer copper zones and Step 1 fanouts.
Runs in < 0.1s without redundant DRC.
"""
import uuid, re
from tune_drc import BAK_FILE
from perfect_targets import PERFECT_TARGETS
from router_engine import get_pad, seg, via

def build_base_board():
    with open(BAK_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.splitlines(True)
    tracks_start = len(lines)
    for idx, l in enumerate(lines):
        if l.startswith("\t(segment") or l.startswith("\t(via") or l.startswith("\t(arc") or l.startswith("\t(zone"):
            tracks_start = idx
            break
    base_text = "".join(lines[:tracks_start])

    def fix_jbnc_pads(txt):
        def repl_bnc(m):
            blk = m.group(0)
            blk = re.sub(r'\(pad\s+"2"\s+thru_hole\s+oval\s+\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(size\s+3\.5\s+7\)',
                         r'(pad "2" thru_hole circle (at \1 \2 \3) (size 3.2 3.2)', blk)
            return blk
        return re.sub(r'\t\(footprint\s+"[^\"]+".*?\(property\s+"Reference"\s+"J_BNC".*?\n\t\)', repl_bnc, txt, flags=re.DOTALL)

    clean_base = fix_jbnc_pads(base_text)

    def remove_sexp_blocks(txt, tag_prefix):
        result = []
        idx = 0
        n = len(txt)
        while idx < n:
            if txt.startswith(tag_prefix, idx):
                j = idx + txt[idx:].index("(")
                depth = 1
                j += 1
                in_quote = False
                while j < n and depth > 0:
                    char = txt[j]
                    if char == '"' and txt[j-1] != '\\':
                        in_quote = not in_quote
                    elif not in_quote:
                        if char == '(': depth += 1
                        elif char == ')': depth -= 1
                    j += 1
                while j < n and txt[j] in ('\r', '\n'):
                    j += 1
                idx = j
            else:
                result.append(txt[idx])
                idx += 1
        return "".join(result)

    clean_base = remove_sexp_blocks(clean_base, "\t(gr_line")

    targets = dict(PERFECT_TARGETS)
    targets['C_PH_FILT'] = (85.0, 113.0, 0.0)
    targets['FB1'] = (80.5, 114.5, 0.0)
    targets['C_U9_VCC'] = (90.8, 113.0, 90.0)
    targets['RV1'] = (100.2, 114.0, 0.0)

    def repl_fp(m):
        full_block = m.group(0)
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', full_block)
        if not ref_m: return full_block
        ref = ref_m.group(1)
        if ref not in targets: return full_block

        tgt = targets[ref]
        nx, ny = tgt[0], tgt[1]
        nrot = tgt[2] if len(tgt) > 2 else None

        def repl_at(at_m):
            rot_str = f" {nrot:.1f}" if nrot is not None else (f" {at_m.group(3)}" if at_m.group(3) else "")
            return f"(at {nx:.4f} {ny:.4f}{rot_str})"

        return re.sub(r'\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)(?:\s+([0-9\.\-]+))?\)', repl_at, full_block, count=1)

    fp_base = re.sub(r'\(footprint\s+"[^"]+".*?\n\t\)', repl_fp, clean_base, flags=re.DOTALL)

    edge_cuts = """\t(gr_line (start 73 55) (end 75 53) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-01"))
\t(gr_line (start 75 53) (end 123 53) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-02"))
\t(gr_line (start 123 53) (end 125 55) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-03"))
\t(gr_line (start 125 55) (end 125 126) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-04"))
\t(gr_line (start 125 126) (end 123 128) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-05"))
\t(gr_line (start 123 128) (end 75 128) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-06"))
\t(gr_line (start 75 128) (end 73 126) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-07"))
\t(gr_line (start 73 126) (end 73 55) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-08"))
"""

    def make_zone(net_name, layer, pts):
        uid = str(uuid.uuid4())
        pts_str = " ".join([f"(xy {x} {y})" for x, y in pts])
        return f"""\t(zone
\t\t(net "{net_name}")
\t\t(layer "{layer}")
\t\t(uuid "{uid}")
\t\t(hatch edge 0.5)
\t\t(connect_pads
\t\t\t(clearance 0.25)
\t\t)
\t\t(min_thickness 0.25)
\t\t(fill yes
\t\t\t(thermal_gap 0.25)
\t\t\t(thermal_bridge_width 0.35)
\t\t\t(island_removal_mode 0)
\t\t)
\t\t(polygon
\t\t\t(pts
\t\t\t\t{pts_str}
\t\t\t)
\t\t)
\t)
"""

    def make_keepout(pts):
        uid = str(uuid.uuid4())
        pts_str = " ".join([f"(xy {x} {y})" for x, y in pts])
        return f"""\t(zone
\t\t(layers "F.Cu" "B.Cu" "In1.Cu" "In2.Cu")
\t\t(uuid "{uid}")
\t\t(hatch full 0.508)
\t\t(connect_pads
\t\t\t(clearance 0)
\t\t)
\t\t(min_thickness 0.254)
\t\t(keepout
\t\t\t(tracks not_allowed)
\t\t\t(vias not_allowed)
\t\t\t(copperpour not_allowed)
\t\t)
\t\t(fill
\t\t\t(thermal_gap 0.508)
\t\t\t(thermal_bridge_width 0.508)
\t\t\t(island_removal_mode 0)
\t\t)
\t\t(polygon
\t\t\t(pts
\t\t\t\t{pts_str}
\t\t\t)
\t\t)
\t)
"""

    zones_text = ""
    zones_text += make_keepout([(89.0, 53.0), (111.0, 53.0), (111.0, 56.0), (89.0, 56.0)])
    full_outline = [(73.0, 53.0), (125.0, 53.0), (125.0, 128.0), (73.0, 128.0)]
    zones_text += make_zone("GND", "F.Cu", full_outline)
    zones_text += make_zone("GND", "B.Cu", full_outline)
    zones_text += make_zone("GND", "In1.Cu", full_outline)
    zones_text += make_zone("+3V3", "In2.Cu", full_outline)

    routes = ""

    # 1. +3V3 FANOUT VIAS
    p_u6_2 = get_pad('+3V3', 'U6', '2')
    routes += seg(p_u6_2['x'], p_u6_2['y'], 89.8, p_u6_2['y'], "F.Cu", "+3V3", 0.30)
    routes += via(89.8, p_u6_2['y'], "+3V3")

    p_mb = get_pad('+3V3', 'C_MCU_BULK', '1')
    p_ren = get_pad('+3V3', 'R_EN', '2')
    routes += seg(p_ren['x'], p_ren['y'], p_mb['x'], p_mb['y'], "F.Cu", "+3V3", 0.25)
    routes += seg(p_mb['x'], p_mb['y'], 84.2, 75.0, "F.Cu", "+3V3", 0.25)
    routes += via(84.2, 75.0, "+3V3")

    p_md = get_pad('+3V3', 'C_MCU_DEC', '1')
    routes += seg(p_md['x'], p_md['y'], p_md['x'], 78.5, "F.Cu", "+3V3", 0.25)
    routes += via(p_md['x'], 78.5, "+3V3")

    p_rpu = get_pad('+3V3', 'R_RTC_PU', '2')
    routes += seg(p_rpu['x'], p_rpu['y'], 85.8, p_rpu['y'], "F.Cu", "+3V3", 0.25)
    routes += via(85.8, p_rpu['y'], "+3V3")

    p_rio = get_pad('+3V3', 'R_IO0', '2')
    routes += seg(p_rio['x'], p_rio['y'], 116.2, p_rio['y'], "F.Cu", "+3V3", 0.25)
    routes += via(116.2, p_rio['y'], "+3V3")

    p_sda_pu = get_pad('+3V3', 'R_SDA_PU', '2')
    p_scl_pu = get_pad('+3V3', 'R_SCL_PU', '2')
    routes += seg(p_scl_pu['x'], p_scl_pu['y'], 116.2, p_scl_pu['y'], "F.Cu", "+3V3", 0.25)
    routes += seg(116.2, p_scl_pu['y'], 116.2, p_sda_pu['y'], "F.Cu", "+3V3", 0.25)
    routes += seg(p_sda_pu['x'], p_sda_pu['y'], 116.2, p_sda_pu['y'], "F.Cu", "+3V3", 0.25)
    routes += via(116.2, 68.2, "+3V3")

    p_g22 = get_pad('+3V3', 'U_GPS', '22')
    p_g23 = get_pad('+3V3', 'U_GPS', '23')
    routes += seg(p_g23['x'], p_g23['y'], p_g22['x'], p_g22['y'], "B.Cu", "+3V3", 0.30)
    routes += seg(p_g22['x'], p_g22['y'], 110.2, 67.6, "B.Cu", "+3V3", 0.30)
    routes += via(110.2, 67.6, "+3V3")

    p_cg1 = get_pad('+3V3', 'C_GPS1', '1')
    p_cg2 = get_pad('+3V3', 'C_GPS2', '1')
    routes += seg(p_cg1['x'], p_cg1['y'], 102.22, 60.2, "B.Cu", "+3V3", 0.25)
    routes += via(102.22, 60.2, "+3V3")
    routes += seg(p_cg2['x'], p_cg2['y'], 98.05, 60.2, "B.Cu", "+3V3", 0.25)
    routes += via(98.05, 60.2, "+3V3")

    routes += seg(111.85, 105.0, 114.5, 105.0, "F.Cu", "+3V3", 0.40)
    routes += via(114.5, 105.0, "+3V3")

    p_clo = get_pad('+3V3', 'C_LDO_OUT', '1')
    routes += seg(p_clo['x'], p_clo['y'], 120.7, p_clo['y'], "B.Cu", "+3V3", 0.35)
    routes += via(120.7, p_clo['y'], "+3V3")

    p_cld = get_pad('+3V3', 'C_LDO_DEC', '1')
    routes += seg(p_cld['x'], p_cld['y'], 120.7, p_cld['y'], "B.Cu", "+3V3", 0.35)
    routes += via(120.7, p_cld['y'], "+3V3")

    routes += seg(104.85, 115.675, 103.2, 115.675, "B.Cu", "+3V3", 0.25)
    routes += via(103.2, 115.675, "+3V3")

    p_crtc = get_pad('+3V3', 'C_RTC_VCC', '1')
    routes += seg(p_crtc['x'], p_crtc['y'], p_crtc['x'], 107.5, "B.Cu", "+3V3", 0.25)
    routes += via(p_crtc['x'], 107.5, "+3V3")

    p_cds = get_pad('+3V3', 'C_DS_VCC', '1')
    p_rds = get_pad('+3V3', 'R_DS_PU', '2')
    routes += seg(p_rds['x'], p_rds['y'], p_cds['x'], p_cds['y'], "F.Cu", "+3V3", 0.25)
    routes += seg(p_rds['x'], p_rds['y'], p_rds['x'], 113.0, "F.Cu", "+3V3", 0.25)
    routes += via(p_rds['x'], 113.0, "+3V3")

    p_rtds = get_pad('+3V3', 'R_TDS_REF', '2')
    routes += seg(p_rtds['x'], p_rtds['y'], 110.41, 113.3, "F.Cu", "+3V3", 0.25)
    routes += via(110.41, 113.3, "+3V3")

    p_clcd = get_pad('+3V3', 'C_LCD_VCC', '1')
    routes += seg(p_clcd['x'], p_clcd['y'], p_clcd['x'], 116.0, "F.Cu", "+3V3", 0.25)
    routes += via(p_clcd['x'], 116.0, "+3V3")

    # 2. +5V POWER TRUNK
    p_d1_1 = get_pad('+5V', 'D1', '1')
    p_cbo2 = get_pad('+5V', 'C_BST_OUT2', '1')
    p_cbo1 = get_pad('+5V', 'C_BST_OUT1', '1')
    p_cldo_in = get_pad('+5V', 'C_LDO_IN', '1')
    p_u5_3 = get_pad('+5V', 'U5', '3')
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

    routes += via(92.5, 108.0, "+5V")
    routes += seg(92.5, 108.0, p_cff_1['x'], p_cff_1['y'], "B.Cu", "+5V", 0.25)
    routes += seg(p_cff_1['x'], p_cff_1['y'], p_rfb1_1['x'], p_rfb1_1['y'], "B.Cu", "+5V", 0.25)

    return fp_base.rstrip() + "\n" + edge_cuts + zones_text + routes
