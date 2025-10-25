#!/usr/bin/env python3
"""
Tests for Deterministic Oracle Module

Validates:
1. High-precision π computation using Chudnovsky and Ramanujan series
2. Convergence behavior of hypergeometric series
3. Oracle accuracy against known values
4. Integration with QMC benchmark infrastructure
"""

import sys
import os
import math
import unittest
from mpmath import mp, mpf

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from oracle import DeterministicOracle


class TestOraclePrecision(unittest.TestCase):
    """Test oracle precision and accuracy."""
    
    def setUp(self):
        """Set up oracle for tests."""
        self.oracle = DeterministicOracle(precision=100)
    
    def test_chudnovsky_convergence(self):
        """Test Chudnovsky series converges rapidly."""
        # With just 2 terms, should get ~28 decimal places
        pi_2_terms = self.oracle.compute_pi_chudnovsky(terms=2)
        pi_true = mp.pi
        
        error = abs(pi_2_terms - pi_true)
        # Should be better than 1e-27 (allowing margin)
        self.assertLess(float(error), 1e-27, 
                       "Chudnovsky series with 2 terms should achieve ~27+ digits")
    
    def test_ramanujan_convergence(self):
        """Test Ramanujan series converges."""
        # With 3 terms, should get ~24 decimal places
        pi_3_terms = self.oracle.compute_pi_ramanujan(terms=3)
        pi_true = mp.pi
        
        error = abs(pi_3_terms - pi_true)
        # Should be better than 1e-23 (allowing margin)
        self.assertLess(float(error), 1e-23,
                       "Ramanujan series with 3 terms should achieve ~23+ digits")
    
    def test_pi_cache(self):
        """Test π value caching works."""
        # First call computes
        pi_1 = self.oracle.get_pi()
        
        # Second call should use cache
        pi_2 = self.oracle.get_pi()
        
        self.assertEqual(pi_1, pi_2, "Cached π should match computed π")
    
    def test_pi_matches_known_value(self):
        """Test computed π matches known value to high precision."""
        pi_computed = self.oracle.get_pi()
        
        # Known π to 50 decimal places
        pi_known = mpf("3.14159265358979323846264338327950288419716939937510")
        
        error = abs(pi_computed - pi_known)
        self.assertLess(float(error), 1e-50,
                       "Computed π should match known value to 50 digits")
    
    def test_circle_area_exact(self):
        """Test exact circle area computation."""
        radius = 1.0
        area = self.oracle.circle_area_exact(radius)
        
        # Should equal π
        pi_val = self.oracle.get_pi()
        self.assertEqual(area, pi_val, "Unit circle area should equal π")
        
        # Test with different radius
        radius = 2.0
        area = self.oracle.circle_area_exact(radius)
        expected = pi_val * 4  # π * r² = π * 4
        
        error = abs(area - expected)
        self.assertLess(float(error), 1e-90, "Circle area formula should be exact")
    
    def test_estimate_error(self):
        """Test error estimation for π approximations."""
        # Test with rough approximation
        estimate = 3.14
        error = self.oracle.estimate_pi_error(estimate)
        
        # Error should be approximately 0.00159...
        self.assertAlmostEqual(error, 0.001592654, places=6,
                              msg="Error calculation should be accurate")
        
        # Test with better approximation
        estimate = 3.141592653
        error = self.oracle.estimate_pi_error(estimate)
        
        self.assertLess(error, 1e-9, "Error for good approximation should be small")


class TestConvergenceOracle(unittest.TestCase):
    """Test convergence oracle functionality."""
    
    def setUp(self):
        """Set up oracle for tests."""
        self.oracle = DeterministicOracle(precision=100)
    
    def test_convergence_oracle_structure(self):
        """Test convergence oracle returns expected structure."""
        # Simple estimator: always returns 3.0
        def constant_estimator(N):
            return 3.0
        
        sample_counts = [100, 1000, 10000]
        results = self.oracle.convergence_oracle(sample_counts, constant_estimator)
        
        # Check structure
        self.assertIn('N', results)
        self.assertIn('estimates', results)
        self.assertIn('errors', results)
        self.assertIn('rel_errors', results)
        self.assertIn('log_N', results)
        self.assertIn('true_value', results)
        
        # Check lengths
        self.assertEqual(len(results['N']), len(sample_counts))
        self.assertEqual(len(results['estimates']), len(sample_counts))
        self.assertEqual(len(results['errors']), len(sample_counts))
    
    def test_convergence_oracle_constant_error(self):
        """Test oracle correctly tracks constant error."""
        # Estimator always returns 3.0
        def constant_estimator(N):
            return 3.0
        
        sample_counts = [100, 1000]
        results = self.oracle.convergence_oracle(sample_counts, constant_estimator)
        
        # All errors should be the same
        error_1 = results['errors'][0]
        error_2 = results['errors'][1]
        
        self.assertAlmostEqual(error_1, error_2, places=10,
                              msg="Constant estimator should have constant error")
    
    def test_convergence_oracle_improving_estimator(self):
        """Test oracle tracks improving estimates."""
        # Simple estimator that monotonically approaches π
        # Uses π_estimate = π - 1/N to guarantee decrease
        pi_approx = 3.141592653589793
        
        def improving_estimator(N):
            return pi_approx - 1.0 / N
        
        sample_counts = [100, 1000, 10000]
        results = self.oracle.convergence_oracle(sample_counts, improving_estimator)
        
        # Errors should decrease monotonically
        for i in range(len(results['errors']) - 1):
            self.assertGreater(results['errors'][i], results['errors'][i+1],
                             msg=f"Improving estimator should have decreasing error: "
                                 f"error[{i}]={results['errors'][i]:.6e} should be > "
                                 f"error[{i+1}]={results['errors'][i+1]:.6e}")


