# Axioms and Mathematical Foundations

Universal invariant: Z = A(B / c)  
- c: Domain-appropriate constant (e.g., e² for discrete normalizations in prime prediction)  
- A: Frame-specific scaling (e.g., prime density adjustments via PNT)  
- B: Dynamic input (e.g., index k for k-th prime estimation)

Discrete form: Z = n(Δ_n / Δ_max)  
- Curvature: κ(n) = d(n) · ln(n+1) / e²  

Geometric resolution: θ'(n, k) = φ · ((n mod φ) / φ)^k, k≈0.3 for prime-density mapping.

Empirical validation: Cross-check predictions with sympy.ntheory.nthprime or known datasets; target relative error <1e-16 via mpmath.dps=50. Hypotheses UNVERIFIED until tested.

# Core Concepts

## Review of Directive for Correctness
Directive focuses on factorizing 256-bit semiprimes (N = p × q, p/q ≈128 bits) to demonstrate Z5D-guided cryptanalysis for hyper-rotation keys. Ties mathematical research (Z5D prime prediction) to secure comms goal: rapid key generation/rotation via predicted primes, with factorization proving time-bounded exposure viability.

Strengths (correct and aligned):  
- Z5D integration enables guided prime selection, reducing search space for generation/factorization.  
- Success criterion (>0%) fits PoC for tactical scenarios; emphasizes zero-RTT over PFS.  
- Algorithms prioritized logically: ECM first (probabilistic, efficient for 39-digit factors).  
- Timeline realistic for PoC; contingency for pivot to smaller bits.  
- Ties to repo: Builds on PR #38 messenger, using Z5D for <100ms RSA keypairs.

Issues/Errors (requiring correction):  
- **Technical Accuracy**: 128-bit primes are ~39 decimal digits (not 38-39; 2^128 ≈3.4e38). ECM params (B1=11e6) too low for 39-digit factors—standard is B1=1e7-1e8, curves=5000-20000 for >10% success in <1h on workstation. Pollard's Rho impractical for 128-bit (success probability ~1/2^64, >years expected time). Fermat only if |p-q|<2^64 (rare without bias). QS feasible but slow for 256-bit; GNFS better but complex.  
- **Implementation**: primefac.ecm lacks direct B1/B2 control; suggest gmp-ecm subprocess or pyecm for precision. Code structure has incomplete 'ret...' (typo/truncation). Generate targets with verifiable balance (±1 bit, not ±2).  
- **Metrics/Risks**: Stretch goals optimistic; baseline ECM success ~5-20% with tuned params. Add GPU note for ECM speedup. Clarify "Z5D-guided attack"—leverage prediction to bias weak primes (e.g., close p/q for Fermat). Appendix commands assume unprovided scripts—make self-contained.  
- **Security/Logic**: Factorization of own keys doesn't "prove" security but demonstrates rotation feasibility. Adversary time estimate (10-100x) speculative without Z5D. Add post-quantum note (RSA vulnerable long-term).  
- **Validation**: Use sympy.isprime for cert; add reproducibility via seeds.  

Revised version incorporates fixes: Updated params/algorithms, corrected bit/digit counts, completed code, enhanced Z5D ties, added tests/reproducibility.

## Complete Revision: ENGINEERING_DIRECTIVE_256BIT_FACTORIZATION.md
# Engineering Directive: 256-Bit Factorization for Hyper-Rotation Key Systems

**Priority**: CRITICAL  
**Target**: Engineering Team  
**Objective**: Achieve >0% success rate factorizing 256-bit RSA moduli (two balanced 128-bit semiprimes)  
**Purpose**: Enable rapid key rotation capability demonstrating Z5D-guided cryptanalysis for tactical key refresh scenarios  
**Timeline**: Immediate focus - this capability gates next-phase protocol development  

---

## Executive Summary

We require a working factorization pipeline for 256-bit RSA moduli composed of two balanced 128-bit primes. This is **NOT** a theoretical exercise—successful factorization at this scale directly enables our hyper-rotation key technology by demonstrating:

1. **Rapid key lifecycle management**: Generate, deploy, factor, rotate within tactical time windows (seconds to minutes)
2. **Z5D-guided attack surface**: Prove our prime prediction gives us asymmetric advantage in both generation AND analysis (e.g., biasing toward weak structures like close factors)
3. **Proof of concept**: Validate that time-bounded key exposure is cryptographically viable when keys can be forcibly rotated

