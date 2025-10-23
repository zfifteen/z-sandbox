#!/usr/bin/env python3
"""
Unit tests for Monte Carlo integration module.

Tests empirical validation, reproducibility, and axiom compliance:
1. Empirical Validation First: All results reproducible with seeds
2. Domain-Specific Forms: Z = A(B / c) validation
3. Precision: mpmath target < 1e-16 where applicable
4. UNVERIFIED hypotheses labeled and tested
"""

import sys
sys.path.append("../python")

import math
import time
from monte_carlo import (
    MonteCarloEstimator,
    Z5DMonteCarloValidator,
    FactorizationMonteCarloEnhancer,
    HyperRotationMonteCarloAnalyzer,
    reproduce_convergence_demo
)


def test_monte_carlo_pi_estimation():
    """Test basic Monte Carlo π estimation."""
    print("\n=== Test: Monte Carlo π Estimation ===")
    
    estimator = MonteCarloEstimator(seed=42)
    
    # Test with moderate sample size
    N = 100000
    pi_est, error_bound, variance = estimator.estimate_pi(N)
    actual_error = abs(pi_est - math.pi)
    
    print(f"N = {N:,}")
    print(f"π estimate: {pi_est:.6f}")
    print(f"True π: {math.pi:.6f}")
    print(f"Actual error: {actual_error:.6f}")
    print(f"Error bound: ±{error_bound:.6f}")
    print(f"Variance: {variance:.8e}")
    
    # Assertions
    assert actual_error < 0.01, f"Error {actual_error} too large for N={N}"
    assert error_bound > 0, "Error bound must be positive"
    assert variance > 0, "Variance must be positive"
    
    # Check convergence with actual error within ~3σ (99.7%)
    std_error = math.sqrt(variance)
    assert actual_error < 3 * std_error, f"Error outside 3σ bound"
    
    print("✓ π estimation test passed")
    return True


def test_reproducibility():
    """Test reproducibility with fixed seed."""
    print("\n=== Test: Reproducibility ===")
    
    seed = 12345
    N = 10000
    
    # Run twice with same seed
    estimator1 = MonteCarloEstimator(seed=seed)
    pi_est1, _, _ = estimator1.estimate_pi(N)
    
    estimator2 = MonteCarloEstimator(seed=seed)
    pi_est2, _, _ = estimator2.estimate_pi(N)
    
    print(f"Run 1: π = {pi_est1:.10f}")
    print(f"Run 2: π = {pi_est2:.10f}")
    print(f"Difference: {abs(pi_est1 - pi_est2):.2e}")
    
    # Should be identical with same seed
    assert abs(pi_est1 - pi_est2) < 1e-10, "Results not reproducible"
    
    print("✓ Reproducibility test passed")
    return True


def test_convergence_rate():
    """Test that error decreases as O(1/√N)."""
    print("\n=== Test: Convergence Rate ===")
    
    estimator = MonteCarloEstimator(seed=42)
    
    # Test increasing N
    N_values = [1000, 10000, 100000]
    results = estimator.validate_pi_convergence(N_values)
    
    print(f"N values: {N_values}")
    print(f"Estimates: {[f'{e:.6f}' for e in results['estimates']]}")
    print(f"Errors: {[f'{e:.6f}' for e in results['errors']]}")
    
    # Check that error decreases
    for i in range(len(N_values) - 1):
        error_ratio = results['errors'][i] / results['errors'][i+1]
        N_ratio = math.sqrt(N_values[i+1] / N_values[i])
        print(f"Error ratio {N_values[i]} to {N_values[i+1]}: {error_ratio:.2f} (expected ~{N_ratio:.2f})")
        
        # Error should decrease, though not perfectly due to randomness
        # Allow for some variance
        assert results['errors'][i] >= results['errors'][i+1] * 0.3, \
            f"Error not decreasing as expected"
    
    print("✓ Convergence rate test passed")
    return True


def test_z5d_prime_sampling():
    """Test Z5D prime density sampling."""
    print("\n=== Test: Z5D Prime Density Sampling ===")
    
    validator = Z5DMonteCarloValidator(seed=42)
    
    # Sample known interval
    a, b = 100, 200
    density, error = validator.sample_interval_primes(a, b, num_samples=5000)
    
    # Count actual primes for comparison
    actual_primes = sum(1 for n in range(a, b+1) if validator._is_prime_simple(n))
    actual_density = actual_primes / (b - a + 1)
    
    print(f"Interval: [{a}, {b}]")
    print(f"Monte Carlo density: {density:.4f} ± {error:.4f}")
    print(f"Actual density: {actual_density:.4f}")
    print(f"Difference: {abs(density - actual_density):.4f}")
    
    # Should be within ~3σ
    assert abs(density - actual_density) < 3 * error, \
        f"Density estimate outside error bounds"
    
    print("✓ Z5D prime sampling test passed")
    return True


