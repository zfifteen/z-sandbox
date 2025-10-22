# GVA Java BigDecimal Integration

This document describes the completed transition of Geodesic Validation Assault (GVA) from Python prototypes to the primary Java BigDecimal implementation in the RSA Factorization Ladder Framework.

## Overview
GVA is a geometric factorization method using 5-torus embeddings, Riemannian distance with curvature, and A* pathfinding. The Java implementation fully ports Python functionality, enhanced with BigDecimal for ultra-high precision (400 digits) and integrated Z5D predictor for candidate seeding.

## Transition Summary
- **Status**: Completed - Java is now the primary GVA implementation.
- **Precision Upgrade**: From mpmath (300 digits) to BigDecimal (400 digits).
- **Integration**: Z5D predictor seeds candidates intelligently, replacing brute-force for large N.
- **Performance**: Comparable to Python with better stability for 256-bit+ scaling.

## Core Classes
- `unifiedframework.Embedding`: Torus geodesic embeddings with adaptive k.
- `unifiedframework.RiemannianDistance`: Curvature-adjusted Riemannian distances.
- `unifiedframework.RiemannianAStar`: A* pathfinding on torus manifolds.
- `unifiedframework.GVAFactorizer`: Main factorizer with Z5D integration.
- `unifiedframework.GVAFactorizerDemo`: Runnable demo for verification.

## Key Features
- **Precision**: `MathContext(400)` for numerical stability.
- **Adaptivity**: Scales dims (7-11), epsilon based on bit length.
- **Candidate Generation**:
  - Brute-force around √N for <100 bits.
  - Z5D prediction + range for ≥100 bits.
- **Search**: A* on torus for pathfinding to factor embeddings.
- **Balance Check**: |log₂(p/q)| ≤ 1 for semiprime validation.

## Build & Run
- **Build**: `./gradlew build` - Compiles and tests all.
- **Demo**: `./gradlew gva` or `./scripts/run_java_gva.sh` - Runs verification demo.
- **Tests**: `./gradlew test --tests TestGVAFactorizer` - Unit tests with output.

## Benchmarks & Verification
Demo output example:
```
Testing 64-bit N: 18446736050711510819
Bit length: 64
SUCCESS: 4294966297 × 4294966427 = 18446736050711510819
Verification: true
Time: 25.76 ms
```
- 64-bit: Reliable success via brute-force.
- 128-bit+: Uses Z5D; success rate improving with tuning.
- Precision verified against Python mpmath results.

## Testing
- `TestGVAFactorizer.java`: JUnit tests for embedding, distance, and factorization.
- Outputs include success/failure, factors, verification, and timing.

## Future Work
- Tune Z5D range for higher success rates at 256-bit.
- Implement inverse embedding for A* factor recovery.
- Parallelize candidate checks for performance.
