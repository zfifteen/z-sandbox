#!/usr/bin/env python3
"""
Test script for evaluating Geodesic Validation Assault on unbalanced 51-bit semiprimes.
Includes the corrected case and random unbalanced tests.
"""

import random
import math
import time
import sympy as sp
from mpmath import mp

# Set high precision
mp.dps = 50

def is_prime_miller_rabin(n: int, rounds: int = 10) -> bool:
    """Miller-Rabin primality test."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23]  # Sufficient for n < 2^64

    def check_composite(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return False
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return False
        return True

    for witness in witnesses:
        if witness >= n:
            continue
        if check_composite(witness):
            return False
    return True

def generate_prime(bit_size: int, seed: int) -> int:
    """Generate a random prime of specified bit size."""
    rng = random.Random(seed)
    while True:
        p = rng.getrandbits(bit_size)
        p |= (1 << (bit_size - 1))
        p |= 1
        if is_prime_miller_rabin(p):
            return p

def generate_unbalanced_semiprime(small_prime: int, large_bits: int, seed: int) -> tuple[int, int, int]:
    """Generate N = small_prime * large_prime, where large_prime has large_bits."""
    large_prime = generate_prime(large_bits, seed)
    N = small_prime * large_prime
    return N, small_prime, large_prime

# Test on the corrected 51-bit unbalanced semiprime
N = 1125907423042007
p_true = 61343
q_true = 18354293449

print("Testing on corrected 51-bit unbalanced semiprime...")
print(f"N = {N} ({N.bit_length()} bits)")
print(f"p = {p_true} ({p_true.bit_length()} bits)")
print(f"q = {q_true} ({q_true.bit_length()} bits)")
print(f"Verification: p * q = {p_true * q_true} == N? {p_true * q_true == N}")

# Test GVA from manifold_50bit.py
import sys
sys.path.append('.')
from manifold_50bit import gva_factorize_50bit

print("\nTesting Geodesic Validation Assault...")
start_time = time.time()
result = gva_factorize_50bit(N)
elapsed = time.time() - start_time

if result[0]:
    found_p, found_q, dist = result
    print(f"SUCCESS: Found factors {found_p} × {found_q}")
    print(f"Correct? {found_p == p_true and found_q == q_true}")
    print(f"Distance: {dist:.4f}")
    print(f"Time: {elapsed:.3f}s")
else:
    print(f"FAILED: No factors found in {elapsed:.3f}s")

# Additional random tests
print("\n=== Random Unbalanced Semiprime Tests ===")
num_tests = 5
successes = 0

for i in range(num_tests):
    # Generate random unbalanced semiprime ~50 bits
    small_prime = sp.nextprime(random.randint(2**10, 2**15))
    large_bits = 50 - small_prime.bit_length()
    seed = random.randint(0, 2**32)
    N_test, p_test, q_test = generate_unbalanced_semiprime(small_prime, large_bits, seed)
    
    print(f"\nTest {i+1}: N={N_test} ({N_test.bit_length()} bits), p={p_test} ({p_test.bit_length()} bits), q={q_test} ({q_test.bit_length()} bits)")
    
    start_time = time.time()
    result_test = gva_factorize_50bit(N_test)
    elapsed = time.time() - start_time
    
    if result_test[0]:
        found_p, found_q, dist = result_test
        correct = {found_p, found_q} == {p_test, q_test}
        if correct:
            successes += 1
            print(f"  SUCCESS: Distance {dist:.4f}, Time {elapsed:.3f}s")
        else:
            print(f"  WRONG FACTORS: Found {found_p} × {found_q}, Expected {p_test} × {q_test}")
    else:
        print(f"  FAILED: Time {elapsed:.3f}s")

print(f"\nRandom Test Summary: {successes}/{num_tests} successes")