# Formal Mathematical Foundation: Planar Topology Embedding

## Theorem 1 (Kuratowski Planar Bus Reduction)
Let $B = \{e_1, e_2, \dots, e_N\}$ denote an ordered $N$-conductor bus originating from an IC footprint pin-out $P = (p_1, \dots, p_N)$ and terminating at connector header $C = (c_1, \dots, c_N)$ in a 2D planar Euclidean manifold $\mathbb{R}^2$.
If the cyclic permutation $\pi: P 	o C$ satisfies monotonicity:
$$\pi(i) < \pi(j) \iff i < j, \quad orall 1 \le i < j \le N$$
Then there exists a topological embedding of all $N$ interconnects on a single planar conductor layer without crossings ($\mathcal{C}(e_i \cap e_j) = \emptyset, orall i 
eq j$), bounded by minimum clearance $\delta_{min} \ge 0.15	ext{ mm}$.

### Corollary 1.1 (Orthogonal Layering & Staggered Underpass)
When routing through a corridor containing $K$ rigid topological obstacles (component courtyards, ground vias), the bus interconnects can be decomposed into orthogonal layer projections:
- Layer $L_1$ (Top, F.Cu): Horizontal components with angle $	heta \in \{0, \pi\}$
- Layer $L_4$ (Bottom, B.Cu): Vertical components with angle $	heta \in \{\pi/2, 3\pi/2\}$
Via placement for layer transitions must follow staggered underpass ordering:
$$\Delta y_{via}(i, i+1) \ge 	ext{Drill} + 2\cdot	ext{AnnularRing} + \delta_{min}$$
guaranteeing zero annular collision and preserving return ground plane integrity on $L_2$.
