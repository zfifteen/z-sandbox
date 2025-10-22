#!/usr/bin/env python3
"""
127-bit Validation Experiment
=============================

This script addresses the critical question from the issue:
"What's the TRUE success rate at 127-bit?"

The issue reports 100% success on 10 samples (10/10), which is statistically
extraordinary given prior results of 16% at 128-bit.

This experiment tests 100 samples to determine if:
1. The 100% success rate holds (breakthrough)
2. It drops to 30-50% (significant improvement)
3. It reverts to ~16% (statistical fluke)

Following the exact specification from the issue.
"""

import math
import time
import random
import sympy
from mpmath import mp, mpf, sqrt, power, frac, log, exp

# High precision for 127-bit
mp.dps = 400

phi = (1 + sqrt(5)) / 2
c = float(exp(2))

def adaptive_threshold(N, epsilon_mult=1.0):
    """
    Adaptive threshold for GVA based on curvature.
    ε = 0.2 / (1 + κ) * epsilon_mult
    """
    kappa = 4 * math.log(N + 1) / c
    return (0.2 / (1 + kappa)) * epsilon_mult

def embed_torus_geodesic(n, dims=11):
    """
    Torus geodesic embedding for GVA.
    Uses adaptive k parameter: k = 0.5 / log2(log2(n+1))
    """
    x = mpf(n) / c
    # Adaptive k as specified in the issue
    k = 0.5 / math.log2(math.log2(float(n) + 1))
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
    kappa = 4 * math.log(N + 1) / c
    deltas = [min(abs(c1 - c2), 1 - abs(c1 - c2)) for c1, c2 in zip(coords1, coords2)]
    dist_sq = sum((delta * (1 + kappa * delta))**2 for delta in deltas)
    return math.sqrt(dist_sq)

def check_balance(p, q):
    """
    Check if p and q are balanced: |ln(p/q)| <= ln(2)
    """
    if p == 0 or q == 0:
        return False
    ratio = abs(math.log2(p / q))
    return ratio <= 1

def generate_balanced_127bit_semiprime(seed):
    """
    Generate N = p * q with 127-bit size.
    Uses deterministic seed for reproducibility.
    """
    random.seed(seed)
    # For 127-bit N, we need p, q around 2^63.5 each
    base = 2**63
    offset = random.randint(0, 10**6)
    p = sympy.nextprime(base + offset)
    q = sympy.nextprime(base + offset + random.randint(1, 10**5))
    N = p * q
    # Ensure it's 127-bit (not 128-bit)
    while N.bit_length() > 127:
        offset = random.randint(0, 10**6)
        p = sympy.nextprime(base + offset)
        q = sympy.nextprime(base + offset + random.randint(1, 10**5))
        N = p * q
    return N, p, q

def gva_factorize_127bit(N, dims=11, R=1000000, epsilon_mult=1.0):
    """
    GVA for 127-bit balanced semiprimes.
    Returns (p, q, distance) if successful, (None, None, None) otherwise.
    """
    epsilon = adaptive_threshold(N, epsilon_mult)
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

