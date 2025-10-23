#!/usr/bin/env python3
"""
Reproduction of GVA Simulations for 256-bit and 512-bit Semiprimes
Based on GOAL.md specifications
"""

import math
import time
from mpmath import *

# Set high precision for large numbers
mp.dps = 200

phi = (1 + sqrt(5)) / 2
c = math.exp(2)

def compute_kappa(N):
    """Compute Riemannian curvature κ(N) = 4 * ln(N+1) / e²"""
    return 4 * log(mpf(N) + 1) / c

def compute_k(N):
    """Compute resolution scalar k = 0.3 / log₂(log₂(N))"""
    return 0.3 / log2(log2(mpf(N)))

def compute_theta_prime(k):
    """Compute angular resolution θ' = 2πk"""
    return 2 * pi * k

def compute_sqrt_N(N):
    """Compute high-precision square root of N"""
    return sqrt(mpf(N))

def adaptive_threshold(N):
    """Adaptive threshold ε = 0.2 / (1 + κ)"""
    kappa = compute_kappa(N)
    return 0.2 / (1 + kappa)

def embed_torus_geodesic(n, dims=11):
    """Torus geodesic embedding"""
    x = mpf(n) / c
    k = compute_k(n)
    coords = []
    for _ in range(dims):
        x = phi * power(frac(x / phi), k)
        coords.append(frac(x))
    return tuple(coords)

def riemannian_distance(coords1, coords2, N):
    """Riemannian distance on torus"""
    kappa = compute_kappa(N)
    deltas = [min(abs(c1 - c2), 1 - abs(c1 - c2)) for c1, c2 in zip(coords1, coords2)]
    dist_sq = sum((delta * (1 + kappa * delta))**2 for delta in deltas)
    return sqrt(dist_sq)

def check_balance(p, q):
    """Check balance: |log₂(p/q)| <= 1"""
    if p == 0 or q == 0:
        return False
    ratio = abs(log2(mpf(p) / mpf(q)))
    return ratio <= 1

def gva_factorize(N, R=1000000, step_size=1):
    """GVA factorization with stepping"""
    epsilon = adaptive_threshold(N)
    emb_N = embed_torus_geodesic(N)
    sqrtN = int(compute_sqrt_N(N))
    iterations = 0

    # Step towards p and q directions (simplified A* like stepping)
    for direction in [-1, 1]:
        candidate = sqrtN
        for i in range(R):
            candidate += direction * step_size
            iterations += 1
            if candidate <= 1 or candidate >= N or N % candidate != 0:
                continue
            p = candidate
            q = N // p
            if not (isprime(p) and isprime(q)):
                continue
            if not check_balance(p, q):
                continue
            emb_p = embed_torus_geodesic(p)
            emb_q = embed_torus_geodesic(q)
            dist_p = riemannian_distance(emb_N, emb_p, N)
            dist_q = riemannian_distance(emb_N, emb_q, N)
            min_dist = min(dist_p, dist_q)
            if min_dist < epsilon:
                return p, q, float(min_dist), iterations
    return None, None, None, iterations

def run_simulation(name, p, q, expected_success=True):
    """Run simulation for given p, q"""
    N = p * q
    print(f"\n=== {name} Simulation ===")
    print(f"p = {p}")
    print(f"q = {q}")
    print(f"N = {N} ({N.bit_length()} bits)")

    # Compute parameters
    kappa = compute_kappa(N)
    k = compute_k(N)
    theta_prime = compute_theta_prime(k)
    sqrt_N = compute_sqrt_N(N)

    print(f"\nκ(N) = {kappa}")
    print(f"k = {k}")
    print(f"φ = {phi}")
    print(f"θ' = {theta_prime}")
    print(f"√N = {sqrt_N}")

    # Attempt factorization
    start_time = time.time()
    result = gva_factorize(N, R=1000000, step_size=1)
    end_time = time.time()

    runtime = end_time - start_time
    success = result[0] is not None
    print(f"\nSuccess: {success}")
    if success:
        found_p, found_q, dist, iters = result
        print(f"Factors: [{found_p}, {found_q}]")
        print(f"Balance Check: |log₂(p/q)| ≈ {abs(log2(mpf(found_p)/mpf(found_q))):.6f} ≤ 1? {check_balance(found_p, found_q)}")
        print(f"Runtime: {runtime:.4f} s")
        print(f"Iterations: {iters}")
        print(f"Z-Guard: {iters} / 10^6 ≈ {iters/1000000:.3f} < 1? {iters < 1000000}")
    else:
        print(f"Runtime: {runtime:.4f} s (no success)")

    return success, runtime, result

if __name__ == "__main__":
    # 256-bit exact values from GOAL.md
    p_256 = 278740696864128514312399069880853440543
    q_256 = 278740696864128514312399069880853887911

    # 512-bit exact values from GOAL.md
    p_512 = 32143673861973166475031346481898343462879321300384830086262659798768353509133
    q_512 = 32143673861973166475031346481898343462879321300384830086262659798768354192651

    # Run 256-bit simulation
    success_256, runtime_256, result_256 = run_simulation("256-bit", p_256, q_256)

    # Run 512-bit simulation (may take longer)
    print("\nNote: 512-bit simulation may take significant time...")
    success_512, runtime_512, result_512 = run_simulation("512-bit", p_512, q_512)

    # Summary
    print("\n=== Reproduction Summary ===")
    print(f"256-bit Success: {success_256}, Runtime: {runtime_256:.4f}s")
    print(f"512-bit Success: {success_512}, Runtime: {runtime_512:.4f}s")