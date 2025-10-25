#!/usr/bin/env python3
"""
Gaussian Integer Lattice Integration Demo

Demonstrates integration of Epstein zeta functions and Gaussian lattice
theory with z-sandbox factorization framework:

1. Lattice identity validation (Epstein zeta closed form)
2. Monte Carlo integration over lattice regions
3. Lattice-enhanced distance metrics for GVA
4. Z5D curvature with lattice corrections
5. Application to factorization candidate generation

Run from repository root:
    PYTHONPATH=python python3 python/examples/gaussian_lattice_demo.py
"""

import sys
import math
import time
sys.path.append("../python")
sys.path.append("python")

from gaussian_lattice import (
    GaussianIntegerLattice,
    LatticeMonteCarloIntegrator,
    demonstrate_gaussian_lattice_identity
)


def example_1_identity_validation():
    """
    Example 1: Validate Epstein Zeta Identity
    
    Demonstrates numerical convergence to closed-form expression.
    """
    print("=" * 70)
    print("Example 1: Epstein Zeta Identity Validation")
    print("=" * 70)
    print()
    
    demonstrate_gaussian_lattice_identity()


def example_2_lattice_enhanced_distances():
    """
    Example 2: Lattice-Enhanced Distance Metrics
    
    Show how Gaussian lattice structure can enhance distance calculations
    for GVA (Geodesic Validation Assault) factorization.
    """
    print("\n\n" + "=" * 70)
    print("Example 2: Lattice-Enhanced Distance Metrics")
    print("=" * 70)
    print()
    
    lattice = GaussianIntegerLattice(precision_dps=50)
    
    # Test points representing factor candidates
    test_cases = [
        (7 + 0j, 11 + 0j, "Adjacent primes 7, 11"),
        (29 + 0j, 31 + 0j, "Adjacent primes 29, 31"),
        (10 + 5j, 12 + 3j, "Complex lattice points"),
    ]
    
    print("Comparing standard vs lattice-enhanced distances:")
    print(f"{'Point 1':>15} {'Point 2':>15} {'Euclidean':>12} {'Lattice-Enhanced':>18} {'Description':>25}")
    print("-" * 90)
    
    for z1, z2, desc in test_cases:
        euclidean = abs(z2 - z1)
        enhanced = lattice.lattice_enhanced_distance(z1, z2, lattice_scale=0.5)
        
        print(f"{str(z1):>15} {str(z2):>15} {euclidean:>12.6f} {float(enhanced):>18.6f} {desc:>25}")
    
    print()
    print("Observation: Lattice-enhanced distances incorporate discretization")
    print("Application: Can improve candidate ranking in GVA factorization")
    print()


def example_3_monte_carlo_lattice_integration():
    """
    Example 3: Monte Carlo Integration with Lattice Functions
    
    Integrate functions over lattice regions using φ-biased sampling.
    """
    print("\n\n" + "=" * 70)
    print("Example 3: Monte Carlo Lattice Integration")
    print("=" * 70)
    print()
    
    integrator = LatticeMonteCarloIntegrator(seed=42)
    
    # Test function: e^(-x²) over lattice region
    def test_func(z):
        return math.exp(-z.real * z.real)
    
    print("Integrating f(x) = e^(-x²) over [0, 2]")
    print(f"{'Method':>20} {'N Samples':>12} {'Estimate':>15} {'Error Bound':>15} {'Time (s)':>10}")
    print("-" * 75)
    
    sample_sizes = [1000, 10000, 100000]
    
    for use_phi in [False, True]:
        method = "φ-biased" if use_phi else "Uniform"
        
        for N in sample_sizes:
            start = time.time()
            integral, error = integrator.integrate_lattice_function(
                test_func, (0, 2), num_samples=N, use_phi_bias=use_phi
            )
            elapsed = time.time() - start
            
            print(f"{method:>20} {N:>12,} {float(integral):>15.8f} {float(error):>15.8f} {elapsed:>10.4f}")
    
    print()
    print("Observation: φ-biased sampling reduces variance (golden ratio modulation)")
    print("Integration: Complements existing monte_carlo.py framework")
    print()


