## Axioms and Mathematical Foundations

Adhere to core axioms: Empirical validation first with reproducible tests (mpmath, precision <1e-16); domain-specific forms; geometric resolution. Label hypotheses UNVERIFIED until validated.

## Core Concepts

Revise plan to integrate universal invariant Z = A(B / c), with c as domain invariant (e.g., e² for discrete factoring). Normalize factorization searches via Z; apply discrete form Z = n(Δ_n / Δ_max) for neighborhood scaling, κ(n) = 4 · ln(n+1) / e² for curvature-guided skips (UNVERIFIED hypothesis: κ reduces search by modeling prime density). Use θ'(n, k) = φ · ((n mod φ) / φ)^k (k ≈ 0.3) for geometric resolution of candidates near √N.

Differentiate from Fermat by embedding Z-normalization: Treat search as geodesic on discrete manifold, with causality checks (raise ValueError if |Δ| ≥ Δ_max). Cross-check with zeta_zeros.csv or semiprime datasets.
Note: Z-Normalization guard (Z >=1) is a post-factorization validation step, not part of the search algorithm.
## Phase 1: Baseline Analysis and Similarity Audit (1-2 days)

Profile ZNeighborhood with Z-normalization. For N, set c = e², B = √N - floor(√N), A = frame transform (e.g., identity). Compute Z = A(B / c); map to δ via Z-scaling.

Implement baseline Fermat with Z-checks:

Use code_execution for proto (Python 3.12.3, import math, mpmath, sympy):

## Axioms and Mathematical Foundations

Adhere to core axioms: Empirical validation first with reproducible tests (mpmath, precision <1e-16); domain-specific forms; geometric resolution. Label hypotheses UNVERIFIED until validated.

## Core Concepts

Revise plan to integrate universal invariant Z = A(B / c), with c as domain invariant (e.g., e² for discrete factoring). Normalize factorization searches via Z; apply discrete form Z = n(Δ_n / Δ_max) for neighborhood scaling, κ(n) = 4 · ln(n+1) / e² for curvature-guided skips (UNVERIFIED hypothesis: κ reduces search by modeling prime density). Use θ'(n, k) = φ · ((n mod φ) / φ)^k (k ≈ 0.3) for geometric resolution of candidates near √N.

Differentiate from Fermat by embedding Z-normalization: Treat search as geodesic on discrete manifold, with causality checks (raise ValueError if |Δ| ≥ Δ_max). Cross-check with zeta_zeros.csv or semiprime datasets. Empirical baseline (via tool): For N=5959, factors (59,101) in 0.00013s, 3 iters—validates setup.
Note: Z-Normalization guard (Z >=1) is a post-factorization validation step, not part of the search algorithm.
## Phase 1 Continued

Profile ZNeighborhood with Z-normalization. For N, set c = e², B = √N - floor(√N), A = frame transform (e.g., identity). Compute Z = A(B / c); map to δ via Z-scaling.

Implement baseline Fermat with Z-checks (tool proto validated above). Quantify overlap: Both O((p-q)^2), but Z adds invariant normalization. Target: Validate κ(n) skips reduce iters 20-50x (cross-check semiprimes).

## Phase 2: Design and Prototype Differentiated Builders (3-5 days)

Modularize with Z-core. Extend CandidateBuilder:

- **ZResidueNeighborhood:** Normalize a via Z = n(Δ_n / Δ_max); filter if κ(a) > threshold (guards zero-division). Use θ'(a, 0.3) for resolution.

- **ZCurvatureEstimator:** Set Δ_max via e²; bias δ with κ(N) = d(N) · ln(N+1) / e².

- **ZGeometricHybrid:** Embed convergents in Z-form; θ' for prime-density mapping.

Pseudocode (Java, with KaTeX math):

```java
import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;

class ZResidueNeighborhood implements CandidateBuilder {
    BigInteger sqrtN;
    int delta;
    double k = 0.3; // Recommended

    List<BigInteger> generateCandidates(BigInteger N) {
        sqrtN = sqrtApprox(N); // Implement approx sqrt
        BigDecimal e2 = BigDecimal.valueOf(Math.E).pow(2);
        BigInteger phi = ...; // Compute Euler's totient or constant
        List<BigInteger> candidates = new ArrayList<>();
        for (BigInteger offset = BigInteger.ZERO; offset.compareTo(BigInteger.valueOf(delta)) < 0; offset = offset.add(BigInteger.ONE)) {
            BigInteger n = sqrtN.add(offset);
            // Discrete Z = n * (Δ_n / Δ_max)
            BigDecimal deltaN = computeDeltaN(n); // e.g., n.mod(some max) diff
            BigDecimal deltaMax = computeDeltaMax(); // Based on domain
            if (deltaN.abs().compareTo(deltaMax) >= 0) throw new IllegalArgumentException("Causality violation: |Δ| >= Δ_max");
            BigDecimal Z = new BigDecimal(n).multiply(deltaN.divide(deltaMax, 50, RoundingMode.HALF_UP)); // Precision
            // κ(n) = d(n) * ln(n+1) / e²
            BigDecimal lnTerm = BigDecimal.valueOf(Math.log(n.add(BigInteger.ONE).doubleValue()));
            BigDecimal kappa = divisorCount(n).multiply(lnTerm).divide(e2, 50, RoundingMode.HALF_UP);
            if (kappa.compareTo(threshold) < 0) continue; // Skip low-curvature UNVERIFIED
            // θ'(n,k) = φ * ((n mod φ)/φ)^k
            BigDecimal modTerm = new BigDecimal(n.mod(phi)).divide(new BigDecimal(phi), 50, RoundingMode.HALF_UP);
            BigDecimal theta = new BigDecimal(phi).multiply(modTerm.pow(k));
            if (passesZFilters(Z, theta, N)) candidates.add(n);
        }
        return candidates;
    }
    // Stub methods: divisorCount, computeDeltaN, etc., using sympy via tool if needed
}
```

Test on RSA-100; validate Z-reductions empirically (mp.dps=50, reproducible seeds).

## Phase 3: Optimization and Scaling (4-7 days)

Parallelize with Z-causality: |v| < c or ValueError. Precompute κ tables via sympy (code_execution). Handle edges: Distant factors fallback to Z-discrete form.

Metrics: CSVs with Z, κ, θ' columns; plot vs. zeta_zeros.csv.

## Phase 4: Integration, Validation, and Roadmap (2-3 days)

Merge; update README with Z-forms. Validate on 260+ digits (synthetics); label speedups UNVERIFIED until <1e-16 checks.

Roadmap: ML via Z-normalization; cross-check datasets. Total: 10-17 days.