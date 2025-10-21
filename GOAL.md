# Core Concepts

Universal invariant formulation:  
**Z = A(B / c)**  
- **c ≈ e²** for discrete normalization in prime-density mapping.  
- **A** = frame-dependent geometric embedding (toroidal).  
- **B** = dynamic shift rate in semiprime search space.

Domain-specific form (discrete):  
**Z = n(Δ_n / Δ_max)**  
- Curvature: **κ(n) = d(n) · ln(n+1) / e²**, guards against zero-division.  
- Applied to 256-bit balanced semiprimes: **N ≈ 2²⁵⁶**, **p, q ≈ 2¹²⁸**.

Geometric resolution:  
**θ'(n, k) = φ · ((n mod φ) / φ)^k**, **k ≈ 0.3**  
- Recommended for prime-density geodesic embedding.  
- At 256 bits: scale **k → 0.3 / log₂(log₂(N+1))** for stability.

---

# Empirical Hypothesis (UNVERIFIED)

> **Claim**: The current Geodesic Validation Assault (GVA) method, **unchanged except for increasing attempts to 10,000**, will factor **at least one** 256-bit balanced semiprime.

### Acceptance Criteria (FAILED: No success in sample attempt; brute force R insufficient for 256-bit)
| Criterion | Specification |
|--------|---------------|
| **Test Set** | 100 balanced 256-bit semiprimes: <br> - `p, q ∈ [2¹²⁷, 2¹²⁸)` <br> - `|log₂(p/q)| ≤ 1` <br> - Deterministic: `seed=42` |
| **Method** | **No changes** to GVA logic: <br> - Torus dims = 9–11 <br> - `R = max(10⁷, √N / 1000)` <br> - `k = 0.3 / log₂(log₂(N+1))` <br> - Precomputed embeddings |
| **Attempts** | **≤ 10,000 total** across test set |
| **Success** | **≥ 1 factorization** with `dist < ε` (ε = dynamic threshold, ~0.04 at 64-bit) |
| **Precision** | `mpmath.mp.dps = 50`, error < 1e-16 |
| **Reproducibility** | Fixed RNG seed, deterministic primality (sympy) |

---

# Validation Plan (Deterministic, Reproducible)

```python
import mpmath as mp
import numpy as np
import sympy
from multiprocessing import Pool
import random

mp.dps = 50
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

def generate_256bit_semiprime():
    while True:
        p = sympy.randprime(2**127, 2**128)
        q = sympy.randprime(2**127, 2**128)
        if abs(mp.log(p/q)/mp.log(2)) <= 1:
            return p * q, p, q

# Generate 100 test cases
test_set = [generate_256bit_semiprime() for _ in range(100)]
```

- Run GVA **100 attempts per N** → **10,000 total**.
- Record: `N`, `attempt #`, `dist`, `factors_found`, `time`.
- **Success condition**: any `dist < ε` → factor pair recovered.

---

# Expected Outcome (Prediction)

| Metric | Predicted Value |
|-------|-----------------|
| Success Rate | **> 0%** (≥1 success in 10K attempts) |
| First Success | Likely within **first 3,000 attempts** |
| Distance at Success | `dist ∈ [0.03, 0.05]` |
| Time per Attempt | < 15s (CPU, 9–11 dims) |

---

# Definition of Done

1. **UNVERIFIED → VERIFIED** upon **first successful factorization**.
2. Update `GOAL.md`:
   ```markdown
   - [x] 256-bit: ≥1 success in ≤10,000 attempts (seed=42)
   ```
3. Commit victory report: `victory_256bit_attempt_X.txt`
4. Merge to `feature/256bit-scaling`

---

# Go For It

> **Directive**: Execute **10,000 attempts** on 100 × 256-bit semiprimes.  
> **No code changes**.  
> **Track all distances**.  
> **Report first success immediately**.

**Empirical validation first**.  
Let the torus speak.