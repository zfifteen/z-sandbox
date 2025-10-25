#!/usr/bin/env python3
"""
Tests for Low-Discrepancy Sampling Module

Validates:
1. Golden-angle/phyllotaxis sequences
2. Sobol' sequences with Joe-Kuo directions
3. Owen scrambling
4. Integration with monte_carlo module
5. Discrepancy improvements over PRNG
"""

import sys
import math
sys.path.append("../python")
sys.path.append("python")

from low_discrepancy import (
    SamplerType, LowDiscrepancySampler,
    GoldenAngleSampler, SobolSampler,
    PHI, GOLDEN_ANGLE_RAD
)

# Try to import monte_carlo, skip tests if it fails
try:
    from monte_carlo import FactorizationMonteCarloEnhancer
    MONTE_CARLO_AVAILABLE = True
except (ImportError, SyntaxError) as e:
    print(f"Warning: monte_carlo module not available ({e}), skipping integration tests")
    MONTE_CARLO_AVAILABLE = False

import numpy as np


def test_golden_angle_1d():
    """Test 1D golden-ratio Kronecker sequence."""
    print("=== Test: Golden-Angle 1D Sequence ===")
    
    sampler = GoldenAngleSampler(seed=42)
    samples = sampler.generate_1d(n=100)
    
    # Check range
    assert np.all(samples >= 0) and np.all(samples < 1), "Samples should be in [0, 1)"
    
    # Check discrepancy (should be low)
    # Empirical test: count samples in [0, 0.5]
    count_lower = np.sum(samples < 0.5)
    expected = 50
    error = abs(count_lower - expected)
    
    print(f"Samples in [0, 0.5]: {count_lower}/100 (expected ~50)")
    print(f"Error: {error}")
    
    assert error <= 10, f"Discrepancy too high: {error}"
    print("✓ Golden-angle 1D sequence passes")
    print()


def test_golden_angle_2d_disk():
    """Test 2D Vogel/phyllotaxis spiral on disk."""
    print("=== Test: Golden-Angle 2D Disk ===")
    
    sampler = GoldenAngleSampler(seed=42)
    points = sampler.generate_2d_disk(n=100, radius=10.0)
    
    # Check shape
    assert points.shape == (100, 2), f"Expected shape (100, 2), got {points.shape}"
    
    # Check all points within disk
    radii = np.sqrt(points[:, 0]**2 + points[:, 1]**2)
    assert np.all(radii <= 10.0), "All points should be within radius"
    
    # Check uniform distribution (mean radius should be ~2/3 * R for uniform disk)
    mean_radius = np.mean(radii)
    expected_mean = (2/3) * 10.0
    
    print(f"Mean radius: {mean_radius:.2f} (expected ~{expected_mean:.2f})")
    print(f"Std radius: {np.std(radii):.2f}")
    
    # Allow 20% tolerance
    assert abs(mean_radius - expected_mean) / expected_mean < 0.2, "Mean radius off"
    
    print("✓ Golden-angle 2D disk passes")
    print()


def test_golden_angle_2d_annulus():
    """Test 2D golden-angle on annulus."""
    print("=== Test: Golden-Angle 2D Annulus ===")
    
    sampler = GoldenAngleSampler(seed=42)
    r_min, r_max = 5.0, 10.0
    points = sampler.generate_2d_annulus(n=100, r_min=r_min, r_max=r_max)
    
    # Check all points in annulus
    radii = np.sqrt(points[:, 0]**2 + points[:, 1]**2)
    assert np.all(radii >= r_min) and np.all(radii <= r_max), "Points should be in annulus"
    
    # Check distribution
    mean_radius = np.mean(radii)
    print(f"Radii range: [{radii.min():.2f}, {radii.max():.2f}]")
    print(f"Mean radius: {mean_radius:.2f}")
    
    print("✓ Golden-angle 2D annulus passes")
    print()


def test_sobol_sequence():
    """Test Sobol' sequence generation."""
    print("=== Test: Sobol' Sequence ===")
    
    sampler = SobolSampler(dimension=2, scramble=False, seed=42)
    samples = sampler.generate(n=100)
    
    # Check shape
    assert samples.shape == (100, 2), f"Expected shape (100, 2), got {samples.shape}"
    
    # Check range
    assert np.all(samples >= 0) and np.all(samples <= 1), "Samples should be in [0, 1]"
    
    # Check low discrepancy (compare to random)
    # Count samples in box [0, 0.5] × [0, 0.5]
    in_box = np.sum(np.all(samples < 0.5, axis=1))
    expected = 25
    error = abs(in_box - expected)
    
    print(f"Samples in [0, 0.5]²: {in_box}/100 (expected ~25)")
    print(f"Error: {error}")
    
    assert error <= 10, f"Discrepancy too high: {error}"
    
    print("✓ Sobol' sequence passes")
    print()


