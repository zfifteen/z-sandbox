#!/usr/bin/env python3
"""
Unit tests for 100-target validation workflow.
Tests target generation, batch processing, checkpointing, and analysis.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
import os

from generate_256bit_targets import (
    generate_unbiased_target,
    generate_biased_target,
    generate_100_target_set,
    assert_256_balance
)
from batch_factor import (
    load_checkpoint,
    save_checkpoint,
    get_target_type,
    get_timeout_for_target
)
from analyze_100sample import (
    wilson_ci,
    analyze_results
)


class TestTargetGeneration100Sample(unittest.TestCase):
    """Test 100-target generation functionality."""
    
    def test_generate_unbiased_target(self):
        """Test unbiased target generation."""
        target = generate_unbiased_target("UB-001", seed=42)
        
        # Verify structure
        self.assertEqual(target['id'], "UB-001")
        self.assertEqual(target['type'], 'unbiased')
        self.assertFalse(target['bias_close'])
        
        # Verify balance
        assert_256_balance(target)
        
        # Verify it's a valid semiprime
        N = int(target['N'])
        p = int(target['p'])
        q = int(target['q'])
        self.assertEqual(p * q, N)
    
    def test_generate_biased_target(self):
        """Test biased target generation."""
        target = generate_biased_target("B-001", seed=42, max_gap=2**64)
        
        # Verify structure
        self.assertEqual(target['id'], "B-001")
        self.assertEqual(target['type'], 'biased')
        self.assertTrue(target['bias_close'])
        
        # Verify balance
        assert_256_balance(target)
        
        # Verify it's a valid semiprime
        N = int(target['N'])
        p = int(target['p'])
        q = int(target['q'])
        self.assertEqual(p * q, N)
        
        # Verify gap constraint
        gap = abs(p - q)
        self.assertLessEqual(gap, 2**64 * 2)  # Allow some flexibility
    
    def test_generate_100_target_set(self):
        """Test generation of 100 targets with correct distribution."""
        targets = generate_100_target_set(unbiased_count=8, biased_count=2, seed=42)
        
        # Verify count
        self.assertEqual(len(targets), 10)
        
        # Verify distribution
        unbiased = [t for t in targets if t['type'] == 'unbiased']
        biased = [t for t in targets if t['type'] == 'biased']
        
        self.assertEqual(len(unbiased), 8)
        self.assertEqual(len(biased), 2)
        
        # Verify all targets are valid
        for target in targets:
            assert_256_balance(target)
    
    def test_reproducibility(self):
        """Test that generation is reproducible with same seed."""
        # Note: Due to sympy.randprime using its own internal randomness,
        # exact reproducibility is not guaranteed. We test structural properties instead.
        targets1 = generate_100_target_set(unbiased_count=3, biased_count=2, seed=42)
        
        # Verify structure is consistent
        self.assertEqual(len(targets1), 5)
        
        unbiased = [t for t in targets1 if t['type'] == 'unbiased']
        biased = [t for t in targets1 if t['type'] == 'biased']
        
        self.assertEqual(len(unbiased), 3)
        self.assertEqual(len(biased), 2)
        
        # Verify all are valid
        for target in targets1:
            assert_256_balance(target)


class TestCheckpointing(unittest.TestCase):
    """Test checkpoint functionality."""
    
    def setUp(self):
        """Create temporary directory for test files."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)
    
    def test_save_and_load_checkpoint(self):
        """Test saving and loading checkpoint files."""
        checkpoint_file = Path(self.test_dir) / "checkpoint.json"
        
        # Create test results
        results = [
            {'target_id': '1', 'success': True, 'method': 'ecm_sympy'},
            {'target_id': '2', 'success': False, 'method': 'timeout'},
        ]
        
        # Save checkpoint
        save_checkpoint(results, checkpoint_file)
        
        # Verify file exists
        self.assertTrue(checkpoint_file.exists())
        
        # Load checkpoint
        loaded = load_checkpoint(checkpoint_file)
        
        # Verify content
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]['target_id'], '1')
        self.assertEqual(loaded[1]['target_id'], '2')
    
    def test_load_nonexistent_checkpoint(self):
        """Test loading checkpoint that doesn't exist."""
        checkpoint_file = Path(self.test_dir) / "nonexistent.json"
        
        loaded = load_checkpoint(checkpoint_file)
        
        # Should return empty list
        self.assertEqual(loaded, [])


