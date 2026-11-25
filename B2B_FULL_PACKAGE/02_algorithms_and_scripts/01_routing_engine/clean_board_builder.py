import re, uuid

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

def make_clean_compact_board():
    with open(r'A:\DEVICE\KiCad_Project\WaterSensor.kicad_pcb.bak_before_compact', 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Cleanly remove ALL old segments, vias, and arcs
    text = remove_sexp_blocks(text, "\t(segment")
    text = remove_sexp_blocks(text, "\t(via")
    text = remove_sexp_blocks(text, "\t(arc")

    # 2. Cleanly remove old gr_lines (Edge.Cuts)
    text = remove_sexp_blocks(text, "\t(gr_line")

    # 3. Relocate footprints to PERFECT_TARGETS
    from base_builder import PERFECT_TARGETS
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

    text = re.sub(r'\(footprint\s+"[^"]+".*?\n\t\)', repl_fp, text, flags=re.DOTALL)

    # 4. Fix J_BNC pad 2 (from 3.5x7 oval to 3.2 circle to prevent edge cuts collision)
    def repl_bnc(m):
        blk = m.group(0)
        blk = re.sub(r'\(pad\s+"2"\s+thru_hole\s+oval\s+\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(size\s+3\.5\s+7\)',
                     r'(pad "2" thru_hole circle (at \1 \2 \3) (size 3.2 3.2)', blk)
        return blk
    text = re.sub(r'\t\(footprint\s+"[^\"]+".*?\(property\s+"Reference"\s+"J_BNC".*?\n\t\)', repl_bnc, text, flags=re.DOTALL)

    # 4b. Reassign R_BAT1.1 net from VBAT_RAW to VBAT_SW (Remediate Flaw 2.1)
    text = text.replace('(net "VBAT_RAW")\n\t\t\t(uuid "8ddfd0d4-b886-4fa5-a979-e8920e973299")',
                        '(net "VBAT_SW")\n\t\t\t(uuid "8ddfd0d4-b886-4fa5-a979-e8920e973299")')

    # 5. Add clean 52x75mm Edge.Cuts
    edge_cuts_new = """\t(gr_line (start 73 55) (end 75 53) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-01"))
\t(gr_line (start 75 53) (end 123 53) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-02"))
\t(gr_line (start 123 53) (end 125 55) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-03"))
\t(gr_line (start 125 55) (end 125 126) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-04"))
\t(gr_line (start 125 126) (end 123 128) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-05"))
\t(gr_line (start 123 128) (end 75 128) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-06"))
\t(gr_line (start 75 128) (end 73 126) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-07"))
\t(gr_line (start 73 126) (end 73 55) (stroke (width 0.15) (type default)) (layer "Edge.Cuts") (uuid "ec-08"))
"""
    # 6. Clip zone boundary polygons from Y=154 down to Y=128
    def fix_zone_pts(m):
        zblk = m.group(0)
        zblk = zblk.replace("154", "128")
        return zblk
    text = re.sub(r'\(zone\s+.*?\n\t\)', fix_zone_pts, text, flags=re.DOTALL)

    # 7. Update split boundary on In2.Cu for +3V3 and +5V to Y=104.0/104.5
    text = text.replace("(xy 125 115) (xy 73 115)", "(xy 125 104) (xy 73 104)")
    text = text.replace("(xy 73 115) (xy 125 115)", "(xy 73 104.5) (xy 125 104.5)")

    # Insert edge cuts before the final closing parenthesis
    last_p = text.rfind(")")
    return text[:last_p] + edge_cuts_new, text[last_p:]

if __name__ == '__main__':
    base_prefix, base_suffix = make_clean_compact_board()
    print("Clean board generated successfully! Prefix len:", len(base_prefix))
