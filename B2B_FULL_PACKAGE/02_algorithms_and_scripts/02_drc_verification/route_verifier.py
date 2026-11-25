import sys
sys.path = [p for p in sys.path if "OneDrive" not in p]
import pcbnew
import math

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def segments_intersect(p1, p2, p3, p4):
    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

def point_to_seg_dist(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    l2 = dx*dx + dy*dy
    if l2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1)*dx + (py - y1)*dy) / l2))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)

def seg_to_seg_dist(p1, p2, p3, p4):
    if segments_intersect(p1, p2, p3, p4):
        return 0.0
    d1 = point_to_seg_dist(p1[0], p1[1], p3[0], p3[1], p4[0], p4[1])
    d2 = point_to_seg_dist(p2[0], p2[1], p3[0], p3[1], p4[0], p4[1])
    d3 = point_to_seg_dist(p3[0], p3[1], p1[0], p1[1], p2[0], p2[1])
    d4 = point_to_seg_dist(p4[0], p4[1], p1[0], p1[1], p2[0], p2[1])
    return min(d1, d2, d3, d4)

def seg_to_aabb_dist(ax, ay, bx, by, x1, x2, y1, y2):
    """Exact minimum distance between a 2D line segment and an axis-aligned box."""
    # Ensure box bounds ordered
    if x1 > x2: x1, x2 = x2, x1
    if y1 > y2: y1, y2 = y2, y1

    # Sample endpoints and projection
    points = [(ax, ay), (bx, by)]
    # If horizontal segment
    if ay == by:
        y = ay
        # Overlapping X range?
        seg_min_x, seg_max_x = min(ax, bx), max(ax, bx)
        if seg_max_x >= x1 and seg_min_x <= x2:
            # Overlaps in X
            if y1 <= y <= y2:
                return 0.0
            return min(abs(y - y1), abs(y - y2))
        else:
            dx = max(0.0, x1 - seg_max_x, seg_min_x - x2)
            dy = max(0.0, y1 - y, y - y2)
            return math.hypot(dx, dy)
    elif ax == bx:
        x = ax
        seg_min_y, seg_max_y = min(ay, by), max(ay, by)
        if seg_max_y >= y1 and seg_min_y <= y2:
            if x1 <= x <= x2:
                return 0.0
            return min(abs(x - x1), abs(x - x2))
        else:
            dx = max(0.0, x1 - x, x - x2)
            dy = max(0.0, y1 - seg_max_y, seg_min_y - y2)
            return math.hypot(dx, dy)
    else:
        # Diagonal segment: sample N points along segment
        min_d = 1e9
        for step in range(21):
            t = step / 20.0
            px = ax + t * (bx - ax)
            py = ay + t * (by - ay)
            dx = max(0.0, x1 - px, px - x2)
            dy = max(0.0, y1 - py, py - y2)
            d = math.hypot(dx, dy)
            if d < min_d: min_d = d
        return min_d

