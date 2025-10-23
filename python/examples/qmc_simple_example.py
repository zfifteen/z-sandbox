#!/usr/bin/env python3
"""
Simple example demonstrating QMC variance reduction for RSA factorization.

This script shows how to use the qmc_phi_hybrid mode to generate candidates
for factoring a semiprime.
"""

import sys
import os

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from monte_carlo import FactorizationMonteCarloEnhancer


def main():
    print("=" * 60)
    print("QMC Variance Reduction - Simple Example")
    print("=" * 60)
    print()
    
    # Test semiprime: 899 = 29 × 31
    N = 899
    p = 29
    q = 31
    
    print(f"Factoring: N = {N} = {p} × {q}")
    print()
    
    # Create enhancer with reproducible seed
    seed = 42
    enhancer = FactorizationMonteCarloEnhancer(seed=seed)
    
    # Generate candidates using different modes
    modes = ['uniform', 'qmc_phi_hybrid']
    num_samples = 500
    
    for mode in modes:
        print(f"Mode: {mode}")
        print("-" * 60)
        
        # Generate candidates
        candidates = enhancer.biased_sampling_with_phi(N, num_samples, mode=mode)
        
        print(f"  Generated {len(candidates)} unique candidates")
        print(f"  Sample candidates: {sorted(candidates)[:10]}")
        
        # Check if factors are in candidates
        found_p = p in candidates
        found_q = q in candidates
        
        if found_p:
            print(f"  ✓ Found factor p={p}")
        if found_q:
            print(f"  ✓ Found factor q={q}")
        
        if found_p or found_q:
            print(f"  ✓ SUCCESS: Factor found using {mode} mode!")
        else:
            print(f"  ✗ Factors not in candidate set")
        
        print()
    
    print("=" * 60)
    print("Key Takeaway:")
    print("  QMC-φ hybrid generates more diverse candidates with")
    print("  better coverage of the search space near √N.")
    print("=" * 60)


if __name__ == "__main__":
    main()
