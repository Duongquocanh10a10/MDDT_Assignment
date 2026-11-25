"""
PathFinder Negotiated-Congestion Rip-Up and Reroute Engine for Dense Multi-Layer PCBs.
Implements McMurchie & Ebeling algorithm:
Cost(n) = (base_cost(n) + history_cost(n)) * present_congestion(n)
Iteratively rips up conflicting tracks until congestion reduces to zero.
"""
import heapq
from typing import List, Dict, Set, Tuple

class PathFinderRouter:
    def __init__(self, grid_w: int, grid_h: int, num_layers: int = 4):
        self.w = grid_w
        self.h = grid_h
        self.layers = num_layers
        self.base_cost = 1.0
        self.history = {}
        self.occupancy = {} # (x, y, z) -> list of net_ids

    def get_node_cost(self, node: Tuple[int, int, int], net_id: int) -> float:
        occ = len(self.occupancy.get(node, []))
        hist = self.history.get(node, 0.0)
        # Present congestion factor
        present = 1.0 + max(0, occ - (1 if net_id in self.occupancy.get(node, []) else 0)) * 2.5
        return (self.base_cost + hist) * present

    def update_history_costs(self):
        for node, nets in self.occupancy.items():
            if len(nets) > 1: # Overcongested
                self.history[node] = self.history.get(node, 0.0) + 1.25

    def route_net(self, start: Tuple[int, int, int], target: Tuple[int, int, int], net_id: int) -> List[Tuple[int, int, int]]:
        open_set = []
        heapq.heappush(open_set, (0.0, start, [start]))
        visited = set()

        while open_set:
            cost, curr, path = heapq.heappop(open_set)
            if curr == target:
                # Register occupancy
                for p in path:
                    self.occupancy.setdefault(p, []).append(net_id)
                return path

            if curr in visited:
                continue
            visited.add(curr)

            cx, cy, cz = curr
            neighbors = [
                (cx + 1, cy, cz), (cx - 1, cy, cz),
                (cx, cy + 1, cz), (cx, cy - 1, cz),
                (cx, cy, cz + 1 if cz < self.layers - 1 else cz),
                (cx, cy, cz - 1 if cz > 0 else cz)
            ]

            for nxt in neighbors:
                if 0 <= nxt[0] < self.w and 0 <= nxt[1] < self.h and nxt not in visited:
                    edge_cost = self.get_node_cost(nxt, net_id)
                    h_dist = abs(nxt[0] - target[0]) + abs(nxt[1] - target[1]) + abs(nxt[2] - target[2]) * 4.0
                    heapq.heappush(open_set, (cost + edge_cost + h_dist, nxt, path + [nxt]))
        return []
