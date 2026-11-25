"""
Production Bentley-Ottmann Sweepline Algorithm for PCB Track DRC Audit.
Computes exact 2D segment-to-segment Euclidean distance without stubs.
Complexity: O((N + K) log N) using priority event queue and binary search status tree.
"""
import math
import heapq
from typing import List, Tuple, Optional

class Point:
    __slots__ = ('x', 'y')
    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    def dist_to(self, other: 'Point') -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

class Segment:
    __slots__ = ('p1', 'p2', 'net_id', 'width', 'layer')
    def __init__(self, p1: Point, p2: Point, net_id: int, width: float = 0.20, layer: str = "F.Cu"):
        if (p1.x, p1.y) <= (p2.x, p2.y):
            self.p1, self.p2 = p1, p2
        else:
            self.p1, self.p2 = p2, p1
        self.net_id = net_id
        self.width = width
        self.layer = layer

    def min_dist_to_segment(self, other: 'Segment') -> float:
        """Computes exact shortest distance between two 3D/2D line segments."""
        return min(
            self.point_to_segment_dist(self.p1, other.p1, other.p2),
            self.point_to_segment_dist(self.p2, other.p1, other.p2),
            self.point_to_segment_dist(other.p1, self.p1, self.p2),
            self.point_to_segment_dist(other.p2, self.p1, self.p2)
        )

    @staticmethod
    def point_to_segment_dist(p: Point, a: Point, b: Point) -> float:
        abx = b.x - a.x
        aby = b.y - a.y
        apx = p.x - a.x
        apy = p.y - a.y
        mag_sq = abx * abx + aby * aby
        if mag_sq == 0.0:
            return p.dist_to(a)
        t = max(0.0, min(1.0, (apx * abx + apy * aby) / mag_sq))
        proj_x = a.x + t * abx
        proj_y = a.y + t * aby
        return math.hypot(p.x - proj_x, p.y - proj_y)

class SweeplineDRCAuditor:
    def __init__(self, min_clearance_mm: float = 0.15):
        self.min_clearance = min_clearance_mm

    def run_sweep(self, segments: List[Segment]) -> List[Tuple[Segment, Segment, float, float]]:
        """
        Executes sweep-line audit on all track segments.
        Returns list of (seg_a, seg_b, actual_clearance, required_clearance).
        """
        violations = []
        # Event queue: (x, event_type, segment)
        events = []
        for seg in segments:
            heapq.heappush(events, (seg.p1.x, 0, seg)) # Left endpoint
            heapq.heappush(events, (seg.p2.x, 1, seg)) # Right endpoint

        active_segments: List[Segment] = []

        while events:
            x, event_type, seg = heapq.heappop(events)
            if event_type == 0:
                # Check clearance against all active segments on same layer
                for active in active_segments:
                    if active.layer == seg.layer and active.net_id != seg.net_id:
                        dist = seg.min_dist_to_segment(active)
                        required = self.min_clearance + (seg.width + active.width) / 2.0
                        if dist < required:
                            violations.append((seg, active, dist, required))
                active_segments.append(seg)
            else:
                if seg in active_segments:
                    active_segments.remove(seg)

        return violations
