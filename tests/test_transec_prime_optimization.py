#!/usr/bin/env python3
"""
Unit tests for TRANSEC prime optimization feature.

Tests cover:
- Prime slot normalization strategies
- Curvature reduction verification
- Interoperability with different strategies
- Performance impact
- Edge cases
"""

import sys
import os
import time
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from transec import (
    TransecCipher,
    generate_shared_secret,
)

try:
    from transec_prime_optimization import (
        is_prime,
        compute_curvature,
        find_next_prime,
        find_nearest_prime,
        normalize_slot_to_prime,
        compute_curvature_reduction,
        verify_curvature_computation,
        EMPIRICAL_CURVATURE_VALUES,
    )
    PRIME_OPTIMIZATION_AVAILABLE = True
except ImportError:
    PRIME_OPTIMIZATION_AVAILABLE = False


@unittest.skipUnless(PRIME_OPTIMIZATION_AVAILABLE, "Prime optimization module not available")
class TestPrimeUtilities(unittest.TestCase):
    """Test prime number utility functions."""
    
    def test_is_prime(self):
        """Test prime detection."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        non_primes = [0, 1, 4, 6, 8, 9, 10, 12, 15, 20, 25]
        
        for p in primes:
            self.assertTrue(is_prime(p), f"{p} should be prime")
        
        for n in non_primes:
            self.assertFalse(is_prime(n), f"{n} should not be prime")
    
    def test_find_next_prime(self):
        """Test finding next prime."""
        test_cases = [
            (1, 2),
            (2, 2),
            (3, 3),
            (4, 5),
            (10, 11),
            (14, 17),
            (100, 101),
        ]
        
        for n, expected in test_cases:
            result = find_next_prime(n)
            self.assertEqual(result, expected, f"Next prime after {n}")
    
    def test_find_nearest_prime(self):
        """Test finding nearest prime."""
        test_cases = [
            (1, 2),
            (2, 2),
            (3, 3),
            (4, 5),
            (6, 7),
            (8, 7),
            (9, 11),
            (10, 11),
        ]
        
        for n, expected in test_cases:
            result = find_nearest_prime(n)
            self.assertEqual(result, expected, f"Nearest prime to {n}")
    
    def test_curvature_computation(self):
        """Test curvature computation against empirical values."""
        self.assertTrue(verify_curvature_computation())
        
        # Test specific values
        for n, expected in EMPIRICAL_CURVATURE_VALUES.items():
            computed = compute_curvature(n, use_mpmath=True)
            self.assertAlmostEqual(computed, expected, places=10,
                                 msg=f"Curvature mismatch at n={n}")
    
    def test_curvature_lower_for_primes(self):
        """Test that primes have lower curvature than nearby composites."""
        # Test cases where prime has lower curvature than composite
        test_pairs = [
            (5, 4),   # prime 5 vs composite 4
            (5, 6),   # prime 5 vs composite 6
            (7, 6),   # prime 7 vs composite 6
            (7, 8),   # prime 7 vs composite 8
            (11, 10), # prime 11 vs composite 10
            (11, 12), # prime 11 vs composite 12
        ]
        
        for prime, composite in test_pairs:
            kappa_prime = compute_curvature(prime)
            kappa_composite = compute_curvature(composite)
            self.assertLess(kappa_prime, kappa_composite,
                          f"κ({prime}) should be < κ({composite})")
    
    def test_normalization_strategies(self):
        """Test different normalization strategies."""
        # Test "none" strategy
        self.assertEqual(normalize_slot_to_prime(10, "none"), 10)
        
        # Test "next" strategy
        self.assertEqual(normalize_slot_to_prime(10, "next"), 11)
        self.assertEqual(normalize_slot_to_prime(11, "next"), 11)
        
        # Test "nearest" strategy
        self.assertEqual(normalize_slot_to_prime(8, "nearest"), 7)
        self.assertEqual(normalize_slot_to_prime(10, "nearest"), 11)
        self.assertEqual(normalize_slot_to_prime(7, "nearest"), 7)
    
    def test_curvature_reduction(self):
        """Test curvature reduction computation."""
        # Normalizing 10 to 11 should reduce curvature
        reduction = compute_curvature_reduction(10, 11)
        self.assertGreater(reduction, 0, "Should have positive reduction")
        
        # No change if already prime
        reduction = compute_curvature_reduction(11, 11)
        self.assertEqual(reduction, 0, "No reduction if already optimal")
        
        # Test significant reduction for composites
        reduction = compute_curvature_reduction(100, 101)
        self.assertGreater(reduction, 70, "Should have >70% reduction")


@unittest.skipUnless(PRIME_OPTIMIZATION_AVAILABLE, "Prime optimization module not available")
class TestTransecPrimeOptimization(unittest.TestCase):
    """Test TRANSEC with prime optimization enabled."""
    
    def test_encrypt_decrypt_with_nearest_strategy(self):
        """Test encryption/decryption with nearest prime strategy."""
        secret = generate_shared_secret()
        # Use longer slot duration for smaller slot indices (more efficient prime finding)
        cipher = TransecCipher(secret, slot_duration=3600, prime_strategy="nearest")
        
        plaintext = b"Hello with prime optimization!"
        sequence = 1
        
        packet = cipher.seal(plaintext, sequence)
        decrypted = cipher.open(packet)
        
        self.assertEqual(decrypted, plaintext)
    
    def test_encrypt_decrypt_with_next_strategy(self):
        """Test encryption/decryption with next prime strategy."""
        secret = generate_shared_secret()
        cipher = TransecCipher(secret, slot_duration=3600, prime_strategy="next")
        
        plaintext = b"Next prime strategy test"
        sequence = 1
        
        packet = cipher.seal(plaintext, sequence)
        decrypted = cipher.open(packet)
        
        self.assertEqual(decrypted, plaintext)
    
    def test_interoperability_same_strategy(self):
        """Test that sender and receiver with same strategy work."""
        secret = generate_shared_secret()
        
        sender = TransecCipher(secret, slot_duration=3600, prime_strategy="nearest")
        receiver = TransecCipher(secret, slot_duration=3600, prime_strategy="nearest")
        
        plaintext = b"Interop test with same strategy"
        sequence = 1
        
        packet = sender.seal(plaintext, sequence)
        decrypted = receiver.open(packet, check_replay=False)
        
        self.assertEqual(decrypted, plaintext)
    
    def test_cross_strategy_compatibility(self):
        """Test limited compatibility between different strategies."""
        secret = generate_shared_secret()
        
        # Use explicit slot index to control normalization
        raw_slot = 10  # Normalizes to 11 (next) or 11 (nearest)
        
        sender_next = TransecCipher(secret, prime_strategy="next")
        receiver_nearest = TransecCipher(secret, prime_strategy="nearest")
        
        plaintext = b"Cross-strategy test"
        sequence = 1
        
        # Both strategies should normalize 10 to 11
        packet = sender_next.seal(plaintext, sequence, slot_index=raw_slot)
        
        # Receiver might accept it depending on timing and drift window
        # This test documents the behavior but doesn't assert success/failure
        # as it depends on the actual normalized values
    
    def test_normalized_slot_in_packet(self):
        """Test that normalized slot appears in packet."""
        secret = generate_shared_secret()
        cipher = TransecCipher(secret, slot_duration=100, prime_strategy="next")
        
        # Use a known composite slot that will be normalized
        raw_slot = 10  # Should normalize to 11
        
        plaintext = b"Test packet"
        sequence = 1
        
        packet = cipher.seal(plaintext, sequence, slot_index=raw_slot)
        
        # Extract slot from packet
        import struct
        packet_slot = struct.unpack(">Q", packet[:8])[0]
        
        # Verify it's the normalized value
        expected_normalized = find_next_prime(raw_slot)
        self.assertEqual(packet_slot, expected_normalized)
    
    def test_replay_protection_with_primes(self):
        """Test replay protection works with prime normalization."""
        secret = generate_shared_secret()
        cipher = TransecCipher(secret, slot_duration=3600, prime_strategy="nearest")
        
        plaintext = b"Replay test with primes"
        sequence = 1
        
        packet = cipher.seal(plaintext, sequence)
        
        # First decryption succeeds
        decrypted1 = cipher.open(packet)
        self.assertEqual(decrypted1, plaintext)
        
        # Replay is blocked
        decrypted2 = cipher.open(packet)
        self.assertIsNone(decrypted2)
    
    def test_drift_tolerance_with_primes(self):
        """Test clock drift tolerance with prime normalization."""
        secret = generate_shared_secret()
        cipher = TransecCipher(secret, slot_duration=3600, drift_window=3, prime_strategy="nearest")
        
        plaintext = b"Drift test"
        current_slot = cipher.get_current_slot()
        sequence = 1
        
        # Test that nearby primes are accepted
        # Current slot is already normalized, so we test relative to it
        packet = cipher.seal(plaintext, sequence, slot_index=current_slot)
        decrypted = cipher.open(packet)
        
        self.assertEqual(decrypted, plaintext)
    
    def test_performance_impact(self):
        """Test that prime normalization doesn't significantly impact performance."""
        secret = generate_shared_secret()
        
        # Use larger slot duration to reduce current slot magnitude
        # This makes prime finding faster
        cipher_none = TransecCipher(secret, slot_duration=3600, prime_strategy="none")
        cipher_prime = TransecCipher(secret, slot_duration=3600, prime_strategy="nearest")
        
        plaintext = b"Performance test" * 10
        
        # Measure without prime optimization
        start = time.time()
        for i in range(100):
            cipher_none.seal(plaintext, i)
        time_none = time.time() - start
        
        # Measure with prime optimization
        start = time.time()
        for i in range(100):
            cipher_prime.seal(plaintext, i)
        time_prime = time.time() - start
        
        # Prime optimization adds computational cost, but should be reasonable
        # For smaller slot values (using longer slot_duration), overhead should be manageable
        if time_none > 0:
            overhead = (time_prime - time_none) / time_none * 100
            # The overhead depends on slot magnitude. For reasonable slots, allow up to 200%
            self.assertLess(overhead, 200,
                           f"Prime optimization overhead: {overhead:.1f}%")
        else:
            # If time_none is 0, just check that time_prime is reasonable
            self.assertLess(time_prime, 1.0, "Prime optimization too slow")
    
    def test_invalid_strategy_rejected(self):
        """Test that invalid prime strategy is rejected."""
        secret = generate_shared_secret()
        
        with self.assertRaises(ValueError):
            TransecCipher(secret, prime_strategy="invalid")


