#!/usr/bin/env python3
"""
Elliptical Billiard Model Demo
===============================

Demonstrates the elliptical billiard model for factorization using
wavefront propagation on a curved manifold.

This example shows:
1. How the ellipse property works in log-space
2. How wavefronts converge at factor locations
3. How to extract candidate factors from peak analysis
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import numpy as np
from python.manifold_elliptic import (
    embed_elliptical_billiard,
    propagate_wavefront_sympy,
    detect_convergence_peaks,
    extract_factor_seeds,
    embedTorusGeodesic_with_elliptic_refinement,
    test_ellipse_property
)


def demo_ellipse_property():
    """Demonstrate the log-sum relation and product geometry."""
    print("\n" + "="*70)
    print("DEMO 1: Log-Sum Relation and Product Geometry")
    print("="*70)
    
    print("\nThe fundamental insight: For semiprime N = p × q,")
    print("  N = p × q  (product relationship, defines hyperbola in (p,q) plane)")
    print("  log(N) = log(p) + log(q)  (log-sum identity)")
    print("\nIn log-coordinates (log p, log q), valid factors lie on the LINE:")
    print("  x + y = log(N)")
    print("\nNote: Product geometry suggests Cassini ovals (constant product of")
    print("distances), not ellipses (constant sum). This model uses a heuristic")
    print("approximation for computational tractability.")
    
    test_cases = [
        (11, 13, "Small balanced"),
        (97, 103, "Medium balanced"),
        (7, 149, "Unbalanced"),
    ]
    
    for p, q, desc in test_cases:
        result = test_ellipse_property(p, q)
        N = result['N']
        
        print(f"\n{desc}: N = {N} = {p} × {q}")
        print(f"  Center (log(N)/2): {np.log(N)/2:.4f}")
        print(f"  log(p): {np.log(p):.4f}, distance to center: {result['distance_p_to_center']:.4f}")
        print(f"  log(q): {np.log(q):.4f}, distance to center: {result['distance_q_to_center']:.4f}")
        print(f"  Sum of distances: {result['sum_of_distances']:.4f}")
        
        balance = abs(np.log(p) - np.log(q))
        if balance < 0.5:
            print(f"  → Balanced semiprime: foci are close together")
        else:
            print(f"  → Unbalanced semiprime: foci are farther apart")


def demo_wavefront_convergence():
    """Demonstrate wavefront propagation and convergence."""
    print("\n" + "="*70)
    print("DEMO 2: Wavefront Propagation and Convergence")
    print("="*70)
    
    N = 143  # 11 × 13
    print(f"\nTesting on N = {N} (factors: 11 × 13)")
    
    print("\nStep 1: Create elliptical embedding")
    ellipse_data = embed_elliptical_billiard(N, dims=17)
    print(f"  Semi-major axis: {ellipse_data['semi_major']:.4f}")
    print(f"  Focal distance: {ellipse_data['focal_distance']:.4f}")
    print(f"  Embedded in {len(ellipse_data['focus1'])}-dimensional torus")
    
    print("\nStep 2: Propagate wavefront from N's embedding")
    print("  Solving Helmholtz equation: ∇²u + k²u = 0")
    wavefront = propagate_wavefront_sympy(ellipse_data, N)
    print(f"  Solution type: {wavefront['type']}")
    print(f"  Wave number k: {wavefront['k']:.4f}")
    print(f"  Period T = 2π/k: {2*np.pi/wavefront['k']:.4f}")
    
    print("\nStep 3: Detect convergence peaks")
    print("  Peaks occur where wavefronts self-intersect (factor locations)")
    peaks = detect_convergence_peaks(wavefront, ellipse_data, dims=17)
    print(f"  Found {len(peaks)} peaks")
    print("\n  Top 5 peaks:")
    for i, peak in enumerate(peaks[:5]):
        print(f"    {i+1}. t={peak['time']:.4f}, amplitude={peak['amplitude']:.4f}")
    
    print("\nStep 4: Extract factor candidates from peaks")
    print("  NOTE: These are APPROXIMATE SEEDS, not exact factors")
    factor_seeds = extract_factor_seeds(peaks, ellipse_data, N)
    print(f"  Generated {len(factor_seeds)} candidate pairs")
    print("\n  Top 5 candidates (approximate seeds):")
    for i, seed in enumerate(factor_seeds[:5]):
        p, q = seed['p'], seed['q']
        product = p * q
        is_correct = (product == N)
        status = "✓ EXACT" if is_correct else f"≈ {product} (seed for refinement)"
        print(f"    {i+1}. {p} × {q} = {status} (conf: {seed['confidence']:.3f})")


def demo_full_pipeline():
    """Demonstrate the full integration pipeline."""
    print("\n" + "="*70)
    print("DEMO 3: Full Integration Pipeline")
    print("="*70)
    
    test_cases = [
        143,      # 11 × 13
        323,      # 17 × 19
        10403,    # 101 × 103
    ]
    
    for N in test_cases:
        print(f"\n{'─'*70}")
        print(f"N = {N}")
        print(f"{'─'*70}")
        
        # Run full pipeline
        coords, seeds = embedTorusGeodesic_with_elliptic_refinement(N, k=0.3, dims=17)
        
        print(f"Generated {len(coords)}-D embedding with {len(seeds)} APPROXIMATE candidate seeds")
        
        if len(seeds) > 0:
            print("\nTop 3 candidates (approximate seeds for refinement):")
            for i, seed in enumerate(seeds[:3]):
                p, q = seed['p'], seed['q']
                product = p * q
                error = abs(product - N)
                error_pct = 100 * error / N
                
                print(f"  {i+1}. {p} × {q} = {product}")
                print(f"     Error: {error} ({error_pct:.2f}%)")
                print(f"     Confidence: {seed['confidence']:.4f}")
                
                if product == N:
                    print(f"     ✓✓✓ CORRECT FACTORIZATION!")


def demo_practical_application():
    """Show how to use the elliptic billiard model in practice."""
    print("\n" + "="*70)
    print("DEMO 4: Practical Application")
    print("="*70)
    
    print("\nHow to use the elliptical billiard model for factorization:")
    print("\n1. The model generates CANDIDATE SEEDS, not exact factors")
    print("2. These seeds should be used to initialize other factorization methods")
    print("3. Benefits:")
    print("   - Better initial guesses than random search")
    print("   - Captures geometric structure of the factorization problem")
    print("   - Can be combined with existing GVA/Z5D methods")
    
    print("\nExample workflow:")
    print("  1. Run elliptical billiard model → get candidate seeds")
    print("  2. Use seeds to initialize GVA geodesic search")
    print("  3. Refine with Z5D predictions around seed regions")
    print("  4. Validate with trial division")
    
    print("\nAdvantages over baseline:")
    print("  • Theoretically motivated (ellipse geometry)")
    print("  • Captures log-space relationships")
    print("  • Provides multiple candidate starting points")
    print("  • Can adapt to balanced vs unbalanced semiprimes")


def main():
    """Run all demos."""
    print("="*70)
    print("ELLIPTICAL BILLIARD MODEL FOR FACTORIZATION")
    print("="*70)
    print("\nBased on the mathematical insight:")
    print("  N = p × q  ⟺  log(N) lies on ellipse with foci at log(p), log(q)")
    print("\nWavefront propagation reveals factor locations through")
    print("self-interference patterns in the embedding space.")
    
    demo_ellipse_property()
    demo_wavefront_convergence()
    demo_full_pipeline()
    demo_practical_application()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nFor more information, see:")
    print("  • python/manifold_elliptic.py - Core implementation")
    print("  • tests/test_elliptic_billiard.py - Comprehensive tests")
    print("\n")


if __name__ == "__main__":
    main()
