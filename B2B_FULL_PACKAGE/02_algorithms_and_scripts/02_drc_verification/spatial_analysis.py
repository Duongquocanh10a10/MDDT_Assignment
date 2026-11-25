"""
STEP 1: Parse entire PCB into spatial obstacle map.
Extract ALL segments, vias, pads on each layer with their bounding boxes.
Then for each DRC violation, find the exact collision and determine safe reroute.
"""
import re
import json
import math
from collections import defaultdict

PCB_FILE = r"A:\DEVICE\KiCad_Project\WaterSensor.kicad_pcb.bak_fixes"
OUT_FILE = r"A:\DEVICE\spatial_map.json"

with open(PCB_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# ============================================================
# 1. Parse all segments
# ============================================================
seg_pat = re.compile(
    r'\(segment\s+'
    r'\(start ([\d.]+) ([\d.]+)\)\s+'
    r'\(end ([\d.]+) ([\d.]+)\)\s+'
    r'\(width ([\d.]+)\)\s+'
    r'\(layer "([^"]+)"\)\s+'
    r'\(net "([^"]+)"\)\s+'
    r'\(uuid "([^"]+)"\)',
    re.DOTALL
)

segments = []
for m in seg_pat.finditer(content):
    segments.append({
        'type': 'segment',
        'x1': float(m.group(1)), 'y1': float(m.group(2)),
        'x2': float(m.group(3)), 'y2': float(m.group(4)),
        'width': float(m.group(5)),
        'layer': m.group(6),
        'net': m.group(7),
        'uuid': m.group(8),
    })

# ============================================================
# 2. Parse all vias
# ============================================================
via_pat = re.compile(
    r'\(via\s+'
    r'\(at ([\d.]+) ([\d.]+)\)\s+'
    r'\(size ([\d.]+)\)\s+'
    r'\(drill ([\d.]+)\)\s+'
    r'\(layers "([^"]+)" "([^"]+)"\)\s+'
    r'\(net "([^"]+)"\)\s+'
    r'\(uuid "([^"]+)"\)',
    re.DOTALL
)

vias = []
for m in via_pat.finditer(content):
    vias.append({
        'type': 'via',
        'x': float(m.group(1)), 'y': float(m.group(2)),
        'size': float(m.group(3)),
        'drill': float(m.group(4)),
        'layer1': m.group(5), 'layer2': m.group(6),
        'net': m.group(7),
        'uuid': m.group(8),
    })

# ============================================================
# 3. Parse footprint pads (SMD and THT)
# ============================================================
# Find footprints with their positions first
fp_pat = re.compile(
    r'\(footprint "([^"]+)"[^)]*?\n'
    r'(?:.*?\n)*?'
    r'\s+\(at ([\d.]+) ([\d.]+)(?:\s+([\d.]+))?\)',
    re.DOTALL
)

# Simpler: just find all pad locations from the content
# We need pad centers in board coordinates
# Parse footprints and their pads
pads = []

# Find each footprint block
fp_blocks = []
depth = 0
i = 0
while i < len(content):
    if content[i:i+12] == '\t(footprint ':
        start = i
        depth = 0
        j = i
        while j < len(content):
            if content[j] == '(':
                depth += 1
            elif content[j] == ')':
                depth -= 1
                if depth == 0:
                    fp_blocks.append(content[start:j+1])
                    i = j + 1
                    break
            j += 1
        else:
            break
    else:
        i += 1

print(f"Found {len(fp_blocks)} footprints")

for fp_block in fp_blocks:
    # Get footprint position and rotation
    fp_at = re.search(r'^\t\t\(at ([\d.]+) ([\d.]+)(?:\s+([\d.]+))?\)', fp_block, re.MULTILINE)
    if not fp_at:
        continue
    fp_x, fp_y = float(fp_at.group(1)), float(fp_at.group(2))
    fp_rot = float(fp_at.group(3)) if fp_at.group(3) else 0.0
    fp_rot_rad = math.radians(fp_rot)
    cos_r, sin_r = math.cos(fp_rot_rad), math.sin(fp_rot_rad)

    # Get footprint reference
    fp_ref_m = re.search(r'\(fp_text reference "([^"]+)"', fp_block)
    fp_ref = fp_ref_m.group(1) if fp_ref_m else "?"

    # Find all pads in this footprint
    pad_pat = re.compile(
        r'\(pad "([^"]+)" (\w+) (\w+)\s+'
        r'\(at ([-\d.]+) ([-\d.]+)(?:\s+([\d.]+))?\)\s+'
        r'\(size ([\d.]+) ([\d.]+)\)\s+'
        r'(?:\(layers ([^)]+)\))?'
        r'.*?'
        r'(?:\(net "([^"]+)"\))?',
        re.DOTALL
    )

    for pm in pad_pat.finditer(fp_block):
        pad_num = pm.group(1)
        pad_type = pm.group(2)  # smd, thru_hole
        pad_shape = pm.group(3)  # rect, roundrect, circle, oval
        px, py = float(pm.group(4)), float(pm.group(5))
        pad_rot = float(pm.group(6)) if pm.group(6) else 0.0
        sx, sy = float(pm.group(7)), float(pm.group(8))
        layers_str = pm.group(9) if pm.group(9) else ""
        net = pm.group(10) if pm.group(10) else ""

        # Transform pad position to board coordinates
        bx = fp_x + px * cos_r - py * sin_r
        by = fp_y + px * sin_r + py * cos_r

        # Determine which layers this pad is on
        pad_layers = []
        if "*.Cu" in layers_str or "F.Cu" in layers_str:
            pad_layers.append("F.Cu")
        if "*.Cu" in layers_str or "B.Cu" in layers_str:
            pad_layers.append("B.Cu")
        if "In1.Cu" in layers_str or "*.Cu" in layers_str:
            pad_layers.append("In1.Cu")
        if "In2.Cu" in layers_str or "*.Cu" in layers_str:
            pad_layers.append("In2.Cu")

        pads.append({
            'type': 'pad',
            'ref': fp_ref,
            'pad_num': pad_num,
            'pad_type': pad_type,
            'x': round(bx, 4), 'y': round(by, 4),
            'sx': sx, 'sy': sy,
            'layers': pad_layers,
            'net': net,
        })

print(f"Parsed: {len(segments)} segments, {len(vias)} vias, {len(pads)} pads")

# ============================================================
# 4. Build per-layer obstacle lists
# ============================================================
layer_obstacles = defaultdict(list)

for seg in segments:
    layer_obstacles[seg['layer']].append(seg)

for via in vias:
    layer_obstacles[via['layer1']].append(via)
    layer_obstacles[via['layer2']].append(via)

for pad in pads:
    for layer in pad['layers']:
        layer_obstacles[layer].append(pad)

# ============================================================
# 5. For key problem areas, check what's at specific coordinates
# ============================================================
print("\n" + "="*60)
print("OBSTACLE ANALYSIS FOR PROBLEM ROUTES")
print("="*60)

def obstacles_crossing_x(layer, x, y_min, y_max, exclude_net=None):
    """Find all obstacles on `layer` that a vertical track at X would cross between y_min and y_max"""
    hits = []
    clearance = 0.15  # minimum clearance

    for obj in layer_obstacles.get(layer, []):
        if obj['type'] == 'segment':
            if exclude_net and obj['net'] == exclude_net:
                continue
            sx1, sy1, sx2, sy2 = obj['x1'], obj['y1'], obj['x2'], obj['y2']
            w = obj['width'] / 2 + clearance

            # Horizontal segment crossing our vertical line
            if abs(sy1 - sy2) < 0.01:  # horizontal
                if min(sx1, sx2) - w <= x <= max(sx1, sx2) + w:
                    if y_min <= sy1 <= y_max:
                        hits.append(f"  SEG {obj['net']:15s} Y={sy1:.2f} X=[{min(sx1,sx2):.2f},{max(sx1,sx2):.2f}] w={obj['width']}")

            # Vertical segment parallel to our line
            elif abs(sx1 - sx2) < 0.01:  # vertical
                if abs(sx1 - x) < w + 0.075:  # our track width/2
                    oy_min, oy_max = min(sy1, sy2), max(sy1, sy2)
                    if oy_min <= y_max and oy_max >= y_min:
                        hits.append(f"  SEG {obj['net']:15s} X={sx1:.2f} Y=[{oy_min:.2f},{oy_max:.2f}] PARALLEL! w={obj['width']}")

        elif obj['type'] == 'via':
            if exclude_net and obj['net'] == exclude_net:
                continue
            vr = obj['size'] / 2 + clearance
            if abs(obj['x'] - x) < vr + 0.075 and y_min <= obj['y'] <= y_max:
                hits.append(f"  VIA {obj['net']:15s} at ({obj['x']:.2f}, {obj['y']:.2f}) size={obj['size']}")

        elif obj['type'] == 'pad':
            if exclude_net and obj['net'] == exclude_net:
                continue
            pr = max(obj['sx'], obj['sy']) / 2 + clearance
            if abs(obj['x'] - x) < pr + 0.075 and y_min <= obj['y'] <= y_max:
                hits.append(f"  PAD {obj['ref']:6s}.{obj['pad_num']:3s} [{obj['net']:15s}] at ({obj['x']:.2f}, {obj['y']:.2f}) size=({obj['sx']},{obj['sy']})")

    return hits

def obstacles_crossing_y(layer, y, x_min, x_max, exclude_net=None):
    """Find all obstacles on `layer` that a horizontal track at Y would cross between x_min and x_max"""
    hits = []
    clearance = 0.15

    for obj in layer_obstacles.get(layer, []):
        if obj['type'] == 'segment':
            if exclude_net and obj['net'] == exclude_net:
                continue
            sx1, sy1, sx2, sy2 = obj['x1'], obj['y1'], obj['x2'], obj['y2']
            w = obj['width'] / 2 + clearance

            # Vertical segment crossing our horizontal line
            if abs(sx1 - sx2) < 0.01:  # vertical
                if min(sy1, sy2) - w <= y <= max(sy1, sy2) + w:
                    if x_min <= sx1 <= x_max:
                        hits.append(f"  SEG {obj['net']:15s} X={sx1:.2f} Y=[{min(sy1,sy2):.2f},{max(sy1,sy2):.2f}] w={obj['width']}")

            # Horizontal segment parallel
            elif abs(sy1 - sy2) < 0.01:
                if abs(sy1 - y) < w + 0.075:
                    ox_min, ox_max = min(sx1, sx2), max(sx1, sx2)
                    if ox_min <= x_max and ox_max >= x_min:
                        hits.append(f"  SEG {obj['net']:15s} Y={sy1:.2f} X=[{ox_min:.2f},{ox_max:.2f}] PARALLEL! w={obj['width']}")

        elif obj['type'] == 'via':
            if exclude_net and obj['net'] == exclude_net:
                continue
            vr = obj['size'] / 2 + clearance
            if abs(obj['y'] - y) < vr + 0.075 and x_min <= obj['x'] <= x_max:
                hits.append(f"  VIA {obj['net']:15s} at ({obj['x']:.2f}, {obj['y']:.2f}) size={obj['size']}")

        elif obj['type'] == 'pad':
            if exclude_net and obj['net'] == exclude_net:
                continue
            pr = max(obj['sx'], obj['sy']) / 2 + clearance
            if abs(obj['y'] - y) < pr + 0.075 and x_min <= obj['x'] <= x_max:
                hits.append(f"  PAD {obj['ref']:6s}.{obj['pad_num']:3s} [{obj['net']:15s}] at ({obj['x']:.2f}, {obj['y']:.2f}) size=({obj['sx']},{obj['sy']})")

    return hits

# ============================================================
# Check proposed I2C_SCL corridor on B.Cu at X=108.95
# ============================================================
print("\n--- I2C_SCL B.Cu vertical at X=108.95, Y=[65, 129.45] ---")
hits = obstacles_crossing_x("B.Cu", 108.95, 65.0, 129.45, exclude_net="I2C_SCL")
for h in hits:
    print(h)
print(f"Total obstacles: {len(hits)}")

# Try alternate X values
for test_x in [108.0, 107.5, 109.5, 110.5, 111.0, 112.0, 113.0, 114.0, 115.0, 116.0]:
    hits = obstacles_crossing_x("B.Cu", test_x, 65.0, 129.45, exclude_net="I2C_SCL")
    print(f"  X={test_x}: {len(hits)} obstacles")

# ============================================================
# Check proposed VBAT_SW corridor on B.Cu at X=83.5
# ============================================================
print("\n--- VBAT_SW B.Cu vertical at X=83.5, Y=[69.9, 119.5] ---")
hits = obstacles_crossing_x("B.Cu", 83.5, 69.9, 119.5, exclude_net="VBAT_SW")
for h in hits:
    print(h)
print(f"Total obstacles: {len(hits)}")

for test_x in [82.0, 82.5, 83.0, 84.0, 84.5, 85.0, 81.0, 81.5, 78.0, 79.0]:
    hits = obstacles_crossing_x("B.Cu", test_x, 69.9, 119.5, exclude_net="VBAT_SW")
    print(f"  X={test_x}: {len(hits)} obstacles")

# ============================================================
# Check proposed TDS_ADC corridor on B.Cu at X=98.8
# ============================================================
print("\n--- TDS_ADC B.Cu vertical at X=98.8, Y=[65.37, 93.5] ---")
hits = obstacles_crossing_x("B.Cu", 98.8, 65.37, 93.5, exclude_net="TDS_ADC")
for h in hits:
    print(h)
print(f"Total obstacles: {len(hits)}")

for test_x in [97.5, 98.0, 98.5, 99.0, 99.5, 100.0, 100.5, 101.0]:
    hits = obstacles_crossing_x("B.Cu", test_x, 65.37, 93.5, exclude_net="TDS_ADC")
    print(f"  X={test_x}: {len(hits)} obstacles")

# ============================================================
# Check CHRG_LED via placement near CHRG_ANODE
# ============================================================
print("\n--- Obstacles near CHRG_LED/CHRG_ANODE area (86-88, 93-95) ---")
for obj in layer_obstacles.get("F.Cu", []) + layer_obstacles.get("B.Cu", []):
    if obj['type'] == 'via' or obj['type'] == 'pad':
        x = obj.get('x', 0)
        y = obj.get('y', 0)
        if 86 <= x <= 89 and 92 <= y <= 96:
            net = obj.get('net', '')
            print(f"  {obj['type']} {net} at ({x}, {y})")

# ============================================================
# Check CP_DTR via placement area
# ============================================================
print("\n--- Obstacles near CP_DTR area (92-97, 89-96) ---")
for obj in layer_obstacles.get("F.Cu", []) + layer_obstacles.get("B.Cu", []):
    if obj['type'] in ('via', 'pad'):
        x = obj.get('x', 0)
        y = obj.get('y', 0)
        if 92 <= x <= 97 and 89 <= y <= 96:
            net = obj.get('net', '')
            ref = obj.get('ref', '')
            print(f"  {obj['type']} {ref}.{obj.get('pad_num','')} [{net}] at ({x}, {y})")
