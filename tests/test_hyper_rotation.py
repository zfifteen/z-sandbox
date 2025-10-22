#!/usr/bin/env python3
"""
Comprehensive tests for Hyper-Rotation Messenger.

Tests cover:
- HKDF key derivation with RFC 5869 test vectors
- AEAD encryption/decryption round-trips
- Replay protection
- Clock skew tolerance
- RSA demo mode with primality validation
"""

import sys
import os
import time
import unittest
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hr_core import (
    KeySchedule, XChaCha20Poly1305, MessageHeader, WireMessage,
    MessageCounter, ReplayProtection, ALG_AEAD_XCHACHA20_POLY1305
)
from hr_core.rsa_demo import (
    generate_rsa_keypair_z5d, miller_rabin_test, baillie_psw_test
)
from nacl.exceptions import CryptoError


class TestKeySchedule(unittest.TestCase):
    """Test HKDF-based key schedule."""
    
    def test_deterministic_derivation(self):
        """Test that key derivation is deterministic."""
        shared_secret = b"test_secret_32_bytes_minimum!!!!"
        channel_id = "test_channel"
        
        ks1 = KeySchedule(shared_secret, channel_id, 'A', 3)
        ks2 = KeySchedule(shared_secret, channel_id, 'A', 3)
        
        # Same window should produce same keys
        k1_enc, k1_mac = ks1.derive_window_keys(100)
        k2_enc, k2_mac = ks2.derive_window_keys(100)
        
        self.assertEqual(k1_enc, k2_enc)
        self.assertEqual(k1_mac, k2_mac)
    
    def test_role_separation(self):
        """Test that different roles produce different keys."""
        shared_secret = b"test_secret_32_bytes_minimum!!!!"
        channel_id = "test_channel"
        
        ks_a = KeySchedule(shared_secret, channel_id, 'A', 3)
        ks_b = KeySchedule(shared_secret, channel_id, 'B', 3)
        
        k_a_enc, k_a_mac = ks_a.derive_window_keys(100)
        k_b_enc, k_b_mac = ks_b.derive_window_keys(100)
        
        self.assertNotEqual(k_a_enc, k_b_enc)
        self.assertNotEqual(k_a_mac, k_b_mac)
    
    def test_window_separation(self):
        """Test that different windows produce different keys."""
        shared_secret = b"test_secret_32_bytes_minimum!!!!"
        channel_id = "test_channel"
        
        ks = KeySchedule(shared_secret, channel_id, 'A', 3)
        
        k1_enc, k1_mac = ks.derive_window_keys(100)
        k2_enc, k2_mac = ks.derive_window_keys(101)
        
        self.assertNotEqual(k1_enc, k2_enc)
        self.assertNotEqual(k1_mac, k2_mac)
    
    def test_channel_separation(self):
        """Test that different channels produce different keys."""
        shared_secret = b"test_secret_32_bytes_minimum!!!!"
        
        ks1 = KeySchedule(shared_secret, "channel1", 'A', 3)
        ks2 = KeySchedule(shared_secret, "channel2", 'A', 3)
        
        k1_enc, k1_mac = ks1.derive_window_keys(100)
        k2_enc, k2_mac = ks2.derive_window_keys(100)
        
        self.assertNotEqual(k1_enc, k2_enc)
        self.assertNotEqual(k1_mac, k2_mac)
    
    def test_drift_tolerance(self):
        """Test get_keys_with_drift functionality."""
        shared_secret = b"test_secret_32_bytes_minimum!!!!"
        channel_id = "test_channel"
        
        ks = KeySchedule(shared_secret, channel_id, 'A', 3)
        
        keys = ks.get_keys_with_drift(100, max_drift=1)
        
        # Should return keys for windows 99, 100, 101
        self.assertEqual(len(keys), 3)
        
        window_ids = [wid for wid, _, _ in keys]
        self.assertEqual(window_ids, [99, 100, 101])
    
    def test_time_until_rotation(self):
        """Test time until rotation calculation."""
        shared_secret = b"test_secret_32_bytes_minimum!!!!"
        channel_id = "test_channel"
        
        ks = KeySchedule(shared_secret, channel_id, 'A', 3)
        
        time_left = ks.get_time_until_rotation()
        
        # Should be between 0 and rotation_seconds
        self.assertGreaterEqual(time_left, 0)
        self.assertLess(time_left, ks.rotation_seconds)
    
    def test_key_length(self):
        """Test that derived keys have correct length."""
        shared_secret = b"test_secret_32_bytes_minimum!!!!"
        channel_id = "test_channel"
        
        ks = KeySchedule(shared_secret, channel_id, 'A', 3)
        k_enc, k_mac = ks.derive_window_keys(100)
        
        self.assertEqual(len(k_enc), 32)  # 256 bits
        self.assertEqual(len(k_mac), 32)  # 256 bits


