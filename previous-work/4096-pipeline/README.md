### Project Overview
Z5D Secure RSA-4096 Key Generator is a tool for creating cryptographically secure RSA-4096 keys using a Z5D predictor for prime selection, integrated with high-entropy seed generation. It outputs private keys and self-signed X.509 certificates. Suitable for cryptographic applications; emphasizes entropy and uniqueness. Based on C implementation with dependencies on GMP, MPFR, OpenSSL, and optional OpenMP. Recent commit d0b4646 incorporates benchmark artifacts for H7+Z recursive reduction testing on Apple M1 Max, achieving ~16.2% density at r=0.95 and performance improvements.

### Key Components
- **z5d_key_gen.c**: Main program. Handles configuration, seed derivation, prime generation via Z5D (now with H7+Z recursive reduction), RSA keypair creation, certificate generation, and file output. Uses Miller-Rabin for primality testing with geodesic and standard witnesses. Links Metal framework for M1 Max optimizations.
- **z_seed_generator.h**: Header for seed generation. Provides functions to generate 256-bit seeds from /dev/urandom mixed with system entropy (time, PID, clocks) via SHA-256. Includes error codes and hex conversion utilities.
- **z_seed_errors.h**: Defines error constants for seed generation (e.g., ZSEED_ERR_ENTROPY_UNAVAIL).
- **Makefile**: Builds the tool. Supports Clang, OpenMP (if available), and targets like `z5d_secure_key_gen`. Includes tests for seed generation and cleaning artifacts. Compiles with O2 optimization and Metal framework for M1-specific enhancements.
- **Log File (z5d_secure_key_gen_20250918_052235.txt)**: Baseline execution log from September 18, 2025. Shows configuration, prime generation details (e.g., attempts, timings), and summary over 100 runs. Highlights efficiency (avg 606.76 ms per key) and variability in search efforts.
- **Benchmark Log (z5d_h7z_reduction_bench.log)**: New log from commit d0b4646, covering 50 runs on Apple M1 Max with H7+Z reduction; includes per-run timings, attempts, prime indices, and density alignment.

### Core Functionality
1. **Seed Generation**: Uses OS CSPRNG (/dev/urandom) for base entropy, mixed with additional sources. Ensures 256-bit uniqueness; fails on entropy issues.
2. **Prime Generation**: Derives p/q seeds from base seed. Computes large indices (k_base_p/q) via Z5D predictor (params: kappa_geo=0.3, kappa_star=0.04449, phi=golden ratio), now enhanced with H7+Z recursive reduction for improved density (~16.2% at r=0.95). Searches for primes starting from Z5D estimate using parallel Miller-Rabin (up to 5000 attempts, 10 threads if OpenMP enabled; leverages Metal/AMX on M1 Max for vector ops).
3. **RSA Keypair**: Computes n=p*q, d as modular inverse, CRT params. Uses OpenSSL for structures.
4. **Certificate**: Self-signed X.509 v3 with extensions (basic constraints, key usage). Validity: 30 days default.
5. **Output**: Files in "generated/" with tags from seed hash. Permissions: 0600 for keys.

### Configuration Options
From command-line flags in z5d_key_gen.c:

| Option          | Description                  | Default Value          |
|-----------------|------------------------------|------------------------|
| --bits         | Key size (512-8192)         | 4096                  |
| --e            | Public exponent             | 65537                 |
| --validity-days| Cert validity days          | 30                    |
| --kappa-geo    | Z5D geo param               | 0.300                 |
| --kappa-star   | Z5D star param              | 0.04449               |
| --phi          | Z5D phi param               | 1.618033988749890     |
| --bump-p       | Bump for p (non-negative)   | 0                     |
| --bump-q       | Bump for q (non-negative)   | 1                     |
| --debug        | Verbose logging             | Off                   |
| --quiet        | Suppress output             | Off                   |

### Build and Usage
- **Dependencies**: Clang, GMP, MPFR, OpenSSL, libomp (optional for parallel search), Metal framework (for M1 Max optimizations).
- **Build**: Run `make` to compile `z5d_secure_key_gen`. Supports OpenMP and Metal linking.
- **Run**: `./z5d_secure_key_gen [options]`. Generates keys/cert in "generated/".
- **Tests**: `make test` for full run; `make test-seed` for seed validation; `make demo-seed` for seed demo.
- **Clean**: `make clean` removes binaries and outputs.

### Performance Insights (from Log)
- **Baseline (100 runs, pre-H7+Z)**: Avg time 606.76 ms (min 103 ms, max 10338 ms). Avg attempts: p=719.34, q=780.06. Throughput: Avg 3372.8 attempts/sec. Prime index ratio: Avg 1.00187.
- **Updated (50 runs, commit d0b4646 with H7+Z on M1 Max)**: Avg time 464.18 ms (~23% speedup vs. baseline). Avg attempts: p=1025.56 (min 38, max 3529), q=741.32 (min 9, max 3946); combined 1766.88. Prime index ratio: Avg 1.09118 (min 0.545969, max 1.93839; aligns with ~16.2% density at r=0.95). Throughput: Avg 3517.7 attempts/sec (benefits from OpenMP, Metal/AMX integration). No errors; suggests efficient prime distribution via recursive reduction.

### AMX-Optimized Reproduction (2025-10-10)
Steps on Apple M1 Max:
1. `make clean`
2. `make` (builds with `-O3 -mcpu=apple-m1 -DZ5D_USE_AMX=1`)
3. `Z5D_USE_AMX=1 OMP_NUM_THREADS=10 python3 benchmark_smoke.py -n 100`

Results:
- `z5d_secure_key_gen`: mean 0.372 s (min 0.099 s, max 1.047 s)
- `openssl genpkey`: mean 1.065 s (min 0.129 s, max 3.996 s)

The benchmark script logs raw per-run timings for both generators and can be re-run for larger samples. Generated key/cert outputs are stored under `generated/` and may be removed after benchmarking (`rm -f generated/z5d_key_gen-*.{key,crt}`).

### Security Notes
- Entropy: Strict fail on /dev/urandom issues; no fallbacks.
- Memory: Uses OPENSSL_cleanse for sensitive data.
- Primes: 2048-bit each; Z5D with H7+Z for prediction, bumps for variability.
- Outputs: Owner-only permissions; unique per run via system-generated seeds. H7+Z reduction maintains cryptographic strength while improving efficiency.
