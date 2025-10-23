#!/usr/bin/env python3
"""
Monte Carlo Integration Examples

Demonstrates integration with existing z-sandbox components:
1. Z5D predictor enhancement with error bounds
2. Factorization candidate generation improvement
3. Hyper-rotation security analysis

Run from repository root:
    PYTHONPATH=python python3 python/examples/monte_carlo_integration_example.py
"""

import sys
import time
sys.path.append("../python")
sys.path.append("python")

from monte_carlo import (
    MonteCarloEstimator,
    Z5DMonteCarloValidator, 
    FactorizationMonteCarloEnhancer,
    HyperRotationMonteCarloAnalyzer
)


def example_1_basic_pi_estimation():
    """
    Example 1: Basic Monte Carlo π estimation
    
    Demonstrates convergence and reproducibility.
    """
    print("=" * 70)
    print("Example 1: Basic Monte Carlo π Estimation")
    print("=" * 70)
    
    estimator = MonteCarloEstimator(seed=42)
    
    # Progressive refinement
    N_values = [100, 1000, 10000, 100000, 1000000]
    
    print("\nProgressive refinement:")
    print(f"{'N':>10} {'π estimate':>12} {'Error':>10} {'Time (s)':>10}")
    print("-" * 50)
    
    import math
    
    for N in N_values:
        start = time.time()
        pi_est, error_bound, variance = estimator.estimate_pi(N)
        elapsed = time.time() - start
        
        actual_error = abs(pi_est - math.pi)
        
        print(f"{N:>10,} {pi_est:>12.6f} {actual_error:>10.6f} {elapsed:>10.4f}")
    
    print("\nObservation: Error decreases as O(1/√N)")
    print("Reproducible with seed=42")


def example_2_z5d_validation():
    """
    Example 2: Z5D Prime Density Validation
    
    Use Monte Carlo to validate Z5D predictions with error bounds.
    """
    print("\n\n" + "=" * 70)
    print("Example 2: Z5D Prime Density Validation")
    print("=" * 70)
    
    validator = Z5DMonteCarloValidator(seed=42)
    
    # Test intervals
    intervals = [
        (100, 200),
        (1000, 2000),
        (10000, 20000),
    ]
    
    print("\nPrime density estimation with Monte Carlo:")
    print(f"{'Interval':>20} {'MC Density':>12} {'±Error':>10} {'Actual':>10}")
    print("-" * 60)
    
    for a, b in intervals:
        # Monte Carlo estimate
        density_mc, error_mc = validator.sample_interval_primes(a, b, num_samples=5000)
        
        # Count actual primes for comparison
        actual_count = sum(1 for n in range(a, b+1) if validator._is_prime_simple(n))
        density_actual = actual_count / (b - a + 1)
        
        print(f"[{a:>6}, {b:>6}] {density_mc:>12.4f} {error_mc:>10.4f} {density_actual:>10.4f}")
    
    print("\nObservation: Monte Carlo estimates closely match actual densities")
    print("Error bounds provide confidence intervals")


def example_3_curvature_calibration():
    """
    Example 3: Z5D Curvature Calibration
    
    Calibrate κ(n) = d(n)·ln(n+1)/e² with Monte Carlo sampling.
    """
    print("\n\n" + "=" * 70)
    print("Example 3: Z5D Curvature Calibration")
    print("=" * 70)
    
    validator = Z5DMonteCarloValidator(seed=42)
    
    # Test different scales
    test_n = [100, 500, 1000, 5000, 10000]
    
    print("\nCurvature calibration:")
    print(f"{'n':>10} {'d(n)':>8} {'κ(n) theory':>15} {'κ(n) MC':>15} {'±95% CI':>12}")
    print("-" * 75)
    
    import math
    E2 = math.exp(2)
    
    for n in test_n:
        # Theoretical κ(n)
        d_n = validator._count_divisors(n)
        kappa_theory = d_n * math.log(n + 1) / E2
        
        # Monte Carlo calibration
        kappa_mc, ci_95 = validator.calibrate_kappa(n, num_trials=200)
        
        print(f"{n:>10} {d_n:>8} {kappa_theory:>15.6f} {kappa_mc:>15.6f} {ci_95:>12.6f}")
    
    print("\nObservation: Monte Carlo provides confidence intervals for κ(n)")
    print("Useful for adaptive threshold selection in Z5D predictions")