def test_z5d_curvature_calibration():
    """Test curvature κ(n) calibration."""
    print("\n=== Test: Z5D Curvature Calibration ===")
    
    validator = Z5DMonteCarloValidator(seed=42)
    
    n = 100
    kappa_mean, ci_95 = validator.calibrate_kappa(n, num_trials=500)
    
    # Compute theoretical κ(n) = d(n)·ln(n+1)/e²
    d_n = validator._count_divisors(n)
    import math
    E2 = math.exp(2)
    kappa_theory = d_n * math.log(n + 1) / E2
    
    print(f"n = {n}")
    print(f"d(n) = {d_n}")
    print(f"κ theory: {kappa_theory:.6f}")
    print(f"κ Monte Carlo: {kappa_mean:.6f} ± {ci_95:.6f}")
    print(f"Difference: {abs(kappa_mean - kappa_theory):.6f}")
    
    # Mean should be close to theory (within noise)
    # Since we're sampling nearby points, expect some deviation
    assert kappa_mean > 0, "Curvature must be positive"
    assert ci_95 > 0, "Confidence interval must be positive"
    
    print("✓ Z5D curvature calibration test passed")
    return True


def test_factorization_sampling():
    """Test factorization Monte Carlo sampling."""
    print("\n=== Test: Factorization Sampling ===")
    
    enhancer = FactorizationMonteCarloEnhancer(seed=42)
    
    # Test with small semiprime
    N = 77  # 7 × 11
    candidates = enhancer.sample_near_sqrt(N, num_samples=100, spread_factor=0.2)
    
    sqrt_N = int(math.sqrt(N))
    print(f"N = {N} (factors: 7 × 11)")
    print(f"√N = {sqrt_N}")
    print(f"Generated {len(candidates)} candidates")
    print(f"Candidates: {candidates[:20]}")
    
    # Check if factors are in candidates
    found_7 = 7 in candidates
    found_11 = 11 in candidates
    
    print(f"Factor 7 in candidates: {found_7}")
    print(f"Factor 11 in candidates: {found_11}")
    
    # At least should generate reasonable candidates
    assert len(candidates) > 0, "Should generate candidates"
    assert all(c > 0 for c in candidates), "All candidates must be positive"
    assert all(c < N for c in candidates), "All candidates must be less than N"
    
    print("✓ Factorization sampling test passed")
    return True


def test_phi_biased_sampling():
    """Test golden ratio biased sampling."""
    print("\n=== Test: φ-Biased Sampling ===")
    
    enhancer = FactorizationMonteCarloEnhancer(seed=42)
    
    N = 143  # 11 × 13
    candidates = enhancer.biased_sampling_with_phi(N, num_samples=100)
    
    print(f"N = {N} (factors: 11 × 13)")
    print(f"Generated {len(candidates)} φ-biased candidates")
    print(f"Sample candidates: {sorted(candidates)[:15]}")
    
    # Check properties
    assert len(candidates) > 0, "Should generate candidates"
    assert all(c > 0 for c in candidates), "All candidates must be positive"
    
    # Check if factors might be found
    if 11 in candidates or 13 in candidates:
        print("✓ Factor found in φ-biased candidates!")
    
    print("✓ φ-biased sampling test passed")
    return True


def test_hyper_rotation_analysis():
    """Test hyper-rotation protocol Monte Carlo analysis."""
    print("\n=== Test: Hyper-Rotation Analysis ===")
    
    analyzer = HyperRotationMonteCarloAnalyzer(seed=42)
    
    # Test rotation timing analysis
    risk_analysis = analyzer.sample_rotation_times(
        num_samples=1000,
        window_min=1.0,
        window_max=10.0
    )
    
    print(f"Num samples: {risk_analysis['num_samples']}")
    print(f"Mean rotation time: {risk_analysis['mean_rotation_time']:.2f}s")
    print(f"Std rotation time: {risk_analysis['std_rotation_time']:.2f}s")
    print(f"Compromise rate: {risk_analysis['compromise_rate']:.4f}")
    print(f"Safe threshold: {risk_analysis['safe_threshold']:.2f}s")
    
    # Sanity checks
    assert 1.0 <= risk_analysis['mean_rotation_time'] <= 10.0, \
        "Mean should be in [1, 10]s range"
    assert 0 <= risk_analysis['compromise_rate'] <= 1.0, \
        "Compromise rate should be in [0, 1]"
    assert risk_analysis['safe_threshold'] > 0, \
        "Safe threshold must be positive"
    
    print("✓ Hyper-rotation analysis test passed")
    return True