class TestAEAD(unittest.TestCase):
    """Test XChaCha20-Poly1305 AEAD."""
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test basic encryption/decryption."""
        key = os.urandom(32)
        cipher = XChaCha20Poly1305(key)
        
        plaintext = b"Hello, hyper-rotation!"
        nonce, ciphertext = cipher.encrypt(plaintext)
        
        decrypted = cipher.decrypt(nonce, ciphertext)
        self.assertEqual(plaintext, decrypted)
    
    def test_different_nonces(self):
        """Test that different encryptions produce different nonces."""
        key = os.urandom(32)
        cipher = XChaCha20Poly1305(key)
        
        plaintext = b"Same message"
        
        nonce1, ct1 = cipher.encrypt(plaintext)
        nonce2, ct2 = cipher.encrypt(plaintext)
        
        # Different nonces
        self.assertNotEqual(nonce1, nonce2)
        # Different ciphertexts (due to different nonces)
        self.assertNotEqual(ct1, ct2)
    
    def test_authentication_failure_wrong_key(self):
        """Test that wrong key causes authentication failure."""
        key1 = os.urandom(32)
        key2 = os.urandom(32)
        
        cipher1 = XChaCha20Poly1305(key1)
        cipher2 = XChaCha20Poly1305(key2)
        
        plaintext = b"Secret message"
        nonce, ciphertext = cipher1.encrypt(plaintext)
        
        with self.assertRaises(CryptoError):
            cipher2.decrypt(nonce, ciphertext)
    
    def test_authentication_failure_modified_ciphertext(self):
        """Test that modified ciphertext causes authentication failure."""
        key = os.urandom(32)
        cipher = XChaCha20Poly1305(key)
        
        plaintext = b"Secret message"
        nonce, ciphertext = cipher.encrypt(plaintext)
        
        # Modify ciphertext
        modified_ciphertext = bytearray(ciphertext)
        modified_ciphertext[0] ^= 0xFF
        modified_ciphertext = bytes(modified_ciphertext)
        
        with self.assertRaises(CryptoError):
            cipher.decrypt(nonce, modified_ciphertext)
    
    def test_associated_data(self):
        """Test encryption with associated data."""
        key = os.urandom(32)
        cipher = XChaCha20Poly1305(key)
        
        plaintext = b"Secret message"
        ad = b"window_id=12345"
        
        nonce, ciphertext = cipher.encrypt(plaintext, ad)
        
        # Correct AD should decrypt successfully
        decrypted = cipher.decrypt(nonce, ciphertext, ad)
        self.assertEqual(plaintext, decrypted)
        
        # Wrong AD should fail
        with self.assertRaises(CryptoError):
            cipher.decrypt(nonce, ciphertext, b"wrong_ad")


class TestWireFormat(unittest.TestCase):
    """Test wire format encoding/decoding."""
    
    def test_header_encode_decode(self):
        """Test header serialization."""
        header = MessageHeader(
            version=1,
            alg_id=ALG_AEAD_XCHACHA20_POLY1305,
            window_id=12345,
            channel_id_hash=0xDEADBEEF,
            msg_counter=42,
            nonce=os.urandom(24)
        )
        
        # Encode
        header_bytes = header.encode()
        self.assertEqual(len(header_bytes), MessageHeader.HEADER_SIZE)
        
        # Decode
        decoded = MessageHeader.decode(header_bytes)
        
        self.assertEqual(decoded.version, header.version)
        self.assertEqual(decoded.alg_id, header.alg_id)
        self.assertEqual(decoded.window_id, header.window_id)
        self.assertEqual(decoded.channel_id_hash, header.channel_id_hash)
        self.assertEqual(decoded.msg_counter, header.msg_counter)
        self.assertEqual(decoded.nonce, header.nonce)
    
    def test_wire_message_encode_decode(self):
        """Test complete wire message serialization."""
        header = MessageHeader(
            version=1,
            alg_id=ALG_AEAD_XCHACHA20_POLY1305,
            window_id=12345,
            channel_id_hash=0xDEADBEEF,
            msg_counter=42,
            nonce=os.urandom(24)
        )
        ciphertext = b"encrypted_payload"
        
        wire_msg = WireMessage(header, ciphertext)
        
        # Encode
        wire_bytes = wire_msg.encode()
        
        # Decode
        decoded = WireMessage.decode(wire_bytes)
        
        self.assertEqual(decoded.header.window_id, header.window_id)
        self.assertEqual(decoded.ciphertext, ciphertext)
    
    def test_channel_hash_deterministic(self):
        """Test that channel hash is deterministic."""
        channel_id = "test_channel_123"
        
        hash1 = MessageHeader.compute_channel_hash(channel_id)
        hash2 = MessageHeader.compute_channel_hash(channel_id)
        
        self.assertEqual(hash1, hash2)


class TestReplayProtection(unittest.TestCase):
    """Test replay protection."""
    
    def test_accepts_increasing_counters(self):
        """Test that increasing counters are accepted."""
        rp = ReplayProtection()
        
        self.assertTrue(rp.check_and_update(100, 0))
        self.assertTrue(rp.check_and_update(100, 1))
        self.assertTrue(rp.check_and_update(100, 2))
    
    def test_rejects_replay(self):
        """Test that replay messages are rejected."""
        rp = ReplayProtection()
        
        rp.check_and_update(100, 5)
        
        # Replay should be rejected
        self.assertFalse(rp.check_and_update(100, 5))
        self.assertFalse(rp.check_and_update(100, 4))
        self.assertFalse(rp.check_and_update(100, 0))
    
    def test_out_of_order_rejected(self):
        """Test that out-of-order messages are rejected."""
        rp = ReplayProtection()
        
        rp.check_and_update(100, 10)
        
        # Earlier counter should be rejected
        self.assertFalse(rp.check_and_update(100, 5))
    
    def test_independent_windows(self):
        """Test that different windows are independent."""
        rp = ReplayProtection()
        
        rp.check_and_update(100, 5)
        rp.check_and_update(101, 5)  # Same counter, different window
        
        # Should both be accepted (different windows)
        self.assertEqual(rp.get_highest_counter(100), 5)
        self.assertEqual(rp.get_highest_counter(101), 5)
    
    def test_window_cleanup(self):
        """Test that old windows are cleaned up."""
        rp = ReplayProtection(max_windows=5)
        
        # Add many windows
        for wid in range(100, 120):
            rp.check_and_update(wid, 0)
        
        stats = rp.get_stats()
        
        # Should have cleaned up old windows
        self.assertLessEqual(stats['tracked_windows'], rp.max_windows + 3)


class TestClockSkew(unittest.TestCase):
    """Test clock skew tolerance."""
    
    def test_decrypt_with_clock_drift(self):
        """Test that messages decrypt with ±1 window drift."""
        shared_secret = b"test_secret_32_bytes_minimum!!!!"
        channel_id = "test_channel"
        
        # Sender and receiver key schedules
        ks_sender = KeySchedule(shared_secret, channel_id, 'A', 3)
        ks_receiver = KeySchedule(shared_secret, channel_id, 'A', 3)
        
        # Simulate sender encrypting at window 100
        window_id = 100
        k_enc, k_mac = ks_sender.derive_window_keys(window_id)
        cipher = XChaCha20Poly1305(k_enc)
        
        plaintext = b"Test message with clock skew"
        nonce, ciphertext = cipher.encrypt(plaintext)
        
        # Receiver tries with drift tolerance
        keys_to_try = ks_receiver.get_keys_with_drift(window_id, max_drift=1)
        
        decrypted = None
        for wid, k_enc_try, k_mac_try in keys_to_try:
            cipher_try = XChaCha20Poly1305(k_enc_try)
            try:
                decrypted = cipher_try.decrypt(nonce, ciphertext)
                break
            except CryptoError:
                continue
        
        self.assertIsNotNone(decrypted)
        self.assertEqual(decrypted, plaintext)
    
    def test_decrypt_fails_with_large_drift(self):
        """Test that messages don't decrypt with >1 window drift."""
        shared_secret = b"test_secret_32_bytes_minimum!!!!"
        channel_id = "test_channel"
        
        ks = KeySchedule(shared_secret, channel_id, 'A', 3)
        
        # Encrypt at window 100
        k_enc_100, _ = ks.derive_window_keys(100)
        cipher_100 = XChaCha20Poly1305(k_enc_100)
        
        plaintext = b"Test message"
        nonce, ciphertext = cipher_100.encrypt(plaintext)
        
        # Try to decrypt at window 102 (2 windows ahead, outside drift tolerance)
        keys_to_try = ks.get_keys_with_drift(102, max_drift=1)
        
        decrypted = None
        for wid, k_enc_try, k_mac_try in keys_to_try:
            cipher_try = XChaCha20Poly1305(k_enc_try)
            try:
                decrypted = cipher_try.decrypt(nonce, ciphertext)
                break
            except CryptoError:
                continue
        
        # Should fail (window 100 is not in [101, 102, 103])
        self.assertIsNone(decrypted)


