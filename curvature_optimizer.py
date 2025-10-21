#!/usr/bin/env python3
"""
Optimize local curvature scaling parameter for maximum candidate reduction.
Grid search over scale values to find optimal enhancement divisor.
"""

import math
import time
from test_curved_geometry import curved_geometric_factorize, generate_balanced_semiprime
from z5d_predictor import theta_prime

def test_curvature_scale(scale_divisor, N, true_p, true_q):
    """Test factorization with specific curvature scale."""
    # Temporarily modify the riemannian_dist function
    # We need to patch it for this test
    original_riemannian = None

    try:
        # Import and patch
        import test_curved_geometry
        original_riemannian = test_curved_geometry.riemannian_dist

        def patched_riemannian(a, b, N, k=None):
            base_dist = test_curved_geometry.circ_dist(a, b)
            x = math.log2(N)
            global_curvature = 1 / (2 * (1 + x**2))

            local_curvature = 0
            if k is not None:
                enhancement = theta_prime(N, k)
                local_curvature = -enhancement / scale_divisor

            warped_dist = base_dist * (1 + global_curvature + local_curvature)
            return min(max(warped_dist, 0), 1)

        test_curved_geometry.riemannian_dist = patched_riemannian

        stages = [(5, 0.05), (10, 0.002), (15, 0.0001), (20, 0.00005)]
        start_time = time.time()
        found_p, found_q, metadata = curved_geometric_factorize(N, stages, use_curved=True)
        elapsed = time.time() - start_time

        success = found_p and {found_p, found_q} == {true_p, true_q}
        reduction = metadata.get('reduction_pct', 0) if success else 0

        return {
            'scale': scale_divisor,
            'success': success,
            'time': elapsed,
            'reduction': reduction
        }

    finally:
        # Restore original
        if original_riemannian:
            test_curved_geometry.riemannian_dist = original_riemannian

def optimize_curvature():
    """Grid search over curvature scale parameters."""
    print("=== Local Curvature Optimization: Grid Search ===\n")

    # Test case
    N, true_p, true_q = generate_balanced_semiprime(34, 42)
    print(f"Test Case: N={N}, factors={true_p}×{true_q}\n")

    # Scale divisors to test
    scale_divisors = [50, 75, 100, 125, 150, 200, 300, 500, 1000]

    results = []
    for divisor in scale_divisors:
        print(f"Testing scale divisor: {divisor}")
        result = test_curvature_scale(divisor, N, true_p, true_q)
        print(f"  Result: {'SUCCESS' if result['success'] else 'FAILED'} - {result['time']:.3f}s - {result['reduction']:.1f}% reduction")
        results.append(result)

    # Find best
    successful = [r for r in results if r['success']]
    if successful:
        best = max(successful, key=lambda x: x['reduction'])
        print("\n=== OPTIMIZATION RESULTS ===")
        print(f"Best scale divisor: {best['scale']}")
        print(f"Reduction: {best['reduction']:.1f}%")
        print(f"Time: {best['time']:.3f}s")

        # Save results
        with open('curvature_optimization.log', 'w') as f:
            f.write("Curvature Scale Optimization Results\n")
            f.write("=" * 40 + "\n")
            f.write(f"Test Case: N={N}\n")
            f.write(f"True Factors: {true_p}×{true_q}\n\n")
            for r in results:
                f.write(f"Scale {r['scale']}: {'SUCCESS' if r['success'] else 'FAILED'} - {r['reduction']:.1f}% - {r['time']:.3f}s\n")
            f.write(f"\nBest: Scale {best['scale']} - {best['reduction']:.1f}% reduction\n")

        return best['scale']
    else:
        print("\nNo successful optimizations found.")
        return None

if __name__ == "__main__":
    best_scale = optimize_curvature()
    print(f"\nRecommended scale divisor: {best_scale}")
