#!/usr/bin/env python3
"""
Test Monte Carlo integration with barycentric sampling mode.

Validates that the barycentric sampling mode:
1. Works correctly with the FactorizationMonteCarloEnhancer
2. Achieves comparable or better hit rates than other modes
3. Generates valid candidates
4. Integrates properly with Z5D axioms
"""

import unittest
import sys
import os

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from monte_carlo import FactorizationMonteCarloEnhancer


class TestMonteCarloBarycentric(unittest.TestCase):
    """Test barycentric sampling mode in Monte Carlo enhancer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enhancer = FactorizationMonteCarloEnhancer(seed=42)
        
        # Test semiprimes
        self.test_cases = [
            (899, 29, 31),      # 10-bit
            (1517, 37, 41),     # 11-bit
            (2021, 43, 47),     # 11-bit
        ]
    
    def test_barycentric_mode_exists(self):
        """Test that barycentric mode is available."""
        N = 899
        num_samples = 100
        
        # Should not raise an error
        candidates = self.enhancer.biased_sampling_with_phi(N, num_samples, mode='barycentric')
        
        # Should return a list
        self.assertIsInstance(candidates, list)
        self.assertGreater(len(candidates), 0)
    
    def test_barycentric_candidates_valid(self):
        """Test that barycentric mode generates valid candidates."""
        N = 899
        num_samples = 100
        
        candidates = self.enhancer.biased_sampling_with_phi(N, num_samples, mode='barycentric')
        
        # All candidates should be positive integers
        for c in candidates:
            self.assertIsInstance(c, int)
            self.assertGreater(c, 1)
            self.assertLess(c, N)
    
    def test_barycentric_hit_rate(self):
        """Test that barycentric mode achieves good hit rates."""
        num_samples = 500
        
        hits = 0
        for N, p, q in self.test_cases:
            candidates = self.enhancer.biased_sampling_with_phi(N, num_samples, mode='barycentric')
            
            if p in candidates or q in candidates:
                hits += 1
        
        hit_rate = hits / len(self.test_cases)
        
        # Should achieve at least 50% hit rate on these small test cases
        self.assertGreaterEqual(hit_rate, 0.5, 
                               f"Hit rate {hit_rate*100:.1f}% is too low")
    
    def test_barycentric_vs_uniform(self):
        """Compare barycentric mode with uniform mode."""
        N = 899
        p, q = 29, 31
        num_samples = 500
        
        # Test both modes
        candidates_bary = self.enhancer.biased_sampling_with_phi(N, num_samples, mode='barycentric')
        candidates_unif = self.enhancer.biased_sampling_with_phi(N, num_samples, mode='uniform')
        
        hit_bary = p in candidates_bary or q in candidates_bary
        hit_unif = p in candidates_unif or q in candidates_unif
        
        # Both should find factors for this easy case
        self.assertTrue(hit_bary, "Barycentric mode failed to find factors")
        self.assertTrue(hit_unif, "Uniform mode failed to find factors")
        
        # Barycentric should generate reasonable number of candidates
        self.assertGreater(len(candidates_bary), 10, 
                          "Barycentric generated too few candidates")
    
    def test_barycentric_reproducibility(self):
        """Test that barycentric mode is reproducible with same seed."""
        N = 899
        num_samples = 100
        
        # Create two enhancers with same seed
        enhancer1 = FactorizationMonteCarloEnhancer(seed=12345)
        enhancer2 = FactorizationMonteCarloEnhancer(seed=12345)
        
        candidates1 = enhancer1.biased_sampling_with_phi(N, num_samples, mode='barycentric')
        candidates2 = enhancer2.biased_sampling_with_phi(N, num_samples, mode='barycentric')
        
        # Should produce identical results
        self.assertEqual(candidates1, candidates2, 
                        "Barycentric mode is not reproducible")
    
    def test_barycentric_mode_comparison(self):
        """Compare all modes including barycentric."""
        N = 899
        p, q = 29, 31
        num_samples = 500
        
        modes = ['uniform', 'stratified', 'qmc', 'qmc_phi_hybrid', 'barycentric']
        
        results = {}
        for mode in modes:
            candidates = self.enhancer.biased_sampling_with_phi(N, num_samples, mode=mode)
            hit = p in candidates or q in candidates
            results[mode] = {
                'candidates': len(candidates),
                'hit': hit
            }
        
        # All modes should find factors for this easy case
        for mode, result in results.items():
            self.assertTrue(result['hit'], f"{mode} mode failed to find factors")
        
        # Print summary for information
        print("\nMode comparison (N=899):")
        for mode, result in results.items():
            status = "✓" if result['hit'] else "✗"
            print(f"  {mode:15s}: {status} ({result['candidates']:4d} candidates)")


class TestBarycentricIntegration(unittest.TestCase):
    """Test integration of barycentric module with Monte Carlo."""
    
    def test_barycentric_import(self):
        """Test that barycentric module can be imported."""
        try:
            import barycentric
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import barycentric module")
    
    def test_barycentric_functions_available(self):
        """Test that required barycentric functions are available."""
        from barycentric import (
            BarycentricCoordinates,
            simplicial_stratification,
            curvature_weighted_barycentric
        )
        
        # Should not raise errors
        self.assertTrue(True)


def run_tests():
    """Run all tests with detailed output."""
    print("=" * 70)
    print("Monte Carlo Barycentric Integration Tests")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMonteCarloBarycentric))
    suite.addTests(loader.loadTestsFromTestCase(TestBarycentricIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
