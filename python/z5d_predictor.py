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
    base_enhancement = 4.66  # Mean from discussion (bootstrap CI [3.41%, 5.69%])
    k_factor = max(0.5, min(1.5, 1 + (k - 300) * 0.0001))  # Small variation around k=300
    n_factor = max(0.8, min(1.2, 1 - (math.log2(n) - 30) * 0.01))  # Small variation
    enhancement = base_enhancement * k_factor * n_factor
    return max(0, enhancement)

def z5d_predict(k):
    """
    Z5D prime predictor using high-precision arithmetic.
    Returns predicted prime location for index k.
    """
    k_mp = mpf(k)

    # Compute log(k) and log(log(k))
    log_k = log(k_mp)
    log_log_k = log(log_k)

    # Base PNT approximation
    temp1 = log_log_k - 2
    temp2 = temp1 / log_k
    temp3 = log_k + log_log_k - 1 + temp2
    pnt = k_mp * temp3

    # Density correction
    d_term = -0.00247 * pnt

    # Exponential term
    temp_exp = exp(log_k / E2)
    e_term = KAPPA_STAR_DEFAULT * temp_exp * pnt

    # Final prediction
    pred = pnt + d_term + e_term

    return int(pred)

def z5d_search_candidates(k, max_offset=500):
    """
    Generate candidate primes around Z5D prediction for index k.
    """
    center = z5d_predict(k)

    if center % 2 == 0:
        center += 1

    candidates = []

    for offset in range(max_offset + 1):
        if offset == 0:
            cand = center
        else:
            cand = center + offset * 2
            if cand > 0:
                candidates.append(cand)
            cand = center - offset * 2
            if cand > 0:
                candidates.append(cand)

    prime_candidates = [c for c in candidates if is_probable_prime_basic(c)]

    return prime_candidates[:1000]

def is_probable_prime_basic(n):
    """Basic primality check."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def get_factor_candidates(N):
    """
    Generate prime candidates for factorization of N using Z5D-enhanced approach.
    Returns list of (candidate, k, weight) tuples for per-candidate curvature.
    """
    sqrt_N = int(math.sqrt(N))

    k_estimate = int(sqrt_N / math.log(sqrt_N))

    k_min = max(1, k_estimate - 1000)
    k_max = k_estimate + 1001
    k_range = range(k_min, k_max, 50)
    candidate_data = []  # List of (candidate, k, weight)
    for k in k_range:
        enhancement = theta_prime(N, k)
        weight = 1 + enhancement / 100
        cands = z5d_search_candidates(k, max_offset=200)
        for cand in cands:
            candidate_data.append((cand, k, weight))

    # Traditional sieving for small primes
    sieve_candidates = list(primerange(2, min(sqrt_N + 1, 20000)))
    for cand in sieve_candidates:
        candidate_data.append((cand, None, 1.0))

    # Deduplicate by candidate, keeping highest weight
    best_data = {}  # candidate -> (k, weight)
    for cand, k, weight in candidate_data:
        if cand not in best_data or weight > best_data[cand][1]:
            best_data[cand] = (k, weight)

    # Filter to <= √N
    filtered_data = [(cand, k, weight) for cand, (k, weight) in best_data.items() if cand <= sqrt_N]

    # Sort by weight descending
    filtered_data.sort(key=lambda x: x[2], reverse=True)

    return filtered_data[:5000]

if __name__ == "__main__":
    print("Testing Z5D Prime Predictor with per-candidate k")
    print("=" * 50)

    test_ks = [100, 1000, 10000, 100000]
    for k in test_ks:
        pred = z5d_predict(k)
        print(f"k={k}: predicted prime ≈ {pred} (bit length: {pred.bit_length()})")

    N = 11541040183
    print(f"\nGenerating candidates for N={N}")
    candidates = get_factor_candidates(N)
    print(f"Found {len(candidates)} candidates")
    print(f"Top 5: {[(c, k, round(w, 3)) for c, k, w in candidates[:5]]}")

    true_p, true_q = 106661, 108203
    for cand, k, w in candidates[:10]:
        if cand == true_p:
            print(f"True p {true_p} found at position {candidates.index((cand, k, w))}, k={k}, weight={w:.3f}")
        elif cand == true_q:
            print(f"True q {true_q} found (but > √N, excluded)")

def geodesic_superpose(N, k_set):
    """
    Superpose multiple geodesic paths from different k starting points.
    Returns combined factor candidates.
    """
    path_candidates = set()

    for k in k_set:
        # Get Z5D prediction for this k
        pred = z5d_predict(k)

        # Search outward for candidates
        candidates = z5d_search_candidates(k, max_offset=100)

        # Add to combined set
        path_candidates.update(candidates)

        # Check if prediction itself is a factor
        if N % pred == 0:
            q = N // pred
            return pred, q  # Direct hit

    return list(path_candidates)

def adaptive_epsilon(N, k, base_epsilon=0.12):
    """
    Adaptive ε threshold based on local curvature.
    Shrinks threshold in high-density regions.
    """
    enhancement = theta_prime(N, k)
    curvature_factor = 1 + enhancement / 100  # Scale based on density
    return base_epsilon / curvature_factor

def get_superposed_candidates(N, k_set=[10, 20, 30, 40, 50]):
    """
    Get candidates using multi-scale geodesic superposition.
    """
    superposed = geodesic_superpose(N, k_set)
    return superposed