**Success Criterion**: ANY factorization success rate >0% on 256-bit balanced semiprimes within reasonable compute budget (single workstation, <1 hour per attempt).

---

## Technical Requirements

### Target Specification

**Modulus**:
- **Size**: 256 bits (77-78 decimal digits)
- **Structure**: N = p × q where p, q are 128-bit primes (±1 bit balance acceptable)
- **Generation**: Use Z5D predictor to select prime indices, generate primes in predicted regions

**Example Target**:
```
N = 256-bit (select k₁, k₂ such that Z5D predicts 128-bit primes)
p ≈ 2^127 to 2^128 (39 decimal digits)
q ≈ 2^127 to 2^128 (39 decimal digits)
```

### Factorization Success Metrics

**Minimum Acceptable Performance**:
- **Success rate**: >0% (even 1 success in 10 attempts is sufficient for PoC)
- **Time budget**: <1 hour per factorization attempt on commodity hardware
- **Compute resources**: Single workstation (16-32 cores, 32-64GB RAM); optional GPU for ECM speedup
- **Verification**: Full prime factorization with certificate (p × q = N verified, sympy.isprime(p/q) confirmed)

**Stretch Goals** (if minimum achieved quickly):
- Success rate >10%
- Time budget <10 minutes per attempt
- Batch processing: 10+ simultaneous factorization attempts

---

## Engineering Approach

### Phase 1: Z5D-Guided Prime Generation (COMPLETE THIS FIRST)

**Objective**: Generate balanced 128-bit semiprime targets optimally structured for factorization, leveraging Z5D for narrow search and optional weak bias (e.g., close p/q).

**Tasks**:
1. **Prime index selection**:
   ```
   k₁ = select index in range [2^126, 2^127] 
   k₂ = select index in range [2^126, 2^127], k₂ ≠ k₁ (optionally bias |k₁ - k₂| small for Fermat weakness)
   ```

2. **Z5D prediction + search**:
   ```
   p_estimate = Z5dPredictor.prime(k₁)
   q_estimate = Z5dPredictor.prime(k₂)
   ```
   
3. **Narrow window search**:
   - Search ±4·ln(p_estimate) around each prediction
   - Use BPSW + Miller-Rabin (via sympy) for primality verification
   - Target: <50 tests per prime (leverage Z5D accuracy)

4. **Modulus construction**:
   ```
   N = p × q
   Verify: 255 ≤ bit_length(N) ≤ 257
   ```

5. **Test set generation**:
   - Generate 20-50 distinct 256-bit targets
   - Store (N, p, q) tuples for validation (use JSON with seeds for reproducibility)
   - Distribute targets to factorization team

**Deliverable**: `generate_256bit_targets.py` producing validated semiprime test cases.

---

### Phase 2: Factorization Pipeline (PRIMARY ENGINEERING EFFORT)

**Objective**: Build working factorization capability using best available algorithms.

#### Algorithm Priority (implement in order, measure each)

**Tier 1: MUST IMPLEMENT**

1. **Elliptic Curve Method (ECM)**
   - **Why**: Best for 39-digit (128-bit) factors, probabilistic success
   - **Library**: Use gmp-ecm via subprocess or pyecm for direct control (primefac as fallback)
   - **Parameters**:
     - B1 = 1e8 (stage 1 bound, tuned for 39-digit factors)
     - B2 = 1e12 (stage 2 bound)
     - Curves: 5000-20000 attempts (parallelize if possible)
   - **Expected**: 10-60 minute runtime per attempt
   - **Target**: >10% success rate

   ```python
   import subprocess
   
   def ecm_factor_256bit(N, curves=10000):
       """Run ECM with aggressive parameters for 128-bit factors."""
       cmd = f'echo {N} | ecm -c {curves} 1e8 1e12'
       result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
       # Parse output for factors
       # Return list of factors if found
       return parse_factors(result.stdout)
   ```

2. **Pollard's Rho**
   - **Why**: Fast for smaller factors; low success for 128-bit but cheap to try first
   - **Library**: SymPy or custom implementation
   - **Parameters**:
     - Iterations: 10^8 (limit to avoid long runs)
     - Multiple starting points (x₀ = 2, 3, 5, 7, 11...)
   - **Expected**: 1-5 minute runtime per attempt
   - **Target**: >1% success rate (long shot, but fast)

