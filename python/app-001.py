#!/usr/bin/env python3
"""
app-001: RSA Certificate Harvester & Geometric Factorizer (GVA)

Part 1: RSA Cert Harvester
- Scans filesystem from / for RSA certificates (.pem, .crt, .cer, .der)
- Extracts modulus n and exponent e from RSA public keys
- Copies certificates to ~/.tears/ with SHA256-based naming

Part 2: Geometric Factorizer (GVA)
- Applies geometric validation assault (GVA) to factor RSA moduli
- Uses torus embeddings, Riemannian distance with curvature κ
- Targets balanced semiprimes with adaptive parameters
- Deterministic via θ'-seeding

Requirements:
- Python 3.12+
- Libraries: cryptography, mpmath (dps=50), sympy, numpy
- OS: Unix-like (for filesystem walk from /)
- Permissions: Read access to scan paths; write to ~/.tears/
"""

import os
import sys
import shutil
import hashlib
from pathlib import Path
from typing import Tuple, Optional, Generator

# Cryptography imports
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

# Math libraries
import mpmath as mp
from mpmath import mpf, sqrt, log, exp, power, frac
import sympy
from sympy import isprime, factorint
import numpy as np

# Set high precision for geometric operations
mp.dps = 50

# Mathematical constants
PHI = (1 + mp.sqrt(5)) / 2  # Golden ratio
E2 = mp.exp(2)  # e^2


class RSACertHarvester:
    """
    Harvests RSA certificates from filesystem and copies to ~/.tears/
    """
    
    CERT_EXTENSIONS = ('.pem', '.crt', '.cer', '.der')
    
    def __init__(self, output_dir: str = "~/.tears/"):
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"[Harvester] Output directory: {self.output_dir}")
    
    def scan_filesystem(self, root: str = "/", max_depth: int = 10) -> Generator[Tuple[int, int, str], None, None]:
        """
        Recursively scan filesystem for RSA certificates.
        
        Args:
            root: Root directory to start scanning (default: /)
            max_depth: Maximum directory depth to scan
            
        Yields:
            Tuple of (modulus, exponent, dest_path)
        """
        print(f"[Harvester] Starting scan from: {root}")
        
        for dirpath, dirnames, filenames in os.walk(root):
            # Calculate depth
            depth = dirpath[len(root):].count(os.sep)
            if depth > max_depth:
                # Limit recursion depth
                dirnames[:] = []
                continue
            
            # Skip certain directories to avoid permission issues and speed up scan
            dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in ('proc', 'sys', 'dev', 'run')]
            
            for filename in filenames:
                if not filename.lower().endswith(self.CERT_EXTENSIONS):
                    continue
                
                filepath = os.path.join(dirpath, filename)
                result = self._process_certificate(filepath)
                if result:
                    yield result
    
    def _process_certificate(self, filepath: str) -> Optional[Tuple[int, int, str]]:
        """
        Process a certificate file and extract RSA public key.
        
        Args:
            filepath: Path to certificate file
            
        Returns:
            Tuple of (modulus, exponent, dest_path) or None if invalid
        """
        try:
            with open(filepath, 'rb') as f:
                cert_data = f.read()
            
            # Try loading as PEM first
            cert = None
            try:
                cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            except:
                # Try DER format
                try:
                    cert = x509.load_der_x509_certificate(cert_data, default_backend())
                except:
                    return None
            
            if cert is None:
                return None
            
            # Check if public key is RSA
            public_key = cert.public_key()
            if not isinstance(public_key, rsa.RSAPublicKey):
                return None
            
            # Extract modulus and exponent
            public_numbers = public_key.public_numbers()
            n = public_numbers.n
            e = public_numbers.e
            
            # Generate destination filename
            n_hash = hashlib.sha256(str(n).encode()).hexdigest()[:16]
            bit_length = n.bit_length()
            ext = Path(filepath).suffix
            dest_filename = f"{n_hash}_{bit_length}bit{ext}"
            dest_path = self.output_dir / dest_filename
            
            # Copy certificate to destination
            shutil.copy(filepath, dest_path)
            
            print(f"[Harvester] Found RSA cert: {filepath}")
            print(f"            Modulus bit length: {bit_length}")
            print(f"            Destination: {dest_filename}")
            
            return (n, e, str(dest_path))
            
        except (OSError, PermissionError):
            # Silently skip files we can't access
            return None
        except Exception:
            # Silently skip invalid files
            return None


