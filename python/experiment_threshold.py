#!/usr/bin/env python3
"""
Threshold Sensitivity Analysis
===============================

From the issue:
"Vary epsilon to find optimal threshold - find the ROC curve"

Tests epsilon multipliers: [0.5, 0.75, 1.0, 1.5, 2.0]
Tracks true positives and false positives for each threshold.
"""

import math
import time
import random
import sympy
from mpmath import mp, mpf, sqrt, power, frac, log, exp

mp.dps = 400
phi = (1 + sqrt(5)) / 2
c = float(exp(2))

def adaptive_threshold_with_mult(N, epsilon_mult=1.0):
    kappa = 4 * math.log(N + 1) / c
    return (0.2 / (1 + kappa)) * epsilon_mult

def embed_torus_geodesic(n, dims=11):
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

def gva_factorize_with_epsilon(N, epsilon_mult, dims=11, R=1000000):
    """
    Returns (found_p, found_q, distance, is_correct)
    """
    epsilon = adaptive_threshold_with_mult(N, epsilon_mult)
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

def test_threshold_sensitivity():
    """
    Test different epsilon multipliers to find optimal threshold.
    """
    print("=" * 70)
    print("THRESHOLD SENSITIVITY ANALYSIS")
    print("=" * 70)
    print("\nTesting epsilon multipliers: [0.5, 0.75, 1.0, 1.5, 2.0]")
    print("Sample size: 20 per multiplier")
    print()
    
    epsilon_multipliers = [0.5, 0.75, 1.0, 1.5, 2.0]
    results = {}
    
    # Pre-generate test cases for consistency
    test_cases = []
    for seed in range(20):
        N, true_p, true_q = generate_balanced_127bit_semiprime(seed)
        test_cases.append((N, true_p, true_q, seed))
    
    for eps_mult in epsilon_multipliers:
        print(f"\n{'='*70}")
        print(f"Testing ε × {eps_mult}")
        print('='*70)
        
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        true_negatives = 0
        total_time = 0
        distances = []
        
        for N, true_p, true_q, seed in test_cases:
            start_time = time.time()
            found_p, found_q, dist = gva_factorize_with_epsilon(N, eps_mult)
            end_time = time.time()
            elapsed = end_time - start_time
            total_time += elapsed
            
            if found_p is not None:
                if {found_p, found_q} == {true_p, true_q}:
                    true_positives += 1
                    distances.append(dist)
                    status = "✓ TP"
                else:
                    false_positives += 1
                    status = "✗ FP"
            else:
                false_negatives += 1
                status = "✗ FN"
            
            if seed < 5:  # Print first 5
                print(f"  Trial {seed}: {status} (time={elapsed:.3f}s)")
        
        total_trials = len(test_cases)
        success_rate = true_positives / total_trials
        fp_rate = false_positives / total_trials
        fn_rate = false_negatives / total_trials
        avg_time = total_time / total_trials
        avg_dist = sum(distances) / len(distances) if distances else float('inf')
        
        # Precision and Recall
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        results[eps_mult] = {
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'success_rate': success_rate,
            'fp_rate': fp_rate,
            'fn_rate': fn_rate,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'avg_time': avg_time,
            'avg_distance': avg_dist,
        }
        
        print(f"\nResults for ε × {eps_mult}:")
        print(f"  True Positives:  {true_positives}")
        print(f"  False Positives: {false_positives}")
        print(f"  False Negatives: {false_negatives}")
        print(f"  Success Rate: {success_rate*100:.1f}%")
        print(f"  Precision: {precision*100:.1f}%")
        print(f"  Recall: {recall*100:.1f}%")
        print(f"  F1 Score: {f1:.3f}")
        print(f"  Average time: {avg_time:.3f}s")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'ε Mult':<10} {'TP':<6} {'FP':<6} {'FN':<6} {'Success':<10} {'Precision':<12} {'F1':<8}")
    print("-" * 70)
    for eps_mult in epsilon_multipliers:
        r = results[eps_mult]
        print(f"{eps_mult:<10.2f} {r['true_positives']:<6} {r['false_positives']:<6} {r['false_negatives']:<6} "
              f"{r['success_rate']*100:>6.1f}%    {r['precision']*100:>8.1f}%     {r['f1']:>6.3f}")
    
    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    
    best_f1_mult = max(epsilon_multipliers, key=lambda m: results[m]['f1'])
    best_success_mult = max(epsilon_multipliers, key=lambda m: results[m]['success_rate'])
    
    print(f"Best F1 Score: ε × {best_f1_mult} (F1={results[best_f1_mult]['f1']:.3f})")
    print(f"Best Success Rate: ε × {best_success_mult} ({results[best_success_mult]['success_rate']*100:.1f}%)")
    
    # Analyze trend
    fp_rates = [results[m]['fp_rate'] for m in epsilon_multipliers]
    success_rates = [results[m]['success_rate'] for m in epsilon_multipliers]
    
    if fp_rates[-1] > 0.05:
        print("\n⚠ WARNING: High false positive rate at ε × 2.0")
        print("  Threshold may be too loose")
    
    if success_rates[0] < success_rates[-1]:
        print("\n✓ THRESHOLD OPTIMIZATION:")
        print("  Success rate increases with epsilon multiplier")
        print("  Consider using higher threshold for better recall")
    else:
        print("\n✓ THRESHOLD OPTIMIZATION:")
        print("  Lower epsilon provides better precision")
    
    # ROC-like analysis
    print("\n" + "=" * 70)
    print("ROC CURVE APPROXIMATION (TPR vs FPR)")
    print("=" * 70)
    print("Note: FPR calculation assumes we're only testing actual factors,")
    print("      so FPR represents incorrect factors accepted.")
    print()
    
    for eps_mult in epsilon_multipliers:
        r = results[eps_mult]
        tpr = r['recall']  # True Positive Rate
        fpr = r['fp_rate']  # False Positive Rate
        print(f"ε × {eps_mult}: TPR={tpr*100:>5.1f}%, FPR={fpr*100:>5.1f}%")
    
    return results

if __name__ == "__main__":
    test_threshold_sensitivity()
