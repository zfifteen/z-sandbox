#!/usr/bin/env python3
"""
Test the refined curved geometry factorization with per-candidate local curvature.
Uses (candidate, k, weight) tuples for individualized distance calculations.
"""

import random
import math
import time
from typing import Tuple
import sympy as sp
from mpmath import mp

# Set high precision
mp.dps = 50

def is_prime_miller_rabin(n: int, rounds: int = 10) -> bool:
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23]

    def check_composite(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return False
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return False
        return True

    for witness in witnesses:
        if witness >= n:
            continue
        if check_composite(witness):
            return False
    return True

def generate_prime(bit_size: int, seed: int) -> int:
    rng = random.Random(seed)
    while True:
        p = rng.getrandbits(bit_size)
        p |= (1 << (bit_size - 1))
        p |= 1
        if is_prime_miller_rabin(p):
            return p

def generate_balanced_semiprime(bit_size: int, seed: int) -> Tuple[int, int, int]:
    half_bits = bit_size // 2
    p_bits = half_bits
    q_bits = bit_size - p_bits

    rng = random.Random(seed)
    p_seed = rng.randint(0, 2**32)
    q_seed = rng.randint(0, 2**32)

    p = generate_prime(p_bits, p_seed)
    q = generate_prime(q_bits, q_seed)

    if p > q:
        p, q = q, p

    N = p * q
    return N, p, q

# Core functions - NEW CURVED GEOMETRY
phi = (1 + mp.sqrt(5)) / 2

def theta_curved(m, k):
    if m <= 0:
        return 0.0

    x = mp.power(m / phi, k)
    sqrt_term = mp.sqrt(1 + x**2)
    arg = (sqrt_term - 1) / x
    curved_value = mp.atan(arg)
    normalized = (curved_value + mp.pi/2) / mp.pi
    return float(mp.frac(normalized))

def theta_flat(m, k):
    if m <= 0:
        return 0.0
    ratio = mp.power(m / phi, k)
    scaled = phi * ratio
    return float(mp.frac(scaled))

def circ_dist(a, b):
    diff = mp.fabs(a - b)
    return min(diff, 1 - diff)

def riemannian_dist(a, b, N, k=None):
    base_dist = circ_dist(a, b)
    x = math.log2(N)
    global_curvature = 1 / (2 * (1 + x**2))

    # Local curvature: contract in dense regions
    local_curvature = 0
    if k is not None:
        from z5d_predictor import theta_prime
        enhancement = theta_prime(N, k)
        local_curvature = -enhancement / 100  # Stronger effect: divide by 100 instead of 1000

    warped_dist = base_dist * (1 + global_curvature + local_curvature)
    return min(max(warped_dist, 0), 1)

def curved_geometric_factorize(N, stages, use_curved=True):
    from z5d_predictor import get_factor_candidates
    candidate_tuples = get_factor_candidates(N)  # Now (cand, k, weight) tuples

    initial_count = len(candidate_tuples)

    for i, (k, epsilon) in enumerate(stages):
        if not candidate_tuples:
            break
        th_n = theta_curved(mp.mpf(N), k) if use_curved else theta_flat(mp.mpf(N), k)
        new_cands = []
        for cand, cand_k, weight in candidate_tuples:
            mp_p = mp.mpf(cand)
            th_p = theta_curved(mp_p, k) if use_curved else theta_flat(mp_p, k)
            dist_k = cand_k if cand_k is not None else 0.3
            dist = riemannian_dist(th_n, th_p, N, k=dist_k) if use_curved else circ_dist(th_n, th_p)
            if dist < epsilon:
                new_cands.append((cand, cand_k, weight))
                if N % cand == 0:
                    q = N // cand
                    return cand, q, {
                        'stage_found': i+1,
                        'total_candidates': initial_count,
                        'final_candidates': len(new_cands),
                        'reduction_pct': (1 - len(new_cands)/initial_count)*100 if initial_count > 0 else 0,
                        'method': 'curved_per_candidate' if use_curved else 'flat',
                        'candidate_k': cand_k,
                        'candidate_weight': weight
                    }
        candidate_tuples = new_cands

    return None, None, {'error': 'No factor found', 'final_candidates': len(candidate_tuples), 'reduction_pct': (1 - len(candidate_tuples)/initial_count)*100 if initial_count > 0 else 0}

if __name__ == "__main__":
    test_cases = [
        (34, 42, "34-bit boundary"),
        (34, 123, "34-bit different seed"),
        (36, 456, "36-bit beyond boundary"),
    ]

    stages = [(5, 0.05), (10, 0.002), (15, 0.0001), (20, 0.00005)]

    print("=== Testing Per-Candidate Local Curvature ===\n")
    print("Enhanced local curvature: divide by 100 (vs 1000), per-candidate k assignment\n")

    for bit_size, seed, desc in test_cases:
        print(f"Testing: {desc}")
        N, true_p, true_q = generate_balanced_semiprime(bit_size, seed)
        print(f"N = {N} ({N.bit_length()} bits)")
        print(f"True factors: {true_p} × {true_q}")

        geometries = [
            ("Flat Geometry", False),
            ("Curved Per-Candidate", True),
        ]

        for geo_name, use_curved in geometries:
            print(f"\n  {geo_name}:")
            start_time = time.time()
            found_p, found_q, metadata = curved_geometric_factorize(N, stages, use_curved)
            elapsed = time.time() - start_time

            if found_p:
                success = {found_p, found_q} == {true_p, true_q}
                status = "✅ SUCCESS" if success else "❌ WRONG FACTORS"
                print(f"    {status}: {found_p} × {found_q} in {elapsed:.3f}s")
                if success:
                    print(f"    🎉 BREAKTHROUGH! Boundary dissolved!")
                    print(f"    Details: {metadata}")
            else:
                print(f"    ❌ FAILED: {elapsed:.3f}s, {metadata}")

        print("-" * 80)

    print("\n=== Analysis ===")
    print("Per-candidate k enables true local curvature adaptation.")
    print("Stronger scaling (÷100) amplifies density-based distance warping.")
    print("If breakthrough occurs: Local curvature hypothesis validated!")