def validate_breakthrough(epsilon_mult=1.0, num_samples=100):
    """
    Test if 100% success rate is real.
    Run trials at 127-bit with current best config.
    
    This is THE critical experiment from the issue.
    """
    print("=" * 70)
    print("127-BIT VALIDATION EXPERIMENT")
    print("=" * 70)
    print("\nTesting hypothesis: 100% success rate at 127-bit")
    print("Prior data: 10/10 successes (100%)")
    print(f"Epsilon multiplier: {epsilon_mult}")
    print("Expected outcomes:")
    print("  - >90%: Extraordinary breakthrough")
    print("  - 30-50%: Significant improvement over 16%")
    print("  - ~16%: Confirms original findings")
    print(f"\nRunning {num_samples} samples with dims=11...")
    print()
    
    results = []
    successes = 0
    failures = 0
    total_time = 0
    successful_distances = []
    failed_min_distances = []
    
    for seed in range(num_samples):
        N, true_p, true_q = generate_balanced_127bit_semiprime(seed)
        
        start_time = time.time()
        found_p, found_q, dist = gva_factorize_127bit(N, dims=11, epsilon_mult=epsilon_mult)
        end_time = time.time()
        elapsed = end_time - start_time
        total_time += elapsed
        
        success = False
        if found_p is not None:
            if {found_p, found_q} == {true_p, true_q}:
                successes += 1
                success = True
                successful_distances.append(dist)
                print(f"Trial {seed:3d}: ✓ SUCCESS (dist={dist:.6f}, time={elapsed:.2f}s)")
            else:
                failures += 1
                print(f"Trial {seed:3d}: ✗ WRONG FACTORS")
        else:
            failures += 1
            # For failures, we'd need to track minimum distances seen
            # For now, just record the failure
            print(f"Trial {seed:3d}: ✗ NO FACTORS FOUND (time={elapsed:.2f}s)")
            
        results.append({
            'seed': seed,
            'success': success,
            'distance': dist if dist is not None else float('inf'),
            'time': elapsed,
            'N': N,
            'bits': N.bit_length()
        })
        
        # Early termination option: if we get first failure, note it
        if not success and successes + failures == 1:
            print(f"\n*** First failure at trial {seed} ***\n")
    
    success_rate = successes / num_samples
    avg_time = total_time / num_samples
    
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Success rate: {successes}/{num_samples} ({success_rate*100:.1f}%)")
    print(f"Average time: {avg_time:.2f}s")
    print(f"Total time: {total_time:.2f}s")
    
    if len(successful_distances) > 0:
        print(f"\nSuccessful distances:")
        print(f"  Min: {min(successful_distances):.6f}")
        print(f"  Max: {max(successful_distances):.6f}")
        print(f"  Avg: {sum(successful_distances)/len(successful_distances):.6f}")
    
    # Statistical analysis
    print("\n" + "=" * 70)
    print("STATISTICAL INTERPRETATION")
    print("=" * 70)
    
    if success_rate >= 0.90:
        print("RESULT: BREAKTHROUGH")
        print("The 100% success rate appears to hold!")
        print("This is a major achievement requiring immediate validation.")
    elif success_rate >= 0.30:
        print("RESULT: SIGNIFICANT IMPROVEMENT")
        print(f"Success rate of {success_rate*100:.1f}% is well above the 16% baseline.")
        print("This represents meaningful progress.")
    elif success_rate >= 0.10:
        print("RESULT: CONSISTENT WITH BASELINE")
        print(f"Success rate of {success_rate*100:.1f}% is consistent with prior 16% findings.")
        print("The initial 10/10 was likely statistical variance.")
    else:
        print("RESULT: BELOW BASELINE")
        print(f"Success rate of {success_rate*100:.1f}% is below expectations.")
        print("May need to investigate test methodology.")
    
    # Binomial confidence interval
    from scipy import stats
    ci_low, ci_high = stats.binom.interval(0.95, num_samples, success_rate)
    ci_low_pct = ci_low / num_samples * 100
    ci_high_pct = ci_high / num_samples * 100
    print(f"\n95% Confidence Interval: [{ci_low_pct:.1f}%, {ci_high_pct:.1f}%]")
    
    # Hypothesis test: is this different from 16%?
    try:
        p_value = stats.binomtest(successes, num_samples, 0.16, alternative='two-sided').pvalue
        print(f"P-value (vs 16% null hypothesis): {p_value:.4f}")
    except:
        print(f"P-value calculation skipped (scipy version issue)")
    if p_value < 0.05:
        print("  → Statistically significant difference from 16% baseline!")
    else:
        print("  → Not significantly different from 16% baseline")
    
    return success_rate, results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='127-bit GVA validation')
    parser.add_argument('--epsilon-mult', type=float, default=1.0,
                       help='Epsilon multiplier (default: 1.0)')
    parser.add_argument('--num-samples', type=int, default=100,
                       help='Number of samples to test (default: 100)')
    args = parser.parse_args()
    
    success_rate, results = validate_breakthrough(
        epsilon_mult=args.epsilon_mult,
        num_samples=args.num_samples
    )
