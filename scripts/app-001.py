#!/usr/bin/env python3
"""
app-001: RSA Certificate Harvester and GVA Geometric Factorizer

Harvests RSA certificates from filesystem, extracts moduli, and applies
Geodesic Validation Assault (GVA) factorization to balanced semiprimes.

Requirements: cryptography, mpmath, sympy, numpy
"""

import os
import sys
import math
import shutil
from pathlib import Path
import hashlib

from cryptography import x509
from cryptography.hazmat.primitives import serialization
import mpmath as mp
import sympy
import numpy as np

# Set mpmath precision
mp.dps = 200

# Constants
PHI = mp.mpf((1 + mp.sqrt(5)) / 2)
E2 = mp.exp(2)

def scan_certificates(root="/"):
    """Scan filesystem for certificate files."""
    cert_extensions = {'.pem', '.crt', '.cer', '.der'}
    found_certs = []

    for path in Path(root).rglob('*'):
        if path.suffix.lower() in cert_extensions:
            try:
                with open(path, 'rb') as f:
                    data = f.read()
                    cert = parse_certificate(data)
                    if cert:
                        found_certs.append((cert, path))
            except Exception:
                # Silently skip invalid files
                pass

    return found_certs

def parse_certificate(data):
    """Parse certificate and extract RSA modulus if present."""
    try:
        if b'-----BEGIN' in data:
            cert = x509.load_pem_x509_certificate(data)
        else:
            cert = x509.load_der_x509_certificate(data)

        public_key = cert.public_key()
        if hasattr(public_key, 'public_numbers'):
            n = public_key.public_numbers().n
            e = public_key.public_numbers().e
            return {'n': n, 'e': e, 'bit_length': n.bit_length()}
    except Exception:
        pass
    return None

def save_moduli(certs, output_dir="~/.tears/"):
    """Save moduli to files with unique names."""
    output_path = Path(output_dir).expanduser()
    output_path.mkdir(exist_ok=True)
    saved = []

    for cert_data, original_path in certs:
        n_str = str(cert_data['n'])
        hash_suffix = hashlib.sha256(n_str.encode()).hexdigest()[:16]
        bit_len = cert_data['bit_length']
        ext = original_path.suffix.lower()

        filename = f"{hash_suffix}_{bit_len}bit{ext}"
        dest_path = output_path / filename

        try:
            shutil.copy(original_path, dest_path)
            saved.append((cert_data, dest_path))
            print(f"Saved: {filename} ({bit_len} bits)")
        except Exception as e:
            print(f"Failed to save {filename}: {e}")

    return saved

def curvature_kappa(n):
    """Compute curvature κ(n) = 4 * ln(n+1) / e²."""
    return 4 * mp.log(mp.mpf(n) + 1) / E2

def theta_prime(n, k=0.3):
    """Generate seed θ'(n, k)."""
    mod = n % int(PHI * 10007)
    return float(PHI * (mod / PHI) ** k)

def embed_torus_geodesic(n, dims=9):
    """Embed n in torus with geodesic transformations."""
    x = mp.mpf(n) / E2
    log_log_n = math.log(math.log(float(n) + 1)) / math.log(2)
    k = 0.3 / log_log_n
    coords = []

    for _ in range(dims):
        frac_x = mp.frac(x)
        x = PHI * mp.power(frac_x, k)
        coords.append(mp.frac(x))

    return coords

def riemannian_distance(coords1, coords2, n):
    """Compute Riemannian distance with curvature."""
    kappa = curvature_kappa(n)
    deltas = [min(abs(c1 - c2), 1 - abs(c1 - c2)) for c1, c2 in zip(coords1, coords2)]
    dist_sq = sum((delta * (1 + kappa * delta))**2 for delta in deltas)
    return math.sqrt(float(dist_sq))

def z_normalization_check(delta_n, n):
    """Post-factor Z-guard: Z = Δn / Δmax < 1."""
    delta_max = mp.mpf(2) ** (mp.mpf(n).bit_length() // 2) / E2
    z = delta_n / delta_max
    if z >= 1:
        raise ValueError(f"Causality violation: Z={z} >= 1")
    return z

def gva_factorize(n):
    """GVA factorization for balanced semiprimes."""
    if sympy.isprime(n):
        return None  # Prime

    sqrt_n = int(mp.sqrt(mp.mpf(n)))
    epsilon = 0.2 / (1 + float(curvature_kappa(n)))

    emb_n = embed_torus_geodesic(n)

    # Search around sqrt_n
    range_limit = 10**6
    for d in range(-range_limit, range_limit + 1):
        p = sqrt_n + d
        if p <= 1 or p >= n or n % p != 0:
            continue

        q = n // p
        if not (sympy.isprime(p) and sympy.isprime(q)):
            continue

        # Balance check
        log_p = math.log(p) / math.log(2)
        log_q = math.log(q) / math.log(2)
        if abs(log_p - log_q) > 1:
            continue

        emb_p = embed_torus_geodesic(p)
        emb_q = embed_torus_geodesic(q)

        dist_p = riemannian_distance(emb_n, emb_p, n)
        dist_q = riemannian_distance(emb_n, emb_q, n)

        if dist_p < epsilon or dist_q < epsilon:
            # Z-guard
            delta_n = abs(p - q)
            z_normalization_check(delta_n, n)
            return p, q

    return None  # No factor found

def fallback_factorize(n):
    """Fallback using sympy.factorint."""
    factors = sympy.factorint(n)
    if len(factors) == 2:
        p, q = factors.keys()
        return int(p), int(q)
    return None

def main():
    print("app-001: RSA Certificate Harvester and GVA Factorizer")
    print("=" * 60)

    # Part 1: Harvest
    print("Scanning for certificates...")
    certs = scan_certificates()
    print(f"Found {len(certs)} RSA certificates")

    moduli = save_moduli(certs)
    print(f"Saved {len(moduli)} moduli to ~/.tears/")

    # Part 2: Factorize
    print("\nFactorizing moduli with GVA...")
    for cert_data, path in moduli:
        n = cert_data['n']
        print(f"\nProcessing {path.name} ({n.bit_length()} bits)")

        factors = gva_factorize(n)
        if factors:
            p, q = factors
            print(f"GVA Success: {n} = {p} × {q}")
        else:
            print("GVA failed, trying fallback...")
            factors = fallback_factorize(n)
            if factors:
                p, q = factors
                print(f"Fallback Success: {n} = {p} × {q}")
            else:
                print("Factorization failed")

if __name__ == "__main__":
    main()