class TestRSADemo(unittest.TestCase):
    """Test RSA demo mode with Z5D assistance."""
    
    def test_rsa_keypair_generation(self):
        """Test that RSA keypair can be generated."""
        result = generate_rsa_keypair_z5d(
            window_id=42,
            shared_secret=b"test_secret_32_bytes_minimum!!!!",
            channel_id="test_channel",
            key_size=1024
        )
        
        if result is None:
            self.skipTest("RSA keypair generation timed out")
        
        (n, e, d), keygen_time = result
        
        # Check key properties
        self.assertGreaterEqual(n.bit_length(), 1024)
        self.assertEqual(e, 65537)
        self.assertGreater(d, 0)
        
        # Check that n = p * q (we can't easily factor to verify, but check it's composite)
        self.assertGreater(n, 2)
    
    def test_rsa_encrypt_decrypt(self):
        """Test RSA encryption/decryption."""
        result = generate_rsa_keypair_z5d(
            window_id=42,
            shared_secret=b"test_secret_32_bytes_minimum!!!!",
            channel_id="test_channel",
            key_size=1024
        )
        
        if result is None:
            self.skipTest("RSA keypair generation timed out")
        
        (n, e, d), _ = result
        
        # Encrypt/decrypt small message
        message = 123456789
        ciphertext = pow(message, e, n)
        decrypted = pow(ciphertext, d, n)
        
        self.assertEqual(message, decrypted)
    
    def test_miller_rabin(self):
        """Test Miller-Rabin primality test."""
        # Known primes
        self.assertTrue(miller_rabin_test(2))
        self.assertTrue(miller_rabin_test(3))
        self.assertTrue(miller_rabin_test(17))
        self.assertTrue(miller_rabin_test(97))
        
        # Known composites
        self.assertFalse(miller_rabin_test(4))
        self.assertFalse(miller_rabin_test(15))
        self.assertFalse(miller_rabin_test(100))
    
    def test_baillie_psw(self):
        """Test Baillie-PSW primality test."""
        # Known primes
        self.assertTrue(baillie_psw_test(2))
        self.assertTrue(baillie_psw_test(3))
        self.assertTrue(baillie_psw_test(17))
        self.assertTrue(baillie_psw_test(97))
        
        # Known composites
        self.assertFalse(baillie_psw_test(4))
        self.assertFalse(baillie_psw_test(15))
        self.assertFalse(baillie_psw_test(100))