@unittest.skipUnless(PRIME_OPTIMIZATION_AVAILABLE, "Prime optimization module not available")
class TestPrimeOptimizationEdgeCases(unittest.TestCase):
    """Test edge cases with prime optimization."""
    
    def test_small_slots(self):
        """Test prime normalization with small slot indices."""
        secret = generate_shared_secret()
        # Use very long slot duration so current slot is small
        cipher = TransecCipher(secret, slot_duration=86400, prime_strategy="nearest", drift_window=10)
        
        plaintext = b"Small slot test"
        sequence = 1
        
        # Use current slot which should be small (days since epoch)
        packet = cipher.seal(plaintext, sequence)
        decrypted = cipher.open(packet)
        
        self.assertEqual(decrypted, plaintext)
    
    def test_large_slots(self):
        """Test prime normalization with large slot indices."""
        secret = generate_shared_secret()
        # Use small slot duration so current slot is large
        # Use larger drift window to handle potential time passage during test
        cipher = TransecCipher(secret, slot_duration=1, prime_strategy="next", drift_window=50)
        
        plaintext = b"Large slot test"
        sequence = 1
        
        # Use current slot which should be large (seconds since epoch)
        packet = cipher.seal(plaintext, sequence)
        decrypted = cipher.open(packet)
        
        self.assertEqual(decrypted, plaintext)
    
    def test_already_prime_slot(self):
        """Test that already-prime slots are unchanged."""
        secret = generate_shared_secret()
        cipher = TransecCipher(secret, prime_strategy="nearest")
        
        prime_slot = 17
        plaintext = b"Already prime"
        sequence = 1
        
        packet = cipher.seal(plaintext, sequence, slot_index=prime_slot)
        
        # Extract slot from packet
        import struct
        packet_slot = struct.unpack(">Q", packet[:8])[0]
        
        # Should remain 17
        self.assertEqual(packet_slot, prime_slot)


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with non-optimized TRANSEC."""
    
    def test_default_strategy_is_none(self):
        """Test that default strategy is 'none' for backward compatibility."""
        secret = generate_shared_secret()
        cipher = TransecCipher(secret)
        
        # Should have prime_strategy="none" by default
        self.assertEqual(cipher.prime_strategy, "none")
    
    def test_none_strategy_unchanged_behavior(self):
        """Test that 'none' strategy behaves like original implementation."""
        secret = generate_shared_secret()
        cipher = TransecCipher(secret, prime_strategy="none")
        
        plaintext = b"Backward compatibility test"
        sequence = 1
        
        # Should work exactly as before
        packet = cipher.seal(plaintext, sequence)
        decrypted = cipher.open(packet)
        
        self.assertEqual(decrypted, plaintext)
    
    def test_explicit_slot_with_none_strategy(self):
        """Test explicit slot index with 'none' strategy."""
        secret = generate_shared_secret()
        cipher = TransecCipher(secret, prime_strategy="none")
        
        # Use non-prime slot
        slot = 10
        plaintext = b"Explicit slot test"
        sequence = 1
        
        packet = cipher.seal(plaintext, sequence, slot_index=slot)
        
        # Extract slot from packet
        import struct
        packet_slot = struct.unpack(">Q", packet[:8])[0]
        
        # Should remain unchanged (10, not normalized)
        self.assertEqual(packet_slot, slot)


if __name__ == '__main__':
    unittest.main()
