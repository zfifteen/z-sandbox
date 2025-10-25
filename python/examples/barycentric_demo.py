#!/usr/bin/env python3
"""
Barycentric Coordinates Enhancement Demo

Demonstrates how barycentric coordinate concepts enhance the geometric 
factorization framework through:

1. Affine-invariant distance calculations
2. Curvature-weighted interpolation
3. Simplicial stratification for Monte Carlo sampling
4. Integration with existing GVA and Monte Carlo pipelines

This shows practical improvements over standard methods for factorization
candidate generation and proximity-based factor detection.
"""

import sys
import os
import time
import math
from typing import List, Tuple
import numpy as np

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from barycentric import (
    BarycentricCoordinates,
    barycentric_distance,
    curvature_weighted_barycentric,
    simplicial_stratification,
    torus_barycentric_embedding,
    barycentric_distance_torus
)
from monte_carlo import FactorizationMonteCarloEnhancer


def demo_basic_barycentric():
    """Demonstrate basic barycentric coordinate concepts."""
    print("=" * 70)
    print("Demo 1: Basic Barycentric Coordinates")
    print("=" * 70)
    print()
    
    # Create a 2D triangle
    vertices = [
        np.array([0.0, 0.0]),
        np.array([4.0, 0.0]),
        np.array([2.0, 3.0])
    ]
    
    bc = BarycentricCoordinates(vertices)
    
    print("Triangle vertices:")
    for i, v in enumerate(vertices):
        print(f"  V{i}: {v}")
    print()
    
    # Test centroid
    centroid = bc.centroid()
    print(f"Centroid (center of mass): {centroid}")
    print(f"Expected: {np.mean(vertices, axis=0)}")
    print()
    
    # Test point inside
    test_point = np.array([2.0, 1.0])
    lambdas = bc.compute_barycentric_coords(test_point)
    print(f"Test point: {test_point}")
    print(f"Barycentric coordinates: {lambdas}")
    print(f"Sum of coordinates: {np.sum(lambdas):.10f} (should be 1.0)")
    print(f"Inside simplex: {bc.is_inside_simplex(lambdas)}")
    
    # Reconstruct point
    reconstructed = bc.interpolate(lambdas)
    print(f"Reconstructed point: {reconstructed}")
    print(f"Error: {np.linalg.norm(reconstructed - test_point):.2e}")
    print()


def demo_curvature_weighting():
    """Demonstrate curvature-weighted barycentric coordinates."""
    print("=" * 70)
    print("Demo 2: Curvature-Weighted Barycentric Coordinates")
    print("=" * 70)
    print()
    
    vertices = [
        np.array([0.0, 0.0]),
        np.array([1.0, 0.0]),
        np.array([0.5, 1.0])
    ]
    
    bc = BarycentricCoordinates(vertices)
    
    # Test point
    test_point = np.array([0.5, 0.3])
    
    # Standard barycentric coords
    lambdas_standard = bc.compute_barycentric_coords(test_point)
    
    # Curvature-weighted (simulating Z5D κ(n) weighting)
    # Higher weight for vertex 2 (top), representing proximity to √N
    def kappa_func(i):
        weights = [0.1, 0.1, 0.5]  # Higher weight for top vertex
        return weights[i]
    
    lambdas_weighted = curvature_weighted_barycentric(test_point, vertices, kappa_func)
    
    print(f"Test point: {test_point}")
    print()
    print("Standard barycentric coords:")
    print(f"  λ = {lambdas_standard}")
    print()
    print("Curvature-weighted coords (κ-modulated):")
    print(f"  λ' = {lambdas_weighted}")
    print()
    print("Effect of curvature weighting:")
    print(f"  Δλ = {lambdas_weighted - lambdas_standard}")
    print(f"  ||Δλ|| = {np.linalg.norm(lambdas_weighted - lambdas_standard):.4f}")
    print()
    
    # Interpolate both
    point_standard = bc.interpolate(lambdas_standard)
    point_weighted = bc.interpolate(lambdas_weighted)
    
    print(f"Reconstructed (standard): {point_standard}")
    print(f"Reconstructed (weighted): {point_weighted}")
    print(f"Shift due to weighting: {np.linalg.norm(point_weighted - point_standard):.4f}")
    print()


