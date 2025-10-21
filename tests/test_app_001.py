#!/usr/bin/env python3
"""
Unit tests for app-001: RSA Certificate Harvester & Geometric Factorizer (GVA)
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import importlib.util

# Import app-001.py
spec = importlib.util.spec_from_file_location("app_001", "python/app-001.py")
app_001 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_001)

# Import classes
RSACertHarvester = app_001.RSACertHarvester
GeometricFactorizer = app_001.GeometricFactorizer


def test_geometric_factorizer_small():
    """Test GVA factorizer with small known semiprimes"""
    factorizer = GeometricFactorizer()
    
    # Test case 1: N = 15 = 3 × 5
    print("Test 1: N = 15")
    result = factorizer.geometric_factor(15, max_range=10)
    assert result is not None, "Should find factors for N=15"
    p, q = result
    assert {p, q} == {3, 5}, f"Expected {{3, 5}}, got {{{p}, {q}}}"
    assert p * q == 15, f"Factors should multiply to N: {p} × {q} = {p*q}"
    print(f"  ✓ SUCCESS: {p} × {q} = 15\n")
    
    # Test case 2: N = 21 = 3 × 7
    print("Test 2: N = 21")
    result = factorizer.geometric_factor(21, max_range=10)
    assert result is not None, "Should find factors for N=21"
    p, q = result
    assert {p, q} == {3, 7}, f"Expected {{3, 7}}, got {{{p}, {q}}}"
    assert p * q == 21, f"Factors should multiply to N: {p} × {q} = {p*q}"
    print(f"  ✓ SUCCESS: {p} × {q} = 21\n")
    
    # Test case 3: N = 35 = 5 × 7
    print("Test 3: N = 35")
    result = factorizer.geometric_factor(35, max_range=10)
    assert result is not None, "Should find factors for N=35"
    p, q = result
    assert {p, q} == {5, 7}, f"Expected {{5, 7}}, got {{{p}, {q}}}"
    assert p * q == 35, f"Factors should multiply to N: {p} × {q} = {p*q}"
    print(f"  ✓ SUCCESS: {p} × {q} = 35\n")


def test_geometric_factorizer_prime():
    """Test that GVA correctly identifies primes"""
    factorizer = GeometricFactorizer()
    
    # Test with prime number
    print("Test: N = 17 (prime)")
    result = factorizer.geometric_factor(17, max_range=10)
    assert result is None, "Should return None for prime numbers"
    print("  ✓ SUCCESS: Correctly identified as prime\n")


def test_geometric_factorizer_constants():
    """Test mathematical constants are correctly set"""
    factorizer = GeometricFactorizer()
    
    # Test φ (golden ratio)
    import mpmath as mp
    expected_phi = (1 + mp.sqrt(5)) / 2
    assert abs(factorizer.phi - expected_phi) < 1e-10, "φ should be golden ratio"
    print(f"  ✓ φ = {float(factorizer.phi):.10f}")
    
    # Test e²
    expected_e2 = mp.exp(2)
    assert abs(factorizer.e2 - expected_e2) < 1e-10, "e2 should be exp(2)"
    print(f"  ✓ e² = {float(factorizer.e2):.10f}\n")


def test_curvature():
    """Test curvature calculation"""
    factorizer = GeometricFactorizer()
    
    # Test curvature formula: κ(n) = 4 * ln(n+1) / e²
    import mpmath as mp
    n = 100
    kappa = factorizer.curvature(n)
    expected = mp.mpf(4) * mp.log(mp.mpf(n + 1)) / mp.exp(2)
    
    assert abs(kappa - expected) < 1e-10, "Curvature calculation incorrect"
    print(f"  ✓ κ(100) = {float(kappa):.10f}\n")


def test_resolution():
    """Test resolution calculation"""
    factorizer = GeometricFactorizer()
    
    # Test resolution formula: θ'(n, k) = φ * ((mod / φ) ** k)
    n = 100
    k = 0.3
    theta = factorizer.resolution(n, k)
    
    assert isinstance(theta, float), "Resolution should return float"
    assert theta > 0, "Resolution should be positive"
    print(f"  ✓ θ'(100, 0.3) = {theta:.10f}\n")


def test_z_normalize():
    """Test Z-normalization"""
    factorizer = GeometricFactorizer()
    import mpmath as mp
    
    # Test with valid delta (small value that won't violate causality)
    N = 100
    delta_n = mp.mpf(1)  # Use a smaller delta
    Z = factorizer.z_normalize(delta_n, N)
    
    assert Z < 1, "Z should be less than 1 for valid case"
    print(f"  ✓ Z = {float(Z):.10f} < 1")
    
    # Test causality violation (Z >= 1)
    try:
        delta_max = mp.mpf(2 ** (N.bit_length() // 2)) / factorizer.e2
        invalid_delta = delta_max * 2  # This should cause Z >= 1
        Z_invalid = factorizer.z_normalize(invalid_delta, N)
        assert False, "Should raise ValueError for Z >= 1"
    except ValueError as e:
        assert "Causality violation" in str(e)
        print(f"  ✓ Causality guard working\n")


def test_check_balance():
    """Test balance checking"""
    factorizer = GeometricFactorizer()
    
    # Balanced factors (ratio close to 1)
    assert factorizer.check_balance(5, 7) == True, "5 and 7 should be balanced"
    print("  ✓ 5 × 7: balanced")
    
    # Unbalanced factors (large ratio)
    assert factorizer.check_balance(2, 1000) == False, "2 and 1000 should be unbalanced"
    print("  ✓ 2 × 1000: unbalanced")
    
    # Edge case: zero
    assert factorizer.check_balance(0, 5) == False, "Should handle zero"
    print("  ✓ Zero handling: correct\n")


def test_rsa_harvester():
    """Test RSA certificate harvester"""
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    import datetime
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as test_dir:
        with tempfile.TemporaryDirectory() as output_dir:
            # Generate test certificate
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=512,
                backend=default_backend()
            )
            
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, 'test.example.com'),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.now(datetime.UTC)
            ).not_valid_after(
                datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
            ).sign(private_key, hashes.SHA256(), default_backend())
            
            # Save certificate
            cert_path = os.path.join(test_dir, 'test.pem')
            with open(cert_path, 'wb') as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # Create harvester
            harvester = RSACertHarvester(output_dir=output_dir)
            
            # Harvest certificates
            results = list(harvester.scan_filesystem(root=test_dir, max_depth=1))
            
            assert len(results) == 1, f"Should find 1 certificate, found {len(results)}"
            
            n, e, dest_path = results[0]
            assert isinstance(n, int), "Modulus should be int"
            assert isinstance(e, int), "Exponent should be int"
            assert os.path.exists(dest_path), "Destination file should exist"
            
            # Verify exponent
            assert e == 65537, f"Exponent should be 65537, got {e}"
            
            print(f"  ✓ Harvested certificate: {n.bit_length()} bits")
            print(f"  ✓ Destination: {os.path.basename(dest_path)}\n")


def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("Running tests for app-001")
    print("=" * 70)
    print()
    
    tests = [
        ("Mathematical Constants", test_geometric_factorizer_constants),
        ("Curvature Calculation", test_curvature),
        ("Resolution Calculation", test_resolution),
        ("Z-Normalization", test_z_normalize),
        ("Balance Checking", test_check_balance),
        ("GVA Factorizer (Small Numbers)", test_geometric_factorizer_small),
        ("GVA Factorizer (Prime Detection)", test_geometric_factorizer_prime),
        ("RSA Certificate Harvester", test_rsa_harvester),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"Test: {name}")
        print("-" * 70)
        try:
            test_func()
            passed += 1
            print(f"✓ PASSED\n")
        except Exception as e:
            failed += 1
            print(f"✗ FAILED: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
