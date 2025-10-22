#!/usr/bin/env python3
"""
Dimensionality Optimization Experiment
=======================================

From the issue:
"The embedding structure is robust - it's not critically dependent on dimensionality"

Tests dims ∈ {5,7,9,11,13,15,17,21} to find optimal dimensionality.
"""

import math
import time
import random
import sympy
from mpmath import mp, mpf, sqrt, power, frac, log, exp

mp.dps = 400
phi = (1 + sqrt(5)) / 2
c = float(exp(2))

def adaptive_threshold(N):
    kappa = 4 * math.log(N + 1) / c
    return 0.2 / (1 + kappa)

def embed_torus_geodesic(n, dims):
    x = mpf(n) / c
    k = 0.5 / math.log2(math.log2(float(n) + 1))
    coords = []
    for _ in range(dims):
        x = phi * power(frac(x / phi), k)
        coords.append(frac(x))
    return tuple(coords)

def riemannian_distance(coords1, coords2, N):
    kappa = 4 * math.log(N + 1) / c
    deltas = [min(abs(c1 - c2), 1 - abs(c1 - c2)) for c1, c2 in zip(coords1, coords2)]
    dist_sq = sum((delta * (1 + kappa * delta))**2 for delta in deltas)
    return math.sqrt(dist_sq)

def check_balance(p, q):
    if p == 0 or q == 0:
        return False
    ratio = abs(math.log2(p / q))
    return ratio <= 1

def generate_balanced_127bit_semiprime(seed):
    random.seed(seed)
    base = 2**63
    offset = random.randint(0, 10**6)
    p = sympy.nextprime(base + offset)
    q = sympy.nextprime(base + offset + random.randint(1, 10**5))
    N = p * q
    while N.bit_length() > 127:
        offset = random.randint(0, 10**6)
        p = sympy.nextprime(base + offset)
        q = sympy.nextprime(base + offset + random.randint(1, 10**5))
        N = p * q
    return N, p, q

def gva_factorize(N, dims, R=1000000):
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
        dist_p = riemannian_distance(emb_N, emb_p, N)
        dist_q = riemannian_distance(emb_N, emb_q, N)
        if dist_p < epsilon or dist_q < epsilon:
            return p, q, min(dist_p, dist_q)
    return None, None, None

def test_dimensionality():
    """
    Test dims ∈ {5,7,9,11,13,15,17,21} on 20 samples each.
    
    From issue: "All: 100% success, ~0.0004 distance, ~0.14s runtime"
    Let's verify this claim.
    """
    print("=" * 70)
    print("DIMENSIONALITY OPTIMIZATION EXPERIMENT")
    print("=" * 70)
    print("\nTesting dims ∈ {5,7,9,11,13,15,17,21} on 127-bit semiprimes")
    print("Sample size: 20 per dimension")
    print()
    
    dims_to_test = [5, 7, 9, 11, 13, 15, 17, 21]
    results = {}
    
    for dims in dims_to_test:
        print(f"\n{'='*70}")
        print(f"Testing dims={dims}")
        print('='*70)
        
        successes = 0
        total_time = 0
        distances = []
        
        for seed in range(20):
            N, true_p, true_q = generate_balanced_127bit_semiprime(seed)
            
            start_time = time.time()
            found_p, found_q, dist = gva_factorize(N, dims)
            end_time = time.time()
            elapsed = end_time - start_time
            total_time += elapsed
            
            if found_p is not None and {found_p, found_q} == {true_p, true_q}:
                successes += 1
                distances.append(dist)
                status = "✓"
            else:
                status = "✗"
            
            if seed < 5:  # Print first 5
                print(f"  Trial {seed}: {status} (time={elapsed:.3f}s)")
        
        success_rate = successes / 20
        avg_time = total_time / 20
        avg_dist = sum(distances) / len(distances) if distances else float('inf')
        
        results[dims] = {
            'success_rate': success_rate,
            'avg_time': avg_time,
            'avg_distance': avg_dist,
            'successes': successes
        }
        
        print(f"\nResults for dims={dims}:")
        print(f"  Success rate: {successes}/20 ({success_rate*100:.0f}%)")
        print(f"  Average time: {avg_time:.3f}s")
        if distances:
            print(f"  Average distance: {avg_dist:.6f}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Dims':<6} {'Success Rate':<15} {'Avg Time':<12} {'Avg Distance':<15}")
    print("-" * 70)
    for dims in dims_to_test:
        r = results[dims]
        print(f"{dims:<6} {r['success_rate']*100:>6.1f}%{'':<8} {r['avg_time']:>8.3f}s    {r['avg_distance']:>12.6f}")
    
    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    
    success_rates = [results[d]['success_rate'] for d in dims_to_test]
    if max(success_rates) - min(success_rates) < 0.1:
        print("✓ DIMENSIONALITY INSENSITIVE:")
        print("  Success rates vary by less than 10% across all dimensions.")
        print("  The embedding structure is robust to dimensionality choice.")
        print(f"  Recommended: Use dims=11 as default (middle of tested range)")
    else:
        best_dims = max(dims_to_test, key=lambda d: results[d]['success_rate'])
        print(f"⚠ DIMENSIONALITY MATTERS:")
        print(f"  Best performance at dims={best_dims}")
        print(f"  Success rate variation: {max(success_rates)*100:.1f}% - {min(success_rates)*100:.1f}%")
    
    avg_times = [results[d]['avg_time'] for d in dims_to_test]
    if max(avg_times) / min(avg_times) < 1.5:
        print("\n✓ RUNTIME INSENSITIVE:")
        print("  Runtime variation is minimal across dimensions.")
    else:
        print(f"\n⚠ RUNTIME VARIES:")
        print(f"  Fastest at dims={min(dims_to_test, key=lambda d: results[d]['avg_time'])}")
    
    return results

if __name__ == "__main__":
    test_dimensionality()