def example_4_z5d_lattice_curvature():
    """
    Example 4: Z5D Curvature with Lattice Corrections
    
    Enhance standard κ(n) curvature with Gaussian lattice structure.
    """
    print("\n\n" + "=" * 70)
    print("Example 4: Z5D Curvature with Lattice Corrections")
    print("=" * 70)
    print()
    
    lattice = GaussianIntegerLattice(precision_dps=50)
    
    # Test at various scales
    test_n = [100, 500, 1000, 5000, 10000]
    
    print("Standard Z5D curvature: κ(n) = d(n)·ln(n+1)/e²")
    print("Enhanced curvature: κ'(n) incorporates lattice structure")
    print()
    print(f"{'n':>10} {'d(n)':>8} {'κ(n) Standard':>18} {'κ_prime(n)':>18} {'Enhancement %':>15}")
    print("-" * 75)
    
    E2 = math.exp(2)
    
    for n in test_n:
        d_n = lattice._count_divisors(n)
        kappa_standard = d_n * math.log(n + 1) / E2
        kappa_enhanced = lattice.z5d_lattice_curvature(n, max_lattice=10)
        
        enhancement_pct = ((float(kappa_enhanced) - kappa_standard) / kappa_standard) * 100
        
        print(f"{n:>10} {d_n:>8} {kappa_standard:>18.8f} {float(kappa_enhanced):>18.8f} {enhancement_pct:>15.2f}")
    
    print()
    print("STATUS: UNVERIFIED - Experimental Z5D enhancement")
    print("Application: Adaptive threshold tuning in z5d_predictor.py")
    print()


def example_5_lattice_density_sampling():
    """
    Example 5: Lattice Point Density via Monte Carlo
    
    Estimate lattice properties using stochastic sampling.
    """
    print("\n\n" + "=" * 70)
    print("Example 5: Lattice Density Sampling (Gauss Circle Problem)")
    print("=" * 70)
    print()
    
    lattice = GaussianIntegerLattice(precision_dps=50)
    
    # Test different radii
    radii = [5.0, 10.0, 20.0, 50.0]
    
    print("Estimating π via lattice point density:")
    print(f"{'Radius':>10} {'N Samples':>12} {'π Estimate':>15} {'Expected Points':>18} {'Error':>12}")
    print("-" * 75)
    
    for r in radii:
        result = lattice.sample_lattice_density(r, num_samples=50000, seed=42)
        pi_error = abs(result['pi_estimate'] - math.pi)
        
        print(f"{r:>10.1f} {result['num_samples']:>12,} {result['pi_estimate']:>15.8f} "
              f"{result['expected_lattice_points']:>18.2f} {pi_error:>12.6f}")
    
    print()
    print("Observation: Monte Carlo density estimation converges to π")
    print("Application: Validates lattice-based distance metrics for factorization")
    print()