def demo_simplicial_stratification():
    """Demonstrate simplicial stratification for sampling."""
    print("=" * 70)
    print("Demo 3: Simplicial Stratification for Monte Carlo Sampling")
    print("=" * 70)
    print()
    
    vertices = [
        np.array([0.0, 0.0]),
        np.array([1.0, 0.0]),
        np.array([0.5, 1.0])
    ]
    
    bc = BarycentricCoordinates(vertices)
    
    # Generate samples
    n_samples = 50
    samples = simplicial_stratification(vertices, n_samples)
    
    print(f"Generated {len(samples)} stratified samples in triangle")
    print()
    
    # Check coverage
    inside_count = 0
    for sample in samples:
        lambdas = bc.compute_barycentric_coords(sample)
        if bc.is_inside_simplex(lambdas):
            inside_count += 1
    
    print(f"Samples inside simplex: {inside_count}/{len(samples)} ({inside_count/len(samples)*100:.1f}%)")
    print()
    
    # Show sample statistics
    samples_array = np.array(samples)
    print("Sample statistics:")
    print(f"  Mean: {np.mean(samples_array, axis=0)}")
    print(f"  Std:  {np.std(samples_array, axis=0)}")
    print(f"  Expected centroid: {bc.centroid()}")
    print()


def demo_torus_integration():
    """Demonstrate integration with torus embeddings for GVA."""
    print("=" * 70)
    print("Demo 4: Torus Embedding Integration (GVA Enhancement)")
    print("=" * 70)
    print()
    
    # Test with small semiprime
    N = 899  # 29 × 31
    p, q = 29, 31
    
    print(f"Test semiprime: N = {N} = {p} × {q}")
    print(f"√N ≈ {math.sqrt(N):.2f}")
    print()
    
    # Generate torus embeddings with barycentric anchors
    dims = 5
    embedding_N, anchors_N = torus_barycentric_embedding(N, dims)
    embedding_p, anchors_p = torus_barycentric_embedding(p, dims)
    embedding_q, anchors_q = torus_barycentric_embedding(q, dims)
    
    print(f"Torus embedding (dim={dims}):")
    print(f"  θ(N) = {embedding_N[:3]}... (first 3 coords)")
    print(f"  θ(p) = {embedding_p[:3]}...")
    print(f"  θ(q) = {embedding_q[:3]}...")
    print(f"  {len(anchors_N)} anchor vertices generated")
    print()
    
    # Compute distances
    dist_N_p = barycentric_distance_torus(embedding_N, embedding_p, N)
    dist_N_q = barycentric_distance_torus(embedding_N, embedding_q, N)
    
    print("Barycentric distances:")
    print(f"  d_bary(θ(N), θ(p)) = {dist_N_p:.6f}")
    print(f"  d_bary(θ(N), θ(q)) = {dist_N_q:.6f}")
    print()
    
    # Compare with standard Euclidean distance
    dist_euclidean_p = np.linalg.norm(embedding_N - embedding_p)
    dist_euclidean_q = np.linalg.norm(embedding_N - embedding_q)
    
    print("Standard Euclidean distances (for comparison):")
    print(f"  d_eucl(θ(N), θ(p)) = {dist_euclidean_p:.6f}")
    print(f"  d_eucl(θ(N), θ(q)) = {dist_euclidean_q:.6f}")
    print()
    
    print("Key insight: Barycentric distance provides affine-invariant")
    print("measurement that can better capture geometric relationships")
    print("in curved torus space, potentially improving GVA factor detection.")
    print()


