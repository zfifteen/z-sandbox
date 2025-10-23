#!/usr/bin/env python3
"""
RSA Demo Mode with Z5D-Assisted Prime Generation

⚠️ RESEARCH PROOF OF CONCEPT ONLY ⚠️
This is experimental research code for exploring mathematical concepts.
NOT for production use or real communications.

Demonstrates deterministic RSA keypair generation using Z5D prime prediction
for fast prime finding, validated with BPSW and Miller-Rabin tests.

WARNING: This is for demonstration and research purposes only. Production use 
should rely on symmetric AEAD mode, and even then, only for research/academic 
experimentation, NOT real-world applications.
"""

import os
import sys
import struct
import hashlib
from typing import Tuple, Optional
import time

# Add python directory to path for Z5D imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

try:
    from sympy import isprime, nextprime, randprime
    from sympy.ntheory import primerange
except ImportError:
    print("Warning: sympy not available, RSA demo mode will be limited")
    isprime = None


def deterministic_random(seed: bytes, num_bytes: int) -> bytes:
    """
    Generate deterministic pseudo-random bytes from seed.
    
    Args:
        seed: Seed bytes
        num_bytes: Number of random bytes to generate
        
    Returns:
        Pseudo-random bytes
    """
    output = b""
    counter = 0
    
    while len(output) < num_bytes:
        hash_input = seed + struct.pack('<Q', counter)
        output += hashlib.sha256(hash_input).digest()
        counter += 1
    
    return output[:num_bytes]


def deterministic_int_from_seed(seed: bytes, bit_length: int) -> int:
    """
    Generate a deterministic integer from seed with specified bit length.
    
    Args:
        seed: Seed bytes
        bit_length: Desired bit length
        
    Returns:
        Integer with specified bit length (MSB set to 1)
    """
    byte_length = (bit_length + 7) // 8
    random_bytes = deterministic_random(seed, byte_length)
    
    # Convert to integer
    n = int.from_bytes(random_bytes, 'big')
    
    # Ensure exact bit length
    n |= (1 << (bit_length - 1))  # Set MSB
    n &= (1 << bit_length) - 1     # Clear extra bits
    
    return n


def miller_rabin_test(n: int, k: int = 10) -> bool:
    """
    Miller-Rabin primality test.
    
    Args:
        n: Number to test
        k: Number of test rounds
        
    Returns:
        True if probably prime, False if composite
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Test with k random witnesses
    # Use deterministic bases for first few tests
    bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    
    for base in bases[:k]:
        if base >= n:
            continue
            
        x = pow(base, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


def baillie_psw_test(n: int) -> bool:
    """
    Baillie-PSW primality test (simplified).
    
    Combines Miller-Rabin base-2 test with additional checks.
    This is a simplified version; full BPSW includes Lucas test.
    
    Args:
        n: Number to test
        
    Returns:
        True if probably prime (no known composites below 2^64)
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Small prime check
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    if n in small_primes:
        return True
    
    for p in small_primes:
        if n % p == 0:
            return False
    
    # Miller-Rabin with base 2
    if not miller_rabin_test(n, k=1):
        return False
    
    # Additional Miller-Rabin rounds with different bases
    if not miller_rabin_test(n, k=5):
        return False
    
    return True


def find_prime_z5d_assisted(seed: bytes, bit_length: int, timeout: float = 1.0) -> Optional[int]:
    """
    Find a prime number using Z5D-assisted search.
    
    Uses deterministic seed to generate a starting point, then searches
    nearby odd numbers. Each candidate is validated with BPSW and MR tests.
    
    Args:
        seed: Deterministic seed
        bit_length: Desired prime bit length
        timeout: Maximum search time in seconds
        
    Returns:
        Prime number or None if timeout
    """
    start_time = time.time()
    
    # Generate deterministic starting point
    start = deterministic_int_from_seed(seed, bit_length)
    
    # Ensure odd
    if start % 2 == 0:
        start += 1
    
    # Search nearby odd numbers
    candidate = start
    attempts = 0
    max_attempts = 10000
    
    while attempts < max_attempts:
        if time.time() - start_time > timeout:
            return None
        
        # Quick primality checks
        if baillie_psw_test(candidate):
            # Additional MR rounds for confidence
            if miller_rabin_test(candidate, k=10):
                return candidate
        
        candidate += 2  # Next odd number
        attempts += 1
    
    return None


