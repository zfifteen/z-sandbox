# RSA Factorization Ladder Framework

A comprehensive Java framework for testing and benchmarking integer factorization methods against RSA challenges, featuring a "ladder" approach that incrementally scales from 200 to 260+ digits. Includes RSA challenge validation, pluggable candidate builders, performance metrics, and BigDecimal support for ultra-high scale computations.

**Also includes:** TRANSEC - Time-Synchronized Encryption for zero-handshake encrypted messaging, inspired by military frequency-hopping COMSEC.

> **Highlights**
>
> - **RSA Challenge Harness:** Validates factored entries (RSA-100 to RSA-250) with strict integrity checks
> - **Factorization Ladder:** Incremental testing from 200-260 digits with configurable builders
> - **Candidate Builders:** ZNeighborhood, ResidueFilter, HybridGcd, MetaSelection strategies
> - **Performance Metrics:** CSV logging, plotting, and BigDecimal timings up to 10^1233
> - **BigDecimal Support:** Ultra-high scale computations with stable accuracy
> - **TRANSEC Protocol:** Zero-RTT encrypted messaging for tactical/industrial applications

---

## Table of Contents
- [Quick Start](#quick-start)
- [RSA Challenge Framework](#rsa-challenge-framework)
- [Factorization Ladder](#factorization-ladder)
- [Candidate Builders](#candidate-builders)
- [BigDecimal / Ultra-High Scale](#bigdecimal--ultra-high-scale)
- [Benchmarks & Metrics](#benchmarks--metrics)
- [TRANSEC - Zero-Handshake Encryption](#transec---zero-handshake-encryption)
- [Tests](#tests)
- [Continuous Integration](#continuous-integration)
- [Documentation](#documentation)
- [Design Notes](#design-notes)
- [Limits & Caveats](#limits--caveats)
- [Roadmap](#roadmap)
- [License](#license)

---

## Quick Start

### Requirements
- Java 17+ (recommended)
- Gradle wrapper included

### Build & Run Tests
```bash
# Build and run all tests
./gradlew test

# Run RSA challenge tests
./gradlew test --tests "unifiedframework.TestRSAChallenges"

# Run integration tests (RSA-260)
./gradlew integrationTest
```

### Run Factorization Ladder
```bash
# Run ladder with ZNeighborhood builder
./gradlew ladder

# Run RSA-260 factorization attempt
./gradlew rsa260

# Run BigDecimal performance demos
./gradlew demo
./gradlew demofull
```

### CLI Commands
```bash
# Run ladder benchmark
java -cp build/libs/z5d-0.0.1.jar tools.BenchLadder --ladder --builder ZNeighborhood

# Run RSA-260 attempt
java -cp build/libs/z5d-0.0.1.jar tools.BenchLadder --rsa260
```

Results are logged to `ladder_results.csv` and `test_output.log`.

---

## RSA Challenge Framework

Comprehensive test harness for RSA factorization challenges:

- **Factored Challenges:** RSA-100, RSA-129, RSA-155, RSA-250 with known factors
- **Integrity Validation:** Strict checks for p*q==N and primality
- **Adversarial Testing:** RSA-260 integration tests (enabled via `-Dintegration=true`)
- **CSV Diagnostics:** Self-diagnosing data mismatches with exact diffs

```java
// Validate RSA challenge
boolean valid = TestRSAChallenges.validFactorization(N, p, q);
```

---

## Factorization Ladder

Incremental benchmarking framework scaling from 200 to 260+ digits:

- **Semiprime Generation:** Balanced p,q pairs using Miller-Rabin primality
- **Candidate Testing:** Pluggable builders generate factorization candidates
- **Metrics Logging:** CSV output with success rates, timing, reduction percentages
- **Resumeable Execution:** Designed for long-running attempts

### Ladder Results (Sample)
| Digits | Builder | Candidates | Time (ms) | Success | Reduction % |
|--------|---------|------------|-----------|---------|-------------|
| 200    | ZNeighborhood | 10,002 | 5 | true | 30.1 |
| 210    | ZNeighborhood | 10,002 | 4 | true | 28.7 |
| ...    | ...     | ...   | ... | ... | ... |
| 260    | MetaSelection | 6,253 | 12 | false | 0.0 |

---

## Candidate Builders

Pluggable strategies for generating factorization candidates:

### ZNeighborhood
Builds candidates around √N with configurable spread.

### ResidueFilter
Filters candidates to specific residue classes (e.g., ≡3 mod 4).

### HybridGcd
Advanced filtering with modular constraints.

### MetaSelection
Combines multiple builders for optimal coverage.

```java
CandidateBuilder builder = new MetaSelection();
List<BigInteger> candidates = builder.build(N, 10000, seed);
```

### GVA (Geodesic Validation Assault)
Geometric factorization using torus embeddings and Riemannian distance with curvature.
Validates factors via proximity in high-dimensional manifold space.

```java
CandidateBuilder builder = new GVA();
List<BigInteger> candidates = builder.build(N, 10000, seed);
```Combines multiple builders for optimal coverage.

```java
CandidateBuilder builder = new MetaSelection();
List<BigInteger> candidates = builder.build(N, 10000, seed);
```

---

## BigDecimal / Ultra-High Scale

Extended support for computations beyond double precision limits:

- **Scale Range:** 10^306 to 10^1233+ with stable relative accuracy
- **Performance:** Sub-millisecond timings for ultra-high scales
- **Integration:** Z5D predictor for large-scale prime counting

### BigDecimal Timings (Sample)
- 10^306: ~2-3 ms
- 10^800: ~4 ms
- 10^1233: ~5-9 ms

```java
// Ultra-high scale prediction
String result = Z5dPredictor.z5dPrimeString("1e1233", 0, 0, 0, true);
```

---

## Benchmarks & Metrics

Comprehensive performance analysis:

- **Ladder Metrics:** Success rates, timing, candidate reduction
- **BigDecimal Sweep:** Timings across 10^100 to 10^2000 scales
- **CSV Logging:** `ladder_results.csv`, `z5d_performance_log.csv`
- **Plotting:** Python scripts generate performance visualizations

### Typical Results
- **Ladder Throughput:** ~500-1000 candidates/ms
- **BigDecimal Accuracy:** Within 10% of PNT baseline
- **Memory Efficient:** Handles 260+ digit numbers

---

## TRANSEC - Zero-Handshake Encryption

**Inspired by military frequency-hopping radio COMSEC (SINCGARS, HAVE QUICK)**, TRANSEC adapts time-synchronized key rotation to software-defined networking, eliminating handshake latency in tactical/industrial scenarios where zero-RTT encryption is required.

### Key Features

- **Zero-RTT Communication**: No handshake overhead after initial bootstrap
- **Time-Sliced Keying**: Deterministic key rotation based on time epochs
- **Military-Grade Design**: Adapted from TRANSEC/COMSEC paradigms
- **Sub-millisecond Latency**: ~0.3ms RTT for encrypted UDP packets
- **3,000+ msg/sec Throughput**: High-performance AEAD encryption

### Quick Start

```python
from transec import TransecCipher, generate_shared_secret

# Generate or provision shared secret
secret = generate_shared_secret()

# Create cipher instances
cipher = TransecCipher(secret, slot_duration=5, drift_window=2)

# Encrypt message (no handshake needed!)
packet = cipher.seal(b"Hello, TRANSEC!", sequence=1)

# Decrypt message
plaintext = cipher.open(packet)
```

### UDP Demo

```bash
# Terminal 1: Start server
python3 python/transec_udp_demo.py server

# Terminal 2: Run benchmark
python3 python/transec_udp_demo.py benchmark --count 100
```

**Benchmark Results** (localhost UDP):
- Success rate: 100%
- Average RTT: 0.34ms
- Throughput: 2,942 msg/sec

### Use Cases

- **Tactical Communications**: Drone swarms, battlefield mesh networks
- **Critical Infrastructure**: SCADA/power grid telemetry where TLS latency is unacceptable
- **Autonomous Systems**: V2V messaging, vehicle platoons
- **Edge Computing**: Low-latency IoT mesh networks
- **High-Frequency Trading**: Sub-millisecond encrypted market data feeds

### Documentation

- [TRANSEC Specification](docs/TRANSEC.md) - Full protocol specification with security model
- [Usage Guide](docs/TRANSEC_USAGE.md) - API reference, examples, and best practices
- [Test Suite](tests/test_transec.py) - Comprehensive test coverage (25 tests)
- [UDP Demo](python/transec_udp_demo.py) - Working client/server example

### Security Model

**Protected Against:**
- ✓ Passive eavesdropping (ChaCha20-Poly1305 AEAD)
- ✓ Replay attacks (sequence number tracking)
- ✓ Packet injection (authenticated encryption)
- ✓ Tampered messages (AEAD integrity verification)

**Tradeoffs (COMSEC model):**
- Shared secret compromise requires network-wide rekey (no forward secrecy without ratcheting)
- Requires time synchronization (±2 slots tolerance by default)
- Not suitable for long-term perfect forward secrecy use cases

**Best for:** Systems that prioritize zero-latency encryption over PFS, where handshake overhead is unacceptable (tactical, real-time control, autonomous systems).

---

## Tests

Comprehensive test suite:

- **RSA Validation:** Factored challenges with integrity checks
- **Factorization Testing:** Synthetic semiprimes across digit ranges
- **Builder Verification:** Candidate generation and filtering
- **BigDecimal Validation:** Ultra-high scale accuracy
- **Integration Tests:** RSA-260 attempts (opt-in)
- **TRANSEC Tests:** Encryption, replay protection, drift tolerance (25 tests)

```bash
# Run all tests
./gradlew test

# Run integration tests
./gradlew integrationTest

# Run specific test class
./gradlew test --tests "unifiedframework.TestRSAChallenges"

# Run TRANSEC tests
python3 tests/test_transec.py -v
```

---

## Continuous Integration

GitHub Actions workflow (`.github/workflows/ci.yml`) runs:
- Full test suite with coverage
- Integration tests
- Performance logging
- Artifact uploads for trend analysis

## Documentation

This section provides links to detailed documentation in the `docs/` folder, organized by category.

### TRANSEC (Time-Synchronized Encryption)
- [TRANSEC Specification](docs/TRANSEC.md): Full protocol specification with security model, threat analysis, and cryptographic primitives.
- [TRANSEC Usage Guide](docs/TRANSEC_USAGE.md): Complete API reference, examples, configuration options, and best practices.

### GVA (Geodesic Validation Assault) Research
- [GVA Mathematical Framework](docs/GVA_Mathematical_Framework.md): Formal mathematical foundations and algorithm overview for GVA factorization.
- [GVA Method Explanation](docs/GVA_Method_Explanation.md): Detailed explanation with examples, insights, and Z-normalized metrics for GVA performance.
- [GVA 128-bit Validation Report](docs/GVA_128bit_Validation_Report.md): Empirical validation results for 128-bit semiprime factorization using GVA.
- [Victory 128-bit Report](docs/victory_128bit_report.md): Summary of 128-bit GVA achievements and milestones.
- [Victory 64-bit Report](docs/victory_64bit_report.md): Report on 64-bit GVA factorization success.

### Breakthrough and Victory Reports
- [Victory Declaration](docs/victory_declaration.md): Official declaration of factorization victories across bit scales.
- [Victory Final Report](docs/victory_final_report.md): Comprehensive final report on all victory milestones.
- [40-bit Victory](docs/40bit_victory.md): Specific report on 40-bit factorization breakthrough.
- [Boundary Breakthrough Report](docs/boundary_breakthrough_report.md): Analysis of dissolving factorization boundaries with dynamic curvature.
- [Paradigm Shift Report](docs/paradigm_shift_report.md): Investigation into curved geometry revolution for factorization.

### Analysis and Metrics
- [Balanced Analysis Report](docs/balanced_analysis_report.md): Statistical analysis of balanced semiprime factorization.
- [Curved Space Analysis](docs/curved_space_analysis.md): Testing boundary solutions in curved geometric spaces.
- [40-bit Detailed Metrics](docs/40bit_detailed_metrics.md): Detailed metrics and test results for 40-bit manifold assaults.
- [Research Update 60-bit](docs/research_update_60bit.md): Updates on 60-bit unbalanced semiprime factorization.

### Validation and Resolution
- [Validation Summary](docs/VALIDATION_SUMMARY.md): Comprehensive summary of validation processes and results.
- [PR25 Contradiction Resolution](docs/PR25_Contradiction_Resolution.md): Resolution of contradictions in pull request #25.
- [Resolution Complete](docs/RESOLUTION_COMPLETE.md): Final overview of resolved issues and contradictions.

### Frameworks and Goals
- [GOAL.md](docs/GOAL.md): Project goals, directives, and mathematical foundations.
- [Final Framework Report](docs/final_framework_report.md): Report on the complete curved manifold framework.
- [Final Revolution Report](docs/final_revolution_report.md): Summary of the Copernican revolution in geometric factorization.

### Z5D and BigDecimal
- [Z5D Documentation](docs/z5d_documentation.md): Documentation for Z5D prime predictor and enhancements.
- [Z5D Integration Report](docs/z5d_integration_report.md): Report on Z5D integration and paradigm shifts.
- [BigDecimal Upgrade](docs/BIGDECIMAL_UPGRADE.md): Upgrades and enhancements for BigDecimal support.

### Security and Testing
- [Security](docs/SECURITY.md): Security considerations and measures.
- [Test RSA](docs/test-RSA.md): RSA challenge testing documentation.

### Miscellaneous
- [GROK.md](docs/GROK.md): AI-assisted research notes and insights.
- [Literature Assessment](docs/LITERATURE_ASSESSMENT.md): Assessment of relevant literature.
- [Multi Z5D Variants](docs/MultiZ5DVariants.md): Exploration of multiple Z5D predictor variants.
- [256-bit Test Setup Documentation](docs/256bit_test_setup_documentation.md): Setup guide for 256-bit GVA testing.
- [Reproducibility Steps](docs/reproducibility_steps.md): Steps for reproducing benchmark results.

---

---

## Core Mathematics
## Geodesic Validation Assault (GVA)n
n
A geometry-driven factorization method for balanced semiprimes, leveraging Riemannian distance on torus embeddings.n
n
### Mathematical Basisn
GVA embeds numbers into a d-dimensional torus using iterated fractional parts modulated by the golden ratio φ. Factors are detected by proximity in embedding space.n
n
**Key Components:**n
- **Embedding:** θ(n) = iterative frac(n / e² * φ^k)n
- **Distance:** Riemannian metric with curvature κ = 4 ln(N+1)/e²n
- **Search:** A*/parallel offset search from √Nn
- **Validation:** Accept if dist(θ(N), θ(p)) < ε or dist(θ(N), θ(q)) < εn
n
### Algorithm Overviewn
1. Compute emb_N = embed(N)n
2. For d in [-R, R] (parallel/A*):n
   - p = √N + dn
   - If p divides N and p,q prime and balanced:n
     - If dist < ε: return p,qn
n
### Scaling Results
- **64-bit:** 12% success on 100 samples
- **128-bit:** 16% success on 100 samples (VERIFIED)

n
### Pseudocoden
```pythonn
def embed(n, dims=11):n
    k = 0.5 / log2(log2(n+1))n
    x = n / exp(2)n
    coords = [frac(phi * frac(x / phi)**k) for _ in range(dims)]n
    return coordsn
n
def dist(coords1, coords2, N):n
    kappa = 4 * log(N+1) / exp(2)n
    return sqrt(sum((min(abs(c1-c2), 1-abs(c1-c2)) * (1 + kappa * delta))**2 for c1,c2,delta in zip(coords1, coords2, deltas)))n
n
def gva_factorize(N):n
    # Parallel/A* search implementationn
    passn
```n
n
### Referencesn
- Torus embeddings for number theoryn
- Riemannian geometry applications in cryptographyn

### Z5D Prime Predictor
The Z5D predictor estimates the k-th prime number (pₖ) using an enhanced Prime Number Theorem (PNT) approximation:

**Base PNT Formula:**
```
π(k) ≈ li(k) = ∫₂ᵏ dt/ln(t)
```

**Z5D Enhancement:**
```
p̂ₖ ≈ π⁻¹(k) + D(k) + E(k)
```
Where:
- **π⁻¹(k)**: Inverse prime counting function (PNT-based)
- **D(k)**: Dilation correction term
- **E(k)**: Curvature correction term
- **Auto-calibration:** Adaptive parameters (c, k*, κ) selected by scale

**Accuracy:** Relative error ~10^-4 at reference points, stable across 10^5 to 10^305 scales.

### FactorizationShortcut
Leverages mathematical properties for efficient factorization candidate generation:

**Key Insight:** For semiprime N = p × q, factors cluster around √N with predictable distributions.

**Shortcut Methods:**
- **Z-Neighborhood:** Generate candidates in [√N - δ, √N + δ] range
- **Residue Filtering:** Apply modular constraints (e.g., ≡3 mod 4) to reduce search space
- **Hybrid Approaches:** Combine multiple mathematical filters for optimal reduction

**Effectiveness:** Achieves 99%+ capture rates with 20-30x search space reduction on 200-260 digit semiprimes.

---

## Design Notes

- **Modular Architecture:** Pluggable builders and extensible metrics
- **Balanced Semiprimes:** Realistic factorization targets using Miller-Rabin primality
- **Performance Focus:** Optimized for benchmarking large-scale attempts
- **BigDecimal Integration:** Seamless ultra-high scale support for mathematical computations

---

## Limits & Caveats

- **Synthetic Testing:** Ladder uses generated semiprimes, not real RSA moduli
- **Builder Limitations:** Current builders insufficient for RSA-260 factorization
- **Memory Scaling:** Large candidate sets require appropriate heap sizing
- **BigDecimal Overhead:** Performance trade-off for arbitrary precision

---

## Roadmap

- **Advanced Builders:** Implement lattice-based and mathematical constant strategies
- **Checkpointing:** Add resume capability for interrupted long runs
- **Parallel Processing:** Multi-threaded candidate generation
- **Real RSA Integration:** Support for actual RSA challenge moduli
- **Performance Optimization:** Further reduce per-candidate overhead

---

## License

[MIT License](LICENSE)


## 128-bit GVA Scaling Progress

The Python-based Geodesic Validation Assault (GVA) has been successfully scaled to 128-bit balanced semiprimes:

### Implementation
- **Algorithm:** Torus embedding with golden ratio (φ) and adaptive curvature
- **Dimensions:** 9-dimensional torus for 128-bit scale
- **Parameters:** Adaptive k = 0.3 / log₂(log₂(n+1)), threshold ε = 0.2 / (1 + κ)
- **Search:** True geometry-guided: computes Riemannian distances for all candidates in [-R, R] before divisibility checks, ranks by distance ascending, tests modulus on top-K (K=256) closest

### Test Results (100 samples with spread primes)
- **Success Rate:** 5% (5/100 factorizations successful)
- **Average Time:** 0.44s per sample
- **False Positive Rate:** 0%
- **Prime Generation:** Uses spread primes with offsets up to 10^9 (non-trivial targets)

### Key Findings
- Success rate drops from 16% (close primes) to 5% (spread primes), confirming GVA's sensitivity to prime proximity
- Successful samples have geometric distance < 0.0015, well below threshold ε ≈ 0.004143
- All 5 successful factorizations completed in < 0.22s
- **Milestone Status:** ✓ VERIFIED (>0% success rate achieved on genuinely balanced semiprimes)

### Documentation
- See [victory_128bit_report.md](docs/victory_128bit_report.md) for detailed analysis
- See [GOAL.md](GOAL.md) for theoretical framework and future directions
- Test suite: `tests/test_gva_128.py`
- Implementation: `python/manifold_128bit.py`

### Running the Tests
```bash
cd /home/runner/work/z-sandbox/z-sandbox
PYTHONPATH=python python3 tests/test_gva_128.py
```