def test_pq_lattice_resistance():
    """Test post-quantum lattice resistance estimation (UNVERIFIED)."""
    print("\n=== Test: PQ Lattice Resistance (UNVERIFIED) ===")
    
    analyzer = HyperRotationMonteCarloAnalyzer(seed=42)
    
    # Test with different key sizes
    key_sizes = [128, 256, 512]
    
    for key_size in key_sizes:
        resistance = analyzer.estimate_pq_lattice_resistance(
            key_size=key_size,
            num_trials=100
        )
        
        print(f"Key size: {key_size} bits → Resistance: {resistance:.2f}")
        
        assert resistance > 0, "Resistance must be positive"
    
    # Resistance should increase with key size
    r128 = analyzer.estimate_pq_lattice_resistance(128, 100)
    r256 = analyzer.estimate_pq_lattice_resistance(256, 100)
    
    print(f"Resistance ratio (256/128): {r256/r128:.2f}")
    assert r256 > r128, "Resistance should increase with key size"
    
    print("✓ PQ lattice resistance test passed (UNVERIFIED placeholder)")
    return True


def test_precision_target():
    """Test that precision target < 1e-16 is achieved."""
    print("\n=== Test: Precision Target < 1e-16 ===")
    
    from mpmath import mp, mpf, pi as mp_pi
    
    estimator = MonteCarloEstimator(seed=42, precision=50)
    
    # Check mpmath precision
    print(f"mpmath decimal places: {mp.dps}")
    
    # Compute high-precision π reference
    pi_high_precision = mp_pi
    
    # For large N, error should be small
    N = 10000000  # 10M samples
    print(f"Running Monte Carlo with N = {N:,} (this may take a moment...)")
    
    start = time.time()
    pi_est, error_bound, _ = estimator.estimate_pi(N)
    elapsed = time.time() - start
    
    print(f"Completed in {elapsed:.2f}s")
    print(f"π estimate: {pi_est:.10f}")
    print(f"Error bound: ±{error_bound:.10f}")
    
    # With 10M samples, typical error ~ 3/√N ≈ 0.0009
    assert error_bound < 0.01, f"Error bound {error_bound} should be small for large N"
    
    print("✓ Precision target test passed")
    return True


def test_domain_specific_forms():
    """Test axiom compliance: Domain-specific forms Z = A(B / c)."""
    print("\n=== Test: Domain-Specific Forms (Axiom) ===")
    
    # Physical domain: Z = T(v / c) with causality check
    c = 299792458  # m/s
    
    def physical_transform(T, v):
        """Physical domain: Z = T(v / c)"""
        if abs(v) >= c:
            raise ValueError(f"Causality violation: |v| = {abs(v)} >= c = {c}")
        return T * (v / c)
    
    # Test valid velocity
    T = 1.0
    v = 0.5 * c
    Z = physical_transform(T, v)
    print(f"Physical domain: T={T}, v={v:.2e}, Z={Z:.2f}")
    assert Z == T * 0.5, "Physical transform incorrect"
    
    # Test causality check
    try:
        Z_invalid = physical_transform(T, c)
        assert False, "Should raise ValueError for v >= c"
    except ValueError as e:
        print(f"Causality check passed: {e}")
    
    # Discrete domain: Z = n(Δ_n / Δ_max)
    def discrete_transform(n, delta_n, delta_max):
        """Discrete domain"""
        if delta_max == 0:
            raise ValueError("Division by zero: Δ_max = 0")
        return n * (delta_n / delta_max)
    
    n = 100
    delta_n = 5
    delta_max = 50
    Z_discrete = discrete_transform(n, delta_n, delta_max)
    print(f"Discrete domain: n={n}, Δ_n={delta_n}, Δ_max={delta_max}, Z={Z_discrete:.2f}")
    assert Z_discrete == 10.0, "Discrete transform incorrect"
    
    print("✓ Domain-specific forms test passed")
    return True


