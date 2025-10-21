#!/usr/bin/env python3
"""
Rigorous testing of geometric factorization on balanced semiprimes.
Both factors are of comparable size (roughly half the total bits).
No prior knowledge of factors used in testing.
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

def generate_balanced_semiprime(bit_size: int, seed: int) -> Tuple[int, int, int]:
    """
    Generate a balanced semiprime N = p × q where both p and q have roughly bit_size/2 bits.
    """
    half_bits = bit_size // 2
    # Make them as equal as possible, but allow slight variation
    p_bits = half_bits
    q_bits = bit_size - p_bits

    rng = random.Random(seed)
    p_seed = rng.randint(0, 2**32)
    q_seed = rng.randint(0, 2**32)

    p = generate_prime(p_bits, p_seed)
    q = generate_prime(q_bits, q_seed)

    # Ensure p <= q for consistency
    if p > q:
        p, q = q, p

    N = p * q
    return N, p, q

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

def multi_stage_geometric_factorize(N, stages, max_candidates=10000):
    """
    Attempt to factor N using geometric method, returning found factors or None.
    """
    mp_n = mp.mpf(N)
    sqrt_n = int(mp.sqrt(N)) + 1
    candidates = list(sp.primerange(2, min(sqrt_n, max_candidates)))
    initial_count = len(candidates)

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

    return None, None, {'error': 'No factor found', 'final_candidates': len(candidates), 'reduction_pct': (1 - len(candidates)/initial_count)*100 if initial_count > 0 else 0}

if __name__ == "__main__":
    # Test cases: various bit sizes for balanced semiprimes
    bit_sizes = [30, 32, 34, 36]
    seeds = [42, 123, 456, 789, 101112]  # Multiple seeds per size for statistical significance

    # Stages based on previous successful configurations
    stages = [(5, 0.05), (10, 0.002), (15, 0.0001), (20, 0.00005)]

    results = []

    print("=== Rigorous Geometric Factorization Testing on Balanced Semiprimes ===\n")

    for bit_size in bit_sizes:
        print(f"Testing {bit_size}-bit balanced semiprimes:")
        successes = 0
        total_tests = len(seeds)

        for i, seed in enumerate(seeds):
            N, true_p, true_q = generate_balanced_semiprime(bit_size, seed)
            print(f"  Test {i+1}: N={N} ({N.bit_length()} bits), p={true_p} ({true_p.bit_length()} bits), q={true_q} ({true_q.bit_length()} bits)")

            start_time = time.time()
            found_p, found_q, metadata = multi_stage_geometric_factorize(N, stages)
            elapsed = time.time() - start_time

            if found_p:
                if {found_p, found_q} == {true_p, true_q}:
                    print("    ✅ SUCCESS: Correct factors found")
                    print(f"    Time: {elapsed:.3f}s")
                    print(f"    Metadata: {metadata}")
                    successes += 1
                else:
                    print("    ❌ WRONG FACTORS: Found different primes")
                    print(f"    Found: {found_p} × {found_q}, Expected: {true_p} × {true_q}")
            else:
                print("    ❌ FAILED: No factors found")
                print(f"    Time: {elapsed:.3f}s")
                print(f"    Metadata: {metadata}")

        success_rate = successes / total_tests * 100
        print(f"  Success rate for {bit_size}-bit: {successes}/{total_tests} ({success_rate:.1f}%)\n")

        results.append({
            'bit_size': bit_size,
            'successes': successes,
            'total_tests': total_tests,
            'success_rate': success_rate
        })

    print("=== SUMMARY ===")
    for res in results:
        print(f"{res['bit_size']}-bit: {res['successes']}/{res['total_tests']} ({res['success_rate']:.1f}%)")

    # Analyze the 34-bit boundary
    thirty_four = next((r for r in results if r['bit_size'] == 34), None)
    if thirty_four:
        if thirty_four['success_rate'] == 0:
            print("\nCONCLUSION: 34-bit boundary confirmed. Geometric factorization fails on balanced semiprimes at this scale.")
        else:
            print(f"\nINTERESTING: {thirty_four['success_rate']:.1f}% success rate at 34-bit suggests potential for occasional breakthroughs.")

    print("\nThis testing uses no prior knowledge of factors - purely geometric clustering approach.")