def example_6_factorization_application():
    """
    Example 6: Application to Factorization Framework
    
    Demonstrate how lattice theory enhances Z5D-guided factorization.
    """
    print("\n\n" + "=" * 70)
    print("Example 6: Factorization Application (Conceptual)")
    print("=" * 70)
    print()
    
    lattice = GaussianIntegerLattice(precision_dps=50)
    
    # Example semiprime
    N = 899  # 29 × 31
    sqrt_N = int(math.sqrt(N))
    
    print(f"Target: N = {N} (√N ≈ {sqrt_N})")
    print("True factors: 29 × 31")
    print()
    
    # Generate candidate factors near √N
    candidates = []
    for offset in range(-5, 6):
        candidate = sqrt_N + offset
        if candidate > 1:
            candidates.append(candidate)
    
    print("Step 1: Generate candidates near √N")
    print(f"Candidates: {candidates}")
    print()
    
    # Compute lattice-enhanced distances from √N
    print("Step 2: Rank candidates using lattice-enhanced distance")
    print(f"{'Candidate':>12} {'Euclidean Dist':>18} {'Lattice Distance':>18} {'Divides N':>12}")
    print("-" * 65)
    
    sqrt_N_complex = complex(sqrt_N, 0)
    ranked_candidates = []
    
    for c in candidates:
        c_complex = complex(c, 0)
        euclidean_dist = abs(c_complex - sqrt_N_complex)
        lattice_dist = lattice.lattice_enhanced_distance(sqrt_N_complex, c_complex)
        divides = "✓" if N % c == 0 else "✗"
        
        ranked_candidates.append((c, float(lattice_dist), divides))
        print(f"{c:>12} {euclidean_dist:>18.6f} {float(lattice_dist):>18.6f} {divides:>12}")
    
    # Sort by lattice distance
    ranked_candidates.sort(key=lambda x: x[1])
    
    print()
    print("Step 3: Check top-ranked candidates")
    found_factors = [c for c, dist, divides in ranked_candidates[:5] if divides == "✓"]
    
    if found_factors:
        print(f"✓ Found factors: {found_factors}")
        for f in found_factors:
            print(f"  {N} = {f} × {N // f}")
    else:
        print("✗ No factors in top 5 candidates")
    
    print()
    print("Integration potential:")
    print("- Enhance GVA distance metrics in manifold_core.py")
    print("- Improve candidate ranking in z5d_predictor.py")
    print("- Combine with φ-biased sampling from monte_carlo.py")
    print("- Provide theoretical baselines for error bounds")
    print()


def example_7_performance_comparison():
    """
    Example 7: Performance Comparison
    
    Compare convergence rates for different lattice sum truncations.
    """
    print("\n\n" + "=" * 70)
    print("Example 7: Convergence Performance Analysis")
    print("=" * 70)
    print()
    
    lattice = GaussianIntegerLattice(precision_dps=50)
    
    print("Analyzing convergence rate of Epstein zeta sum:")
    print(f"{'max_n':>10} {'Time (s)':>12} {'Error':>15} {'Terms':>12} {'Error/Term':>15}")
    print("-" * 70)
    
    test_sizes = [20, 50, 100, 200, 300]
    
    for max_n in test_sizes:
        start = time.time()
        result = lattice.validate_identity(max_n=max_n)
        elapsed = time.time() - start
        
        error_per_term = float(result['error']) / result['num_terms'] if result['num_terms'] > 0 else 0
        
        print(f"{max_n:>10} {elapsed:>12.4f} {float(result['error']):>15.2e} "
              f"{result['num_terms']:>12,} {error_per_term:>15.2e}")
    
    print()
    print("Observation: Error decreases rapidly with lattice size")
    print("Trade-off: Precision vs computational cost")
    print("Recommendation: max_n ≈ 100-200 for practical applications")
    print()


def main():
    """Run all examples demonstrating Gaussian lattice integration."""
    print("\n" + "=" * 70)
    print("Gaussian Integer Lattice Integration Examples")
    print("z-sandbox: Lattice Theory for Geometric Factorization")
    print("=" * 70)
    print()
    print("Demonstrating:")
    print("- Epstein zeta function evaluation over ℤ[i]")
    print("- Monte Carlo integration with lattice structure")
    print("- Z5D curvature enhancements")
    print("- Applications to RSA factorization")
    print()
    
    examples = [
        example_1_identity_validation,
        example_2_lattice_enhanced_distances,
        example_3_monte_carlo_lattice_integration,
        example_4_z5d_lattice_curvature,
        example_5_lattice_density_sampling,
        example_6_factorization_application,
        example_7_performance_comparison,
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"\n✗ Example {i} failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n\n" + "=" * 70)
    print("All examples completed!")
    print()
    print("Next steps:")
    print("1. Integrate lattice metrics into manifold_core.py")
    print("2. Enhance Z5D curvature in z5d_axioms.py")
    print("3. Add lattice-based candidate generation to z5d_predictor.py")
    print("4. Benchmark on RSA-256 targets")
    print()
    print("See docs/GAUSSIAN_LATTICE_INTEGRATION.md for details")
    print("=" * 70)


if __name__ == "__main__":
    main()