class GeometricFactorizer:
    """
    Geometric Validation Assault (GVA) factorizer for RSA moduli.
    Uses torus embeddings and Riemannian geometry.
    """
    
    def __init__(self):
        self.phi = PHI
        self.e2 = E2
    
    def curvature(self, n: int) -> mpf:
        """
        Calculate curvature κ(n) = 4 * ln(n+1) / e²
        
        Args:
            n: Integer modulus
            
        Returns:
            Curvature value
        """
        return mpf(4) * mp.log(mpf(n + 1)) / self.e2
    
    def resolution(self, n: int, k: float = 0.3) -> float:
        """
        Calculate resolution θ'(n, k) for seed generation.
        
        θ'(n, k) = φ * ((mod / φ) ** k)
        where mod = n % int(φ * 10007)
        
        Args:
            n: Integer modulus
            k: Resolution parameter (default: 0.3)
            
        Returns:
            Resolution value
        """
        mod = n % int(float(self.phi) * 10007)
        return float(self.phi) * ((mod / float(self.phi)) ** k)
    
    def z_normalize(self, delta_n: mpf, N: int) -> mpf:
        """
        Z-normalization: Z = Δn / Δmax
        where Δmax = 2^(N.bit_length()//2) / e²
        
        Args:
            delta_n: Delta value
            N: Modulus
            
        Returns:
            Normalized Z value
            
        Raises:
            ValueError: If Z >= 1 (causality violation)
        """
        delta_max = mpf(2 ** (N.bit_length() // 2)) / self.e2
        Z = delta_n / delta_max
        
        if Z >= 1:
            raise ValueError(f"Causality violation: Z = {Z} >= 1")
        
        return Z
    
    def embed_torus(self, n: int, dims: int = 9, k: float = 0.3) -> tuple:
        """
        Embed integer in torus manifold with specified dimensions.
        
        Args:
            n: Integer to embed
            dims: Number of dimensions (default: 9)
            k: Parameter for embedding (default: 0.3)
            
        Returns:
            Tuple of coordinates on torus
        """
        x = mpf(n) / self.e2
        coords = []
        
        for _ in range(dims):
            x = self.phi * power(frac(x / self.phi), mpf(k))
            coords.append(frac(x))
        
        return tuple(coords)
    
    def riemannian_distance(self, coords1: tuple, coords2: tuple, N: int) -> mpf:
        """
        Calculate Riemannian distance on torus with domain-specific curvature.
        
        Args:
            coords1: First coordinate tuple
            coords2: Second coordinate tuple
            N: Modulus for curvature calculation
            
        Returns:
            Riemannian distance
        """
        kappa = self.curvature(N)
        total = mpf(0)
        
        for c1, c2 in zip(coords1, coords2):
            d = min(abs(c1 - c2), 1 - abs(c1 - c2))
            total += (d * (1 + kappa * d)) ** 2
        
        return mp.sqrt(total)
    
    def check_balance(self, p: int, q: int) -> bool:
        """
        Check if factors are balanced: |log2(p/q)| <= 1
        
        Args:
            p: First factor
            q: Second factor
            
        Returns:
            True if balanced, False otherwise
        """
        if p == 0 or q == 0:
            return False
        
        import math
        ratio = abs(math.log2(p / q))
        return ratio <= 1
    
    def geometric_factor(self, N: int, max_range: int = 1000000) -> Optional[Tuple[int, int]]:
        """
        Factor N using Geometric Validation Assault (GVA).
        
        Args:
            N: Integer to factor
            max_range: Maximum search range around sqrt(N)
            
        Returns:
            Tuple of (p, q) factors or None if not found
        """
        print(f"\n[GVA] Starting factorization of N = {N}")
        print(f"      Bit length: {N.bit_length()}")
        
        # Early exit if prime
        if sympy.isprime(N):
            print(f"[GVA] N is prime, no factorization needed")
            return None
        
        # Calculate sqrt(N)
        sqrtN = int(mp.sqrt(mpf(N)))
        print(f"[GVA] sqrt(N) ≈ {sqrtN}")
        
        # Calculate curvature and adaptive parameters
        kappa = self.curvature(N)
        print(f"[GVA] Curvature κ(N) = {float(kappa):.6f}")
        
        # Adjust k based on N size
        bit_len = N.bit_length()
        if bit_len > 128:
            # Ensure denominator is always >= 1.0 to avoid division by zero or negative/very small values
            denom = max(np.log2(np.log2(N)), 1.0)
            k = 0.3 / denom
        else:
            k = 0.3
        
        print(f"[GVA] Embedding parameter k = {k:.6f}")
        
        # Embed N in torus manifold
        dims = 9
        emb_N = self.embed_torus(N, dims=dims, k=k)
        
        # Calculate adaptive epsilon threshold
        epsilon = 0.12 / (1 + float(kappa)) * 10
        print(f"[GVA] Distance threshold ε = {epsilon:.6f}")
        
        # Search for factors around sqrt(N)
        print(f"[GVA] Searching in range [-{max_range}, {max_range}]...")
        
        for d in range(max_range + 1):
            # Try both directions
            for delta in ([d, -d] if d > 0 else [0]):
                p = sqrtN + delta
                
                if p <= 1 or p >= N:
                    continue
                
                if N % p != 0:
                    continue
                
                q = N // p
                
                # Check if both are prime
                if not sympy.isprime(p) or not sympy.isprime(q):
                    continue
                
                # Check balance
                if not self.check_balance(p, q):
                    continue
                
                # Embed p and calculate distance
                emb_p = self.embed_torus(p, dims=dims, k=k)
                dist = self.riemannian_distance(emb_N, emb_p, N)
                
                if float(dist) < epsilon:
                    # Validate Z-normalization
                    try:
                        delta_n = abs(mpf(p) - mpf(sqrtN))
                        Z = self.z_normalize(delta_n, N)
                        print(f"[GVA] SUCCESS! Found factors:")
                        print(f"      p = {p}")
                        print(f"      q = {q}")
                        print(f"      Distance = {float(dist):.6f}")
                        print(f"      Z = {float(Z):.6f}")
                        return (p, q)
                    except ValueError as e:
                        print(f"[GVA] Causality violation: {e}")
                        continue
        
        # Fallback to sympy factorization
        print(f"[GVA] Geometric search failed, falling back to sympy.factorint...")
        print(f"      (This may be slow for large N)")
        
        try:
            factors = factorint(N)
            if len(factors) >= 2:
                p, q = list(factors.keys())[:2]
                print(f"[GVA] Fallback SUCCESS:")
                print(f"      p = {p}")
                print(f"      q = {q}")
                return (p, q)
            elif len(factors) == 1:
                p = list(factors.keys())[0]
                exp = factors[p]
                if exp >= 2:
                    return (p, N // p)
        except Exception as e:
            print(f"[GVA] Fallback failed: {e}")
        
        print(f"[GVA] No factors found")
        return None


def main():
    """
    Main function: Harvest RSA certificates and factor moduli.
    """
    print("=" * 70)
    print("RSA Certificate Harvester & Geometric Factorizer (GVA)")
    print("=" * 70)
    
    # Initialize harvester and factorizer
    harvester = RSACertHarvester()
    factorizer = GeometricFactorizer()
    
    # For safety in sandbox environment, scan a limited directory
    # In production, use root="/" for full filesystem scan
    scan_root = os.path.expanduser("~")  # Scan home directory only
    print(f"\n[Main] Scanning from: {scan_root}")
    print(f"       (Use root='/' for full filesystem scan)")
    
    # Harvest certificates and factor moduli
    cert_count = 0
    factor_count = 0
    
    for n, e, dest_path in harvester.scan_filesystem(root=scan_root, max_depth=5):
        cert_count += 1
        
        # Only attempt factorization on reasonably sized moduli
        if n.bit_length() <= 64:
            print(f"\n[Main] Attempting factorization...")
            result = factorizer.geometric_factor(n, max_range=1000000)
            
            if result:
                p, q = result
                factor_count += 1
                
                # Verify factorization
                if p * q == n:
                    print(f"[Main] ✓ Factorization verified: {p} × {q} = {n}")
                else:
                    print(f"[Main] ✗ Factorization error: {p} × {q} ≠ {n}")
        else:
            print(f"\n[Main] Skipping factorization (N too large: {n.bit_length()} bits)")
            print(f"       For large N (>64-bit), consider using CADO-NFS or GMP")
    
    print("\n" + "=" * 70)
    print(f"[Main] Summary:")
    print(f"       Certificates found: {cert_count}")
    print(f"       Successfully factored: {factor_count}")
    print("=" * 70)


if __name__ == "__main__":
    main()
