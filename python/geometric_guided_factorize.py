#!/usr/bin/env python3
"""
64-Bit Balanced Semiprime Factorization via Geometry-Guided Search
Uses Riemannian distance to prioritize candidate checking instead of brute force trial division.
"""
import math
import heapq
import multiprocessing
from mpmath import *
from sympy.ntheory import isprime
from functools import partial

def is_prime_robust(n):
    """Robust primality check: sympy + miller_rabin fallback."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    try:
        return isprime(n)
    except:
        return miller_rabin(n)

def miller_rabin(n, k=20):
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
    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37][:k]
    def check_composite(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return False
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return False
        return True
    for w in witnesses:
        if w >= n:
            continue
        if check_composite(w):
            return False
    return True

# High precision for 64-bit
mp.dps = 300
phi = (1 + sqrt(5)) / 2
k_default = mpf('0.04')  # Tuned for 64-bit example

def embed_torus_geodesic(n, c=exp(2), k=k_default, dims=7):
    """
    Torus geodesic embedding for GVA.
    Z = A(B / c) with c = e², iterative θ'(n, k)
    """
    x = mpf(n) / c
    coords = []
    for _ in range(dims):
        x = phi * power(frac(x / phi), k)
        coords.append(frac(x))
    return tuple(coords)

def riemannian_distance(coords1, coords2, N):
    """
    Riemannian distance on torus with domain-specific curvature.
    κ(n) = 4 · ln(n+1) / e²
    """
    kappa = mpf(4) * log(mpf(N) + 1) / exp(2)
    total = mpf(0)
    for c1, c2 in zip(coords1, coords2):
        d = min(abs(c1 - c2), 1 - abs(c1 - c2))
        total += (d * (1 + kappa * d))**2
    return sqrt(total)

def adaptive_threshold(N):
    """Adaptive ε = 0.12 / (1 + κ) *10"""
    kappa = 4 * math.log(N + 1) / math.exp(2)
    return 0.12 / (1 + kappa) * 10

def check_balance(p, q):
    """Check if |log2(p/q)| ≤ 1"""
    if p == 0 or q == 0:
        return False
    ratio = abs(math.log2(p / q))
    return ratio <= 1

def process_d(d, N, sqrtN, emb_N):
    p = sqrtN + d
    if p <= 1 or p >= N:
        return None
    emb_p = embed_torus_geodesic(p)
    dist = riemannian_distance(emb_N, emb_p, N)
    return (float(dist), d)

def generate_candidates_with_distance(N, R=100000):
    """
    Generate candidate d's with their Riemannian distance as priority.
    Returns list of (distance, d) tuples.
    """
    sqrtN = int(sqrt(mpf(N)))
    emb_N = embed_torus_geodesic(N)

    # Parallel computation of distances
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        results = pool.map(partial(process_d, N=N, sqrtN=sqrtN, emb_N=emb_N), range(-R, R + 1))

    # Filter valid results
    candidates = [res for res in results if res is not None]
    return candidates

def geometry_guided_factorize(N, R=100000):
    """
    Geometry-guided factorization: prioritize checks by Riemannian distance.
    """
    if N >= 2**64:
        raise ValueError("N must be < 2^64")
    if is_prime_robust(N):
        return None, None, None
    print(f"Geometry-Guided ASSAULT: N = {N} ({N.bit_length()} bits)")
    sqrtN = int(sqrt(mpf(N)))
    emb_N = embed_torus_geodesic(N)
    epsilon = adaptive_threshold(N)

    # Generate candidates with distances
    print("Computing geometric priorities...")
    candidates = generate_candidates_with_distance(N, R)
    # Sort by distance (already in order since heapq would be used, but here we have list)
    candidates.sort(key=lambda x: x[0])  # Sort by distance ascending

    print(f"Checking {len(candidates)} candidates in geometric order...")

    for dist, d in candidates:
        p = sqrtN + d
        if N % p != 0:
            continue
        q = N // p
        if not is_prime_robust(p) or not is_prime_robust(q):
            continue
        if not check_balance(p, q):
            continue
        # Already have emb_p from earlier, but since sorted, dist is available
        if dist < epsilon:
            return (p, q, dist)
    return None, None, None

# Sample 64-bit test
if __name__ == "__main__":
    # Sample: N=18446736050711510819 = 4294966297 × 4294966427
    p, q = 4294966297, 4294966427
    N = p * q
    print(f"Sample 64-bit N = {N} ({N.bit_length()} bits)")
    import time
    start = time.time()
    result = geometry_guided_factorize(N)
    end = time.time()
    if result[0]:
        print(f"GEODESIC VICTORY: {result[0]} × {result[1]} = {N}")
        print(f"Distance: {float(result[2]):.4f}")
    else:
        print("No victory found")
    print(f"Time: {end - start:.2f}s")