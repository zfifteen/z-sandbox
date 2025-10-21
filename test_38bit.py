#!/usr/bin/env python3
"""
38-Bit Assault: Test 5x balanced semiprimes with advanced curved factorization.
Target: <2s per factorization.
"""

import time
from test_curved_geometry import curved_geometric_factorize, generate_balanced_semiprime

def assault_38bit():
    """Launch 38-bit testbed."""
    stages = [(5, 0.05), (10, 0.002), (15, 0.0001), (20, 0.00005)]
    results = []

    print("=== 38-Bit Assault: Advanced Curved Factorization ===\n")
    print("Features: Per-candidate local curvature + adaptive ε thresholds\n")

    for i in range(5):
        seed = 100 + i * 17  # Varied seeds
        N, true_p, true_q = generate_balanced_semiprime(38, seed)
        print(f"Assault {i+1}: N={N} ({N.bit_length()} bits)")
        print(f"  Target: {true_p} × {true_q}")

        start_time = time.time()
        found_p, found_q, metadata = curved_geometric_factorize(
            N, stages, use_curved=True, use_adaptive_epsilon=True
        )
        elapsed = time.time() - start_time

        if found_p and {found_p, found_q} == {true_p, true_q}:
            success = True
            reduction = metadata.get('reduction_pct', 0)
            print("  ✅ VICTORY: Factors recovered")
            print(f"  Time: {elapsed:.3f}s")
            print(f"  Reduction: {reduction:.1f}%")
        else:
            success = False
            print("  ❌ FAILED: Boundary holds")
            print(f"  Time: {elapsed:.3f}s")

        results.append({
            'assault': i+1,
            'N': N,
            'success': success,
            'time': elapsed,
            'reduction': metadata.get('reduction_pct', 0) if success else 0
        })

        print("-" * 60)

    # Summary
    victories = sum(1 for r in results if r['success'])
    avg_time = sum(r['time'] for r in results) / len(results)
    avg_reduction = sum(r['reduction'] for r in results if r['success']) / max(victories, 1)

    print("=== ASSAULT SUMMARY ===")
    print(f"Victories: {victories}/5 ({victories*20:.0f}%)")
    print(f"Average Time: {avg_time:.3f}s")
    if victories > 0:
        print(f"Average Reduction: {avg_reduction:.1f}%")
    print(f"Target Met: {'YES' if avg_time < 2.0 else 'NO'} (<2s)")
    print(f"Boundary Status: {'BREACHED' if victories > 0 else 'HOLDS'}")

    # Log results
    with open('38bit_assault.log', 'w') as f:
        f.write("38-Bit Assault Results\n")
        f.write("=" * 40 + "\n")
        for r in results:
            f.write(f"Assault {r['assault']}: {'VICTORY' if r['success'] else 'FAILED'} - {r['time']:.3f}s - {r['reduction']:.1f}%\n")
        f.write(f"\nOverall: {victories}/5 victories - Avg time: {avg_time:.3f}s\n")

    return results

if __name__ == "__main__":
    results = assault_38bit()
