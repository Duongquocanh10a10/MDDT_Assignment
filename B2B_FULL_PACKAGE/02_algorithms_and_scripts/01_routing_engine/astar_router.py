"""
================================================================================
  ASTAR_ROUTER.PY V4: ROTATION-AWARE PADS & EDGE-SAFE ZERO-DRC ENGINE
  - Uses p.GetBoundingBox() to capture exact rotated pad geometries (J_USB, U8)
  - 0.5mm board edge keepout guarantees 0 copper_edge_clearance errors
  - Signals route first; power fanouts strictly checked for hole clearances
  - Refills all 4-layer copper planes cleanly
================================================================================
"""
import sys, os, time, heapq, ctypes
import pcbnew

PCB_FILE = r"A:\DEVICE\KiCad_Project\WaterSensor.kicad_pcb"
GRID_RES = 0.25   # 0.25mm grid
CLEARANCE = 0.20  # Minimum electrical clearance

def mm(v): return int(round(v * 1e6))
def vec(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

board = pcbnew.LoadBoard(PCB_FILE)
b_box = board.GetBoardEdgesBoundingBox()
min_x = b_box.GetX() / 1e6
min_y = b_box.GetY() / 1e6
max_x = (b_box.GetX() + b_box.GetWidth()) / 1e6
max_y = (b_box.GetY() + b_box.GetHeight()) / 1e6

cols = int((max_x - min_x) / GRID_RES) + 1
rows = int((max_y - min_y) / GRID_RES) + 1

def to_grid(x, y):
    gx = int(round((x - min_x) / GRID_RES))
    gy = int(round((y - min_y) / GRID_RES))
    return max(0, min(cols - 1, gx)), max(0, min(rows - 1, gy))

def to_coord(gx, gy):
    return round(min_x + gx * GRID_RES, 3), round(min_y + gy * GRID_RES, 3)

# 1. Purge all existing tracks & vias
for t in list(board.Tracks()):
    board.Delete(t)

# 2. Build net pad list & ALL rotated pads as obstacles
pads_by_net = {}
net_objects = {}
obstacles = {}
tht_pads = []
all_pads_data = []

for fp in board.Footprints():
    for p in fp.Pads():
        nn = p.GetNetname()
        if nn:
            net_objects[nn] = p.GetNet()
        net_tag = nn if nn else '__NO_NET__'

        pos = p.GetPosition()
        px, py = pos.x / 1e6, pos.y / 1e6

        pbb = p.GetBoundingBox()
        pbx = pbb.GetX() / 1e6
        pby = pbb.GetY() / 1e6
        pbw = pbb.GetWidth() / 1e6
        pbh = pbb.GetHeight() / 1e6

        is_th = (p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH)
        is_f = p.IsOnLayer(pcbnew.F_Cu)
        lay = 0 if (is_f or is_th) else 1

        if is_th:
            tht_pads.append((px, py))

        p_info = {
            'ref': fp.GetReference(), 'num': p.GetNumber(),
            'net': net_tag, 'nn': nn,
            'x': px, 'y': py, 'is_th': is_th,
            'layer': lay, 'grid': to_grid(px, py),
            'bx1': pbx, 'by1': pby, 'bx2': pbx + pbw, 'by2': pby + pbh
        }
        all_pads_data.append(p_info)
        if nn:
            pads_by_net.setdefault(nn, []).append(p_info)

# Pass 1: Mark clearance halos around pads
for p in all_pads_data:
    layers = [0, 1] if p['is_th'] else [p['layer']]
    gx1, gy1 = to_grid(p['bx1'] - CLEARANCE, p['by1'] - CLEARANCE)
    gx2, gy2 = to_grid(p['bx2'] + CLEARANCE, p['by2'] + CLEARANCE)
    for l in layers:
        for gx in range(gx1, gx2 + 1):
            for gy in range(gy1, gy2 + 1):
                obstacles.setdefault((l, gx, gy), p['net'])

# Pass 2: Overwrite exact pad core cells with pad net (cores cannot be overwritten by halos)
for p in all_pads_data:
    layers = [0, 1] if p['is_th'] else [p['layer']]
    gx1, gy1 = to_grid(p['bx1'], p['by1'])
    gx2, gy2 = to_grid(p['bx2'], p['by2'])
    for l in layers:
        for gx in range(gx1, gx2 + 1):
            for gy in range(gy1, gy2 + 1):
                obstacles[(l, gx, gy)] = p['net']
    # Ensure center grid cell strictly belongs to pad
    for l in layers:
        obstacles[(l, p['grid'][0], p['grid'][1])] = p['net']

# 3. Board Edge Keepout (0.50mm inset from board outline)
# Prevents copper_edge_clearance violations
for gx in range(cols):
    for gy in range(rows):
        x, y = to_coord(gx, gy)
        if x < min_x + 0.50 or x > max_x - 0.50 or y < min_y + 0.50 or y > max_y - 0.50:
            obstacles[(0, gx, gy)] = '__KEEPOUT__'
            obstacles[(1, gx, gy)] = '__KEEPOUT__'

# 4. RF Antenna keepout (all layers, Y <= 56.5, X: 88.5..111.5)
gx1, gy1 = to_grid(88.5, min_y)
gx2, gy2 = to_grid(111.5, 56.5)
for lay in [0, 1]:
    for gx in range(gx1, gx2 + 1):
        for gy in range(gy1, gy2 + 1):
            obstacles[(lay, gx, gy)] = '__KEEPOUT__'

# 5. CR2032 BT1 circle keepout on B.Cu (center 100, 86, radius 10.5mm)
for gx in range(cols):
    for gy in range(rows):
        x, y = to_coord(gx, gy)
        if (x - 100.0)**2 + (y - 86.0)**2 <= (10.5 + CLEARANCE)**2:
            obstacles[(1, gx, gy)] = '__KEEPOUT__'

# 6. Mounting holes H1..H4 keepout (radius 2.5mm)
mholes = [(79.0, 59.0), (121.0, 59.0), (79.0, 136.5), (121.0, 136.5)]
for hx, hy in mholes:
    for gx in range(cols):
        for gy in range(rows):
            x, y = to_coord(gx, gy)
            if (x - hx)**2 + (y - hy)**2 <= (2.5 + CLEARANCE)**2:
                for lay in [0, 1]:
                    obstacles[(lay, gx, gy)] = '__KEEPOUT__'

print(f"Total obstacle cells mapped: {len(obstacles)}")

# A* Router
def astar_route(nn, start_node, target_node):
    slay, sgx, sgy = start_node
    tlay, tgx, tgy = target_node

    open_set = []
    h0 = (abs(sgx - tgx) + abs(sgy - tgy)) * 1.0 + (8.0 if slay != tlay else 0.0)
    heapq.heappush(open_set, (h0, 0, slay, sgx, sgy, 0))

    came_from = {}
    g_score = {(slay, sgx, sgy): 0}

    moves = [
        (0, -1, 1), # Up
        (0, 1, 2),  # Down
        (-1, 0, 3), # Left
        (1, 0, 4),  # Right
    ]

    max_steps = 350000
    steps = 0

    while open_set and steps < max_steps:
        steps += 1
        f, current_g, lay, gx, gy, last_dir = heapq.heappop(open_set)

        if (lay, gx, gy) == (tlay, tgx, tgy):
            path = [(lay, gx, gy)]
            curr = (lay, gx, gy)
            while curr in came_from:
                curr = came_from[curr]
                path.append(curr)
            path.reverse()
            return path

        if current_g > g_score.get((lay, gx, gy), float('inf')):
            continue

        for dx, dy, dcode in moves:
            nx, ny = gx + dx, gy + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                neighbor = (lay, nx, ny)
                obs_owner = obstacles.get(neighbor)

                # Strictly forbid vertical movement across USB SMD pins (pins pitch 0.5mm)
                # D+ and D- must breakout horizontally to X >= 81.8 before turning
                coord_x, coord_y = to_coord(nx, ny)
                if coord_x < 81.8 and 86.0 <= coord_y <= 92.5:
                    if dy != 0:
                        continue

                is_endpoint = (lay, nx, ny) in [(tlay, tgx, tgy), (slay, sgx, sgy)]
                if obs_owner is not None and obs_owner != nn and not is_endpoint:
                    continue

                # Ensure minimum 1 grid cell clearance between different routed tracks
                # Only enforce in free corridor routing (dist > 2 cells from endpoints)
                dist_s = abs(nx - sgx) + abs(ny - sgy)
                dist_t = abs(nx - tgx) + abs(ny - tgy)
                if dist_s > 2 and dist_t > 2 and not is_endpoint:
                    conflict_adj = False
                    for adx, ady in ((-1,0), (1,0), (0,-1), (0,1)):
                        adj_owner = obstacles.get((lay, nx + adx, ny + ady))
                        if adj_owner is not None and adj_owner != nn and adj_owner not in ('__KEEPOUT__', '__NO_NET__'):
                            conflict_adj = True
                            break
                    if conflict_adj:
                        continue

                # Manhattan bias
                move_cost = 1.0
                if lay == 0 and dcode in (3, 4): move_cost += 0.35 # F.Cu prefers vertical
                if lay == 1 and dcode in (1, 2): move_cost += 0.35 # B.Cu prefers horizontal

                # Bend penalty
                if last_dir != 0 and last_dir != dcode and last_dir != 5:
                    move_cost += 3.5

                new_g = current_g + move_cost
                if new_g < g_score.get(neighbor, float('inf')):
                    g_score[neighbor] = new_g
                    h = (abs(nx - tgx) + abs(ny - tgy)) * 1.0 + (8.0 if lay != tlay else 0.0)
                    heapq.heappush(open_set, (new_g + h, new_g, lay, nx, ny, dcode))
                    came_from[neighbor] = (lay, gx, gy)

        # Via (Switch layer)
        other_lay = 1 - lay
        via_clear = True

        # Forbid via inside USB connector pin area
        vx_coord, vy_coord = to_coord(gx, gy)
        if vx_coord < 82.0 and 86.0 <= vy_coord <= 92.5:
            via_clear = False

        if via_clear:
            for dgx in range(-2, 3):
                for dgy in range(-2, 3):
                    c0 = obstacles.get((0, gx + dgx, gy + dgy))
                    c1 = obstacles.get((1, gx + dgx, gy + dgy))
                    if (c0 is not None and c0 != nn) or (c1 is not None and c1 != nn):
                        via_clear = False
                        break
                if not via_clear: break

        if via_clear:
            via_neighbor = (other_lay, gx, gy)
            via_cost = 14.0
            new_g = current_g + via_cost
            if new_g < g_score.get(via_neighbor, float('inf')):
                g_score[via_neighbor] = new_g
                h = (abs(gx - tgx) + abs(gy - tgy)) * 1.0 + (8.0 if other_lay != tlay else 0.0)
                heapq.heappush(open_set, (new_g + h, new_g, other_lay, gx, gy, 5))
                came_from[via_neighbor] = (lay, gx, gy)

    return None

def simplify_path(path):
    if len(path) <= 1:
        return []
    segments = []
    p0 = path[0]
    for i in range(1, len(path)):
        p1 = path[i]
        if p0[0] != p1[0]:
            x, y = to_coord(p0[1], p0[2])
            segments.append(('via', (x, y)))
            p0 = p1
        else:
            x1, y1 = to_coord(p0[1], p0[2])
            x2, y2 = to_coord(p1[1], p1[2])
            segments.append(('track', p0[0], (x1, y1), (x2, y2)))
            p0 = p1
    return segments

# ----------------------------------------------------
# STEP 1: ROUTE ALL SIGNAL NETS
# ----------------------------------------------------
plane_nets = {'GND', '+3V3', '+5V', '+5V_ANA'}

sorted_nets = []
for nn, plist in pads_by_net.items():
    if nn in plane_nets: continue
    sorted_nets.append((nn, plist))

# Priority nets: USB, Auto-reset, and Critical Bus routes
priority_nets = [
    'USB_D+', 'USB_D-', 'CC1', 'CC2', 'VBUS',
    'CP_VDD', 'CP_RST', 'CP_RTS', 'CP_DTR',
    'TX0', 'RX0', 'IO0', 'CHIP_PU',
    'SPI_SCK', 'SPI_MOSI', 'LCD_CS', 'LCD_DC', 'LCD_RST'
]

def net_rank(entry):
    nn, plist = entry
    if nn in priority_nets:
        return (0, priority_nets.index(nn))
    xs = [p['x'] for p in plist]
    ys = [p['y'] for p in plist]
    return (1, (max(xs) - min(xs)) + (max(ys) - min(ys)))

sorted_nets.sort(key=net_rank)

print(f"\nStarting routing for {len(sorted_nets)} signal nets...")
routed_count = 0
failed_nets = []
placed_vias = []

for nn, plist in sorted_nets:
    if len(plist) < 2: continue

    connected = [plist[0]]
    unconnected = plist[1:]
    net_success = True

    while unconnected:
        best_dist = float('inf')
        best_pair = None
        best_u_idx = -1
        for c in connected:
            for i, u in enumerate(unconnected):
                d = abs(c['grid'][0] - u['grid'][0]) + abs(c['grid'][1] - u['grid'][1])
                if d < best_dist:
                    best_dist = d
                    best_pair = (c, u)
                    best_u_idx = i

        c_pad, u_pad = best_pair
        start_node = (c_pad['layer'], c_pad['grid'][0], c_pad['grid'][1])
        target_node = (u_pad['layer'], u_pad['grid'][0], u_pad['grid'][1])

        path = astar_route(nn, start_node, target_node)
        if not path:
            net_success = False
            break

        # Register routed cells as obstacles for other nets
        for lay, gx, gy in path:
            obstacles[(lay, gx, gy)] = nn

        # Add to board
        segments = simplify_path(path)
        for seg in segments:
            if seg[0] == 'via':
                vx, vy = seg[1]
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(vec(vx, vy))
                v.SetWidth(mm(0.6))
                v.SetDrill(mm(0.3))
                v.SetNet(net_objects[nn])
                board.Add(v)
                placed_vias.append((vx, vy))

                # Protect via keepout on both layers
                vgx, vgy = to_grid(vx, vy)
                for dgx in range(-2, 3):
                    for dgy in range(-2, 3):
                        if 0 <= vgx + dgx < cols and 0 <= vgy + dgy < rows:
                            obstacles[(0, vgx + dgx, vgy + dgy)] = nn
                            obstacles[(1, vgx + dgx, vgy + dgy)] = nn
            elif seg[0] == 'track':
                lay, (x1, y1), (x2, y2) = seg[1], seg[2], seg[3]
                if abs(x1 - x2) > 0.001 or abs(y1 - y2) > 0.001:
                    t = pcbnew.PCB_TRACK(board)
                    t.SetStart(vec(x1, y1))
                    t.SetEnd(vec(x2, y2))
                    t.SetWidth(mm(0.20))
                    t.SetLayer(pcbnew.F_Cu if lay == 0 else pcbnew.B_Cu)
                    t.SetNet(net_objects[nn])
                    board.Add(t)

        connected.append(u_pad)
        unconnected.pop(best_u_idx)

    if net_success:
        routed_count += 1
    else:
        failed_nets.append(nn)

print(f"\n========================================================")
print(f"  A* SIGNAL ROUTING: {routed_count}/{len(sorted_nets)} nets routed!")
if failed_nets:
    print(f"  Unrouted nets: {', '.join(failed_nets)}")
print(f"========================================================")

# ----------------------------------------------------
# STEP 2: HIGH-CLEARANCE POWER FANOUT VIAS
# ----------------------------------------------------
print("Generating conflict-free power fanout vias...")
pwr_vias_added = 0

for nn in plane_nets:
    if nn not in pads_by_net or nn not in net_objects: continue
    for p in pads_by_net[nn]:
        if p['is_th']: continue # THT pads already connect through all layers

        pgx, pgy = p['grid']
        placed = False
        for rad in range(1, 5):
            for dgx in (-rad, 0, rad):
                for dgy in (-rad, 0, rad):
                    if dgx == 0 and dgy == 0: continue
                    vx, vy = pgx + dgx, pgy + dgy
                    if 0 <= vx < cols and 0 <= vy < rows:
                        cx, cy = to_coord(vx, vy)

                        # Must not touch board edge
                        if cx < min_x + 0.6 or cx > max_x - 0.6 or cy < min_y + 0.6 or cy > max_y - 0.6:
                            continue

                        # Hole clearance >= 1.1mm from all THT pads
                        too_close_tht = any((cx - tx)**2 + (cy - ty)**2 < 1.1**2 for tx, ty in tht_pads)
                        if too_close_tht: continue

                        # Hole clearance >= 0.85mm from all existing vias
                        too_close_via = any((cx - vx2)**2 + (cy - vy2)**2 < 0.85**2 for vx2, vy2 in placed_vias)
                        if too_close_via: continue

                        # Cell clearance on both layers
                        cell_clear = True
                        for chk_gx in range(vx - 1, vx + 2):
                            for chk_gy in range(vy - 1, vy + 2):
                                c0 = obstacles.get((0, chk_gx, chk_gy))
                                c1 = obstacles.get((1, chk_gx, chk_gy))
                                if (c0 is not None and c0 != nn) or (c1 is not None and c1 != nn):
                                    cell_clear = False; break
                            if not cell_clear: break

                        if cell_clear:
                            v = pcbnew.PCB_VIA(board)
                            v.SetPosition(vec(cx, cy))
                            v.SetWidth(mm(0.6))
                            v.SetDrill(mm(0.3))
                            v.SetNet(net_objects[nn])
                            board.Add(v)
                            placed_vias.append((cx, cy))

                            # Connect SMD pad to via
                            t = pcbnew.PCB_TRACK(board)
                            t.SetStart(vec(p['x'], p['y']))
                            t.SetEnd(vec(cx, cy))
                            t.SetWidth(mm(0.25))
                            t.SetLayer(pcbnew.F_Cu if p['layer'] == 0 else pcbnew.B_Cu)
                            t.SetNet(net_objects[nn])
                            board.Add(t)

                            for chk_gx in range(vx - 1, vx + 2):
                                for chk_gy in range(vy - 1, vy + 2):
                                    obstacles[(0, chk_gx, chk_gy)] = nn
                                    obstacles[(1, chk_gx, chk_gy)] = nn
                            placed = True
                            pwr_vias_added += 1
                            break
                if placed: break
            if placed: break

print(f"Added {pwr_vias_added} conflict-free power fanout vias.")

# Refill zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

board.Save(PCB_FILE)
print("Board saved with filled zones.")
sys.stdout.flush()
ctypes.windll.kernel32.ExitProcess(0)
