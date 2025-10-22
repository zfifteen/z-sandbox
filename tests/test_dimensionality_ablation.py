#!/usr/bin/env python3
"""
Dimensionality Ablation Study for Elliptical Billiard Model
=============================================================

Tests the effect of embedding dimensionality on seed quality.
Compares dims ∈ {2, 3, 5, 9, 17} as suggested in review.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from python.manifold_elliptic import embedTorusGeodesic_with_elliptic_refinement


def test_dimensionality_ablation():
    """
    Test seed quality across different embedding dimensions.
    Validates the choice of dims=17 vs alternatives.
    """
    print("="*70)
    print("DIMENSIONALITY ABLATION STUDY")
    print("="*70)
    
    # Test cases: small balanced semiprimes with known factors
    test_cases = [
        (143, 11, 13, "11 × 13"),
        (323, 17, 19, "17 × 19"),
        (10403, 101, 103, "101 × 103"),
    ]
    
    dimensions = [2, 3, 5, 9, 17]
    
    print("\nTesting embedding dimensions:", dimensions)
    print("\n" + "="*70)
    
    results = []
    
    for N, true_p, true_q, desc in test_cases:
        print(f"\nN = {N} ({desc})")
        print("-"*70)
        
        case_results = {'N': N, 'true_p': true_p, 'true_q': true_q, 'dims': {}}
        
        for dims in dimensions:
            # Run embedding with this dimensionality
            try:
                coords, seeds = embedTorusGeodesic_with_elliptic_refinement(
                    N, k=0.3, dims=dims
                )
                
                # Find best seed (closest to true factors)
                best_error = float('inf')
                best_seed = None
                
                for seed in seeds[:10]:  # Check top 10 seeds
                    p_seed, q_seed = seed['p'], seed['q']
                    
                    # Calculate error as min distance to true factors
                    error1 = abs(p_seed - true_p) + abs(q_seed - true_q)
                    error2 = abs(p_seed - true_q) + abs(q_seed - true_p)
                    error = min(error1, error2)
                    
                    if error < best_error:
                        best_error = error
                        best_seed = seed
                
                # Calculate relative error percentage
                rel_error = 100 * best_error / (true_p + true_q)
                
                case_results['dims'][dims] = {
                    'best_error': best_error,
                    'rel_error': rel_error,
                    'best_seed': best_seed,
                    'num_seeds': len(seeds)
                }
                
                print(f"  dims={dims:2d}: error={best_error:4d} ({rel_error:5.2f}%), "
                      f"seeds={len(seeds):2d}, best={best_seed['p']}×{best_seed['q']}")
                
            except Exception as e:
                print(f"  dims={dims:2d}: ERROR - {str(e)}")
                case_results['dims'][dims] = {'error': str(e)}
        
        results.append(case_results)
    
    # Summary analysis
    print("\n" + "="*70)
    print("SUMMARY ANALYSIS")
    print("="*70)
    
    # Average relative error by dimension
    avg_errors = {d: [] for d in dimensions}
    for case in results:
        for dims in dimensions:
            if dims in case['dims'] and 'rel_error' in case['dims'][dims]:
                avg_errors[dims].append(case['dims'][dims]['rel_error'])
    
    print("\nAverage relative error by dimension:")
    for dims in dimensions:
        if avg_errors[dims]:
            avg = np.mean(avg_errors[dims])
            std = np.std(avg_errors[dims])
            print(f"  dims={dims:2d}: {avg:6.2f}% ± {std:5.2f}%")
        else:
            print(f"  dims={dims:2d}: No valid results")
    
    # Find best dimension
    best_dim = min(avg_errors.keys(), 
                   key=lambda d: np.mean(avg_errors[d]) if avg_errors[d] else float('inf'))
    
    print(f"\n{'='*70}")
    print(f"Best dimension: {best_dim}")
    print(f"Average error: {np.mean(avg_errors[best_dim]):.2f}%")
    print(f"{'='*70}")
    
    # Recommendation
    print("\nRecommendation:")
    if best_dim == 17:
        print("  ✓ Current choice (dims=17) is optimal among tested values")
    else:
        print(f"  ⚠ Consider using dims={best_dim} instead of dims=17")
        print(f"    Improvement: {np.mean(avg_errors[17]) - np.mean(avg_errors[best_dim]):.2f}%")
    
    return results


if __name__ == "__main__":
    results = test_dimensionality_ablation()
    
    print("\n" + "="*70)
    print("ABLATION STUDY COMPLETE")
    print("="*70)
    print("\nNote: This is a preliminary study with small test cases.")
    print("More comprehensive testing needed with larger semiprimes and")
    print("statistical significance testing for robust conclusions.")
    print()
