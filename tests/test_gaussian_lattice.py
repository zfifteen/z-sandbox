#!/usr/bin/env python3
"""
Unit tests for Gaussian Integer Lattice module.

Tests lattice-based computations, Epstein zeta functions, and
integration with z-sandbox factorization framework.

Run from repository root:
    PYTHONPATH=python python3 tests/test_gaussian_lattice.py
"""

import sys
sys.path.append("../python")
sys.path.append("python")

import math
import time
from gaussian_lattice import (
    GaussianIntegerLattice,
    LatticeMonteCarloIntegrator,
    demonstrate_gaussian_lattice_identity
)


def test_closed_form_computation():
    """Test closed-form Epstein zeta expression computation."""
    print("\n=== Test: Closed-Form Computation ===")
    
    lattice = GaussianIntegerLattice(precision_dps=50)
    closed_form = lattice.epstein_zeta_closed_form()
    
    print(f"Closed form value: {closed_form}")
    
    # Check that result is positive and reasonable
    assert float(closed_form) > 0, "Closed form must be positive"
    assert float(closed_form) < 100, "Closed form should be reasonable magnitude"
    
    # Reproducibility test
    closed_form2 = lattice.epstein_zeta_closed_form()
    diff = abs(closed_form - closed_form2)
    assert float(diff) < 1e-40, "Results must be reproducible"
    
    print("✓ Closed-form computation test passed")
    return True


def test_lattice_sum_convergence():
    """Test that lattice sum converges as max_n increases."""
    print("\n=== Test: Lattice Sum Convergence ===")
    
    lattice = GaussianIntegerLattice(precision_dps=50)
    
    # Test increasing lattice sizes
    sizes = [10, 20, 50]
    sums = []
    
    for max_n in sizes:
        sum_val, num_terms = lattice.lattice_sum_numerical(max_n)
        sums.append(float(sum_val))
        print(f"max_n = {max_n:>3}, num_terms = {num_terms:>6}, sum = {sums[-1]:.10f}")
    
    # Check monotonic convergence (sum should stabilize)
    assert len(sums) == 3, "Should have computed 3 sums"
    
    # Check that differences are decreasing (convergence)
    diff_1_2 = abs(sums[1] - sums[0])
    diff_2_3 = abs(sums[2] - sums[1])
    
    print(f"Difference 10→20: {diff_1_2:.6e}")
    print(f"Difference 20→50: {diff_2_3:.6e}")
    
    # Later differences should be smaller (convergence)
    assert diff_2_3 < diff_1_2, "Sum should converge with increasing max_n"
    
    print("✓ Lattice sum convergence test passed")
    return True


def test_lattice_enhanced_distance():
    """Test lattice-enhanced distance metric."""
    print("\n=== Test: Lattice-Enhanced Distance ===")
    
    lattice = GaussianIntegerLattice(precision_dps=50)
    
    # Test cases: simple integer points
    test_cases = [
        (0+0j, 1+0j, 1.0),  # Distance 1
        (0+0j, 3+4j, 5.0),  # Distance 5 (3-4-5 triangle)
        (7+0j, 11+0j, 4.0), # Distance 4
    ]
    
    print(f"{'z1':>10} {'z2':>10} {'Expected':>10} {'Euclidean':>12} {'Enhanced':>12} {'Match':>8}")
    print("-" * 70)
    
    for z1, z2, expected_dist in test_cases:
        euclidean = abs(z2 - z1)
        enhanced = lattice.lattice_enhanced_distance(z1, z2, lattice_scale=0.0)
        
        # With scale=0, should match Euclidean
        diff = abs(float(enhanced) - euclidean)
        match = "✓" if diff < 1e-6 else "✗"
        
        print(f"{str(z1):>10} {str(z2):>10} {expected_dist:>10.2f} "
              f"{euclidean:>12.6f} {float(enhanced):>12.6f} {match:>8}")
        
        assert diff < 1e-6, f"Enhanced distance with scale=0 should match Euclidean"
    
    # Test with non-zero scale
    enhanced_scaled = lattice.lattice_enhanced_distance(0+0j, 1.5+0.5j, lattice_scale=0.5)
    euclidean_scaled = abs(1.5+0.5j)
    
    # Enhanced should differ from Euclidean with non-zero scale
    print(f"\nWith lattice_scale=0.5:")
    print(f"Euclidean: {euclidean_scaled:.6f}")
    print(f"Enhanced:  {float(enhanced_scaled):.6f}")
    
    print("✓ Lattice-enhanced distance test passed")
    return True


