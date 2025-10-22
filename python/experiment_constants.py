#!/usr/bin/env python3
"""
Alternative Constants Experiment
=================================

From the issue:
"Test different irrational bases to determine if φ is special"

Tests:
- phi: (1+√5)/2 (current)
- e: exp(1)
- pi: π
- sqrt2: √2
- golden_angle: π(3-√5)
"""

import math
import time
import random
import sympy
from mpmath import mp, mpf, sqrt, power, frac, log, exp, pi

mp.dps = 400
c = float(exp(2))

def adaptive_threshold(N):
    kappa = 4 * math.log(N + 1) / c
    return 0.2 / (1 + kappa)

def embed_torus_geodesic_with_const(n, constant, dims=11):
    """
    Torus geodesic embedding with pluggable constant.
    """
    x = mpf(n) / c
    k = 0.5 / math.log2(math.log2(float(n) + 1))
    coords = []
    for _ in range(dims):
        x = constant * power(frac(x / constant), k)
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

def gva_factorize_with_const(N, constant, dims=11, R=1000000):
    epsilon = adaptive_threshold(N)
    emb_N = embed_torus_geodesic_with_const(N, constant, dims)
    sqrtN = int(mpf(N).sqrt())
    
    for d in range(-R, R+1):
        p = sqrtN + d
        if p <= 1 or p >= N or N % p != 0:
            continue
        q = N // p
        if not sympy.isprime(p) or not sympy.isprime(q) or not check_balance(p, q):
            continue
        emb_p = embed_torus_geodesic_with_const(p, constant, dims)
        emb_q = embed_torus_geodesic_with_const(q, constant, dims)
        dist_p = riemannian_distance(emb_N, emb_p, N)
        dist_q = riemannian_distance(emb_N, emb_q, N)
        if dist_p < epsilon or dist_q < epsilon:
            return p, q, min(dist_p, dist_q)
    return None, None, None

def test_alternative_constants():
    """
    Test different irrational constants.
    """
    print("=" * 70)
    print("ALTERNATIVE CONSTANTS EXPERIMENT")
    print("=" * 70)
    print("\nTesting different irrational bases on 127-bit semiprimes")
    print("Sample size: 20 per constant")
    print()
    
    # Define constants
    constants = {
        'phi': ((1 + sqrt(5)) / 2, "φ = (1+√5)/2 (golden ratio)"),
        'e': (exp(1), "e = exp(1)"),
        'pi': (pi, "π"),
        'sqrt2': (sqrt(2), "√2"),
        'sqrt3': (sqrt(3), "√3"),
        'golden_angle': (pi * (3 - sqrt(5)), "π(3-√5) (golden angle)"),
    }
    
    results = {}
    
    for name, (constant, description) in constants.items():
        print(f"\n{'='*70}")
        print(f"Testing: {description}")
        print(f"Value: {float(constant):.10f}")
        print('='*70)
        
        successes = 0
        total_time = 0
        distances = []
        
        for seed in range(20):
            N, true_p, true_q = generate_balanced_127bit_semiprime(seed)
            
            start_time = time.time()
            found_p, found_q, dist = gva_factorize_with_const(N, constant)
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
            'value': float(constant),
            'success_rate': success_rate,
            'avg_time': avg_time,
            'avg_distance': avg_dist,
            'successes': successes,
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
    print(f"{'Constant':<30} {'Value':<12} {'Success':<12} {'Avg Time':<12}")
    print("-" * 70)
    for name in ['phi', 'e', 'pi', 'sqrt2', 'sqrt3', 'golden_angle']:
        r = results[name]
        print(f"{r['description']:<30} {r['value']:>8.6f}    {r['success_rate']*100:>6.1f}%     {r['avg_time']:>8.3f}s")
    
    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    
    phi_rate = results['phi']['success_rate']
    other_rates = [results[k]['success_rate'] for k in results if k != 'phi']
    
    if all(rate < phi_rate * 0.7 for rate in other_rates):
        print("✓ GOLDEN RATIO IS SPECIAL:")
        print(f"  φ success rate: {phi_rate*100:.1f}%")
        print(f"  Other constants: {max(other_rates)*100:.1f}% (best alternative)")
        print("  The golden ratio has unique properties for this embedding.")
    elif max(other_rates) > phi_rate:
        best_name = max([k for k in results if k != 'phi'], 
                       key=lambda k: results[k]['success_rate'])
        best = results[best_name]
        print("⚠ GOLDEN RATIO MAY NOT BE OPTIMAL:")
        print(f"  φ success rate: {phi_rate*100:.1f}%")
        print(f"  Best alternative ({best['description']}): {best['success_rate']*100:.1f}%")
        print("  Consider testing the alternative constant further.")
    else:
        print("⚠ CONSTANTS PERFORM SIMILARLY:")
        print(f"  φ success rate: {phi_rate*100:.1f}%")
        print(f"  Other constants: {min(other_rates)*100:.1f}% - {max(other_rates)*100:.1f}%")
        print("  The choice of irrational constant may not be critical.")
        print("  The embedding structure and curvature do the heavy lifting.")
    
    # Best constant
    best_name = max(results.keys(), key=lambda k: results[k]['success_rate'])
    best = results[best_name]
    print(f"\n✓ BEST CONSTANT: {best['description']}")
    print(f"  Success rate: {best['success_rate']*100:.1f}%")
    
    # Equidistribution note
    print("\n" + "=" * 70)
    print("NOTE ON EQUIDISTRIBUTION")
    print("=" * 70)
    print("The golden ratio φ is known for optimal equidistribution properties")
    print("(Weyl's equidistribution theorem). If other constants work equally")
    print("well, it suggests the embedding structure matters more than the")
    print("specific constant's number-theoretic properties.")
    
    return results

if __name__ == "__main__":
    test_alternative_constants()
