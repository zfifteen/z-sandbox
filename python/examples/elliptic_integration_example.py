#!/usr/bin/env python3
"""
Integration Example: Elliptical Billiard Model with GVA
=========================================================

This example shows how to integrate the elliptical billiard model
with existing GVA (Geodesic Validation Assault) methods.

The workflow:
1. Use elliptical billiard to generate candidate seeds
2. Initialize GVA search around each seed
3. Validate candidates using existing methods
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import numpy as np
from python.manifold_elliptic import (
    embedTorusGeodesic_with_elliptic_refinement,
    test_ellipse_property
)


def generate_candidates_around_seed(p_seed, N, radius=100):
    """
    Generate candidates around a seed value.
    This simulates a GVA-style search in the neighborhood of a seed.
    
    Args:
        p_seed: Seed value for factor p
        N: The semiprime to factor
        radius: Search radius around seed
    
    Returns:
        List of candidate values
    """
    candidates = []
    sqrt_N = int(np.sqrt(N))
    
    # Search in a window around the seed
    start = max(2, min(p_seed - radius, sqrt_N - radius))
    end = min(N, max(p_seed + radius, sqrt_N + radius))
    
    for p in range(start, end):
        if N % p == 0:
            q = N // p
            candidates.append((p, q))
    
    return candidates


def elliptic_gva_hybrid(N, top_k=5, search_radius=100):
    """
    Hybrid approach combining elliptical billiard seeds with GVA-style search.
    
    Args:
        N: The semiprime to factor
        top_k: Number of top seeds to explore
        search_radius: How far to search around each seed
    
    Returns:
        Dictionary with results
    """
    print(f"\n{'='*70}")
    print(f"Hybrid Elliptic-GVA Factorization: N = {N}")
    print(f"{'='*70}\n")
    
    # Step 1: Generate seeds using elliptical billiard model
    print("Step 1: Generating candidate seeds with elliptical billiard model...")
    coords, seeds = embedTorusGeodesic_with_elliptic_refinement(N, k=0.3, dims=17)
    
    print(f"  Generated {len(seeds)} candidate seeds")
    print(f"  Will explore top {top_k} seeds\n")
    
    # Step 2: For each seed, perform local search
    print("Step 2: Local search around top seeds...")
    
    all_candidates = []
    for i, seed in enumerate(seeds[:top_k]):
        p_seed = seed['p']
        confidence = seed['confidence']
        
        print(f"\n  Seed {i+1}: p ≈ {p_seed} (confidence: {confidence:.3f})")
        
        # Search around this seed
        candidates = generate_candidates_around_seed(p_seed, N, search_radius)
        
        if candidates:
            print(f"    ✓ Found {len(candidates)} candidates in neighborhood")
            for p, q in candidates:
                all_candidates.append({
                    'p': p,
                    'q': q,
                    'seed_index': i,
                    'seed_confidence': confidence,
                    'distance_from_seed': abs(p - p_seed)
                })
        else:
            print(f"    ✗ No candidates found in radius {search_radius}")
    
    # Step 3: Validate and rank candidates
    print(f"\n{'─'*70}")
    print("Step 3: Validating candidates...")
    
    valid_factors = []
    for candidate in all_candidates:
        p, q = candidate['p'], candidate['q']
        if p * q == N:
            valid_factors.append(candidate)
            print(f"  ✓✓✓ VALID: {p} × {q} = {N}")
            print(f"      From seed #{candidate['seed_index']+1}")
            print(f"      Distance from seed: {candidate['distance_from_seed']}")
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Seeds explored: {top_k}")
    print(f"Total candidates found: {len(all_candidates)}")
    print(f"Valid factorizations: {len(valid_factors)}")
    
    if valid_factors:
        print(f"\n✓ SUCCESS: Factorization found!")
        best = valid_factors[0]
        print(f"  {best['p']} × {best['q']} = {N}")
    else:
        print(f"\n✗ No valid factorization found in current search")
        print(f"  Consider: increasing search_radius or exploring more seeds")
    
    return {
        'N': N,
        'seeds_explored': top_k,
        'candidates_found': len(all_candidates),
        'valid_factors': valid_factors,
        'success': len(valid_factors) > 0
    }


def benchmark_hybrid_approach():
    """Benchmark the hybrid approach on various semiprimes."""
    print("\n" + "="*70)
    print("BENCHMARK: Hybrid Elliptic-GVA Approach")
    print("="*70)
    
    test_cases = [
        (143, "11 × 13", 50),      # Small balanced
        (323, "17 × 19", 50),      # Medium balanced  
        (1189, "29 × 41", 100),    # Larger balanced
        (2021, "43 × 47", 100),    # Another test
    ]
    
    results = []
    
    for N, description, radius in test_cases:
        print(f"\n{'─'*70}")
        print(f"Testing N = {N} ({description})")
        print(f"{'─'*70}")
        
        result = elliptic_gva_hybrid(N, top_k=5, search_radius=radius)
        results.append(result)
        
        if result['success']:
            factors = result['valid_factors'][0]
            print(f"✓ Found: {factors['p']} × {factors['q']}")
        else:
            print(f"✗ Failed to factor")
    
    # Overall summary
    print("\n" + "="*70)
    print("OVERALL BENCHMARK RESULTS")
    print("="*70)
    
    success_count = sum(1 for r in results if r['success'])
    total = len(results)
    success_rate = 100 * success_count / total
    
    print(f"Success rate: {success_count}/{total} ({success_rate:.1f}%)")
    print(f"Average candidates per test: {np.mean([r['candidates_found'] for r in results]):.1f}")
    
    return results


def demonstrate_seed_quality():
    """Demonstrate how seed quality improves with the elliptical model."""
    print("\n" + "="*70)
    print("DEMONSTRATION: Seed Quality Analysis")
    print("="*70)
    
    N = 10403  # 101 × 103
    true_p, true_q = 101, 103
    
    print(f"\nN = {N} (true factors: {true_p} × {true_q})")
    
    # Get seeds from elliptical billiard
    coords, seeds = embedTorusGeodesic_with_elliptic_refinement(N, k=0.3, dims=17)
    
    print(f"\nSeed Quality Metrics:")
    print(f"{'─'*70}")
    
    for i, seed in enumerate(seeds[:10]):
        p_seed = seed['p']
        
        # Calculate error metrics
        error_abs = abs(p_seed - true_p)
        error_pct = 100 * error_abs / true_p
        
        print(f"\nSeed {i+1}:")
        print(f"  Value: {p_seed}")
        print(f"  True factor: {true_p}")
        print(f"  Absolute error: {error_abs}")
        print(f"  Relative error: {error_pct:.2f}%")
        print(f"  Confidence: {seed['confidence']:.4f}")
        
        # Quality rating
        if error_pct < 1:
            print(f"  Quality: ★★★★★ Excellent")
        elif error_pct < 5:
            print(f"  Quality: ★★★★☆ Very Good")
        elif error_pct < 10:
            print(f"  Quality: ★★★☆☆ Good")
        elif error_pct < 20:
            print(f"  Quality: ★★☆☆☆ Fair")
        else:
            print(f"  Quality: ★☆☆☆☆ Poor")


def main():
    """Run all integration examples."""
    print("="*70)
    print("ELLIPTICAL BILLIARD MODEL - INTEGRATION EXAMPLES")
    print("="*70)
    print("\nThese examples show how to integrate the elliptical billiard model")
    print("with existing factorization methods like GVA.")
    
    # Example 1: Single factorization with hybrid approach
    print("\n" + "="*70)
    print("EXAMPLE 1: Single Factorization")
    print("="*70)
    elliptic_gva_hybrid(143, top_k=5, search_radius=50)
    
    # Example 2: Benchmark on multiple cases
    print("\n" + "="*70)
    print("EXAMPLE 2: Benchmark Suite")
    print("="*70)
    benchmark_hybrid_approach()
    
    # Example 3: Seed quality analysis
    print("\n" + "="*70)
    print("EXAMPLE 3: Seed Quality Analysis")
    print("="*70)
    demonstrate_seed_quality()
    
    print("\n" + "="*70)
    print("INTEGRATION EXAMPLES COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Elliptical billiard provides good initial seeds")
    print("  2. Seeds can guide local search methods")
    print("  3. Hybrid approach combines strengths of both methods")
    print("  4. Confidence scores help prioritize search")
    print("  5. Works best with balanced semiprimes")
    print()


if __name__ == "__main__":
    main()
