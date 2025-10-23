#!/usr/bin/env python3
"""
Test script for hybrid factorization with zeta tuning
"""

from geometric_factorization import unified_factorization, ZETA_ZEROS_IMAG

def test_small_semiprime():
    """Test on N=91 (7 × 13)"""
    N = 91
    factors, theta = unified_factorization(N, ZETA_ZEROS_IMAG)
    print(f"N={N} factors found: {factors}")
    print(f"Theta value: {theta}")
    if factors:
        print(f"Verification: {N} % {factors[0]} = {N % factors[0]}")
        print(f"Success: {factors[0] in [7, 13]}")
    else:
        print("No factors found")

def test_large_semiprime():
    """Test on N=100160063 (10007 × 10009)"""
    N = 100160063
    factors, theta = unified_factorization(N, ZETA_ZEROS_IMAG)
    print(f"N={N} factors found: {factors}")
    print(f"Theta value: {theta}")
    if factors:
        print(f"Verification: {N} % {factors[0]} = {N % factors[0]}")
    else:
        print("No factors found - may need parameter tuning")

if __name__ == '__main__':
    print("Testing hybrid factorization with zeta tuning")
    print("=" * 50)
    test_small_semiprime()
    print()
    test_large_semiprime()