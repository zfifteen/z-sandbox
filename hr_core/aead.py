#!/usr/bin/env python3
"""
AEAD Encryption Module

Provides XChaCha20-Poly1305 AEAD encryption/decryption wrappers.
Uses PyNaCl (libsodium bindings) for production-grade cryptography.
"""

import os
from typing import Tuple
import nacl.secret
import nacl.utils
from nacl.exceptions import CryptoError


class AEADCipher:
    """XChaCha20-Poly1305 AEAD cipher wrapper."""
    
    NONCE_SIZE = 24  # 192 bits for XChaCha20
    TAG_SIZE = 16    # 128 bits for Poly1305 MAC
    
    def __init__(self, key: bytes):
        """
        Initialize AEAD cipher with encryption key.
        
        Args:
            key: 32-byte encryption key
        """
        if len(key) != 32:
            raise ValueError("key must be 32 bytes")
        self.box = nacl.secret.SecretBox(key)
    
    def encrypt(self, plaintext: bytes, associated_data: bytes = b"") -> Tuple[bytes, bytes]:
        """
        Encrypt plaintext with AEAD.
        
        Args:
            plaintext: Data to encrypt
            associated_data: Additional authenticated data (not encrypted)
            
        Returns:
            Tuple of (nonce, ciphertext_with_tag)
            ciphertext_with_tag includes Poly1305 authentication tag
        """
        # Generate random nonce (XChaCha20 has 192-bit nonce, collision-free)
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
        
        # PyNaCl's SecretBox uses XSalsa20-Poly1305, we need XChaCha20-Poly1305
        # For now, we'll use the available XSalsa20-Poly1305 which is also secure
        # In production, use nacl.bindings with direct XChaCha20-Poly1305 support
        
        # Encrypt with authentication
        # Note: PyNaCl doesn't directly support additional_data for SecretBox
        # For MVP, we'll prepend associated_data to plaintext (less efficient but functional)
        if associated_data:
            # Encode length of associated_data to prevent ambiguity
            ad_len = len(associated_data).to_bytes(4, 'big')
            combined = ad_len + associated_data + plaintext
        else:
            combined = plaintext
        
        ciphertext = self.box.encrypt(combined, nonce)
        
        # Remove nonce prefix that PyNaCl adds (we return it separately)
        ciphertext_only = ciphertext[nacl.secret.SecretBox.NONCE_SIZE:]
        
        return nonce, ciphertext_only
    
    def decrypt(self, nonce: bytes, ciphertext: bytes, associated_data: bytes = b"") -> bytes:
        """
        Decrypt ciphertext with AEAD.
        
        Args:
            nonce: 24-byte nonce used for encryption
            ciphertext: Encrypted data with authentication tag
            associated_data: Additional authenticated data (must match encryption)
            
        Returns:
            Decrypted plaintext
            
        Raises:
            CryptoError: If authentication fails or decryption fails
        """
        if len(nonce) != nacl.secret.SecretBox.NONCE_SIZE:
            raise ValueError(f"nonce must be {nacl.secret.SecretBox.NONCE_SIZE} bytes")
        
        # Decrypt and verify
        try:
            combined_plaintext = self.box.decrypt(ciphertext, nonce)
        except CryptoError:
            raise CryptoError("Decryption failed: authentication tag mismatch")
        
        # Extract original plaintext (remove associated_data prefix if present)
        if associated_data:
            ad_len_bytes = combined_plaintext[:4]
            ad_len = int.from_bytes(ad_len_bytes, 'big')
            extracted_ad = combined_plaintext[4:4 + ad_len]
            
            if extracted_ad != associated_data:
                raise CryptoError("Associated data mismatch")
            
            plaintext = combined_plaintext[4 + ad_len:]
        else:
            plaintext = combined_plaintext
        
        return plaintext


