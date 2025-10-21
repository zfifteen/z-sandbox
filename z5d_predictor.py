#!/usr/bin/env python3
"""
Z5D Prime Predictor - Python implementation based on geodesic_z5d_search.c
Provides high-precision prime prediction for efficient candidate generation.
"""

import math
from mpmath import mp, mpf, log, exp
from sympy import primerange

# Constants from the C code
KAPPA_GEO_DEFAULT = 0.3
KAPPA_STAR_DEFAULT = 0.04449
PHI = (1 + math.sqrt(5)) / 2
E2 = math.exp(2)  # e^2 invariant

# Set high precision
mp.dps = 256  # Match C code's MP_DPS

def z5d_predict(k):
    """
    Z5D prime predictor using high-precision arithmetic.
    Returns predicted prime location for index k.

    Based on: pred = pnt + d_term + e_term
    where pnt is the prime number theorem approximation,
    d_term is the density correction, e_term is the exponential scaling.
    """
    k_mp = mpf(k)

    # Compute log(k) and log(log(k))
    log_k = log(k_mp)
    log_log_k = log(log_k)

    # Base PNT approximation: k * (log(k) + log(log(k)) - 1 + (log(log(k)) - 2)/log(k))
    temp1 = log_log_k - 2
    temp2 = temp1 / log_k
    temp3 = log_k + log_log_k - 1 + temp2
    pnt = k_mp * temp3

    # Density correction: d_term = -0.00247 * pnt
    d_term = -0.00247 * pnt

    # Exponential term: e_term = KAPPA_STAR_DEFAULT * exp(log(k)/E2) * pnt
    temp_exp = exp(log_k / E2)
    e_term = KAPPA_STAR_DEFAULT * temp_exp * pnt

    # Final prediction
    pred = pnt + d_term + e_term

    return int(pred)

def z5d_search_candidates(k, max_offset=500):
    """
    Generate candidate primes around Z5D prediction for index k.
    Returns list of candidate primes using outward search strategy.
    """
    center = z5d_predict(k)

    # Make center odd
    if center % 2 == 0:
        center += 1

    candidates = []

    # Search outward: center, then ±2, ±4, etc.
    for offset in range(max_offset + 1):
        if offset == 0:
            cand = center
        else:
            # Test center + offset*2
            cand = center + offset * 2
            if cand > 0:  # Ensure positive
                candidates.append(cand)

            # Test center - offset*2
            cand = center - offset * 2
            if cand > 0:
                candidates.append(cand)

    # Filter to probable primes (basic check, could use Miller-Rabin)
    prime_candidates = [c for c in candidates if is_probable_prime_basic(c)]

    return prime_candidates[:1000]  # Limit for practicality

def is_probable_prime_basic(n):
    """Basic primality check for filtering."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # Check divisibility by small primes
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def get_factor_candidates(N):
    """
    Generate prime candidates for factorization of N using Z5D-enhanced approach.
    Estimates k ≈ N / log(N) and searches around predicted primes.
    """
    # Rough estimate of prime index for factors near √N
    sqrt_N = int(math.sqrt(N))
    k_estimate = int(sqrt_N / math.log(sqrt_N))

    # Get candidates around the estimated k
    candidates = z5d_search_candidates(k_estimate)

    # Also add some from traditional sieving for completeness
    sieve_candidates = list(primerange(2, min(sqrt_N + 1, 10000)))

    # Combine and deduplicate
    all_candidates = list(set(candidates + sieve_candidates))
    all_candidates.sort()

    return all_candidates

if __name__ == "__main__":
    # Test the Z5D predictor
    print("Testing Z5D Prime Predictor")
    print("=" * 40)

    test_ks = [100, 1000, 10000, 100000]
    for k in test_ks:
        pred = z5d_predict(k)
        print(f"k={k}: predicted prime ≈ {pred} (bit length: {pred.bit_length()})")

    # Test candidate generation for a semiprime
    N = 11541040183  # 34-bit from our tests
    print(f"\nGenerating candidates for N={N}")
    candidates = get_factor_candidates(N)
    print(f"Found {len(candidates)} candidates")
    print(f"Sample candidates: {candidates[:10]}")

    # Check if true factors are in candidates
    true_p, true_q = 106661, 108203
    p_found = true_p in candidates
    q_found = true_q in candidates
    print(f"True p ({true_p}) in candidates: {p_found}")
    print(f"True q ({true_q}) in candidates: {q_found}")