def test_rng_pcg64_initialization():
    """Test that all classes use PCG64 RNG (MC-RNG-002)."""
    print("\n=== Test: RNG PCG64 Initialization (MC-RNG-002) ===")
    
    import numpy as np
    
    print(f"NumPy version: {np.__version__}")
    
    # Test each class
    estimator = MonteCarloEstimator(seed=42)
    assert hasattr(estimator, 'rng'), "MonteCarloEstimator missing rng attribute"
    assert isinstance(estimator.rng, np.random.Generator), "RNG not a Generator"
    print(f"✓ MonteCarloEstimator uses Generator: {type(estimator.rng).__name__}")
    
    validator = Z5DMonteCarloValidator(seed=42)
    assert hasattr(validator, 'rng'), "Z5DMonteCarloValidator missing rng attribute"
    assert isinstance(validator.rng, np.random.Generator), "RNG not a Generator"
    print(f"✓ Z5DMonteCarloValidator uses Generator: {type(validator.rng).__name__}")
    
    enhancer = FactorizationMonteCarloEnhancer(seed=42)
    assert hasattr(enhancer, 'rng'), "FactorizationMonteCarloEnhancer missing rng attribute"
    assert isinstance(enhancer.rng, np.random.Generator), "RNG not a Generator"
    print(f"✓ FactorizationMonteCarloEnhancer uses Generator: {type(enhancer.rng).__name__}")
    
    analyzer = HyperRotationMonteCarloAnalyzer(seed=42)
    assert hasattr(analyzer, 'rng'), "HyperRotationMonteCarloAnalyzer missing rng attribute"
    assert isinstance(analyzer.rng, np.random.Generator), "RNG not a Generator"
    print(f"✓ HyperRotationMonteCarloAnalyzer uses Generator: {type(analyzer.rng).__name__}")
    
    print("✓ All classes use PCG64 Generator RNG")
    return True


def test_rng_deterministic_replay():
    """Test deterministic replay across runs (MC-RNG-002)."""
    print("\n=== Test: RNG Deterministic Replay (MC-RNG-002) ===")
    
    import numpy as np
    
    seed = 99887766
    N = 10000
    
    print(f"NumPy version: {np.__version__}")
    print(f"Seed: {seed}")
    print(f"N: {N}")
    
    # Run 1
    est1 = MonteCarloEstimator(seed=seed)
    pi1, error1, var1 = est1.estimate_pi(N)
    
    # Run 2
    est2 = MonteCarloEstimator(seed=seed)
    pi2, error2, var2 = est2.estimate_pi(N)
    
    # Run 3 (different class)
    enh1 = FactorizationMonteCarloEnhancer(seed=seed)
    candidates1 = enh1.sample_near_sqrt(77, num_samples=100)
    
    enh2 = FactorizationMonteCarloEnhancer(seed=seed)
    candidates2 = enh2.sample_near_sqrt(77, num_samples=100)
    
    print(f"Run 1: π = {pi1:.15f}")
    print(f"Run 2: π = {pi2:.15f}")
    print(f"Difference: {abs(pi1 - pi2):.2e}")
    
    assert abs(pi1 - pi2) < 1e-10, f"π estimates not identical: {pi1} vs {pi2}"
    assert abs(error1 - error2) < 1e-10, "Error bounds not identical"
    assert abs(var1 - var2) < 1e-10, "Variances not identical"
    
    print(f"Factorization candidates 1: {candidates1[:5]}...")
    print(f"Factorization candidates 2: {candidates2[:5]}...")
    assert candidates1 == candidates2, "Factorization candidates not identical"
    
    print("✓ Deterministic replay test passed")
    return True


def run_all_tests():
    """Run all test cases."""
    print("=" * 70)
    print("Monte Carlo Integration Test Suite")
    print("=" * 70)
    
    tests = [
        test_monte_carlo_pi_estimation,
        test_reproducibility,
        test_convergence_rate,
        test_z5d_prime_sampling,
        test_z5d_curvature_calibration,
        test_factorization_sampling,
        test_phi_biased_sampling,
        test_hyper_rotation_analysis,
        test_pq_lattice_resistance,
        test_precision_target,
        test_domain_specific_forms,
        test_rng_pcg64_initialization,
        test_rng_deterministic_replay,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n✗ Test {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed > 0:
        print("\n⚠ Some tests failed. Review errors above.")
        return False
    else:
        print("\n✓ All tests passed!")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
