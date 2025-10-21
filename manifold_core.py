#!/usr/bin/env python3
"""
Manifold Core: 5-Torus Embedding and Riemannian A* Pathfinder
For 40-bit factorization assault - CORRECTED VERSION
"""

import math
import heapq
from mpmath import mp

# Set precision
mp.dps = 50

PHI = (1 + math.sqrt(5)) / 2

def fractional_part(x):
    """Compute fractional part of a number."""
    return float(mp.frac(x))

def embed_5torus(N, k):
    """
    Embed N into 5-torus using iterative θ' transformations.
    Corrected to match universal invariant formulation Z = A(B / c)
    """
    N_mp = mp.mpf(N)
    k_mp = mp.mpf(k)
    c = mp.exp(2)  # e² invariant
    phi = (1 + mp.sqrt(5)) / 2

    x = N_mp / c  # Start with normalized B/c
    embedding = []
    for _ in range(5):
        x_mod = mp.fmod(x, phi)
        ratio = x_mod / phi
        if ratio <= 0:
            ratio = mp.mpf('1e-50')  # Guard against zero
        x = phi * mp.power(ratio, k_mp)
        embedding.append(float(mp.frac(x)))

    return tuple(embedding)

def curvature(N):
    """
    Calculate curvature κ(n) = d(n) · ln(n+1) / e²
    where d(n) ≈ 4 for semiprimes
    """
    N_mp = mp.mpf(N)
    d_n = 4  # Approximate divisor count for semiprimes
    return mp.mpf(d_n) * mp.log(N_mp + 1) / mp.exp(2)

def riemannian_distance_5d(point1, point2, N=None):
    """
    Riemannian distance on 5-torus with proper curvature κ(n).
    Uses domain-specific discrete form with Δ_n/Δ_max weighting.
    """
    if len(point1) != 5 or len(point2) != 5:
        raise ValueError("Points must be 5D")

    kappa = curvature(mp.mpf(N)) if N else mp.mpf(0.1)  # Default if N not provided

    total_dist = 0
    for i, (c1, c2) in enumerate(zip(point1, point2)):
        # Circular distance
        diff = abs(c1 - c2)
        circ_dist = min(diff, 1 - diff)

        # Curvature warping: circ_dist * (1 + κ * circ_dist)
        # This creates stronger warping for larger distances
        warped_dist = circ_dist * (1 + kappa * circ_dist)
        total_dist += warped_dist ** 2

    return float(mp.sqrt(mp.mpf(total_dist)))

class RiemannianAStar:
    """A* pathfinder using Riemannian distance as cost."""

    def __init__(self, distance_func):
        self.distance_func = distance_func

    def heuristic(self, current, goal):
        """Heuristic: straight-line distance in 5D."""
        return self.distance_func(current, goal)

    def get_neighbors(self, point, step_size=0.01):
        """Generate neighboring points on the torus."""
        neighbors = []
        for i in range(5):
            # Small steps in each dimension
            for delta in [-step_size, step_size]:
                neighbor = list(point)
                neighbor[i] = (neighbor[i] + delta) % 1  # Torus wrapping
                neighbors.append(tuple(neighbor))
        return neighbors

    def find_path(self, start, goal, max_iterations=1000):
        """
        A* search from start to goal on the 5-torus.
        Returns path if found, None otherwise.
        """
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        iterations = 0
        while frontier and iterations < max_iterations:
            iterations += 1
            current_cost, current = heapq.heappop(frontier)

            if self.distance_func(current, goal) < 0.001:  # Close enough
                # Reconstruct path
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for neighbor in self.get_neighbors(current):
                new_cost = cost_so_far[current] + self.distance_func(current, neighbor)
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self.heuristic(neighbor, goal)
                    heapq.heappush(frontier, (priority, neighbor))
                    came_from[neighbor] = current

        return None  # No path found

def inverse_embed_5torus(point_5d, N, k):
    """
    Corrected inverse 5-torus embedding using backward θ' iteration.
    Stable implementation with proper guards.
    """
    try:
        k_mp = mp.mpf(k)
        inv_k = 1 / k_mp
        c = mp.exp(2)  # e²
        phi = (1 + mp.sqrt(5)) / 2

        # Start from coord5 and work backwards
        x = mp.mpf(point_5d[4])

        # Reverse iterations: coord5 → coord4 → ... → coord1
        for i in range(4, 0, -1):
            alpha = mp.power(phi, i+1)
            ratio = x / alpha
            if ratio <= 0:
                return None
            base = mp.power(ratio, inv_k)
            x = alpha * base

        # Now x = coord1 → recover n/c
        alpha = phi  # φ^1
        ratio = x / alpha
        if ratio <= 0:
            return None
        n_over_c = alpha * mp.power(ratio, inv_k)
        n_recovered = n_over_c * c

        # Round and validate
        p_candidate = int(mp.nint(n_recovered))
        if p_candidate <= 1 or p_candidate >= N:
            return None
        if N % p_candidate == 0:
            q_candidate = N // p_candidate
            if is_prime_basic(p_candidate) and is_prime_basic(q_candidate):
                return p_candidate
        return None
    except:
        return None

def is_prime_basic(n):
    """Basic primality check."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def recover_factors_from_path(path, N, k):
    """
    Recover factors from Riemannian A* path.
    Try inverse embedding on path points.
    """
    for point in path:
        p = inverse_embed_5torus(point, N, k)
        if p and N % p == 0:
            q = N // p
            if is_prime_basic(q):
                return p, q
    return None, None

def manifold_factorize(N, k0=0.3, max_attempts=100, use_direct=False):
    """
    Attempt factorization using 5-torus embedding and Riemannian A*.
    Now includes corrected inverse embedding for factor recovery.
    """
    print(f"Manifold factorization for N={N}")

    # Embed N
    N_embedding = embed_5torus(N, k0)

    astar = RiemannianAStar(lambda a, b: riemannian_distance_5d(a, b, N))

    # Try to reach factor embeddings (simplified: use known factor for testing)
    for attempt in range(max_attempts):
        # Perturb N_embedding to simulate factor location
        perturbation = [attempt * 0.001 % 1 for _ in range(5)]
        goal = tuple((N_embedding[i] + perturbation[i]) % 1 for i in range(5))

        path = astar.find_path(N_embedding, goal, max_iterations=200)
        if path:
            print(f"Path found in {len(path)} steps, attempt {attempt}")
            # Try to recover factors from path
            p, q = recover_factors_from_path(path, N, k0)
            if p and q:
                print(f"🎉 VICTORY: Recovered factors {p} × {q} = {p*q}")
                return p, q
            # If no factors found, continue to next attempt

    print("No factorization found within limits")
    return None, None

def test_manifold():
    """Test manifold factorization on a small case."""
    print("=== Manifold Core Test ===\n")

    # Small test case
    N = 11541040183
    result = manifold_factorize(N, k0=0.3, max_attempts=10)

    if result and result[0]:
        print(f"Manifold result: {result}")
    else:
        print("Manifold approach needs refinement")

if __name__ == "__main__":
    test_manifold()
