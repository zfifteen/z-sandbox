#!/usr/bin/env python3
"""
Curvature Formula Ablation Study
=================================

From the issue:
"Test different curvature formulas to determine if curvature is essential or just helpful"

Tests:
1. No curvature (flat torus): κ = 0
2. Current formula: κ = 4 * log(N+1) / e²
3. Simpler: κ = log(N+1)
4. Sublinear: κ = sqrt(log(N+1))
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

def embed_torus_geodesic(n, dims=11):
    x = mpf(n) / c
    k = 0.5 / math.log2(math.log2(float(n) + 1))
    coords = []
    for _ in range(dims):
        x = phi * power(frac(x / phi), k)
        coords.append(frac(x))
    return tuple(coords)

def riemannian_distance_with_kappa(coords1, coords2, N, kappa_fn):
    """
    Riemannian distance with pluggable curvature function.
    """
    kappa = kappa_fn(N)
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

def gva_factorize_with_kappa(N, kappa_fn, dims=11, R=1000000):
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
        dist_p = riemannian_distance_with_kappa(emb_N, emb_p, N, kappa_fn)
        dist_q = riemannian_distance_with_kappa(emb_N, emb_q, N, kappa_fn)
        if dist_p < epsilon or dist_q < epsilon:
            return p, q, min(dist_p, dist_q)
    return None, None, None

def test_curvature_formulas():
    """
    Test different curvature formulas on 20 samples.
    """
    print("=" * 70)
    print("CURVATURE FORMULA ABLATION STUDY")
    print("=" * 70)
    print("\nTesting different curvature formulas on 127-bit semiprimes")
    print("Sample size: 20 per formula")
    print()
    
    # Define curvature variants
    kappa_variants = {
        'no_curvature': (lambda N: 0, "κ = 0 (flat torus)"),
        'current': (lambda N: 4 * math.log(N + 1) / c, "κ = 4·ln(N+1)/e²"),
        'simpler': (lambda N: math.log(N + 1), "κ = ln(N+1)"),
        'sublinear': (lambda N: math.sqrt(math.log(N + 1)), "κ = √(ln(N+1))"),
        'linear': (lambda N: math.log(N + 1) / c, "κ = ln(N+1)/e²"),
    }
    
    results = {}
    
    for name, (kappa_fn, description) in kappa_variants.items():
        print(f"\n{'='*70}")
        print(f"Testing: {description}")
        print('='*70)
        
        successes = 0
        total_time = 0
        distances = []
        
        # Sample N for kappa value display
        N_sample, _, _ = generate_balanced_127bit_semiprime(0)
        kappa_value = kappa_fn(N_sample)
        print(f"Sample κ value for 127-bit N: {kappa_value:.4f}")
        print()
        
        for seed in range(20):
            N, true_p, true_q = generate_balanced_127bit_semiprime(seed)
            
            start_time = time.time()
            found_p, found_q, dist = gva_factorize_with_kappa(N, kappa_fn)
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
        
        results[name] = {
            'description': description,
            'success_rate': success_rate,
            'avg_time': avg_time,
            'avg_distance': avg_dist,
            'successes': successes,
            'kappa_sample': kappa_value
        }
        
        print(f"\nResults for {description}:")
        print(f"  Success rate: {successes}/20 ({success_rate*100:.0f}%)")
        print(f"  Average time: {avg_time:.3f}s")
        if distances:
            print(f"  Average distance: {avg_dist:.6f}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Formula':<30} {'κ(N)':<12} {'Success':<12} {'Avg Time':<12}")
    print("-" * 70)
    for name in ['no_curvature', 'current', 'simpler', 'sublinear', 'linear']:
        r = results[name]
        print(f"{r['description']:<30} {r['kappa_sample']:>8.2f}    {r['success_rate']*100:>6.1f}%     {r['avg_time']:>8.3f}s")
    
    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    
    no_curve_rate = results['no_curvature']['success_rate']
    current_rate = results['current']['success_rate']
    
    if no_curve_rate > current_rate * 0.9:
        print("⚠ CURVATURE MAY NOT BE ESSENTIAL:")
        print(f"  Flat torus (κ=0): {no_curve_rate*100:.1f}%")
        print(f"  Current formula: {current_rate*100:.1f}%")
        print("  The geometric structure works even without curvature.")
    elif no_curve_rate < current_rate * 0.5:
        print("✓ CURVATURE IS CRITICAL:")
        print(f"  Flat torus (κ=0): {no_curve_rate*100:.1f}%")
        print(f"  Current formula: {current_rate*100:.1f}%")
        print("  Curvature significantly improves success rate.")
    else:
        print("⚠ CURVATURE HELPS BUT NOT CRITICAL:")
        print(f"  Flat torus (κ=0): {no_curve_rate*100:.1f}%")
        print(f"  Current formula: {current_rate*100:.1f}%")
        print("  Curvature provides modest improvement.")
    
    # Best formula
    best_name = max(results.keys(), key=lambda k: results[k]['success_rate'])
    best = results[best_name]
    print(f"\n✓ BEST FORMULA: {best['description']}")
    print(f"  Success rate: {best['success_rate']*100:.1f}%")
    
    if best_name != 'current':
        print(f"\n⚠ NOTE: Current formula may not be optimal!")
        print(f"  Consider switching to: {best['description']}")
    
    return results

if __name__ == "__main__":
    test_curvature_formulas()
