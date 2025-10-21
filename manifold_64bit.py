#!/usr/bin/env python3
"""
64-Bit Balanced Semiprime Factorization via Geodesic Validation Assault (GVA)
Scaled with A* pathfinding, adaptive threshold, parallelization.
"""

import math
import heapq
import multiprocessing
from mpmath import *
import sympy

# High precision for 64-bit
mp.dps = 200

phi = (1 + sqrt(5)) / 2
k_default = mpf('0.35')
c = exp(2)

def embed_torus_geodesic(n, k=k_default, dims=7):
    """
    Torus geodesic embedding for GVA.
    Z = A(B / c) with c = e², iterative θ'(n, k)
    """
    x = mpf(n) / c
    coords = []
    for _ in range(dims):
        x = phi * power(frac(x / phi), k)
        coords.append(float(frac(x)))
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
    return float(sqrt(total))

def adaptive_threshold(N):
    """Adaptive ε = 0.12 / (1 + κ)"""
    kappa = 4 * math.log(N + 1) / math.exp(2)
    return 0.12 / (1 + kappa)

def check_balance(p, q):
    """Check if |log2(p/q)| ≤ 1"""
    if p == 0 or q == 0:
        return False
    ratio = abs(math.log2(p / q))
    return ratio <= 1

def a_star_search_offset(N, R=1000000):
    """
    A* search for offset d where candidate p = sqrt(N) + d works.
    Heuristic: h(d) = κ * |d| (approximation)
    """
    sqrtN = int(sqrt(mpf(N)))
    kappa = 4 * math.log(N + 1) / math.exp(2)
    emb_N = embed_torus_geodesic(N)
    epsilon = adaptive_threshold(N)

    # Priority queue: (f_score, d)
    pq = []
    heapq.heappush(pq, (0, 0))  # Start at d=0
    visited = set()

    while pq:
        f, d = heapq.heappop(pq)
        if d in visited:
            continue
        visited.add(d)
        if abs(d) > R:
            continue

        p = sqrtN + d
        if p <= 1 or p >= N:
            continue
        if N % p != 0:
            continue
        q = N // p
        if not sympy.isprime(p) or not sympy.isprime(q):
            continue
        if not check_balance(p, q):
            continue

        emb_p = embed_torus_geodesic(p)
        dist = riemannian_distance(emb_N, emb_p, N)
        if dist < epsilon:
            return p, q, dist

        # Expand to neighbors d±1
        for nd in [d - 1, d + 1]:
            if nd not in visited:
                h = kappa * abs(nd)  # Heuristic
                heapq.heappush(pq, (h, nd))  # g=0, f=h

    return None, None, None

def parallel_offset_search(N, R=1000000, cores=8):
    """
    Parallelized offset search using multiprocessing.
    """
    sqrtN = int(sqrt(mpf(N)))
    epsilon = adaptive_threshold(N)
    emb_N = embed_torus_geodesic(N)

    def check_chunk(offsets):
        for d in offsets:
            p = sqrtN + d
            if p <= 1 or p >= N:
                continue
            if N % p != 0:
                continue
            q = N // p
            if not sympy.isprime(p) or not sympy.isprime(q):
                continue
            if not check_balance(p, q):
                continue
            emb_p = embed_torus_geodesic(p)
            dist = riemannian_distance(emb_N, emb_p, N)
            if dist < epsilon:
                return p, q, dist
        return None

    pool = multiprocessing.Pool(cores)
    chunks = [range(i, R+1, cores) for i in range(cores)]
    chunks += [range(-i, -R-1, -cores) for i in range(1, cores+1)]  # Negative

    results = pool.map(check_chunk, chunks)
    pool.close()
    pool.join()

    for res in results:
        if res:
            return res
    return None, None, None

def gva_factorize_64bit(N, method='parallel', R=1000000, cores=8):
    """
    GVA for 64-bit balanced semiprimes.
    Methods: 'astar', 'parallel', 'brute'
    """
    if N >= 2**64:
        raise ValueError("N must be < 2^64")
    if not sympy.isprime(N):  # Assume semiprime, but check if prime
        pass  # For semiprime, should have two factors

    print(f"GVA-64 ASSAULT: N = {N} ({N.bit_length()} bits)")

    if method == 'astar':
        return a_star_search_offset(N, R)
    elif method == 'parallel':
        return parallel_offset_search(N, R, cores)
    else:
        # Brute force as fallback
        sqrtN = int(sqrt(mpf(N)))
        emb_N = embed_torus_geodesic(N)
        epsilon = adaptive_threshold(N)
        for d in range(-R, R+1):
            p = sqrtN + d
            if p <= 1 or p >= N:
                continue
            if N % p != 0:
                continue
            q = N // p
            if not sympy.isprime(p) or not sympy.isprime(q):
                continue
            if not check_balance(p, q):
                continue
            emb_p = embed_torus_geodesic(p)
            dist = riemannian_distance(emb_N, emb_p, N)
            if dist < epsilon:
                return p, q, dist
        return None, None, None

# Sample 64-bit test
if __name__ == "__main__":
    # Sample from issue: N=13949754606565651 = 3735288611 × 3735288601
    p, q = 3735288611, 3735288601
    N = p * q
    print(f"Sample 64-bit N = {N} ({N.bit_length()} bits)")

    import time
    start = time.time()
    result = gva_factorize_64bit(N, method='brute')
    end = time.time()

    if result[0]:
        print(f"GEODESIC VICTORY: {result[0]} × {result[1]} = {N}")
        print(f"Distance: {result[2]:.4f}")
    else:
        print("No victory found")

    print(f"Time: {end - start:.2f}s")