class TestTheoreticalBounds(unittest.TestCase):
    """Test theoretical error bound calculations."""
    
    def setUp(self):
        """Set up oracle for tests."""
        self.oracle = DeterministicOracle(precision=50)
    
    def test_mc_error_bound_scaling(self):
        """Test MC error bound scales as O(1/√N)."""
        N1 = 100
        N2 = 10000  # 100× larger
        
        error_1 = self.oracle.mc_expected_error(N1)
        error_2 = self.oracle.mc_expected_error(N2)
        
        # Should scale as √(100) = 10
        ratio = error_1 / error_2
        self.assertAlmostEqual(ratio, 10.0, places=1,
                              msg="MC error should scale as 1/√N")
    
    def test_qmc_error_bound_scaling(self):
        """Test QMC error bound has better scaling than MC."""
        N = 10000
        
        mc_error = self.oracle.mc_expected_error(N)
        qmc_error = self.oracle.qmc_expected_error(N, dimension=2)
        
        # QMC should be better than MC for large N
        self.assertLess(qmc_error, mc_error,
                       msg="QMC bound should be better than MC for large N")
    
    def test_qmc_dimension_dependence(self):
        """Test QMC error bound depends on dimension."""
        N = 10000
        
        error_2d = self.oracle.qmc_expected_error(N, dimension=2)
        error_5d = self.oracle.qmc_expected_error(N, dimension=5)
        
        # Higher dimension should have larger bound
        self.assertGreater(error_5d, error_2d,
                         msg="QMC bound should increase with dimension")


class TestOracleIntegration(unittest.TestCase):
    """Test oracle integration with other components."""
    
    def test_oracle_precision_levels(self):
        """Test oracle works at different precision levels."""
        precisions = [50, 100, 200]
        
        for prec in precisions:
            oracle = DeterministicOracle(precision=prec)
            pi_val = oracle.get_pi()
            
            # Should be close to true π
            error = abs(float(pi_val) - math.pi)
            self.assertLess(error, 1e-15,
                          f"Oracle at {prec} precision should compute accurate π")
    
    def test_oracle_method_selection(self):
        """Test different computation methods."""
        oracle = DeterministicOracle(precision=100)
        
        pi_chud = oracle.get_pi(method='chudnovsky', force_recompute=True)
        pi_ram = oracle.get_pi(method='ramanujan', force_recompute=True)
        
        # Both should be close to each other
        difference = abs(pi_chud - pi_ram)
        self.assertLess(float(difference), 1e-30,
                       msg="Different methods should agree to high precision")


class TestOracleReproducibility(unittest.TestCase):
    """Test oracle reproducibility."""
    
    def test_deterministic_computation(self):
        """Test oracle produces same result every time."""
        oracle = DeterministicOracle(precision=100)
        
        # Compute multiple times
        results = []
        for _ in range(3):
            pi_val = oracle.compute_pi_chudnovsky(terms=5)
            results.append(pi_val)
        
        # All should be identical
        for i in range(len(results) - 1):
            self.assertEqual(results[i], results[i+1],
                           msg="Oracle should be deterministic")
    
    def test_precision_independence(self):
        """Test changing precision gives consistent relative results."""
        oracle_50 = DeterministicOracle(precision=50)
        oracle_100 = DeterministicOracle(precision=100)
        
        pi_50 = oracle_50.get_pi()
        pi_100 = oracle_100.get_pi()
        
        # When truncated to 50 digits, should match
        # Convert to string and compare first 50 significant figures
        str_50 = str(pi_50)[:52]  # Include "3." prefix
        str_100 = str(pi_100)[:52]
        
        self.assertEqual(str_50, str_100,
                        msg="Higher precision should agree with lower precision")


def run_tests():
    """Run all oracle tests."""
    print("=" * 80)
    print("Running Oracle Module Tests")
    print("=" * 80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOraclePrecision))
    suite.addTests(loader.loadTestsFromTestCase(TestConvergenceOracle))
    suite.addTests(loader.loadTestsFromTestCase(TestTheoreticalBounds))
    suite.addTests(loader.loadTestsFromTestCase(TestOracleIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestOracleReproducibility))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 80)
    if result.wasSuccessful():
        print("✓ All oracle tests passed!")
    else:
        print("✗ Some tests failed")
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