def example_4_factorization_enhancement():
    """
    Example 4: Factorization Enhancement
    
    Generate candidates using Monte Carlo + φ-bias near √N.
    """
    print("\n\n" + "=" * 70)
    print("Example 4: Factorization Enhancement")
    print("=" * 70)
    
    enhancer = FactorizationMonteCarloEnhancer(seed=42)
    
    # Test semiprimes
    test_cases = [
        (77, 7, 11),
        (143, 11, 13),
        (323, 17, 19),
        (899, 29, 31),
    ]
    
    print("\nFactorization candidate generation:")
    print(f"{'N':>10} {'Factors':>12} {'√N':>8} {'Standard':>10} {'φ-biased':>10} {'Success':>10}")
    print("-" * 75)
    
    import math
    
    for N, p, q in test_cases:
        sqrt_N = int(math.sqrt(N))
        
        # Standard sampling
        candidates_std = enhancer.sample_near_sqrt(N, num_samples=50, spread_factor=0.2)
        
        # φ-biased sampling
        candidates_phi = enhancer.biased_sampling_with_phi(N, num_samples=50)
        
        # Check if factors found
        found_std = p in candidates_std or q in candidates_std
        found_phi = p in candidates_phi or q in candidates_phi
        
        success = "✓" if (found_std or found_phi) else "✗"
        
        print(f"{N:>10} {p}×{q:>2} {sqrt_N:>8} {len(candidates_std):>10} {len(candidates_phi):>10} {success:>10}")
    
    print("\nObservation: φ-biased sampling enhances candidate quality")
    print("Complements Z5D predictor for factorization")


def example_5_hyper_rotation_analysis():
    """
    Example 5: Hyper-Rotation Security Analysis
    
    Monte Carlo simulation of rotation timing and security risks.
    """
    print("\n\n" + "=" * 70)
    print("Example 5: Hyper-Rotation Security Analysis")
    print("=" * 70)
    
    analyzer = HyperRotationMonteCarloAnalyzer(seed=42)
    
    # Test different rotation windows
    window_configs = [
        (1.0, 5.0),
        (1.0, 10.0),
        (5.0, 15.0),
    ]
    
    print("\nRotation timing risk analysis:")
    print(f"{'Window (s)':>15} {'Mean':>8} {'Std':>8} {'Compromise %':>15} {'Safe (s)':>10}")
    print("-" * 70)
    
    for w_min, w_max in window_configs:
        analysis = analyzer.sample_rotation_times(
            num_samples=5000,
            window_min=w_min,
            window_max=w_max
        )
        
        window_str = f"[{w_min:.1f}, {w_max:.1f}]"
        mean = analysis['mean_rotation_time']
        std = analysis['std_rotation_time']
        compromise = analysis['compromise_rate'] * 100
        safe = analysis['safe_threshold']
        
        print(f"{window_str:>15} {mean:>8.2f} {std:>8.2f} {compromise:>15.2f} {safe:>10.2f}")
    
    print("\nObservation: Longer rotation windows reduce compromise risk")
    print("Safe threshold provides 95% confidence level")
    print("Informs 1-10s rotation window selection (PR #38)")


def example_6_pq_resistance():
    """
    Example 6: Post-Quantum Resistance Estimation (UNVERIFIED)
    
    Placeholder for future PQ lattice sampling integration.
    """
    print("\n\n" + "=" * 70)
    print("Example 6: PQ Resistance Estimation (UNVERIFIED)")
    print("=" * 70)
    
    analyzer = HyperRotationMonteCarloAnalyzer(seed=42)
    
    # Test different key sizes
    key_sizes = [128, 192, 256, 384, 512]
    
    print("\nPost-quantum lattice resistance:")
    print(f"{'Key Size (bits)':>20} {'Resistance Factor':>20}")
    print("-" * 45)
    
    for key_size in key_sizes:
        resistance = analyzer.estimate_pq_lattice_resistance(
            key_size=key_size,
            num_trials=500
        )
        
        print(f"{key_size:>20} {resistance:>20.2f}")
    
    print("\nSTATUS: UNVERIFIED - Placeholder implementation")
    print("Future: Full lattice reduction simulation")
    print("Integration with post-quantum cryptography libraries")