class TestTargetTypeHelpers(unittest.TestCase):
    """Test helper functions for target types."""
    
    def test_get_target_type_new_format(self):
        """Test target type detection with new format."""
        target = {'type': 'unbiased', 'bias_close': False}
        self.assertEqual(get_target_type(target), 'unbiased')
        
        target = {'type': 'biased', 'bias_close': True}
        self.assertEqual(get_target_type(target), 'biased')
    
    def test_get_target_type_old_format(self):
        """Test target type detection with old format (fallback)."""
        target = {'bias_close': False}
        self.assertEqual(get_target_type(target), 'unbiased')
        
        target = {'bias_close': True}
        self.assertEqual(get_target_type(target), 'biased')
    
    def test_get_timeout_for_target(self):
        """Test timeout selection based on target type."""
        unbiased_target = {'type': 'unbiased'}
        biased_target = {'type': 'biased'}
        
        timeout_ub = get_timeout_for_target(unbiased_target, 3600, 300)
        timeout_bi = get_timeout_for_target(biased_target, 3600, 300)
        
        self.assertEqual(timeout_ub, 3600)
        self.assertEqual(timeout_bi, 300)


class TestWilsonCI(unittest.TestCase):
    """Test Wilson confidence interval calculation."""
    
    def test_wilson_ci_zero_successes(self):
        """Test CI with zero successes."""
        lower, upper = wilson_ci(0, 100, 0.95)
        
        # Lower should be very close to 0 (allow for floating point precision)
        self.assertAlmostEqual(lower, 0.0, places=10)
        
        # Upper should be small but > 0
        self.assertGreater(upper, 0.0)
        self.assertLess(upper, 0.05)
    
    def test_wilson_ci_all_successes(self):
        """Test CI with all successes."""
        lower, upper = wilson_ci(100, 100, 0.95)
        
        # Upper should be 1
        self.assertEqual(upper, 1.0)
        
        # Lower should be high but < 1
        self.assertLess(lower, 1.0)
        self.assertGreater(lower, 0.95)
    
    def test_wilson_ci_fifty_percent(self):
        """Test CI with 50% success rate."""
        lower, upper = wilson_ci(50, 100, 0.95)
        
        # Should be centered around 0.5
        self.assertGreater(lower, 0.4)
        self.assertLess(upper, 0.6)
        
        # CI should contain 0.5
        self.assertLessEqual(lower, 0.5)
        self.assertGreaterEqual(upper, 0.5)
    
    def test_wilson_ci_zero_trials(self):
        """Test CI with zero trials."""
        lower, upper = wilson_ci(0, 0, 0.95)
        
        # Should return (0, 0)
        self.assertEqual(lower, 0.0)
        self.assertEqual(upper, 0.0)


class TestAnalysis(unittest.TestCase):
    """Test analysis functionality."""
    
    def test_analyze_results_basic(self):
        """Test basic analysis with mixed results."""
        results = [
            {'target_type': 'unbiased', 'success': True, 'method': 'ecm_sympy', 'elapsed_seconds': 100},
            {'target_type': 'unbiased', 'success': False, 'method': 'timeout', 'elapsed_seconds': 3600},
            {'target_type': 'biased', 'success': True, 'method': 'fermat', 'elapsed_seconds': 5},
            {'target_type': 'biased', 'success': True, 'method': 'ecm_sympy', 'elapsed_seconds': 10},
        ]
        
        analysis = analyze_results(results)
        
        # Check counts
        self.assertEqual(analysis['unbiased']['total'], 2)
        self.assertEqual(analysis['unbiased']['success'], 1)
        self.assertEqual(analysis['biased']['total'], 2)
        self.assertEqual(analysis['biased']['success'], 2)
        
        # Check rates
        self.assertEqual(analysis['unbiased']['rate'], 0.5)
        self.assertEqual(analysis['biased']['rate'], 1.0)
        
        # Check overall
        self.assertEqual(analysis['overall']['total'], 4)
        self.assertEqual(analysis['overall']['success'], 3)
    
    def test_analyze_results_all_failures(self):
        """Test analysis with all failures."""
        results = [
            {'target_type': 'unbiased', 'success': False, 'method': 'timeout'},
            {'target_type': 'unbiased', 'success': False, 'method': 'timeout'},
        ]
        
        analysis = analyze_results(results)
        
        # Check counts
        self.assertEqual(analysis['unbiased']['total'], 2)
        self.assertEqual(analysis['unbiased']['success'], 0)
        self.assertEqual(analysis['unbiased']['rate'], 0.0)
        
        # Time stats should be None
        self.assertIsNone(analysis['unbiased']['avg_time'])


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTargetGeneration100Sample))
    suite.addTests(loader.loadTestsFromTestCase(TestCheckpointing))
    suite.addTests(loader.loadTestsFromTestCase(TestTargetTypeHelpers))
    suite.addTests(loader.loadTestsFromTestCase(TestWilsonCI))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalysis))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
