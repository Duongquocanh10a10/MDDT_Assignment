"""
Router Engine: Data definitions and S-expression generators
"""
import uuid, json

with open("A:/DEVICE/pads_summary.json", "r", encoding="utf-8") as f:
    PADS = json.load(f)

def get_pad(net, ref, pin):
    for p in PADS.get(net, []):
        if p['ref'] == ref and str(p['num']) == str(pin):
            return p
    raise ValueError(f"Pad {ref}.{pin} not found on net {net}")

def seg(x1, y1, x2, y2, layer, net, width=0.20):
    if abs(x1 - x2) < 0.0005 and abs(y1 - y2) < 0.0005:
        return ""
    uid = str(uuid.uuid4())
    return f"""\t(segment
\t\t(start {x1:.4f} {y1:.4f})
\t\t(end {x2:.4f} {y2:.4f})
\t\t(width {width:.2f})
\t\t(layer "{layer}")
\t\t(net "{net}")
\t\t(uuid "{uid}")
\t)
"""

def via(x, y, net, size=0.6, drill=0.3):
    uid = str(uuid.uuid4())
    return f"""\t(via
\t\t(at {x:.4f} {y:.4f})
\t\t(size {size:.2f})
\t\t(drill {drill:.2f})
\t\t(layers "F.Cu" "B.Cu")
\t\t(net "{net}")
\t\t(uuid "{uid}")
\t)
"""

def route_L_v_then_h(p1, p2, net, width=0.20):
    """
    1 bend: Vertical on F.Cu from (x1, y1) to (x1, y2),
    via at (x1, y2),
    then Horizontal on B.Cu from (x1, y2) to (x2, y2).
    If p2 is on F.Cu and not TH, via at (x2, y2) or breakout.
    """
    res = ""
    x1, y1 = p1['x'], p1['y']
    x2, y2 = p2['x'], p2['y']
    res += seg(x1, y1, x1, y2, "F.Cu", net, width)
    res += via(x1, y2, net)
    res += seg(x1, y2, x2, y2, "B.Cu", net, width)
    if not p2.get('is_th') and p2.get('fp_layer') != 'B.Cu':
        res += via(x2, y2, net)
    return res

def route_L_h_then_v(p1, p2, net, width=0.20):
    """
    1 bend: Horizontal on B.Cu from (x1, y1) to (x2, y1),
    via at (x2, y1),
    then Vertical on F.Cu from (x2, y1) to (x2, y2).
    """
    res = ""
    x1, y1 = p1['x'], p1['y']
    x2, y2 = p2['x'], p2['y']
    if not p1.get('is_th') and p1.get('fp_layer') != 'B.Cu':
        res += via(x1, y1, net)
    res += seg(x1, y1, x2, y1, "B.Cu", net, width)
    res += via(x2, y1, net)
    res += seg(x2, y1, x2, y2, "F.Cu", net, width)
    return res

def route_Z_via_highway(p1, p2, y_hwy, net, width=0.20):
    """
    2 bends:
    - Vertical on F.Cu from (x1, y1) to (x1, y_hwy)
    - Via at (x1, y_hwy)
    - Horizontal on B.Cu from (x1, y_hwy) to (x2, y_hwy)
    - Via at (x2, y_hwy)
    - Vertical on F.Cu from (x2, y_hwy) to (x2, y2)
    """
    res = ""
    x1, y1 = p1['x'], p1['y']
    x2, y2 = p2['x'], p2['y']
    res += seg(x1, y1, x1, y_hwy, "F.Cu", net, width)
    res += via(x1, y_hwy, net)
    res += seg(x1, y_hwy, x2, y_hwy, "B.Cu", net, width)
    if p2.get('type') == 'thru_hole' or p2.get('fp_layer') == 'B.Cu':
        res += seg(x2, y_hwy, x2, y2, "B.Cu", net, width)
    else:
        res += via(x2, y_hwy, net)
        res += seg(x2, y_hwy, x2, y2, "F.Cu", net, width)
    return res
