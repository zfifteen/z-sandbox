#!/usr/bin/env python3
"""
Testing curved-space geometric factorization on balanced semiprimes.
Implements Metric Tensor Correction and Multi-Geodesic Superposition to probe the 34-bit boundary.
"""

import random
import math
import time
from typing import Tuple, List
import sympy as sp
from mpmath import mp

# Set high precision
mp.dps = 50

def is_prime_miller_rabin(n: int, rounds: int = 10) -> bool:
    """Miller-Rabin primality test."""
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
    """Generate a random prime of specified bit size."""
    rng = random.Random(seed)
    while True:
        p = rng.getrandbits(bit_size)
        p |= (1 << (bit_size - 1))
        p |= 1
        if is_prime_miller_rabin(p):
            return p

def generate_balanced_semiprime(bit_size: int, seed: int) -> Tuple[int, int, int]:
    """Generate a balanced semiprime N = p × q."""
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

# Core functions
phi = (1 + mp.sqrt(5)) / 2

def frac(x):
    return x - mp.floor(x)

def theta(m, k):
    a = frac(m / phi)
    b = mp.power(a, k)
    return frac(phi * b)

def circ_dist(a, b):
    diff = mp.fabs(a - b)
    return min(diff, 1 - diff)

# New curved-space functions
def get_curvature_correction(N):
    """
    Metric tensor correction based on arctan curvature.
    x = log2(N) as coordinate, curvature ~ 1/(1+x^2)
    """
    x = math.log2(N)
    curvature = 1 / (1 + x**2)
    # Correction amplifies distances for small N, reduces for large N
    correction_factor = 1 - (curvature * 0.1)
    return max(0.1, correction_factor)  # Prevent negative/too small

def generate_superimposed_map(N, k_values=[0.1, 0.3, 0.5, 0.7], max_candidates=10000):
    """
    Multi-geodesic superposition: Combine probability maps from multiple k values.
    Returns dict of candidate -> combined_score
    """
    combined_scores = {}

    for k in k_values:
        th_n = theta(N, k)
        candidates = list(sp.primerange(2, min(int(mp.sqrt(N)) + 1, max_candidates)))

        for p in candidates:
            th_p = theta(p, k)
            dist = circ_dist(th_n, th_p)
            score = 1 / (dist + 1e-10)  # Higher score for smaller distance

            if p not in combined_scores:
                combined_scores[p] = 0
            combined_scores[p] += score

    # Normalize scores
    max_score = max(combined_scores.values())
    for p in combined_scores:
        combined_scores[p] /= max_score

    return combined_scores

def curved_geometric_factorize(N, stages, use_curvature=False, use_superposition=False):
    """
    Curved-space factorization with optional enhancements.
    Returns (found_p, found_q, metadata)
    """
    mp_n = mp.mpf(N)
    sqrt_n = int(mp.sqrt(N)) + 1
    candidates = list(sp.primerange(2, min(sqrt_n, 10000)))

    if use_superposition:
        # Use multi-geodesic map for candidate ordering
        scores = generate_superimposed_map(N)
        # Sort candidates by combined score (descending)
        candidates = sorted(scores.keys(), key=lambda p: scores[p], reverse=True)
        candidates = candidates[:len(candidates)//10]  # Top 10% as initial filter

    initial_count = len(candidates)

    for i, (k, epsilon) in enumerate(stages):
        if not candidates:
            break
        th_n = theta(mp_n, k)

        if use_curvature:
            correction = get_curvature_correction(N)
            effective_epsilon = epsilon / correction  # Adjust tolerance
        else:
            effective_epsilon = epsilon

        new_cands = []
        for p in candidates:
            mp_p = mp.mpf(p)
            th_p = theta(mp_p, k)
            dist = circ_dist(th_n, th_p)

            if use_curvature:
                dist *= correction  # Apply correction to distance

            if dist < effective_epsilon:
                new_cands.append(p)
                if N % p == 0:
                    q = N // p
                    return p, q, {
                        'stage_found': i+1,
                        'total_candidates': initial_count,
                        'final_candidates': len(new_cands),
                        'reduction_pct': (1 - len(new_cands)/initial_count)*100 if initial_count > 0 else 0,
                        'method': 'curved' if use_curvature else ('superposition' if use_superposition else 'standard'),
                        'correction_factor': correction if use_curvature else None
                    }
        candidates = new_cands

    return None, None, {'error': 'No factor found', 'final_candidates': len(candidates), 'reduction_pct': (1 - len(candidates)/initial_count)*100 if initial_count > 0 else 0}

if __name__ == "__main__":
    # Test on specific boundary cases
    test_cases = [
        (34, 42, "34-bit boundary case"),
        (34, 123, "34-bit different seed"),
        (36, 456, "36-bit beyond boundary"),
    ]

    stages = [(5, 0.05), (10, 0.002), (15, 0.0001), (20, 0.00005)]

    print("=== Curved-Space Geometric Factorization Testing ===\n")

    for bit_size, seed, desc in test_cases:
        print(f"Testing: {desc}")
        N, true_p, true_q = generate_balanced_semiprime(bit_size, seed)
        print(f"N = {N} ({N.bit_length()} bits)")
        print(f"True factors: {true_p} × {true_q}")

        methods = [
            ("Standard", False, False),
            ("Metric Correction", True, False),
            ("Superposition", False, True),
            ("Combined", True, True),
        ]

        for method_name, use_curv, use_super in methods:
            print(f"\n  Method: {method_name}")
            start_time = time.time()
            found_p, found_q, metadata = curved_geometric_factorize(N, stages, use_curv, use_super)
            elapsed = time.time() - start_time

            if found_p:
                success = {found_p, found_q} == {true_p, true_q}
                status = "✅ SUCCESS" if success else "❌ WRONG FACTORS"
                print(f"    {status}: {found_p} × {found_q} in {elapsed:.3f}s")
                if success:
                    print(f"    Metadata: {metadata}")
            else:
                print(f"    ❌ FAILED: {elapsed:.3f}s, {metadata}")

        print("-" * 60)

    print("\nAnalysis: Check if curved methods improve ranking of true factors or enable factorization.")