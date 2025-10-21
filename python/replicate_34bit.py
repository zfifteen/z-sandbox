#!/usr/bin/env python3
"""
Replicate the 34-bit breakthrough: Run 10x tests on balanced semiprimes.
Validate consistency of local curvature factorization.
"""

import random
import time
from test_curved_geometry import curved_geometric_factorize, generate_balanced_semiprime

def run_replication_tests():
    """Run 10 replication tests on 34-bit balanced semiprimes."""
    stages = [(5, 0.05), (10, 0.002), (15, 0.0001), (20, 0.00005)]
    results = []

    print("=== 34-Bit Breakthrough Replication: 10 Tests ===\n")

    for i in range(10):
        seed = 42 + i * 13  # Varied seeds
        N, true_p, true_q = generate_balanced_semiprime(34, seed)
        print(f"Test {i+1}: N={N} (factors: {true_p}×{true_q})")

        start_time = time.time()
        found_p, found_q, metadata = curved_geometric_factorize(N, stages, use_curved=True)
        elapsed = time.time() - start_time

        if found_p and {found_p, found_q} == {true_p, true_q}:
            success = True
            reduction = metadata.get('reduction_pct', 0)
            print(f"  ✅ SUCCESS: {elapsed:.3f}s, {reduction:.1f}% reduction")
        else:
            success = False
            print(f"  ❌ FAILED: {elapsed:.3f}s")

        results.append({
            'test': i+1,
            'N': N,
            'success': success,
            'time': elapsed,
            'reduction': metadata.get('reduction_pct', 0) if success else 0
        })

    # Summary
    successes = sum(1 for r in results if r['success'])
    avg_time = sum(r['time'] for r in results) / len(results)
    avg_reduction = sum(r['reduction'] for r in results if r['success']) / max(successes, 1)

    print("\n=== SUMMARY ===")
    print(f"Success Rate: {successes}/10 ({successes*10:.0f}%)")
    print(f"Average Time: {avg_time:.3f}s")
    if successes > 0:
        print(f"Average Reduction: {avg_reduction:.1f}%")
    print(f"Breakthrough Consistency: {'HIGH' if successes >= 7 else 'MODERATE' if successes >= 4 else 'LOW'}")

    return results

if __name__ == "__main__":
    results = run_replication_tests()

    # Log to file
    with open('34bit_replication.log', 'w') as f:
        f.write("34-bit Breakthrough Replication Results\n")
        f.write("=" * 40 + "\n")
        for r in results:
            f.write(f"Test {r['test']}: {'SUCCESS' if r['success'] else 'FAILED'} - {r['time']:.3f}s - {r['reduction']:.1f}%\n")
        successes = sum(1 for r in results if r['success'])
        f.write(f"\nOverall: {successes}/10 successes\n")