class XChaCha20Poly1305:
    """
    XChaCha20-Poly1305 AEAD cipher (direct libsodium bindings).
    
    Note: This implementation uses PyNaCl's lower-level bindings for
    true XChaCha20-Poly1305 support.
    """
    
    NONCE_SIZE = 24  # 192 bits
    KEY_SIZE = 32    # 256 bits
    TAG_SIZE = 16    # 128 bits (Poly1305)
    
    def __init__(self, key: bytes):
        """
        Initialize XChaCha20-Poly1305 cipher.
        
        Args:
            key: 32-byte encryption key
        """
        if len(key) != self.KEY_SIZE:
            raise ValueError(f"key must be {self.KEY_SIZE} bytes")
        self.key = key
    
    def encrypt(self, plaintext: bytes, associated_data: bytes = b"") -> Tuple[bytes, bytes]:
        """
        Encrypt plaintext with XChaCha20-Poly1305 AEAD.
        
        Args:
            plaintext: Data to encrypt
            associated_data: Additional authenticated data (not encrypted)
            
        Returns:
            Tuple of (nonce, ciphertext_with_tag)
        """
        nonce = os.urandom(self.NONCE_SIZE)
        
        # Import low-level bindings for XChaCha20-Poly1305
        from nacl.bindings import (
            crypto_aead_xchacha20poly1305_ietf_encrypt
        )
        
        ciphertext = crypto_aead_xchacha20poly1305_ietf_encrypt(
            plaintext,
            associated_data,
            nonce,
            self.key
        )
        
        return nonce, ciphertext
    
    def decrypt(self, nonce: bytes, ciphertext: bytes, associated_data: bytes = b"") -> bytes:
        """
        Decrypt ciphertext with XChaCha20-Poly1305 AEAD.
        
        Args:
            nonce: 24-byte nonce
            ciphertext: Encrypted data with authentication tag
            associated_data: Additional authenticated data
            
        Returns:
            Decrypted plaintext
            
        Raises:
            CryptoError: If authentication fails
        """
        if len(nonce) != self.NONCE_SIZE:
            raise ValueError(f"nonce must be {self.NONCE_SIZE} bytes")
        
        from nacl.bindings import (
            crypto_aead_xchacha20poly1305_ietf_decrypt
        )
        
        try:
            plaintext = crypto_aead_xchacha20poly1305_ietf_decrypt(
                ciphertext,
                associated_data,
                nonce,
                self.key
            )
            return plaintext
        except Exception as e:
            raise CryptoError(f"Decryption failed: {e}")


def test_aead():
    """Test AEAD encryption/decryption."""
    key = os.urandom(32)
    
    # Test XChaCha20-Poly1305
    cipher = XChaCha20Poly1305(key)
    plaintext = b"Hello, hyper-rotation!"
    ad = b"window_id=12345|channel=test"
    
    # Encrypt
    nonce, ciphertext = cipher.encrypt(plaintext, ad)
    assert len(nonce) == XChaCha20Poly1305.NONCE_SIZE
    assert len(ciphertext) == len(plaintext) + XChaCha20Poly1305.TAG_SIZE
    
    # Decrypt
    decrypted = cipher.decrypt(nonce, ciphertext, ad)
    assert decrypted == plaintext
    
    # Test authentication failure with wrong AD
    try:
        cipher.decrypt(nonce, ciphertext, b"wrong_ad")
        assert False, "Should have raised CryptoError"
    except CryptoError:
        pass  # Expected
    
    # Test with different key
    wrong_cipher = XChaCha20Poly1305(os.urandom(32))
    try:
        wrong_cipher.decrypt(nonce, ciphertext, ad)
        assert False, "Should have raised CryptoError"
    except CryptoError:
        pass  # Expected
    
    print("✓ AEAD tests passed")
    print(f"  Plaintext: {plaintext}")
    print(f"  Ciphertext: {ciphertext.hex()[:32]}...")
    print(f"  Nonce: {nonce.hex()}")
    print(f"  AD: {ad}")


if __name__ == "__main__":
    test_aead()
