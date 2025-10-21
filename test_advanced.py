#!/usr/bin/env python3
"""
Advanced test script for geometric factorization research - pushing to 60+ bits.
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

    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23]  # Sufficient for n < 2^64

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

def generate_unbalanced_semiprime(small_prime: int, large_bits: int, seed: int) -> Tuple[int, int, int]:
    """Generate N = small_prime * large_prime, where large_prime has large_bits."""
    large_prime = generate_prime(large_bits, seed)
    N = small_prime * large_prime
    return N, small_prime, large_prime

# Geometric factorization functions
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

def multi_stage_geometric_factorize(N, stages, max_candidates=50000):
    mp_n = mp.mpf(N)
    sqrt_n = int(mp.sqrt(N)) + 1
    candidates = list(sp.primerange(2, min(sqrt_n, max_candidates)))
    initial_count = len(candidates)
    reduction_data = []

    for i, (k, epsilon) in enumerate(stages):
        if not candidates:
            break
        th_n = theta(mp_n, k)
        new_cands = []
        for p in candidates:
            mp_p = mp.mpf(p)
            th_p = theta(mp_p, k)
            d = circ_dist(th_n, th_p)
            if d < epsilon:
                new_cands.append(p)
                if N % p == 0:
                    q = N // p
                    return p, q, {
                        'stage_found': i+1,
                        'total_candidates': initial_count,
                        'final_candidates': len(new_cands),
                        'reduction_pct': (1 - len(new_cands)/initial_count)*100 if initial_count > 0 else 0,
                        'stages_processed': i+1
                    }
        candidates = new_cands
        reduction_data.append({
            'stage': i+1,
            'candidates_after': len(candidates),
            'reduction_pct': (1 - len(candidates)/initial_count)*100 if initial_count > 0 else 0
        })

    return None, None, {'error': 'No factor found', 'reduction_data': reduction_data}

if __name__ == "__main__":
    # Test multiple bit sizes
    test_cases = [
        (1031, 40, 42, "50-bit"),  # Original success
        (1031, 50, 123, "60-bit"),  # Push to 60-bit
        (1031, 60, 456, "70-bit"),  # Push further
    ]

    stages_options = [
        [(5, 0.05), (10, 0.002), (15, 0.0001), (20, 0.00005)],  # Extended
        [(1, 0.1), (5, 0.02), (10, 0.001), (15, 0.0001)],  # Different k
        [(10, 0.01), (20, 0.001), (30, 0.0001)],  # Higher k
    ]

    results = []

    for small_prime, large_bits, seed, label in test_cases:
        print(f"\n=== Testing {label} unbalanced semiprime ===")
        try:
            N, p, q = generate_unbalanced_semiprime(small_prime, large_bits, seed)
            print(f"N = {N} ({N.bit_length()} bits)")
            print(f"p = {p} ({p.bit_length()} bits)")
            print(f"q = {q} ({q.bit_length()} bits)")
            print(f"Verification: p * q = {p * q} == N? {p * q == N}")

            success = False
            for i, stages in enumerate(stages_options):
                print(f"\nTesting stages option {i+1}: {stages}")
                start_time = time.time()
                result_p, result_q, metadata = multi_stage_geometric_factorize(N, stages)
                elapsed = time.time() - start_time

                if result_p:
                    print(f"SUCCESS: Found factors {result_p} × {result_q}")
                    print(f"Correct? {result_p * result_q == N}")
                    print(f"Time: {elapsed:.3f}s")
                    print(f"Metadata: {metadata}")
                    results.append({
                        'label': label,
                        'N': N,
                        'bits': N.bit_length(),
                        'success': True,
                        'stages_option': i+1,
                        'time': elapsed,
                        'reduction_pct': metadata.get('reduction_pct', 0)
                    })
                    success = True
                    break  # Success, no need for other stages
                else:
                    print(f"FAILED: No factors found in {elapsed:.3f}s")
                    print(f"Metadata: {metadata}")

            if not success:
                results.append({
                    'label': label,
                    'N': N,
                    'bits': N.bit_length(),
                    'success': False,
                    'stages_option': None,
                    'time': None,
                    'reduction_pct': None
                })

        except Exception as e:
            print(f"Error in {label}: {e}")
            results.append({
                'label': label,
                'error': str(e)
            })

    print("\n=== SUMMARY ===")
    for res in results:
        if 'error' in res:
            print(f"{res['label']}: ERROR - {res['error']}")
        elif res['success']:
            print(f"{res['label']}: SUCCESS - {res['bits']} bits, {res['time']:.3f}s, {res['reduction_pct']:.1f}% reduction")
        else:
            print(f"{res['label']}: FAILED - {res['bits']} bits")
