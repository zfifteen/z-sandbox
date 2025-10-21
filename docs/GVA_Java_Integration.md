# GVA Java Integration

This document describes the integration of Geodesic Validation Assault (GVA) into the Java RSA Factorization Ladder Framework.

## Overview
GVA is a geometric factorization method using torus embeddings and Riemannian distance with curvature. The Java implementation mirrors the Python proofs, adapted for Java's BigDecimal precision and BigInteger handling.

## Classes
- `gva.Embedding`: Handles torus geodesic embeddings.
- `gva.RiemannianDistance`: Computes curvature-adjusted distances.
- `gva.GVAFactorizer`: Core factorizer implementing `CandidateBuilder`.
- `tools.BenchLadder.GVA`: Wrapper for integration.

## Key Features
- **Precision**: Uses `MathContext(200)` for high accuracy.
- **Adaptivity**: Scales dims, epsilon based on bit length (7 for 64-bit, 9 for 128-bit).
- **Parallelization**: ExecutorService for concurrent factor checks.
- **Integration**: Added to BenchLadder as a candidate builder.

## Benchmarks
- Initial tests on small semiprimes show promise.
- Full 100-sample benchmarks for 64/128-bit pending after testing.

## Testing
Run `TestGVA.java` for validation.

## Future Work
- Optimize embedding calculations.
- Add A* search for better guidance.
- Compare performance against Python.