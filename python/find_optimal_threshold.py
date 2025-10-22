#!/usr/bin/env python3
"""
Find Optimal Threshold
=======================

Efficiently tests multiple epsilon multipliers to find optimal threshold.
Uses 50 samples per multiplier for statistical reliability.
"""

import sys
sys.path.insert(0, '.')

from validate_127bit import (
    generate_balanced_127bit_semiprime,
    gva_factorize_127bit
)
import time

def test_epsilon_mult(epsilon_mult, num_samples=50):
    """Test a specific epsilon multiplier."""
    successes = 0
    total_time = 0
    
    for seed in range(num_samples):
        N, true_p, true_q = generate_balanced_127bit_semiprime(seed)
        
        start = time.time()
        found_p, found_q, dist = gva_factorize_127bit(N, dims=11, epsilon_mult=epsilon_mult)
        elapsed = time.time() - start
        total_time += elapsed
        
        if found_p is not None and {found_p, found_q} == {true_p, true_q}:
            successes += 1
    
    success_rate = successes / num_samples
    avg_time = total_time / num_samples
    
    return {
        'epsilon_mult': epsilon_mult,
        'successes': successes,
        'success_rate': success_rate,
        'avg_time': avg_time,
        'total_time': total_time
    }

def main():
    print("=" * 70)
    print("OPTIMAL THRESHOLD FINDER")
    print("=" * 70)
    print("\nTesting epsilon multipliers on 50 samples each")
    print("Searching for optimal balance of success vs precision")
    print()
    
    # Test range of multipliers
    epsilon_multipliers = [1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0]
    results = []
    
    for eps_mult in epsilon_multipliers:
        print(f"Testing ε × {eps_mult}...", end=' ', flush=True)
        result = test_epsilon_mult(eps_mult, num_samples=50)
        results.append(result)
        print(f"Success: {result['successes']}/50 ({result['success_rate']*100:.0f}%), "
              f"Avg time: {result['avg_time']:.2f}s")
    
    # Summary
    print()
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"{'ε Mult':<10} {'Success':<12} {'Avg Time':<12} {'Total Time'}")
    print("-" * 70)
    for r in results:
        print(f"{r['epsilon_mult']:<10.1f} {r['successes']:>3}/50 ({r['success_rate']*100:>5.1f}%)  "
              f"{r['avg_time']:>8.2f}s    {r['total_time']:>8.1f}s")
    
    # Analysis
    print()
    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    
    best = max(results, key=lambda r: r['success_rate'])
    print(f"\nBest success rate: ε × {best['epsilon_mult']} ({best['success_rate']*100:.1f}%)")
    
    # Find knee point (diminishing returns)
    for i in range(1, len(results)):
        improvement = results[i]['success_rate'] - results[i-1]['success_rate']
        if improvement < 0.05:  # Less than 5% improvement
            print(f"Diminishing returns after ε × {results[i-1]['epsilon_mult']}")
            break
    
    # Compare to baseline
    if best['success_rate'] > 0.16:
        print(f"\n✓ IMPROVEMENT OVER 16% BASELINE")
        print(f"  127-bit with ε × {best['epsilon_mult']}: {best['success_rate']*100:.1f}%")
        print(f"  Baseline 128-bit: 16%")
        print(f"  Improvement: +{(best['success_rate'] - 0.16) * 100:.1f}%")
    
    # Recommendation
    print()
    print("=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)
    
    # Find sweet spot (good success, not too loose)
    reasonable = [r for r in results if r['success_rate'] > 0.20]
    if reasonable:
        recommended = min(reasonable, key=lambda r: r['epsilon_mult'])
        print(f"\nRecommended threshold: ε × {recommended['epsilon_mult']}")
        print(f"  Success rate: {recommended['success_rate']*100:.1f}%")
        print(f"  Average time: {recommended['avg_time']:.2f}s")
        print(f"  Rationale: Good balance of success and precision")
    else:
        print(f"\nRecommended threshold: ε × {best['epsilon_mult']}")
        print(f"  Success rate: {best['success_rate']*100:.1f}%")
        print(f"  Rationale: Best performance in tested range")
    
    print()
    print("Note: Run with 100 samples for publication-quality results:")
    print(f"  python3 validate_127bit.py --epsilon-mult {recommended['epsilon_mult'] if reasonable else best['epsilon_mult']} --num-samples 100")

if __name__ == "__main__":
    main()