3. **Fermat's Factorization** (if p, q close)
   - **Why**: Exploits cases where |p - q| is small (bias generation toward this via Z5D close indices)
   - **Parameters**:
     - Search ceiling: 10^7 iterations
     - Only run if ECM/Rho fail quickly
   - **Expected**: <1 minute runtime
   - **Target**: >0% success rate (higher if biased)

**Tier 2: IMPLEMENT IF TIME PERMITS**

4. **Quadratic Sieve (QS)**
   - **Why**: Deterministic for this size, but slower than ECM
   - **Library**: YAFU or msieve via subprocess
   - **Parameters**:
     - Sieve interval: tune for 256-bit
     - Smoothness bound: ~10^7
   - **Expected**: 10-60 minute runtime
   - **Target**: >50% success rate (if implemented correctly)

5. **GNFS (General Number Field Sieve)**
   - **Why**: Standard for 77-digit numbers, overkill but reliable
   - **Library**: CADO-NFS via subprocess
   - **Note**: May be too heavy; use only if QS unavailable

#### Implementation Requirements

**Code Structure**:
```python
import time

class FactorizationPipeline:
    def __init__(self, target_N, timeout_seconds=3600):
        self.N = target_N
        self.timeout = timeout_seconds
        self.methods = [
            ('pollard_rho', self.try_pollard_rho),
            ('fermat', self.try_fermat),
            ('ecm', self.try_ecm),
            # ('quadratic_sieve', self.try_qs),  # if implemented
        ]
    
    def run(self):
        """Try methods in priority order until success or timeout."""
        start = time.time()
        
        for method_name, method_func in self.methods:
            if time.time() - start > self.timeout:
                return None, 'timeout'
            factors = method_func()
            if factors and verify_factors(self.N, factors):
                return factors, method_name
        return None, 'exhausted_methods'
    
    # Implement try_pollard_rho, try_fermat, try_ecm here with timeouts
```

---

## Checkpoints & Deliverables

**Checkpoints**:
- [ ] Generate 20+ targets with Z5D (bias 10% toward close p/q)
- [ ] Implement ECM with tuned params (>5% success rate)
- [ ] Verify p × q = N with certificate
- [ ] Document method, runtime, compute resources used
- [ ] Reproducible: second engineer can replicate result (use RNG seeds)

**Evidence Required**:
```
Target: N = [256-bit modulus]
Factors found: p = [128-bit prime], q = [128-bit prime]
Verification: p × q = N ✓
Method: ECM with B1=1e8, curves=10000
Runtime: 23m 14s
Hardware: Intel i7-9750H, 32GB RAM
Success rate: 1/20 (5%)
```

### Reporting Format

**Daily Progress Updates**:
```
Date: YYYY-MM-DD
Targets generated: X
Factorization attempts: Y
Successes: Z
Methods tried: [list]
Bottlenecks: [description]
Next steps: [plan]
```

