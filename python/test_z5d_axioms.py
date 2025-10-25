#!/usr/bin/env python3
"""
Unit tests for Z5D Axioms implementation.

Tests empirical validation, numerical stability, and integration with
RSA factorization pipeline according to Z5D axioms.
"""

import unittest
import math
from mpmath import mp, mpf
from z5d_axioms import Z5DAxioms, z5d_enhanced_prime_search, PHI, E2, TARGET_PRECISION


class TestZ5DAxioms(unittest.TestCase):
    """Test core Z5D axioms implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.axioms = Z5DAxioms(precision_dps=50)
    
    def test_universal_invariant_basic(self):
        """Test universal invariant Z = A(B / c)."""
        A = mpf(1.0)
        B = mpf(2.0)
        c = E2
        
        Z = self.axioms.universal_invariant(A, B, c)
        
        # Verify calculation
        expected = A * (B / c)
        self.assertAlmostEqual(float(Z), float(expected), places=15)
    
    def test_universal_invariant_zero_division(self):
        """Test universal invariant raises ValueError for c=0."""
        with self.assertRaises(ValueError):
            self.axioms.universal_invariant(mpf(1), mpf(2), mpf(0))
    
    def test_discrete_domain_form(self):
        """Test discrete domain form Z = n(Δ_n / Δ_max)."""
        n = 100
        delta_n = mpf(1.5)
        delta_max = mpf(10.0)
        
        Z = self.axioms.discrete_domain_form(n, delta_n, delta_max)
        
        # Verify calculation
        expected = mpf(n) * (delta_n / delta_max)
        self.assertEqual(float(Z), float(expected))
    
    def test_discrete_domain_form_zero_division(self):
        """Test discrete domain form raises ValueError for delta_max=0."""
        with self.assertRaises(ValueError):
            self.axioms.discrete_domain_form(100, mpf(1), mpf(0))
    
    def test_curvature_positive(self):
        """Test curvature κ(n) = d(n) · ln(n+1) / e² is positive."""
        n = 1000
        d_n = self.axioms.prime_density_approximation(n)
        
        kappa = self.axioms.curvature(n, d_n)
        
        # Curvature should be positive
        self.assertGreater(float(kappa), 0)
    
    def test_curvature_negative_n(self):
        """Test curvature returns 0 for negative n (guard condition)."""
        kappa = self.axioms.curvature(-10, mpf(1.0))
        self.assertEqual(float(kappa), 0.0)
    
    def test_geometric_resolution_range(self):
        """Test geometric resolution θ'(n, k) is in valid range."""
        n = 10000
        k = 0.3
        
        theta_prime = self.axioms.geometric_resolution(n, k)
        
        # θ' should be positive and bounded by φ
        self.assertGreater(float(theta_prime), 0)
        self.assertLessEqual(float(theta_prime), float(PHI))
    
    def test_geometric_resolution_k_variation(self):
        """Test geometric resolution varies with k parameter."""
        n = 10000
        
        theta1 = self.axioms.geometric_resolution(n, k=0.2)
        theta2 = self.axioms.geometric_resolution(n, k=0.3)
        theta3 = self.axioms.geometric_resolution(n, k=0.5)
        
        # Should vary with k
        self.assertNotEqual(float(theta1), float(theta2))
        self.assertNotEqual(float(theta2), float(theta3))
    
    def test_prime_density_approximation(self):
        """Test prime density d(n) ≈ 1/ln(n)."""
        n = 10000
        
        d_n = self.axioms.prime_density_approximation(n)
        
        # Compare with expected 1/ln(n)
        expected = 1.0 / math.log(n)
        self.assertAlmostEqual(float(d_n), expected, places=10)
    
    def test_prime_density_zero_for_small_n(self):
        """Test prime density returns 0 for n <= 1."""
        self.assertEqual(float(self.axioms.prime_density_approximation(0)), 0.0)
        self.assertEqual(float(self.axioms.prime_density_approximation(1)), 0.0)
    
    def test_z5d_biased_prime_selection_components(self):
        """Test Z5D-biased prime selection returns valid components."""
        target_index = 10000
        
        theta, kappa, bias = self.axioms.z5d_biased_prime_selection(target_index, k=0.3)
        
        # All components should be positive
        self.assertGreater(float(theta), 0)
        self.assertGreater(float(kappa), 0)
        self.assertGreater(float(bias), 0)
    
    def test_z5d_biased_prime_selection_consistency(self):
        """Test Z5D-biased prime selection is deterministic."""
        target_index = 10000
        
        result1 = self.axioms.z5d_biased_prime_selection(target_index, k=0.3)
        result2 = self.axioms.z5d_biased_prime_selection(target_index, k=0.3)
        
        # Should be identical
        self.assertEqual(result1, result2)