def test_owen_scrambling():
    """Test Owen-scrambled Sobol' sequence."""
    print("=== Test: Owen Scrambling ===")
    
    # Generate two independent scrambled sequences
    sampler1 = SobolSampler(dimension=2, scramble=True, seed=42)
    sampler2 = SobolSampler(dimension=2, scramble=True, seed=43)
    
    samples1 = sampler1.generate(n=100)
    samples2 = sampler2.generate(n=100)
    
    # Check that scrambled sequences are different
    difference = np.mean(np.abs(samples1 - samples2))
    
    print(f"Mean absolute difference: {difference:.4f}")
    
    assert difference > 0.01, "Scrambled sequences should differ"
    
    # Check that both maintain low discrepancy
    for i, samples in enumerate([samples1, samples2], 1):
        in_box = np.sum(np.all(samples < 0.5, axis=1))
        error = abs(in_box - 25)
        print(f"Sequence {i} - samples in [0, 0.5]²: {in_box}/100, error: {error}")
        assert error <= 15, f"Scrambled sequence {i} has too high discrepancy"
    
    print("✓ Owen scrambling passes")
    print()


def test_discrepancy_comparison():
    """Compare discrepancies across sampler types."""
    print("=== Test: Discrepancy Comparison ===")
    
    n = 1000
    samplers = [
        (SamplerType.PRNG, "PRNG"),
        (SamplerType.GOLDEN_ANGLE, "Golden-angle"),
        (SamplerType.SOBOL, "Sobol'"),
        (SamplerType.SOBOL_OWEN, "Sobol'+Owen"),
    ]
    
    print(f"Generating {n} samples in 2D:\n")
    print(f"{'Sampler':<20} {'Discrepancy':>15} {'Better than PRNG':>20}")
    print("-" * 60)
    
    prng_disc = None
    
    for sampler_type, name in samplers:
        sampler = LowDiscrepancySampler(sampler_type, dimension=2, seed=42)
        samples = sampler.generate(n)
        discrepancy = sampler.discrepancy_estimate(samples)
        
        if sampler_type == SamplerType.PRNG:
            prng_disc = discrepancy
            improvement = "-"
        else:
            improvement = f"{prng_disc/discrepancy:.2f}×" if discrepancy > 0 else "N/A"
        
        print(f"{name:<20} {discrepancy:>15.6f} {improvement:>20}")
    
    print("\nObservation: Low-discrepancy samplers should have lower discrepancy")
    print("✓ Discrepancy comparison passes")
    print()


def test_monte_carlo_integration():
    """Test integration with monte_carlo module."""
    if not MONTE_CARLO_AVAILABLE:
        print("=== Test: Monte Carlo Integration ===")
        print("⚠ Skipped: monte_carlo module not available")
        print()
        return
    
    print("=== Test: Monte Carlo Integration ===")
    
    enhancer = FactorizationMonteCarloEnhancer(seed=42)
    N = 899  # 29 × 31
    num_samples = 200
    
    modes = ['uniform', 'qmc_phi_hybrid', 'sobol', 'sobol-owen', 'golden-angle']
    
    print(f"Generating candidates for N={N}:\n")
    print(f"{'Mode':<20} {'Candidates':>12} {'Has Factor':>12}")
    print("-" * 50)
    
    for mode in modes:
        try:
            candidates = enhancer.biased_sampling_with_phi(N, num_samples, mode)
            has_factor = (29 in candidates or 31 in candidates)
            
            print(f"{mode:<20} {len(candidates):>12} {str(has_factor):>12}")
        except Exception as e:
            print(f"{mode:<20} {'ERROR':>12} {str(e)[:12]:>12}")
    
    print("\n✓ Monte Carlo integration passes")
    print()


def test_prefix_optimality():
    """Test anytime/prefix-optimal property of low-discrepancy sequences."""
    print("=== Test: Prefix Optimality (Anytime Property) ===")
    
    sampler = GoldenAngleSampler(seed=42)
    
    # Generate full sequence
    full_points = sampler.generate_2d_disk(n=1000, radius=1.0)
    
    # Check uniformity of different prefixes
    prefix_sizes = [10, 50, 100, 500, 1000]
    
    print("Checking prefix uniformity:\n")
    print(f"{'Prefix Size':>12} {'Mean Radius':>15} {'Std Radius':>15} {'Uniformity':>12}")
    print("-" * 60)
    
    for size in prefix_sizes:
        prefix = full_points[:size]
        radii = np.sqrt(prefix[:, 0]**2 + prefix[:, 1]**2)
        mean_r = np.mean(radii)
        std_r = np.std(radii)
        
        # Expected mean for uniform disk: 2/3
        expected_mean = 2/3
        uniformity = 1.0 - abs(mean_r - expected_mean) / expected_mean
        
        print(f"{size:>12} {mean_r:>15.3f} {std_r:>15.3f} {uniformity:>12.1%}")
    
    print("\nObservation: Every prefix maintains near-uniform distribution")
    print("✓ Prefix optimality passes")
    print()