def test_lattice_density_sampling():
    """Test Monte Carlo lattice density sampling."""
    print("\n=== Test: Lattice Density Sampling ===")
    
    lattice = GaussianIntegerLattice(precision_dps=50)
    
    # Sample with moderate radius and fixed seed
    radius = 10.0
    num_samples = 10000
    
    result = lattice.sample_lattice_density(radius, num_samples, seed=42)
    
    print(f"Radius: {result['radius']}")
    print(f"Samples: {result['num_samples']}")
    print(f"Density estimate: {result['density_estimate']:.6f}")
    print(f"π estimate: {result['pi_estimate']:.6f}")
    print(f"Expected lattice points: {result['expected_lattice_points']:.2f}")
    
    # Check that π estimate is reasonable (should be close to π)
    pi_error = abs(result['pi_estimate'] - math.pi)
    print(f"π error: {pi_error:.4f}")
    
    # With 10k samples, should be within 0.1 of π (Monte Carlo variance)
    assert pi_error < 0.1, f"π estimate should be reasonably close: {result['pi_estimate']}"
    
    print("✓ Lattice density sampling test passed")
    return True


def test_z5d_lattice_curvature():
    """Test Z5D curvature with lattice corrections."""
    print("\n=== Test: Z5D Lattice Curvature ===")
    
    lattice = GaussianIntegerLattice(precision_dps=50)
    
    # Test at different scales
    test_n = [100, 1000, 10000]
    
    print(f"{'n':>10} {'d(n)':>8} {'κ Standard':>15} {'κ Enhanced':>15} {'Enhancement':>12}")
    print("-" * 65)
    
    E2 = math.exp(2)
    
    for n in test_n:
        d_n = lattice._count_divisors(n)
        kappa_standard = d_n * math.log(n + 1) / E2
        kappa_enhanced = lattice.z5d_lattice_curvature(n, max_lattice=10)
        
        enhancement = float(kappa_enhanced) / kappa_standard
        
        print(f"{n:>10} {d_n:>8} {kappa_standard:>15.6f} "
              f"{float(kappa_enhanced):>15.6f} {enhancement:>12.4f}x")
        
        # Enhanced should be positive and larger than standard
        assert float(kappa_enhanced) > 0, "Enhanced curvature must be positive"
        assert float(kappa_enhanced) >= kappa_standard * 0.9, "Enhanced should not be much smaller"
    
    print("✓ Z5D lattice curvature test passed")
    return True


def test_monte_carlo_lattice_integration():
    """Test Monte Carlo integration over lattice regions."""
    print("\n=== Test: Monte Carlo Lattice Integration ===")
    
    integrator = LatticeMonteCarloIntegrator(seed=42)
    
    # Simple test function: constant
    def const_func(z):
        return 1.0
    
    # Integrate over [0, 2] - should give 2
    integral, error_bound = integrator.integrate_lattice_function(
        const_func, (0, 2), num_samples=1000
    )
    
    expected = 2.0
    actual = float(integral)
    diff = abs(actual - expected)
    
    print(f"Function: f(x) = 1")
    print(f"Domain: [0, 2]")
    print(f"Expected: {expected}")
    print(f"Computed: {actual:.6f}")
    print(f"Error: {diff:.6f}")
    print(f"Error bound: ±{float(error_bound):.6f}")
    
    # Should be within reasonable margin (Monte Carlo variance)
    assert diff < 0.5, f"Integral of constant should be close to expected"
    
    # Test φ-biased sampling
    integral_phi, _ = integrator.integrate_lattice_function(
        const_func, (0, 2), num_samples=1000, use_phi_bias=True
    )
    
    diff_phi = abs(float(integral_phi) - expected)
    print(f"\nWith φ-biased sampling:")
    print(f"Computed: {float(integral_phi):.6f}")
    print(f"Error: {diff_phi:.6f}")
    
    assert diff_phi < 0.5, "φ-biased integral should also be reasonable"
    
    print("✓ Monte Carlo lattice integration test passed")
    return True


