#!/usr/bin/env python3
"""
Integration Example: Line-Intersection Visualization with GVA Candidate Generation

This example demonstrates how the line-intersection visualization can be used
to complement the existing GVA (Geodesic Validation Assault) candidate generation
for factorization.

This is a conceptual integration showing how the intersection oracle can bootstrap
initial candidates before applying more sophisticated geometric methods.
"""

import sys
import os

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from examples.multiplication_viz_factor import (  # noqa: E402
    intersection_based_candidates,
    draw_intersection_mult_advanced,
)


def demo_gva_integration():
    """
    Demonstrate integration concept with GVA-style factorization.

    This shows how intersection-based candidate generation can complement
    existing GVA methods:
    1. Use intersection oracle to generate initial candidate pool
    2. Rank candidates by geometric proximity (similar to Riemannian distance)
    3. Apply modulus checks on top-K candidates
    """
    print("=" * 70)
    print("GVA Integration Demo: Intersection Oracle + Candidate Ranking")
    print("=" * 70)
    print()

    # Test cases: balanced semiprimes
    test_cases = [
        (143, 11, 13, "Small semiprime"),
        (899, 29, 31, "QMC benchmark case"),
        (10403, 101, 103, "Medium semiprime"),
    ]

    for N, true_p, true_q, description in test_cases:
        print(f"Test: {description} (N={N})")
        print("-" * 70)

        # Step 1: Generate candidates using intersection oracle
        candidates = intersection_based_candidates(N, num_candidates=50)

        # Step 2: Check candidates (simulating GVA modulus testing)
        factors_found = []
        for i, candidate in enumerate(candidates):
            if N % candidate == 0:
                other_factor = N // candidate
                factors_found.append((candidate, other_factor, i))

        # Step 3: Report results
        if factors_found:
            for p, q, rank in factors_found:
                print(f"✓ Found factors: {p} × {q} = {N}")
                print(f"  Factor rank in candidate list: {rank}")
                correct = {p, q} == {true_p, true_q}
                print(f"  Correct: {correct}")
        else:
            print(f"✗ No factors found in top {len(candidates)} candidates")

        print()

    print("=" * 70)
    print("Integration Concept Summary:")
    print()
    print("The intersection oracle provides a fast initial screening that:")
    print("  1. Generates candidates clustered near √N (geometric proximity)")
    print("  2. Reduces search space for subsequent GVA Riemannian distance ranking")
    print("  3. Acts as a 'coarse filter' before fine-grained geometric analysis")
    print()
    print("Potential integration points:")
    print("  - manifold_128bit.py: Bootstrap candidates before torus embedding")
    print("  - monte_carlo.py: Use as variance-reducing strata for sampling")
    print("  - z5d_predictor.py: Combine with θ(n) embedding for refinement")
    print("=" * 70)


def demo_visualization_integration():
    """
    Demonstrate visualization integration for educational purposes.
    """
    print()
    print("=" * 70)
    print("Visualization Integration Demo")
    print("=" * 70)
    print()

    # Create visualization for a known semiprime
    N = 899  # 29 × 31
    p, q = 29, 31

    print(f"Creating visualization for N={N} = {p} × {q}")
    print()

    # Generate visualization showing factors
    draw_intersection_mult_advanced(
        p,
        q,
        highlight_factors=True,
        curvature_weight=True,
        output_file="integration_demo_899.png",
    )

    print("Visualization saved to: integration_demo_899.png")
    print()
    print("This visualization shows:")
    print("  - Line intersections encoding partial products")
    print("  - Factor candidates overlaid near √N")
    print("  - Z5D curvature weighting applied")
    print("  - Actual factors highlighted as vertical lines")
    print()
    print("Educational value:")
    print("  - Makes abstract factorization concepts concrete")
    print("  - Shows why geometric proximity matters")
    print("  - Bridges base-10 intuition to lattice theory")
    print("=" * 70)


if __name__ == "__main__":
    demo_gva_integration()
    demo_visualization_integration()

    print()
    print("Integration demo complete!")
    print()
    print("Next steps for full integration:")
    print("  1. Add intersection_based_candidates() to manifold_128bit.py")
    print("  2. Use as initial candidate generator in gva_factorize_128bit()")
    print("  3. Benchmark success rate improvement on 128-bit targets")
    print("  4. Integrate visualizations into barycentric_demo.py")
    print("  5. Add Monte Carlo sampling integration tests")