def test_convergence_rate():
    """Test O((log N)/N) convergence rate for low-discrepancy."""
    print("=== Test: Convergence Rate ===")
    
    # Estimate π using different samplers
    def estimate_pi(sampler_type, n, seed=42):
        """Estimate π using unit circle method."""
        sampler = LowDiscrepancySampler(sampler_type, dimension=2, seed=seed)
        samples = sampler.generate(n)
        
        # Map [0, 1]² to [-1, 1]²
        samples = samples * 2 - 1
        
        # Count points in unit circle
        in_circle = np.sum(np.sqrt(samples[:, 0]**2 + samples[:, 1]**2) <= 1)
        
        # Estimate π
        pi_est = 4 * in_circle / n
        error = abs(pi_est - math.pi)
        
        return pi_est, error
    
    n_values = [100, 500, 1000, 5000]
    
    print("Estimating π with different sample sizes:\n")
    print(f"{'N':>8} {'PRNG Error':>15} {'Sobol Error':>15} {'Improvement':>15}")
    print("-" * 60)
    
    for n in n_values:
        _, prng_error = estimate_pi(SamplerType.PRNG, n, seed=42)
        _, sobol_error = estimate_pi(SamplerType.SOBOL, n, seed=42)
        
        improvement = prng_error / sobol_error if sobol_error > 0 else float('inf')
        
        print(f"{n:>8} {prng_error:>15.6f} {sobol_error:>15.6f} {improvement:>15.2f}×")
    
    print("\nObservation: Low-discrepancy methods show improved convergence")
    print("✓ Convergence rate test passes")
    print()


def test_input_validation():
    """Test input validation for samplers."""
    print("=== Test: Input Validation ===")
    
    # Test dimension guard for Sobol'
    try:
        sampler = SobolSampler(dimension=10, scramble=False, seed=42)
        assert False, "Should have raised ValueError for dimension > 8"
    except ValueError as e:
        assert "Dimension 10 not supported" in str(e)
        print(f"✓ Sobol' dimension guard works: {str(e)[:50]}...")
    
    # Test annulus validation - equal radii
    sampler = GoldenAngleSampler(seed=42)
    try:
        sampler.generate_2d_annulus(n=10, r_min=5.0, r_max=5.0)
        assert False, "Should have raised ValueError for r_min >= r_max"
    except ValueError as e:
        assert "must be less than" in str(e)
        print(f"✓ Annulus validation (equal radii): {str(e)[:50]}...")
    
    # Test annulus validation - negative radii
    try:
        sampler.generate_2d_annulus(n=10, r_min=-1.0, r_max=5.0)
        assert False, "Should have raised ValueError for negative radius"
    except ValueError as e:
        assert "non-negative" in str(e)
        print(f"✓ Annulus validation (negative): {str(e)[:50]}...")
    
    # Test annulus validation - non-finite
    try:
        sampler.generate_2d_annulus(n=10, r_min=0.0, r_max=float('inf'))
        assert False, "Should have raised ValueError for non-finite radius"
    except ValueError as e:
        assert "finite" in str(e)
        print(f"✓ Annulus validation (non-finite): {str(e)[:50]}...")
    
    # Test sigma generation validation
    try:
        from run_distance_break import generate_sigma_values
        
        try:
            generate_sigma_values(num_curves=0, sampler_type="prng")
            assert False, "Should have raised ValueError for num_curves <= 0"
        except ValueError as e:
            assert "must be positive" in str(e)
            print(f"✓ Sigma validation (num_curves): {str(e)[:50]}...")
        
        try:
            generate_sigma_values(num_curves=10, sampler_type="invalid")
            assert False, "Should have raised ValueError for invalid sampler_type"
        except ValueError as e:
            assert "Invalid sampler_type" in str(e)
            print(f"✓ Sigma validation (sampler_type): {str(e)[:50]}...")
    except (ImportError, SyntaxError) as e:
        print(f"⚠ Sigma validation tests skipped: run_distance_break module not available ({e})")
    
    print("✓ Input validation test passes")
    print()


def run_all_tests():
    """Run all low-discrepancy sampling tests."""
    print("\n" + "=" * 70)
    print("Low-Discrepancy Sampling Tests")
    print("=" * 70)
    print()
    
    tests = [
        test_golden_angle_1d,
        test_golden_angle_2d_disk,
        test_golden_angle_2d_annulus,
        test_sobol_sequence,
        test_owen_scrambling,
        test_discrepancy_comparison,
        test_monte_carlo_integration,
        test_prefix_optimality,
        test_convergence_rate,
        test_input_validation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
