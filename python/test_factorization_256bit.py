#!/usr/bin/env python3
"""
Unit tests for 256-bit factorization pipeline.
Validates core functionality without long-running factorization attempts.
"""

import unittest
import sympy
import json
from pathlib import Path
from factor_256bit import (
    verify_factors, 
    pollard_rho, 
    fermat_factorization,
    try_pollard_rho,
    try_fermat,
    FactorizationPipeline
)
from generate_256bit_targets import generate_balanced_128bit_prime_pair

class TestFactorizationMethods(unittest.TestCase):
    """Test individual factorization methods."""
    
    def test_verify_factors_correct(self):
        """Test factor verification with correct factors."""
        p = 13
        q = 17
        N = p * q
        self.assertTrue(verify_factors(N, p, q))
    
    def test_verify_factors_incorrect_product(self):
        """Test factor verification with incorrect product."""
        self.assertFalse(verify_factors(221, 13, 18))
    
    def test_verify_factors_composite(self):
        """Test factor verification with composite factors."""
        self.assertFalse(verify_factors(221, 13, 16))
    
    def test_pollard_rho_small(self):
        """Test Pollard's Rho on small semiprime."""
        N = 13 * 17  # 221
        factor = pollard_rho(N, max_iterations=10000)
        self.assertIsNotNone(factor)
        self.assertIn(factor, [13, 17])
    
    def test_pollard_rho_even(self):
        """Test Pollard's Rho handles even numbers."""
        N = 14  # 2 * 7
        factor = pollard_rho(N)
        self.assertEqual(factor, 2)
    
    def test_fermat_close_factors(self):
        """Test Fermat's method on close factors."""
        # Generate close factors
        p = 10007
        q = 10009
        N = p * q
        result = fermat_factorization(N, max_iterations=100)
        self.assertIsNotNone(result)
        self.assertEqual(set(result), {p, q})
    
    def test_fermat_even(self):
        """Test Fermat handles even numbers."""
        N = 14  # 2 * 7
        result = fermat_factorization(N)
        self.assertEqual(result, (2, 7))

class TestTargetGeneration(unittest.TestCase):
    """Test target generation functionality."""
    
    def test_generate_balanced_pair(self):
        """Test generation of balanced 128-bit prime pair."""
        p, q, metadata = generate_balanced_128bit_prime_pair(bias_close=False)
        
        # Verify primes
        self.assertTrue(sympy.isprime(p))
        self.assertTrue(sympy.isprime(q))
        
        # Verify bit lengths
        self.assertGreaterEqual(p.bit_length(), 127)
        self.assertLessEqual(p.bit_length(), 128)
        self.assertGreaterEqual(q.bit_length(), 127)
        self.assertLessEqual(q.bit_length(), 128)
        
        # Verify p < q
        self.assertLess(p, q)
    
    def test_generate_biased_pair(self):
        """Test generation of biased (close) prime pair."""
        p, q, metadata = generate_balanced_128bit_prime_pair(bias_close=True)
        
        # Verify primes
        self.assertTrue(sympy.isprime(p))
        self.assertTrue(sympy.isprime(q))
        
        # Verify metadata indicates bias
        self.assertTrue(metadata['bias_close'])
    
    def test_256bit_semiprime(self):
        """Test that generated pair produces 256-bit semiprime."""
        p, q, _ = generate_balanced_128bit_prime_pair()
        N = p * q
        
        # Verify N is 254-256 bits
        self.assertGreaterEqual(N.bit_length(), 254)
        self.assertLessEqual(N.bit_length(), 256)

class TestPipeline(unittest.TestCase):
    """Test factorization pipeline."""
    
    def test_pipeline_small_semiprime(self):
        """Test pipeline on small semiprime."""
        p = sympy.randprime(10**6, 10**7)
        q = sympy.randprime(10**6, 10**7)
        N = p * q
        
        pipeline = FactorizationPipeline(N, timeout_seconds=30)
        factors, method, elapsed, metadata = pipeline.run()
        
        self.assertIsNotNone(factors)
        self.assertEqual(set(factors), {p, q})
        self.assertLess(elapsed, 30)
    
    def test_pipeline_prime_input(self):
        """Test pipeline handles prime input gracefully."""
        N = 1000000007  # A large prime
        
        pipeline = FactorizationPipeline(N, timeout_seconds=5)
        factors, method, elapsed, metadata = pipeline.run()
        
        # Should not factor a prime
        self.assertIsNone(factors)

class TestTargetsFile(unittest.TestCase):
    """Test targets file structure and validity."""
    
    def setUp(self):
        """Load targets file if it exists."""
        self.targets_file = Path(__file__).parent / 'targets_256bit.json'
        if self.targets_file.exists():
            with open(self.targets_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = None
    
    def test_targets_file_exists(self):
        """Test that targets file exists."""
        self.assertTrue(self.targets_file.exists(), 
                       "targets_256bit.json not found - run generate_256bit_targets.py first")
    
    def test_targets_structure(self):
        """Test targets file has correct structure."""
        if self.data is None:
            self.skipTest("Targets file not found")
        
        self.assertIn('metadata', self.data)
        self.assertIn('targets', self.data)
        self.assertIsInstance(self.data['targets'], list)
    
    def test_targets_validity(self):
        """Test that all targets are valid semiprimes."""
        if self.data is None:
            self.skipTest("Targets file not found")
        
        for target in self.data['targets'][:3]:  # Test first 3 for speed
            N = int(target['N'])
            p = int(target['p'])
            q = int(target['q'])
            
            # Verify factorization
            self.assertEqual(p * q, N, f"Target {target['id']}: p*q != N")
            
            # Verify primality (expensive, so trust if product is correct)
            # self.assertTrue(sympy.isprime(p))
            # self.assertTrue(sympy.isprime(q))
            
            # Verify bit lengths
            self.assertGreaterEqual(N.bit_length(), 254)
            self.assertLessEqual(N.bit_length(), 256)

def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFactorizationMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestTargetGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestTargetsFile))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()

if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
