#!/usr/bin/env python3
"""
Demo script for app-001: Shows GVA factorization with known small semiprimes.
"""

import os
import sys

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

# Import app-001 classes
import importlib.util
spec = importlib.util.spec_from_file_location("app_001", "python/app-001.py")
app_001 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_001)

GeometricFactorizer = app_001.GeometricFactorizer


def demo_factorization(N, expected_p, expected_q, max_range=10000):
    """
    Demo factorization of a known semiprime.
    """
    print(f"Testing N = {N} ({N.bit_length()} bits)")
    print(f"Expected factors: p = {expected_p}, q = {expected_q}")
    print("-" * 70)
    
    factorizer = GeometricFactorizer()
    result = factorizer.geometric_factor(N, max_range=max_range)
    
    if result:
        found_p, found_q = result
        
        print("\nVerification:")
        print(f"  Expected: {expected_p} × {expected_q} = {expected_p * expected_q}")
        print(f"  Found:    {found_p} × {found_q} = {found_p * found_q}")
        
        if {found_p, found_q} == {expected_p, expected_q}:
            print("\n  ✓ SUCCESS! Factors match exactly!")
            return True
        else:
            print("\n  ✗ FAILED! Factors don't match")
            return False
    else:
        print("\n  ✗ Factorization failed")
        return False


def main():
    """
    Demonstrate GVA factorization with various test cases.
    """
    print("=" * 70)
    print("app-001 Demo: Geometric Validation Assault (GVA) Factorizer")
    print("=" * 70)
    print()
    
    test_cases = [
        # (N, p, q, max_range)
        (15, 3, 5, 10),
        (21, 3, 7, 10),
        (35, 5, 7, 10),
        (77, 7, 11, 20),
        (143, 11, 13, 30),
        (323, 17, 19, 50),
    ]
    
    results = []
    
    for i, (N, p, q, max_range) in enumerate(test_cases, 1):
        print(f"\nTest Case {i}/{len(test_cases)}")
        print("=" * 70)
        success = demo_factorization(N, p, q, max_range)
        results.append(success)
        print()
    
    # Summary
    print("=" * 70)
    print("Summary:")
    print("-" * 70)
    passed = sum(results)
    total = len(results)
    print(f"  Passed: {passed}/{total}")
    print(f"  Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n  ✓ All tests passed!")
    else:
        print(f"\n  ⚠ {total - passed} test(s) failed")
    
    print("=" * 70)
    print()
    print("Note: For RSA certificate harvesting, run: python3 python/app-001.py")
    print("      This will scan for .pem, .crt, .cer, .der files and attempt")
    print("      factorization on RSA moduli found.")
    print()


if __name__ == "__main__":
    main()
