# app-001: RSA Certificate Harvester & Geometric Factorizer (GVA)

## Overview

app-001 is an integrated application that combines two powerful components:

1. **RSA Certificate Harvester**: Scans the filesystem for RSA certificates and extracts their public key moduli
2. **Geometric Validation Assault (GVA) Factorizer**: Applies geometric factorization techniques to RSA moduli using torus embeddings and Riemannian geometry

## Requirements

- Python 3.12+
- Required libraries:
  - `cryptography` - For certificate parsing
  - `mpmath` (dps=50) - High-precision mathematics
  - `sympy` - For prime checking and fallback factorization
  - `numpy` - Numerical operations
- OS: Unix-like system (for filesystem scanning from `/`)
- Permissions:
  - Read access to scan directories
  - Write access to `~/.tears/` directory

## Installation

```bash
# Install dependencies
pip install -r python/requirements.txt

# The main dependencies are:
pip install cryptography mpmath sympy numpy
```

## Usage

### Basic Usage

Run the main application to harvest certificates and attempt factorization:

```bash
python3 python/app-001.py
```

By default, this scans the user's home directory for RSA certificates. The application will:
1. Find all `.pem`, `.crt`, `.cer`, and `.der` certificate files
2. Extract RSA public key moduli from valid certificates
3. Copy certificates to `~/.tears/` with SHA256-based naming
4. Attempt to factor moduli up to 64 bits using GVA

### Demo Mode

Run the demo to see GVA factorization in action with known test cases:

```bash
python3 python/demo_app_001.py
```

This demonstrates the geometric factorizer on several small semiprimes (15, 21, 35, 77, 143, 323).

### Testing

Run the test suite:

```bash
python3 tests/test_app_001.py
```

This validates:
- Mathematical constants (φ, e²)
- Curvature calculation
- Resolution calculation
- Z-normalization and causality guards
- Balance checking for factors
- GVA factorization correctness
- RSA certificate harvesting

## Components

### 1. RSA Certificate Harvester

**Features:**
- Recursive filesystem traversal
- Support for multiple certificate formats: PEM, DER, CRT, CER
- Extraction of RSA modulus (n) and exponent (e)
- Collision-resistant naming using SHA256 hash
- Silent error handling for permission issues

**Certificate Naming:**
```
{sha256(n)[:16]}_{bit_length}bit.{extension}
```

Example: `f38a1e525b6a3b54_512bit.pem`

### 2. Geometric Validation Assault (GVA) Factorizer

**Mathematical Foundation:**

The GVA factorizer uses geometric techniques based on:

- **Golden Ratio (φ)**: φ = (1 + √5) / 2 ≈ 1.618
- **Euler's Constant**: e² ≈ 7.389

**Key Components:**

1. **Curvature κ(n)**:
   ```
   κ(n) = 4 × ln(n+1) / e²
   ```
   Tunes the maximum search steps and distance thresholds.

2. **Resolution θ'(n, k)**:
   ```
   mod = n % int(φ × 10007)
   θ'(n, k) = φ × ((mod / φ) ** k)
   ```
   Generates deterministic seeds for the search space.

3. **Z-Normalization**:
   ```
   Δmax = 2^(bit_length(N)//2) / e²
   Z = Δn / Δmax
   ```
   Guards against causality violations (requires Z < 1).

4. **Torus Embedding**:
   - Embeds integers in a 9-dimensional torus manifold
   - Uses iterative transformation: `x → φ × (frac(x/φ))^k`

5. **Riemannian Distance**:
   - Calculates geometric distance with curvature correction
   - Distance metric: `d(c1, c2) = √Σ[(d_i × (1 + κ × d_i))²]`

**Algorithm Flow:**

1. Check if N is prime (early exit)
2. Calculate sqrt(N) as starting point
3. Embed N in torus manifold
4. Search in range around sqrt(N)
5. For each candidate p:
   - Check if N % p == 0
   - Verify both p and q are prime
   - Check balance: |log₂(p/q)| ≤ 1
   - Embed p and calculate Riemannian distance
   - Validate Z-normalization
6. Return factors if distance < ε
7. Fallback to sympy.factorint() if geometric search fails

## Output

The application provides detailed output:

```
======================================================================
RSA Certificate Harvester & Geometric Factorizer (GVA)
======================================================================
[Harvester] Output directory: /home/user/.tears

[Main] Scanning from: /home/user
       (Use root='/' for full filesystem scan)
[Harvester] Starting scan from: /home/user
[Harvester] Found RSA cert: /home/user/test_certs/test_cert.pem
            Modulus bit length: 512
            Destination: f38a1e525b6a3b54_512bit.pem

[GVA] Starting factorization of N = 15
      Bit length: 4
[GVA] sqrt(N) ≈ 3
[GVA] Curvature κ(N) = 1.500916
[GVA] Embedding parameter k = 0.300000
[GVA] Distance threshold ε = 0.479824
[GVA] Searching in range [-10, 10]...
[GVA] SUCCESS! Found factors:
      p = 3
      q = 5
      Distance = 0.005143
      Z = 0.000000

======================================================================
[Main] Summary:
       Certificates found: 3
       Successfully factored: 1
======================================================================
```

## Limitations

- **Performance**: GVA is effective for small to medium-sized moduli (up to ~64 bits)
- **Large Moduli**: For N > 256 bits, recommend using:
  - High-performance libraries like GMP via gmpy2
  - CADO-NFS for general number field sieve
  - Specialized quantum algorithms (when available)
- **Balanced Semiprimes**: GVA targets balanced semiprimes where p ≈ q
- **Search Range**: Limited to 10⁶ by default to prevent long execution times

## Security Summary

✓ **CodeQL Analysis**: No security vulnerabilities detected

**Security Considerations:**
- Application only reads certificates, does not access private keys
- Silent error handling prevents information leakage
- No network operations performed
- All file operations respect system permissions

## Extensions

Potential improvements for production use:

1. **Multiprocessing**: Parallelize filesystem scanning and factorization
2. **Database**: Store harvested certificates and factorization results
3. **CADO-NFS Integration**: For factoring larger moduli (256+ bits)
4. **GPU Acceleration**: Use CUDA/OpenCL for parallel candidate testing
5. **Quantum Resistance**: Add Shor's algorithm detection for quantum-vulnerable keys

## License

Part of the z-sandbox repository. See main repository LICENSE for details.

## References

- RSA Cryptosystem: Rivest, Shamir, Adleman (1977)
- Geometric Number Theory: Conway, Sloane
- Riemannian Geometry: Bernhard Riemann
- Golden Ratio Applications: Fibonacci, Lucas sequences