class RouteAuditor:
    def __init__(self, board):
        self.b = board
        self.vias = []
        self.segs = []
        self.pads = []
        self._load()

    def _load(self):
        tracks = list(self.b.GetTracks())
        for t in tracks:
            if isinstance(t, pcbnew.PCB_VIA):
                pos = t.GetPosition()
                self.vias.append({
                    'x': pcbnew.ToMM(pos.x),
                    'y': pcbnew.ToMM(pos.y),
                    'r': 0.30, # standard via 0.6mm diameter
                    'net': str(t.GetNetname())
                })
            else:
                p1 = t.GetStart()
                p2 = t.GetEnd()
                self.segs.append({
                    'x1': pcbnew.ToMM(p1.x),
                    'y1': pcbnew.ToMM(p1.y),
                    'x2': pcbnew.ToMM(p2.x),
                    'y2': pcbnew.ToMM(p2.y),
                    'w': pcbnew.ToMM(t.GetWidth()),
                    'layer': 'F.Cu' if t.GetLayer() == pcbnew.F_Cu else ('B.Cu' if t.GetLayer() == pcbnew.B_Cu else 'Other'),
                    'net': str(t.GetNetname())
                })

        for p in self.b.GetPads():
            pos = p.GetPosition()
            ref = p.GetParentFootprint().GetReference()
            layer = 'F.Cu' if p.IsOnLayer(pcbnew.F_Cu) else ('B.Cu' if p.IsOnLayer(pcbnew.B_Cu) else 'THT')
            bb = p.GetBoundingBox()
            self.pads.append({
                'ref': ref,
                'num': p.GetNumber(),
                'x1': pcbnew.ToMM(bb.GetX()),
                'y1': pcbnew.ToMM(bb.GetY()),
                'x2': pcbnew.ToMM(bb.GetRight()),
                'y2': pcbnew.ToMM(bb.GetBottom()),
                'cx': pcbnew.ToMM(pos.x),
                'cy': pcbnew.ToMM(pos.y),
                'layer': layer,
                'net': str(p.GetNetname())
            })

    def check_all(self, min_clearance=0.15):
        violations = []

        # 1. Wire-to-wire crossings and clearances
        for i in range(len(self.segs)):
            s1 = self.segs[i]
            p1 = (s1['x1'], s1['y1'])
            p2 = (s1['x2'], s1['y2'])
            for j in range(i + 1, len(self.segs)):
                s2 = self.segs[j]
                if s1['layer'] != s2['layer'] or s1['net'] == s2['net']:
                    continue
                p3 = (s2['x1'], s2['y1'])
                p4 = (s2['x2'], s2['y2'])
                d = seg_to_seg_dist(p1, p2, p3, p4)
                clr = d - (s1['w']/2.0 + s2['w']/2.0)
                if clr < min_clearance:
                    violations.append({
                        'type': 'WIRE_WIRE',
                        'net1': s1['net'],
                        'net2': s2['net'],
                        'layer': s1['layer'],
                        'clearance': clr,
                        'pos': f"({s1['x1']},{s1['y1']})->({s1['x2']},{s1['y2']}) vs ({s2['x1']},{s2['y1']})->({s2['x2']},{s2['y2']})"
                    })

        # 2. Via-to-via clearances
        for i in range(len(self.vias)):
            v1 = self.vias[i]
            for j in range(i + 1, len(self.vias)):
                v2 = self.vias[j]
                if v1['net'] == v2['net']:
                    continue
                d = math.hypot(v1['x'] - v2['x'], v1['y'] - v2['y'])
                clr = d - (v1['r'] + v2['r'])
                if clr < min_clearance:
                    violations.append({
                        'type': 'VIA_VIA',
                        'net1': v1['net'],
                        'net2': v2['net'],
                        'layer': 'ALL',
                        'clearance': clr,
                        'pos': f"({v1['x']},{v1['y']}) vs ({v2['x']},{v2['y']})"
                    })

        # 3. Via-to-wire clearances
        for v in self.vias:
            for s in self.segs:
                if v['net'] == s['net']:
                    continue
                d = point_to_seg_dist(v['x'], v['y'], s['x1'], s['y1'], s['x2'], s['y2'])
                clr = d - (v['r'] + s['w']/2.0)
                if clr < min_clearance:
                    violations.append({
                        'type': 'VIA_WIRE',
                        'net1': v['net'],
                        'net2': s['net'],
                        'layer': s['layer'],
                        'clearance': clr,
                        'pos': f"Via {v['net']}({v['x']},{v['y']}) vs Wire {s['net']} {s['layer']} ({s['x1']},{s['y1']})->({s['x2']},{s['y2']})"
                    })

        # 4. Wire-to-pad clearances (different net, same layer)
        for s in self.segs:
            s_min_x = min(s['x1'], s['x2']) - min_clearance - s['w']/2.0
            s_max_x = max(s['x1'], s['x2']) + min_clearance + s['w']/2.0
            s_min_y = min(s['y1'], s['y2']) - min_clearance - s['w']/2.0
            s_max_y = max(s['y1'], s['y2']) + min_clearance + s['w']/2.0
            for p in self.pads:
                if s['net'] == p['net'] or s['net'] == '<no net>':
                    continue
                if p['layer'] != 'THT' and p['layer'] != s['layer']:
                    continue
                if s_max_x < p['x1'] or s_min_x > p['x2'] or s_max_y < p['y1'] or s_min_y > p['y2']:
                    continue
                d = seg_to_aabb_dist(s['x1'], s['y1'], s['x2'], s['y2'], p['x1'], p['x2'], p['y1'], p['y2'])
                clr = d - (s['w'] / 2.0)
                if clr < min_clearance:
                    violations.append({
                        'type': 'WIRE_PAD',
                        'net1': s['net'],
                        'net2': f"{p['ref']}.{p['num']} ({p['net']})",
                        'layer': s['layer'],
                        'clearance': clr,
                        'pos': f"Wire {s['net']}({s['x1']},{s['y1']})->({s['x2']},{s['y2']}) vs Pad {p['ref']}.{p['num']} bbox ({p['x1']:.2f}..{p['x2']:.2f}, {p['y1']:.2f}..{p['y2']:.2f})"
                    })

        return violations

if __name__ == '__main__':
    b = pcbnew.LoadBoard(r'A:\DEVICE\KiCad_Project\WaterSensor_all_connected.kicad_pcb')
    auditor = RouteAuditor(b)
    viols = auditor.check_all(0.15)
    print(f'Total DRC Violations: {len(viols)}')
    types = {}
    for v in viols:
        types[v['type']] = types.get(v['type'], 0) + 1
    print('Breakdown:', types)
    for v in viols[:15]:
        print(f"  [{v['type']}] {v['net1']} vs {v['net2']} clr={v['clearance']:.3f}mm on {v['layer']} @ {v['pos']}")
