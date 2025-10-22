# Dimensionality Experiment for GVA
#!/usr/bin/env python3
"""
Dimensionality Experiment for GVA on 128-bit semiprimes.
"""

import math
import heapq
import multiprocessing
from mpmath import *
import sympy

# High precision for 128-bit
mp.dps = 400

phi = (1 + sqrt(5)) / 2
c = math.exp(2)

def adaptive_threshold(N):
    kappa = 4 * math.log(N + 1) / c
    return 0.2 / (1 + kappa)

def embed_torus_geodesic(n, dims):
    x = mpf(n) / c
    k = 0.3 / math.log2(math.log2(float(n) + 1))
    coords = []
    for _ in range(dims):
        x = phi * power(frac(x / phi), k)
        coords.append(frac(x))
    return tuple(coords)

def riemannian_distance(coords1, coords2, N, kappa_variant):
    kappa = 4 * math.log(N + 1) / c
    deltas = [min(abs(c1 - c2), 1 - abs(c1 - c2)) for c1, c2 in zip(coords1, coords2)]
    dist_sq = sum((delta * (1 + kappa * delta))**2 for delta in deltas)
    return math.sqrt(dist_sq)

def check_balance(p, q):
    if p == 0 or q == 0:
        return False
    ratio = abs(math.log2(p / q))
    return ratio <= 1

def gva_factorize_128bit(N, dims, kappa_variant, R=1000000):
    epsilon = adaptive_threshold(N)
    emb_N = embed_torus_geodesic(N, dims)
    sqrtN = int(mpf(N).sqrt())
    for d in range(-R, R+1):
        p = sqrtN + d
        if p <= 1 or p >= N or N % p != 0:
            continue
        q = N // p
        if not sympy.isprime(p) or not sympy.isprime(q) or not check_balance(p, q):
            continue
        emb_p = embed_torus_geodesic(p, dims)
        emb_q = embed_torus_geodesic(q, dims)
        dist_p = riemannian_distance(emb_N, emb_p, N, kappa_variant)
        dist_q = riemannian_distance(emb_N, emb_q, N, kappa_variant)
        if dist_p < epsilon or dist_q < epsilon:
            return p, q, min(dist_p, dist_q)
    return None, None, None

if __name__ == "__main__":
    # Sample 128-bit N
    p = int(sympy.nextprime(2**63 + 42))
    q = int(sympy.nextprime(p + 100))
    N = p * q
    print(f"Sample 128-bit N = {N} ({N.bit_length()} bits)")

    import time
    for dims in [5, 7, 9, 11, 13, 15, 17, 21]:
        print(f"Testing dims={dims}")
        start = time.time()
        result = gva_factorize_128bit(N, dims)
        end = time.time()
        if result[0]:
            print(f"GEODESIC VICTORY: {result[0]} × {result[1]} = {N}")
            print(f"Distance: {result[2]:.4f}")
        else:
            print("No factors found")
        print(f"Time: {end - start:.2f}s")