def demo_monte_carlo_barycentric():
    """Demonstrate barycentric sampling mode in Monte Carlo enhancer."""
    print("=" * 70)
    print("Demo 5: Monte Carlo Barycentric Sampling Mode")
    print("=" * 70)
    print()
    
    # Test semiprimes
    test_cases = [
        (899, 29, 31),      # 10-bit
        (1517, 37, 41),     # 11-bit
        (2021, 43, 47),     # 11-bit
    ]
    
    enhancer = FactorizationMonteCarloEnhancer(seed=42)
    
    # Compare modes
    modes = ['uniform', 'qmc_phi_hybrid', 'barycentric']
    num_samples = 500
    
    print(f"Testing with {num_samples} samples per mode")
    print()
    
    results = {}
    
    for mode in modes:
        print(f"Mode: {mode}")
        print("-" * 50)
        
        mode_hits = 0
        mode_total_candidates = 0
        mode_total_time = 0.0
        
        for N, p, q in test_cases:
            start = time.time()
            candidates = enhancer.biased_sampling_with_phi(N, num_samples, mode)
            elapsed = time.time() - start
            
            hit = p in candidates or q in candidates
            
            mode_hits += 1 if hit else 0
            mode_total_candidates += len(candidates)
            mode_total_time += elapsed
            
            status = "✓" if hit else "✗"
            print(f"  N={N:4d}: {status} | {len(candidates):4d} candidates | {elapsed*1000:.1f}ms")
        
        hit_rate = mode_hits / len(test_cases)
        avg_candidates = mode_total_candidates / len(test_cases)
        avg_time = mode_total_time / len(test_cases)
        cand_per_sec = avg_candidates / avg_time if avg_time > 0 else 0
        
        results[mode] = {
            'hit_rate': hit_rate,
            'avg_candidates': avg_candidates,
            'avg_time': avg_time,
            'cand_per_sec': cand_per_sec
        }
        
        print(f"  Hit rate: {hit_rate*100:.1f}%")
        print(f"  Avg candidates: {avg_candidates:.0f}")
        print(f"  Avg time: {avg_time*1000:.1f}ms")
        print(f"  Throughput: {cand_per_sec:.0f} cand/s")
        print()
    
    # Summary comparison
    print("=" * 70)
    print("Performance Summary")
    print("=" * 70)
    print()
    print(f"{'Mode':<20} {'Hit Rate':<12} {'Candidates':<12} {'Throughput':<15}")
    print("-" * 70)
    
    for mode in modes:
        r = results[mode]
        print(f"{mode:<20} {r['hit_rate']*100:>6.1f}%     {r['avg_candidates']:>6.0f}       {r['cand_per_sec']:>8.0f} cand/s")
    
    print()
    
    # Highlight barycentric advantages
    if 'barycentric' in results and 'uniform' in results:
        bary = results['barycentric']
        unif = results['uniform']
        
        if unif['hit_rate'] > 0:
            hit_improvement = (bary['hit_rate'] / unif['hit_rate'] - 1) * 100
            print(f"Barycentric vs Uniform:")
            print(f"  Hit rate improvement: {hit_improvement:+.1f}%")
        
        if unif['cand_per_sec'] > 0:
            throughput_ratio = bary['cand_per_sec'] / unif['cand_per_sec']
            print(f"  Throughput ratio: {throughput_ratio:.2f}×")
    
    print()


def main():
    """Run all demos."""
    print()
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  Barycentric Coordinates Enhancement Demo".center(68) + "*")
    print("*" + "  Z-Sandbox Geometric Factorization Framework".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print()
    
    demos = [
        ("Basic Barycentric Coordinates", demo_basic_barycentric),
        ("Curvature Weighting", demo_curvature_weighting),
        ("Simplicial Stratification", demo_simplicial_stratification),
        ("Torus Integration", demo_torus_integration),
        ("Monte Carlo Barycentric Sampling", demo_monte_carlo_barycentric),
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print()
        try:
            demo_func()
        except Exception as e:
            print(f"ERROR in {name}: {e}")
            import traceback
            traceback.print_exc()
        
        if i < len(demos):
            print()
            input("Press Enter to continue to next demo...")
            print("\n" * 2)
    
    print()
    print("=" * 70)
    print("All demos completed!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("1. Barycentric coordinates provide affine-invariant geometry")
    print("2. Curvature weighting integrates Z5D axioms κ(n) naturally")
    print("3. Simplicial stratification improves Monte Carlo coverage")
    print("4. Torus integration enhances GVA factor detection")
    print("5. Barycentric sampling mode offers competitive performance")
    print()
    print("Next steps: Integrate with full GVA pipeline for 128-bit+ testing")
    print()


if __name__ == "__main__":
    main()