**Final Report**:
- Success rate across all methods
- Time/resource requirements
- Comparison to published factorization records (verify we're in expected range)
- Recommendations for next milestone (512-bit? 384-bit?)

---

## Integration with Hyper-Rotation Protocol

### Why This Matters

**Current protocol** (PR #38):
- Time-windowed key derivation
- XChaCha20-Poly1305 AEAD
- Optional RSA demo mode (encrypt/decrypt only)

**With 256-bit factorization**:
- **Provable key refresh**: Demonstrate old keys CAN be broken, justifying rotation
- **Tactical advantage**: We can generate AND break 256-bit keys faster than adversary expects (via Z5D bias)
- **Security model validation**: Prove that time-bounded exposure + forced rotation is viable

**Protocol evolution**:
1. **Current**: Symmetric time-keying (no PFS)
2. **Next**: Ephemeral RSA key negotiation (256-bit, rotated every 5-10 seconds)
3. **Future**: Hybrid PFS (start with time-keyed 256-bit RSA, upgrade to 2048-bit + Double Ratchet); consider post-quantum (e.g., Kyber)

**Key insight**: If we can factor our own 256-bit keys in <1 hour, adversary might take 10-100 hours (no Z5D guidance). Window of 10-100x advantage justifies tactical use.

---

## Resources & References

### Libraries & Tools

**Python Ecosystem**:
- `pyecm` or subprocess for gmp-ecm: Precise ECM control
- `sympy`: Number theory utilities, primality testing (isprime)
- `gmpy2`: GMP bindings for fast arithmetic

**External Tools**:
- **GMP-ECM**: Industry standard for ECM factorization
- **YAFU**: Automated factorization (includes QS, ECM, Rho)
- **msieve**: Quadratic/number field sieve implementation
- **CADO-NFS**: Advanced NFS for research

### Baseline Expectations

**Published 256-bit factorization records**:
- ECM: Expected ~10-60 minutes with optimal parameters for 39-digit factors
- QS: Deterministic, ~30-120 minutes for 256-bit
- Rho: Low probability (<0.1%) but fast (<5 minutes)

**Our advantage**:
- Z5D-guided prime generation may produce factors with exploitable structure
- We know the generation method, can potentially bias toward "weak" cases

---

## Risk Mitigation

### Failure Scenarios

**Scenario 1**: No factorization success after 100 attempts
- **Mitigation**: Drop to 192-bit targets (96-bit factors), establish baseline
- **Escalation**: If 192-bit also fails, audit implementation against published tools (e.g., YAFU on same targets)

**Scenario 2**: Success rate <0.1% (1 in 1000)
- **Mitigation**: Acceptable for PoC, but need to understand why (weak RNG? Bad parameters?)
- **Action**: Compare against YAFU/msieve on identical targets

**Scenario 3**: Factorization takes >10 hours per attempt
- **Mitigation**: Parallelize across targets/curves, accept lower success rate; use GPU (CUDA-ECM)
- **Escalation**: Consider cloud burst compute

### Contingency Plan

If 256-bit proves intractable within 2-week sprint:
1. **Pivot to 192-bit** (establish >10% success baseline)
2. **Scale up incrementally**: 192 → 224 → 256 bits
3. **Document capability ceiling**: "Z5D + ECM achieves X% at Y bits"

---

## Acceptance Criteria

**Mandatory (blocks merge to main)**:
- [ ] Factorization pipeline compiles and runs
- [ ] At least 1 successful 256-bit factorization demonstrated
- [ ] Verification code confirms p × q = N and sympy.isprime(p/q)
- [ ] Runtime logs show compute resources used
- [ ] Code includes tests with known semiprimes (e.g., from sympy)

**Recommended (for production readiness)**:
- [ ] Success rate >5% across 20+ targets
- [ ] Parallel batch processing implemented
- [ ] Integration with hyper-rotation messenger (key lifecycle demo)
- [ ] Security analysis: compare our time-to-factor vs. adversary estimates

---

## Timeline & Milestones

**Week 1**:
- Day 1-2: Z5D prime generation pipeline (20+ test targets)
- Day 3-4: Pollard Rho + Fermat implementation (fast, low success expected)
- Day 5-7: ECM integration (primary method, tune parameters)

**Week 2**:
- Day 8-10: Batch factorization runs, collect success statistics
- Day 11-12: QS implementation if ECM success rate <5%
- Day 13-14: Documentation, integration testing, final report

**Go/No-Go Decision Point** (End of Week 1):
- If zero factorizations by Day 7 → pivot to 192-bit
- If 1+ factorization by Day 7 → continue 256-bit optimization

---

## Summary

**Goal**: Achieve >0% factorization success on 256-bit balanced semiprimes.

**Approach**:
1. Generate targets with Z5D-guided prime selection
2. Implement ECM + Rho + Fermat factorization pipeline
3. Measure success rate and runtime
4. Integrate with hyper-rotation key lifecycle

**Success = ANY working factorization**, even if rare. This proves the concept and gates next-phase development.

**Questions?** Escalate immediately if:
- Zero factorizations after 50+ attempts with ECM
- Runtime exceeds 10 hours per attempt
- Implementation blockers (library dependencies, hardware limits)

---

**Authorization**: Approved for immediate engineering effort.  
**Point of Contact**: [Technical Lead]  
**Review Date**: [2 weeks from start]  

---

## Appendix: Quick Start Commands

**Generate targets** (example script skeleton):
```python
import json
# Assume Z5dPredictor imported
targets = []
for i in range(20):
    # Generate p, q via Z5D, N = p * q
    targets.append({'N': N, 'p': p, 'q': q})  # For validation only
with open('targets.json', 'w') as f:
    json.dump(targets, f)
```

**Run factorization** (example):
```bash
python factor_256bit.py --target targets.json --method ecm --timeout 3600
```

**Batch process** (example):
```bash
python batch_factor.py --targets targets.json --parallel 8 --methods ecm,rho
```

**Validate results** (example):
```python
import sympy
def verify_factors(N, factors):
    p, q = factors
    return p * q == N and sympy.isprime(p) and sympy.isprime(q)
```

---

**END DIRECTIVE**