class TestEmpiricalValidation(unittest.TestCase):
    """Test empirical validation (Axiom 1)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.axioms = Z5DAxioms(precision_dps=50)
    
    def test_empirical_validation_passes(self):
        """Test empirical validation passes all checks."""
        validation = self.axioms.empirical_validation(n_test=10000)
        
        # Should pass all tests
        self.assertTrue(validation['tests_passed'])
        self.assertEqual(len(validation['errors']), 0)
    
    def test_empirical_validation_precision(self):
        """Test empirical validation meets target precision."""
        validation = self.axioms.empirical_validation(n_test=10000)
        
        self.assertEqual(validation['precision_dps'], 50)
        self.assertEqual(validation['target_precision'], TARGET_PRECISION)
    
    def test_empirical_validation_sample_values(self):
        """Test empirical validation returns sample values."""
        validation = self.axioms.empirical_validation(n_test=10000)
        
        # Should have sample values
        self.assertIn('sample_values', validation)
        self.assertIn('theta_prime', validation['sample_values'])
        self.assertIn('curvature', validation['sample_values'])
        self.assertIn('prime_density', validation['sample_values'])
        
        # All should be positive
        self.assertGreater(validation['sample_values']['theta_prime'], 0)
        self.assertGreater(validation['sample_values']['curvature'], 0)
        self.assertGreater(validation['sample_values']['prime_density'], 0)


class TestZ5DEnhancedPrimeSearch(unittest.TestCase):
    """Test Z5D-enhanced prime search."""
    
    def test_prime_search_returns_candidates(self):
        """Test enhanced prime search returns candidates."""
        candidates = z5d_enhanced_prime_search(
            target_value=10000,
            k_resolution=0.3,
            search_window=50
        )
        
        # Should return candidates
        self.assertGreater(len(candidates), 0)
        self.assertLessEqual(len(candidates), 101)  # ±50 window
    
    def test_prime_search_sorted_by_weight(self):
        """Test candidates are sorted by weight (highest first)."""
        candidates = z5d_enhanced_prime_search(
            target_value=10000,
            k_resolution=0.3,
            search_window=50
        )
        
        # Verify sorted descending by weight
        weights = [c['weight'] for c in candidates]
        self.assertEqual(weights, sorted(weights, reverse=True))
    
    def test_prime_search_includes_metadata(self):
        """Test candidates include required metadata."""
        candidates = z5d_enhanced_prime_search(
            target_value=10000,
            k_resolution=0.3,
            search_window=10
        )
        
        # Check first candidate has all fields
        self.assertIn('k', candidates[0])
        self.assertIn('weight', candidates[0])
        self.assertIn('theta_prime', candidates[0])
        self.assertIn('curvature', candidates[0])
    
    def test_prime_search_small_target(self):
        """Test prime search handles small targets."""
        candidates = z5d_enhanced_prime_search(
            target_value=2,
            k_resolution=0.3,
            search_window=5
        )
        
        # Should return [2] or similar
        self.assertGreater(len(candidates), 0)


class TestNumericalStability(unittest.TestCase):
    """Test numerical stability across different scales."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.axioms = Z5DAxioms(precision_dps=50)
    
    def test_stability_small_values(self):
        """Test numerical stability for small values."""
        n = 10
        d_n = self.axioms.prime_density_approximation(n)
        kappa = self.axioms.curvature(n, d_n)
        theta = self.axioms.geometric_resolution(n, k=0.3)
        
        # Should all be finite and positive
        self.assertTrue(math.isfinite(float(kappa)))
        self.assertTrue(math.isfinite(float(theta)))
        self.assertGreater(float(kappa), 0)
        self.assertGreater(float(theta), 0)
    
    def test_stability_large_values(self):
        """Test numerical stability for large values (128-bit scale)."""
        n = 2**127
        d_n = self.axioms.prime_density_approximation(n)
        kappa = self.axioms.curvature(n, d_n)
        theta = self.axioms.geometric_resolution(n, k=0.3)
        
        # Should all be finite and positive
        self.assertTrue(math.isfinite(float(kappa)))
        self.assertTrue(math.isfinite(float(theta)))
        self.assertGreater(float(kappa), 0)
        self.assertGreater(float(theta), 0)
    
    def test_stability_repeated_calls(self):
        """Test stability of repeated calls."""
        n = 10000
        
        results = []
        for _ in range(10):
            theta, kappa, bias = self.axioms.z5d_biased_prime_selection(n, k=0.3)
            results.append((float(theta), float(kappa), float(bias)))
        
        # All results should be identical
        for i in range(1, len(results)):
            self.assertEqual(results[0], results[i])


class TestIntegrationWithRSA(unittest.TestCase):
    """Test integration with RSA factorization pipeline."""
    
    def test_128bit_prime_scale(self):
        """Test Z5D axioms work at 128-bit prime scale."""
        axioms = Z5DAxioms()
        
        # 128-bit prime scale
        target_value = 2**127
        k_estimate = int(target_value / math.log(target_value))
        
        # Apply Z5D bias
        theta, kappa, bias = axioms.z5d_biased_prime_selection(k_estimate, k=0.3)
        
        # Should be finite and valid
        self.assertTrue(math.isfinite(float(theta)))
        self.assertTrue(math.isfinite(float(kappa)))
        self.assertTrue(math.isfinite(float(bias)))
        
        # Should be positive
        self.assertGreater(float(theta), 0)
        self.assertGreater(float(kappa), 0)
        self.assertGreater(float(bias), 0)
    
    def test_k_resolution_recommended_value(self):
        """Test recommended k ≈ 0.3 for prime-density mapping."""
        axioms = Z5DAxioms()
        
        # Test with recommended k=0.3
        theta = axioms.geometric_resolution(10000, k=0.3)
        
        # Should be in valid range
        self.assertGreater(float(theta), 0)
        self.assertLessEqual(float(theta), float(PHI))


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
