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

def theta_prime(n, k, num_bins=24):
    """
    Simulate θ'(n,k) density enhancement as in the provided demos.
    Returns density enhancement percentage.
    """
    # Simplified simulation based on the demos
    # In real demos, it bins numbers and counts primes per bin
    # Here we approximate the enhancement based on k and N
    base_enhancement = 4.66  # Mean from discussion (bootstrap CI [3.41%, 5.69%])
    k_factor = 1 + (k - 0.3) * 0.5  # k=0.3 gives ~4.66%, others vary
    n_factor = 1 - (math.log2(n) - 30) * 0.01  # Slight dependence on log N
    enhancement = base_enhancement * k_factor * n_factor
    return max(0, enhancement)

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
    Estimates k ≈ π(√N) and searches around multiple predicted primes.
    """
    sqrt_N = int(math.sqrt(N))

    # Better k estimation: use prime counting function approximation
    # π(x) ≈ x / ln(x), so k ≈ π(√N) ≈ √N / ln(√N) = √N / (0.5 ln(N))
    k_estimate = int(sqrt_N / math.log(sqrt_N))

    # Generate candidates around multiple k values near the estimate
    # Based on discussion density data: use wider range and denser sampling (every 50th k)
    # Weight candidates by θ'(n,k) density enhancement (mean 4.66%)
    k_min = max(1, k_estimate - 1000)
    k_max = k_estimate + 1001
    k_range = range(k_min, k_max, 50)  # 41 points for better coverage
    z5d_candidates = []
    candidate_weights = {}  # prime -> weight based on θ' enhancement
    for k in k_range:
        enhancement = theta_prime(N, k)  # Density enhancement for this k
        weight = 1 + enhancement / 100  # Weight factor (e.g., 1.0466 for 4.66%)
        cands = z5d_search_candidates(k, max_offset=200)
        for cand in cands:
            z5d_candidates.append(cand)
            candidate_weights[cand] = weight

    # Traditional sieving for small primes
    sieve_candidates = list(primerange(2, min(sqrt_N + 1, 20000)))

    # Combine and deduplicate
    all_candidates = list(set(z5d_candidates + sieve_candidates))
    all_candidates = [c for c in all_candidates if c <= sqrt_N]  # Only primes <= √N

    # Sort by weight (higher weight first), default weight 1 for sieve candidates
    all_candidates.sort(key=lambda c: candidate_weights.get(c, 1), reverse=True)

    return all_candidates[:5000]  # Reasonable limit

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