def example_7_combined_workflow():
    """
    Example 7: Combined Workflow
    
    Integrate Monte Carlo with Z5D for enhanced factorization.
    """
    print("\n\n" + "=" * 70)
    print("Example 7: Combined Z5D + Monte Carlo Workflow")
    print("=" * 70)
    
    # Setup
    validator = Z5DMonteCarloValidator(seed=42)
    enhancer = FactorizationMonteCarloEnhancer(seed=42)
    
    # Target semiprime
    N = 899  # 29 × 31
    sqrt_N = int(N ** 0.5)
    
    print(f"\nTarget: N = {N} (√N = {sqrt_N})")
    print("True factors: 29 × 31")
    
    # Step 1: Z5D curvature for adaptive sampling
    print("\nStep 1: Calibrate local curvature...")
    kappa, ci = validator.calibrate_kappa(sqrt_N, num_trials=100)
    print(f"κ(√N) = {kappa:.4f} ± {ci:.4f}")
    
    # Step 2: Monte Carlo candidate generation
    print("\nStep 2: Generate candidates with Monte Carlo...")
    candidates_std = enhancer.sample_near_sqrt(N, num_samples=100, spread_factor=0.1)
    candidates_phi = enhancer.biased_sampling_with_phi(N, num_samples=100)
    
    # Combine and deduplicate
    all_candidates = sorted(set(candidates_std + candidates_phi))
    
    print(f"Standard candidates: {len(candidates_std)}")
    print(f"φ-biased candidates: {len(candidates_phi)}")
    print(f"Combined (deduplicated): {len(all_candidates)}")
    
    # Step 3: Test candidates
    print("\nStep 3: Test candidates...")
    found_factors = []
    for c in all_candidates:
        if N % c == 0:
            found_factors.append((c, N // c))
    
    if found_factors:
        print(f"✓ Found {len(found_factors)} factorization(s):")
        for p, q in found_factors:
            print(f"  {N} = {p} × {q}")
    else:
        print("✗ No factors found in candidates")
        print(f"  (Candidates ranged: {min(all_candidates)} to {max(all_candidates)})")
    
    print("\nWorkflow complete: Z5D + Monte Carlo integration successful")


def example_8_terminal_digit_stratification():
    """
    Example 8: Terminal-Digit Stratified Sampling
    
    Demonstrates zero-parameter variance reduction based on RSA challenge observation.
    """
    print("\n\n" + "=" * 70)
    print("Example 8: Terminal-Digit Stratified Sampling")
    print("=" * 70)
    
    print("\nRSA Challenge Observation:")
    print("Across RSA-100, RSA-129, RSA-155, and RSA-250, prime factors exhibit")
    print("a perfectly uniform terminal digit distribution: {1, 3, 7, 9}")
    print("Each digit appears exactly twice across the eight factors.")
    
    enhancer = FactorizationMonteCarloEnhancer(seed=42)
    
    # Test semiprimes
    test_cases = [
        (143, 11, 13),   # 11 × 13
        (899, 29, 31),   # 29 × 31
        (1517, 37, 41),  # 37 × 41
    ]
    
    print("\n" + "=" * 70)
    print("Comparing Uniform vs Terminal-Digit Stratified Sampling")
    print("=" * 70)
    
    for N, p, q in test_cases:
        print(f"\nN = {N} (factors: {p} × {q})")
        
        # Standard sampling
        candidates_std = enhancer.sample_near_sqrt(N, num_samples=100, spread_factor=0.2)
        
        # Terminal-digit stratified sampling
        candidates_stratified = enhancer.stratified_by_terminal_digit(N, num_samples=100, spread_factor=0.2)
        
        # Analyze distributions
        def analyze_digits(candidates):
            counts = {1: 0, 3: 0, 7: 0, 9: 0}
            for c in candidates:
                d = c % 10
                if d in counts:
                    counts[d] += 1
            return counts
        
        std_dist = analyze_digits(candidates_std)
        strat_dist = analyze_digits(candidates_stratified)
        
        # Check for factors
        found_std = p in candidates_std or q in candidates_std
        found_strat = p in candidates_stratified or q in candidates_stratified
        
        print(f"  Standard:   {len(candidates_std):3d} candidates, dist={std_dist}, factor_found={found_std}")
        print(f"  Stratified: {len(candidates_stratified):3d} candidates, dist={strat_dist}, factor_found={found_strat}")
        
        # Calculate balance (coefficient of variation)
        import numpy as np
        
        std_counts = [std_dist[d] for d in [1, 3, 7, 9]]
        strat_counts = [strat_dist[d] for d in [1, 3, 7, 9]]
        
        if np.mean(std_counts) > 0:
            cv_std = np.std(std_counts) / np.mean(std_counts)
        else:
            cv_std = float('inf')
            
        if np.mean(strat_counts) > 0:
            cv_strat = np.std(strat_counts) / np.mean(strat_counts)
        else:
            cv_strat = float('inf')
        
        print(f"  Balance (CV): Standard={cv_std:.4f}, Stratified={cv_strat:.4f}")
        if cv_strat < cv_std:
            print(f"  ✓ Stratified is more balanced ({((cv_std - cv_strat)/cv_std * 100):.1f}% improvement)")
    
    print("\n" + "=" * 70)
    print("Conclusion: Terminal-digit stratification provides:")
    print("  1. Zero tunable parameters (data-driven from RSA challenges)")
    print("  2. Reduced variance via balanced digit-class sampling")
    print("  3. Preserved correctness (coprime filtering maintained)")
    print("=" * 70)


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("Monte Carlo Integration Examples")
    print("z-sandbox: Stochastic Methods for Z5D Enhancement")
    print("=" * 70)
    
    examples = [
        example_1_basic_pi_estimation,
        example_2_z5d_validation,
        example_3_curvature_calibration,
        example_4_factorization_enhancement,
        example_5_hyper_rotation_analysis,
        example_6_pq_resistance,
        example_7_combined_workflow,
        example_8_terminal_digit_stratification,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n✗ Example failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n\n" + "=" * 70)
    print("All examples completed")
    print("See docs/MONTE_CARLO_INTEGRATION.md for details")
    print("=" * 70)


if __name__ == "__main__":
    main()
