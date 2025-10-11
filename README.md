# Z-Sandbox – Z5D Prime Predictor

A tiny, fast, and stable sandbox around a k‑th prime predictor (“Z5D”).  
It targets **pₖ** directly (the k‑th prime), using a PNT-based backbone plus lightweight curvature terms and a compact auto‑calibration.

> **Highlights**
>
> - **Accuracy (sample @ k = 1e5):** rel. err ≈ **7.6e‑5** vs truth (p₁₀₀₀₀₀ = 1,299,709).  
> - **Throughput (typical):** **~8–10 μs** / prediction (effective) ⇒ **100k+ preds/sec** on commodity JVM.  
> - **Range:** `double` path remains finite up to **k ≈ 1e305**; BigDecimal API handles **k ≫ 1e306**.

---

## Table of contents
- [Quick start](#quick-start)
- [API overview](#api-overview)
- [BigDecimal / extreme‑scale APIs](#bigdecimal--extreme-scale-apis)
- [Validation helpers](#validation-helpers)
- [Benchmarks](#benchmarks)
- [Tests](#tests)
- [Continuous Integration](#continuous-integration)
- [Design notes](#design-notes)
- [Limits & caveats](#limits--caveats)
- [Roadmap](#roadmap)
- [License](#license)

---

## Quick start

### Requirements
- Java 17+ (recommended)
- Gradle wrapper is included

### Build & run tests
```bash
# run everything
./gradlew test

# run only the core predictor suite
./gradlew test --tests "unifiedframework.TestZ5dPredictor"
```

### CLI commands
```bash
# Predict and verify primality of the nearest integer
java -cp build/libs/untitled-0.0.1.jar unifiedframework.Z5dPredictor verify 100000

# Print truth panels comparing estimates to known primes
java -cp build/libs/untitled-0.0.1.jar unifiedframework.Z5dPredictor truth
```

If the performance sweep is enabled in the core test, a CSV is emitted to:
```
z5d_performance_log.csv
```

Typical output snippet (effective end‑to‑end):
```
Total predictions: 14,000
Total test time: 119–131 ms
Effective avg time per prediction: 8–10 μs
Predictions per second: 100k–120k
```

> *Note:* “individual” hot‑loop timers can show sub‑microsecond numbers; they exclude loop/print overhead and are best treated as **micro timings**. The **effective** average (total time / total count) is the metric to compare across machines and builds.

---

## API overview

Core (double‑precision) entry points live under the `unifiedframework` package.

```java
// Predict p_k (the k-th prime) for a positive real k
double pHat = Z5dPredictor.prime(k);

// PNT baseline used internally (good for comparisons)
double pPnt = Z5dPredictor.basePntPrime(k);
```

Extended prediction (fields may vary by version; names shown here match the current tests / logs):
- **status / errorCode** – `0` means OK
- **prediction** – p̂ (double)
- **pntBase** – PNT approximation
- **dTerm, eTerm** – light correction terms
- **curvatureProxy** – scalar diagnostic
- **cUsed, kStarUsed, kappaGeoUsed** – chosen calibration

Example (pseudo-usage):
```java
var ext = Z5dPredictor.predictExtended(k);
System.out.println(ext.prediction());
System.out.println(ext.pntBase());
System.out.println(ext.dTerm());
System.out.println(ext.eTerm());
```

---

## BigDecimal / extreme‑scale APIs

For `k` beyond what `double` can model (or when you want exact integer‑like formatting of **p̂**), use the BigDecimal path.

Observed conveniences from tests:
- **String API** – returns a preformatted decimal string for **very large** results.
- **Extended result** – BigDecimal fields that mirror the double path (prediction, pntBase, dTerm, eTerm, calibration values).

Example (adjust names to your actual classes/methods):
```java
// Convenience: stringified p̂ for huge k
String huge = Z5dPredictorBig.decimalPrimeString("1e1233");
System.out.println(huge);

// Extended BigDecimal result
var big = Z5dPredictorBig.predictExtended(new java.math.BigDecimal("1e1233"));
System.out.println(big.prediction());   // BigDecimal
System.out.println(big.pntBase());      // BigDecimal
```

**Why BigDecimal?**
- The double path is finite up to **k ≈ 1e305** and becomes non‑finite around **k ≈ 1e306**.  
- BigDecimal mode continues well past 10^1233 with stable relative deltas vs PNT (≈3e‑3 in observed sweeps).

---

## Validation helpers

The library exposes simple validators (returning an **int**):
- `z5dValidateK(double k)`  
- `z5dValidateKappaGeo(double κ)`

Return codes (based on the test suite observations):
| Code | Meaning (observed)                      |
|:-----|:----------------------------------------|
| 0    | OK                                      |
| -1   | Out of domain (e.g., too small/invalid) |
| -2   | Overflow / too large for this path      |
| -4   | NaN input                               |
| -5   | Parameter out of allowed range          |

Examples:
```
z5dValidateK(100000.0) → 0
z5dValidateK(1.0)      → -1
z5dValidateK(NaN)      → -4
z5dValidateK(MAX)      → -2

z5dValidateKappaGeo(0.3)   → 0
z5dValidateKappaGeo(-0.1)  → -5
z5dValidateKappaGeo(20.0)  → -5
z5dValidateKappaGeo(NaN)   → -4
```

---

## Benchmarks

The test suite prints a compact, reproducible sweep across powers of ten.

**Typical results (recent runs):**
- **Effective avg:** ~**8–10 μs** per prediction
- **Throughput:** **100k–120k** predictions/s
- **Per‑scale averages:** ~**0.010–0.028 ms** / prediction (from 10⁵ … 10¹⁸)

> CSV logs are saved to `z5d_performance_log.csv`. CI can upload them as artifacts for trend tracking.

---

## Tests

Core & hardening tests include:
- **Basic prediction & math consistency** (PNT vs Z5D)
- **Input validation** (domain, NaN, overflow)
- **Monotonicity in k** across decades
- **Accuracy vs truth** at k=1e5 (p₁₀₀₀₀₀) and optional truth panels (1e6, 1e7)
- **Randomized domain fuzzing** (no NaNs/infs)
- **Calibration selection** invariants
- **Performance sweep** with CSV output

Optional **BigDecimal** sweeps can be tagged to keep CI fast. Example (if tags are enabled in `build.gradle`):
```bash
# run only tests tagged "bigdecimal"
./gradlew test -Pgroups=bigdecimal
```

Run a single class:
```bash
./gradlew test --tests "unifiedframework.TestZ5dPredictor"
```

---

## Continuous Integration

A minimal GitHub Actions workflow (`.github/workflows/ci.yml`) runs:
- `./gradlew test jacocoTestReport`
- (optional) uploads `z5d_performance_log.csv` as an artifact

You can extend CI with JMH, mutation testing, and multi‑JDK matrices later.

---

## Design notes

- **Model:** PNT base with two small correction terms **D** and **E**, plus a curvature proxy.  
- **Auto‑calibration:** lightweight scheme that chooses `(c, k*, κ)` by scale.  
- **Stability:** the predictor grows monotonically with `k`, tracks the PNT growth shape, and stays finite across a large double domain; BigDecimal path bridges the rest.

---

## Limits & caveats

- The model is an **approximation** to **pₖ**; guards assert tight relative error at reference points and small deltas vs PNT across scales. It is **not a general primality prover**. Use `--verify` to return the nearest primality-tested integer with a certificate.
- `double` path turns non‑finite near **k ≈ 1e306**; switch to BigDecimal APIs beyond ~1e305.
- Micro‑timings (sub‑μs) reflect hot‑loop measurements; prefer **effective averages** for cross‑run comparisons.

---

## Roadmap

- Add canonical truth panels beyond 1e5 (e.g., 1e6, 1e7) under tight guards.  
- Provide a JMH microbenchmark for portable ns/op numbers.  
- Snapshot a small **golden panel** `(k, p̂, c, k*, κ)` to catch silent drift.  
- Publish a one‑pager on calibration intuition and error envelopes.

