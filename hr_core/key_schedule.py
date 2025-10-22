#!/usr/bin/env python3
"""
Hyper-Rotation Key Schedule

⚠️ RESEARCH PROOF OF CONCEPT ONLY ⚠️
This is experimental research code for exploring mathematical concepts.
NOT for production use or real communications.

Implements HKDF-based key derivation for time-windowed encryption keys.
Keys are derived from a shared secret and time bucket, with domain separation.

Based on RFC 5869 (HKDF) and the hyper-rotation specification.
For academic research and mathematical concept exploration only.
"""

import hashlib
import hmac
import struct
import time
from typing import Tuple


class KeySchedule:
    """Manages time-windowed key derivation using HKDF."""
    
    VERSION = 1
    KEY_LENGTH = 32  # 256 bits for XChaCha20
    OKM_LENGTH = 64  # Total output key material
    
    def __init__(
        self, 
        shared_secret: bytes, 
        channel_id: str, 
        role: str,
        rotation_seconds: int = 3
    ):
        """
        Initialize key schedule.
        
        Args:
            shared_secret: High-entropy shared secret (>= 32 bytes recommended)
            channel_id: Channel identifier for domain separation
            role: Role identifier ('A' or 'B') for bidirectional separation
            rotation_seconds: Key rotation window in seconds (1, 3, 5, or 10)
        """
        if len(shared_secret) < 16:
            raise ValueError("shared_secret must be at least 16 bytes")
        if role not in ('A', 'B'):
            raise ValueError("role must be 'A' or 'B'")
        if rotation_seconds not in (1, 3, 5, 10):
            raise ValueError("rotation_seconds must be 1, 3, 5, or 10")
            
        self.shared_secret = shared_secret
        self.channel_id = channel_id
        self.role = role
        self.rotation_seconds = rotation_seconds
        
        # Domain separation context
        self.context = f"Z5D-HR:v{self.VERSION}|{channel_id}|{role}".encode()
        
        # Salt for HKDF-Extract (hash of channel_id for deterministic but unique salt)
        self.salt = hashlib.sha256(channel_id.encode()).digest()
        
    def get_current_window(self, timestamp: float = None) -> int:
        """
        Calculate current time window ID.
        
        Args:
            timestamp: Unix timestamp (seconds), uses current time if None
            
        Returns:
            Window ID (floor(t / rotation_seconds))
        """
        if timestamp is None:
            timestamp = time.time()
        return int(timestamp // self.rotation_seconds)
    
    def derive_window_keys(self, window_id: int) -> Tuple[bytes, bytes]:
        """
        Derive encryption keys for a specific window using HKDF.
        
        Key schedule:
        1. seed = HMAC-SHA256(shared_secret, LE64(window_id))
        2. PRK = HKDF-Extract(salt=H(channel_id), IKM=seed)
        3. OKM = HKDF-Expand(PRK, info=context, L=64)
        4. K_enc = OKM[0:32], K_mac = OKM[32:64]
        
        Args:
            window_id: Time window identifier
            
        Returns:
            Tuple of (encryption_key, mac_key) each 32 bytes
        """
        # Step 1: Derive window-specific seed
        window_bytes = struct.pack('<Q', window_id)  # Little-endian uint64
        seed = hmac.new(self.shared_secret, window_bytes, hashlib.sha256).digest()
        
        # Step 2: HKDF-Extract
        prk = self._hkdf_extract(self.salt, seed)
        
        # Step 3: HKDF-Expand
        okm = self._hkdf_expand(prk, self.context, self.OKM_LENGTH)
        
        # Step 4: Split into encryption and MAC keys
        k_enc = okm[:self.KEY_LENGTH]
        k_mac = okm[self.KEY_LENGTH:self.OKM_LENGTH]
        
        return k_enc, k_mac
    
    def get_current_keys(self, timestamp: float = None) -> Tuple[int, bytes, bytes]:
        """
        Get encryption keys for the current time window.
        
        Args:
            timestamp: Unix timestamp (seconds), uses current time if None
            
        Returns:
            Tuple of (window_id, encryption_key, mac_key)
        """
        window_id = self.get_current_window(timestamp)
        k_enc, k_mac = self.derive_window_keys(window_id)
        return window_id, k_enc, k_mac
    
    def get_keys_with_drift(
        self, 
        window_id: int, 
        max_drift: int = 1
    ) -> list:
        """
        Get keys for window_id and adjacent windows for clock drift tolerance.
        
        Args:
            window_id: Target window ID
            max_drift: Maximum window drift to check (±1 recommended)
            
        Returns:
            List of (window_id, k_enc, k_mac) tuples for windows in range
            [window_id - max_drift, window_id + max_drift]
        """
        keys = []
        for drift in range(-max_drift, max_drift + 1):
            wid = window_id + drift
            if wid >= 0:  # Don't generate keys for negative windows
                k_enc, k_mac = self.derive_window_keys(wid)
                keys.append((wid, k_enc, k_mac))
        return keys
    
    def get_time_until_rotation(self, timestamp: float = None) -> float:
        """
        Get seconds until next key rotation.
        
        Args:
            timestamp: Unix timestamp (seconds), uses current time if None
            
        Returns:
            Seconds remaining until next rotation
        """
        if timestamp is None:
            timestamp = time.time()
        current_window = self.get_current_window(timestamp)
        next_window_start = (current_window + 1) * self.rotation_seconds
        return next_window_start - timestamp
    
    # HKDF implementation (RFC 5869)
    
    def _hkdf_extract(self, salt: bytes, ikm: bytes) -> bytes:
        """
        HKDF-Extract step (RFC 5869).
        
        Args:
            salt: Optional salt value (non-secret random value)
            ikm: Input keying material
            
        Returns:
            Pseudorandom key (PRK)
        """
        if not salt:
            salt = b'\x00' * hashlib.sha256().digest_size
        return hmac.new(salt, ikm, hashlib.sha256).digest()
    
    def _hkdf_expand(self, prk: bytes, info: bytes, length: int) -> bytes:
        """
        HKDF-Expand step (RFC 5869).
        
        Args:
            prk: Pseudorandom key from Extract step
            info: Optional context and application specific information
            length: Length of output keying material in bytes (<= 255*HashLen)
            
        Returns:
            Output keying material (OKM)
        """
        hash_len = hashlib.sha256().digest_size
        if length > 255 * hash_len:
            raise ValueError("length too large for HKDF-Expand")
        
        n = (length + hash_len - 1) // hash_len  # Ceiling division
        okm = b""
        t = b""
        
        for i in range(1, n + 1):
            t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
            okm += t
        
        return okm[:length]


def test_key_schedule():
    """Basic test of key schedule functionality."""
    # Test parameters
    shared_secret = b"high_entropy_secret_key_at_least_32bytes!!"
    channel_id = "test_channel_001"
    
    # Create key schedules for both parties
    ks_a = KeySchedule(shared_secret, channel_id, 'A', rotation_seconds=3)
    ks_b = KeySchedule(shared_secret, channel_id, 'B', rotation_seconds=3)
    
    # Test: Same window, same party -> same keys
    window_id = ks_a.get_current_window()
    keys_a1 = ks_a.derive_window_keys(window_id)
    keys_a2 = ks_a.derive_window_keys(window_id)
    assert keys_a1 == keys_a2, "Deterministic derivation failed"
    
    # Test: Different roles -> different keys
    keys_b = ks_b.derive_window_keys(window_id)
    assert keys_a1 != keys_b, "Role separation failed"
    
    # Test: Different windows -> different keys
    keys_next = ks_a.derive_window_keys(window_id + 1)
    assert keys_a1 != keys_next, "Window separation failed"
    
    # Test: Drift tolerance
    drift_keys = ks_a.get_keys_with_drift(window_id, max_drift=1)
    assert len(drift_keys) == 3, f"Expected 3 drift keys, got {len(drift_keys)}"
    
    # Test: Time until rotation
    time_left = ks_a.get_time_until_rotation()
    assert 0 <= time_left < ks_a.rotation_seconds, "Invalid rotation time"
    
    print("✓ Key schedule tests passed")
    print(f"  Window ID: {window_id}")
    print(f"  K_enc (Party A): {keys_a1[0].hex()[:32]}...")
    print(f"  K_enc (Party B): {keys_b[0].hex()[:32]}...")
    print(f"  Time until rotation: {time_left:.2f}s")


if __name__ == "__main__":
    test_key_schedule()