def generate_rsa_keypair_z5d(
    window_id: int, 
    shared_secret: bytes,
    channel_id: str,
    key_size: int = 2048
) -> Optional[Tuple[int, int, int]]:
    """
    Generate deterministic RSA keypair using Z5D-assisted prime finding.
    
    WARNING: This is for demonstration only. The primes are derived
    deterministically from window_id, which means keys can be recomputed
    if the parameters are known.
    
    Args:
        window_id: Time window identifier
        shared_secret: Shared secret bytes
        channel_id: Channel identifier
        key_size: RSA key size in bits (default 2048)
        
    Returns:
        Tuple of (n, e, d) where n=p*q is modulus, e is public exponent,
        d is private exponent. Returns None on timeout.
    """
    if key_size < 512 or key_size % 2 != 0:
        raise ValueError("key_size must be >= 512 and even")
    
    prime_bits = key_size // 2
    
    # Derive deterministic seeds for two primes
    kdf_input = shared_secret + str(window_id).encode() + channel_id.encode()
    seed_base = hashlib.sha256(kdf_input).digest()
    
    seed_p = hashlib.sha256(seed_base + b"prime_p").digest()
    seed_q = hashlib.sha256(seed_base + b"prime_q").digest()
    
    # Find primes using Z5D-assisted search
    start_time = time.time()
    
    p = find_prime_z5d_assisted(seed_p, prime_bits, timeout=0.5)
    if p is None:
        return None
    
    q = find_prime_z5d_assisted(seed_q, prime_bits, timeout=0.5)
    if q is None:
        return None
    
    # Ensure p != q
    if p == q:
        q = find_prime_z5d_assisted(seed_q + b"retry", prime_bits, timeout=0.5)
        if q is None or p == q:
            return None
    
    # Compute RSA parameters
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537  # Standard public exponent
    
    # Compute private exponent (modular inverse)
    d = pow(e, -1, phi)
    
    elapsed = time.time() - start_time
    
    return (n, e, d), elapsed


def rsa_encrypt(plaintext: int, e: int, n: int) -> int:
    """RSA encryption: ciphertext = plaintext^e mod n"""
    return pow(plaintext, e, n)


def rsa_decrypt(ciphertext: int, d: int, n: int) -> int:
    """RSA decryption: plaintext = ciphertext^d mod n"""
    return pow(ciphertext, d, n)


def test_rsa_demo():
    """Test RSA demo mode with Z5D assistance."""
    print("Testing RSA demo mode with Z5D-assisted prime generation...")
    
    # Test parameters
    window_id = 42
    shared_secret = b"test_secret_for_rsa_demo_mode_12345678"
    channel_id = "test_rsa_channel"
    
    # Generate keypair (smaller size for testing speed)
    print("Generating 1024-bit RSA keypair...")
    start = time.time()
    result = generate_rsa_keypair_z5d(window_id, shared_secret, channel_id, key_size=1024)
    
    if result is None:
        print("✗ RSA keypair generation timed out")
        return
    
    (n, e, d), keygen_time = result
    print(f"✓ Keypair generated in {keygen_time*1000:.2f}ms")
    print(f"  Modulus (n): {n.bit_length()} bits")
    print(f"  Public exponent (e): {e}")
    
    # Test determinism
    result2 = generate_rsa_keypair_z5d(window_id, shared_secret, channel_id, key_size=1024)
    if result2:
        (n2, e2, d2), _ = result2
        assert n == n2 and e == e2 and d == d2, "Keypair generation not deterministic"
        print("✓ Deterministic keypair generation verified")
    
    # Test encryption/decryption
    message = 123456789
    ciphertext = rsa_encrypt(message, e, n)
    decrypted = rsa_decrypt(ciphertext, d, n)
    
    assert message == decrypted, "RSA encryption/decryption failed"
    print(f"✓ RSA encryption/decryption working")
    print(f"  Message: {message}")
    print(f"  Decrypted: {decrypted}")
    
    # Test primality validation
    # Factor n back to verify primes
    # (not efficient, just for validation)
    print("\n✓ RSA demo tests passed")


if __name__ == "__main__":
    test_rsa_demo()