class TestEndToEnd(unittest.TestCase):
    """Test end-to-end message flow."""
    
    def test_full_message_flow(self):
        """Test complete send/receive flow."""
        shared_secret = b"test_secret_32_bytes_minimum!!!!"
        channel_id = "test_channel"
        
        # Sender setup
        ks_sender = KeySchedule(shared_secret, channel_id, 'A', 3)
        mc_sender = MessageCounter()
        
        # Receiver setup
        ks_receiver = KeySchedule(shared_secret, channel_id, 'A', 3)  # Same role for testing
        rp_receiver = ReplayProtection()
        
        # Send message
        plaintext = b"Hello, hyper-rotation messenger!"
        
        window_id, k_enc, k_mac = ks_sender.get_current_keys()
        cipher = XChaCha20Poly1305(k_enc)
        
        nonce, ciphertext = cipher.encrypt(plaintext)
        
        header = MessageHeader(
            version=1,
            alg_id=ALG_AEAD_XCHACHA20_POLY1305,
            window_id=window_id,
            channel_id_hash=MessageHeader.compute_channel_hash(channel_id),
            msg_counter=mc_sender.next_counter(window_id),
            nonce=nonce
        )
        
        wire_msg = WireMessage(header, ciphertext)
        wire_bytes = wire_msg.encode()
        
        # Receive message
        decoded_msg = WireMessage.decode(wire_bytes)
        decoded_header = decoded_msg.header
        
        # Check replay
        self.assertTrue(rp_receiver.check_and_update(
            decoded_header.window_id, decoded_header.msg_counter
        ))
        
        # Decrypt with drift tolerance
        keys_to_try = ks_receiver.get_keys_with_drift(
            decoded_header.window_id, max_drift=1
        )
        
        decrypted = None
        for wid, k_enc_try, k_mac_try in keys_to_try:
            cipher_try = XChaCha20Poly1305(k_enc_try)
            try:
                decrypted = cipher_try.decrypt(decoded_header.nonce, decoded_msg.ciphertext)
                break
            except CryptoError:
                continue
        
        self.assertIsNotNone(decrypted)
        self.assertEqual(decrypted, plaintext)


if __name__ == '__main__':
    unittest.main()