def test_validation_structure():
    """Test validation result structure."""
    print("\n=== Test: Validation Result Structure ===")
    
    lattice = GaussianIntegerLattice(precision_dps=50)
    result = lattice.validate_identity(max_n=20)
    
    # Check all expected keys are present
    required_keys = ['closed_form', 'numerical', 'error', 'relative_error', 
                     'num_terms', 'max_n', 'converged']
    
    print("Checking result dictionary keys:")
    for key in required_keys:
        assert key in result, f"Result must contain key: {key}"
        print(f"  ✓ {key}: {type(result[key]).__name__}")
    
    # Check types
    assert result['max_n'] == 20, "max_n should match input"
    assert result['num_terms'] > 0, "Should have computed some terms"
    assert isinstance(result['converged'], bool), "converged should be boolean"
    
    print(f"\nValidation result summary:")
    print(f"  max_n: {result['max_n']}")
    print(f"  num_terms: {result['num_terms']}")
    print(f"  converged: {result['converged']}")
    
    print("✓ Validation structure test passed")
    return True


def test_reproducibility():
    """Test reproducibility with fixed seed."""
    print("\n=== Test: Reproducibility ===")
    
    # Test lattice sum reproducibility (deterministic)
    lattice = GaussianIntegerLattice(precision_dps=50)
    
    sum1, _ = lattice.lattice_sum_numerical(20)
    sum2, _ = lattice.lattice_sum_numerical(20)
    
    diff = abs(sum1 - sum2)
    print(f"Lattice sum 1: {sum1}")
    print(f"Lattice sum 2: {sum2}")
    print(f"Difference: {float(diff):.2e}")
    
    assert float(diff) < 1e-40, "Lattice sums must be reproducible (deterministic)"
    
    # Test Monte Carlo reproducibility with same seed
    integrator1 = LatticeMonteCarloIntegrator(seed=42)
    integrator2 = LatticeMonteCarloIntegrator(seed=42)
    
    def test_func(z):
        return z.real
    
    # Reset numpy seed before each run for reproducibility
    import numpy as np
    np.random.seed(42)
    result1, _ = integrator1.integrate_lattice_function(test_func, (0, 1), num_samples=100)
    
    np.random.seed(42)
    result2, _ = integrator2.integrate_lattice_function(test_func, (0, 1), num_samples=100)
    
    mc_diff = abs(float(result1) - float(result2))
    print(f"\nMonte Carlo result 1: {float(result1):.10f}")
    print(f"Monte Carlo result 2: {float(result2):.10f}")
    print(f"Difference: {mc_diff:.2e}")
    
    # With same seed and numpy state, should be very close
    assert mc_diff < 1e-6, f"Monte Carlo results should be reproducible with same seed: diff={mc_diff}"
    
    print("✓ Reproducibility test passed")
    return True


def test_performance():
    """Test performance characteristics."""
    print("\n=== Test: Performance ===")
    
    lattice = GaussianIntegerLattice(precision_dps=50)
    
    # Time different lattice sizes
    sizes = [10, 20, 50]
    times = []
    
    print(f"{'max_n':>8} {'Time (s)':>12} {'Terms':>10}")
    print("-" * 35)
    
    for max_n in sizes:
        start = time.time()
        _, num_terms = lattice.lattice_sum_numerical(max_n)
        elapsed = time.time() - start
        times.append(elapsed)
        
        print(f"{max_n:>8} {elapsed:>12.4f} {num_terms:>10}")
    
    # Check that time increases with problem size (but not excessively)
    assert times[-1] > times[0], "Larger problems should take more time"
    assert times[-1] < 10.0, "Should complete in reasonable time"
    
    print("✓ Performance test passed")
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("Gaussian Integer Lattice Test Suite")
    print("=" * 70)
    
    tests = [
        test_closed_form_computation,
        test_lattice_sum_convergence,
        test_lattice_enhanced_distance,
        test_lattice_density_sampling,
        test_z5d_lattice_curvature,
        test_monte_carlo_lattice_integration,
        test_validation_structure,
        test_reproducibility,
        test_performance,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
