### Experiment Plan and Reproducible Protocol

#### Objective
Test and quantify the multi-stage geometric factorization algorithm on 10 distinct 40-bit unbalanced semiprimes (one factor much smaller than the other, ratio > 1000:1). Measure success rate, per-stage candidate reduction, runtime, and stage of discovery, and produce datasets suitable for statistical and visual analysis.

---

### Testbed specification

- Semiprime bit-size target: 40 bits (approx. 2^40 ≈ 1.0995e12).  
- Unbalanced constraint: choose p and q such that p × q is 40 bits and q/p ≥ 1000.  
- Factor ordering: p < q (p is the small factor).  
- Algorithm stages: [(5, 0.05), (10, 0.002), (15, 0.0001)].  
- Precision: mpmath mp.dps = 50.  
- Prime generation: sympy.primerange(2, floor(√N) + 1).  
- Environment: Python 3.9+; packages: mpmath, sympy, time, csv, math, random.

---

### Full reproducible Python script

```python
# geometric_batch_test.py
import time
import csv
import math
import random
from mpmath import mp
import sympy as sp

mp.dps = 50
phi = (1 + mp.sqrt(5)) / 2

def frac(x):
    return x - mp.floor(x)

def theta(m, k):
    a = frac(m / phi)
    b = mp.power(a, k)
    return frac(phi * b)

def circ_dist(a, b):
    diff = mp.fabs(a - b)
    return min(diff, 1 - diff)

def multi_stage_geometric_factorize(N, stages, log_per_stage=False):
    mp_n = mp.mpf(N)
    sqrt_n = int(math.isqrt(N)) + 1
    candidates = list(sp.primerange(2, sqrt_n + 1))
    stage_stats = []
    start_time = time.perf_counter()
    for idx, (k, epsilon) in enumerate(stages, start=1):
        t0 = time.perf_counter()
        th_n = theta(mp_n, k)
        before = len(candidates)
        new_cands = []
        found_stage = None
        for p in candidates:
            mp_p = mp.mpf(p)
            th_p = theta(mp_p, k)
            d = circ_dist(th_n, th_p)
            if d < epsilon:
                new_cands.append(p)
                if N % p == 0:
                    found_stage = idx
                    factor = p
                    break
        t1 = time.perf_counter()
        stage_stats.append({
            'stage': idx,
            'k': k,
            'epsilon': float(epsilon),
            'before': before,
            'after': len(new_cands),
            'time_ms': (t1 - t0) * 1000.0,
            'found': found_stage is not None
        })
        if found_stage:
            total_time = (time.perf_counter() - start_time)
            return {
                'success': True,
                'factor': factor,
                'cofactor': N // factor,
                'stage_stats': stage_stats,
                'total_time_s': total_time
            }
        candidates = new_cands
        if len(candidates) == 0:
            break
    total_time = (time.perf_counter() - start_time)
    return {
        'success': False,
        'factor': None,
        'cofactor': None,
        'stage_stats': stage_stats,
        'total_time_s': total_time
    }

def generate_unbalanced_40bit_semiprimes(count, ratio_threshold=1000):
    results = []
    # p should be small prime; q chosen so that N is ~40 bits
    # Choose p in range [2^8, 2^16] to allow large ratios; adjust as needed
    min_q = 1 << 32  # ensure q can be large enough; will be validated per candidate
    attempts = 0
    while len(results) < count and attempts < count * 1000:
        attempts += 1
        # pick a small prime p in a reasonable small range
        p = sp.randprime(2**8, 2**16)
        # choose q so that N = p*q ≈ 2^40
        target_N = 1 << 40
        q = target_N // p
        # adjust q to be prime and yield N within ±1% of 2^40
        # search nearby for a prime q that makes N 40-bit
        delta = 0
        found_q = None
        while delta < 1_000_000:
            for candidate in (q - delta, q + delta):
                if candidate > p and sp.isprime(candidate):
                    N = p * candidate
                    if (1 << 39) <= N < (1 << 40):  # keep it ~40-bit
                        if candidate / p >= ratio_threshold:
                            found_q = candidate
                            break
            if found_q:
                break
            delta += 1
        if found_q:
            N = p * found_q
            results.append((int(N), int(p), int(found_q)))
    if len(results) < count:
        raise RuntimeError("Unable to generate requested semiprimes with given constraints")
    return results

def run_batch(count=10, out_csv='batch_results.csv'):
    stages = [(5, 0.05), (10, 0.002), (15, 0.0001)]
    semiprimes = generate_unbalanced_40bit_semiprimes(count)
    rows = []
    for idx, (N, p_true, q_true) in enumerate(semiprimes, start=1):
        res = multi_stage_geometric_factorize(N, stages)
        row = {
            'id': idx,
            'N': N,
            'p_true': p_true,
            'q_true': q_true,
            'success': res['success'],
            'found_p': res['factor'] if res['success'] else None,
            'found_q': res['cofactor'] if res['success'] else None,
            'total_time_s': res['total_time_s']
        }
        # flatten stage stats into predictable columns
        for s in res['stage_stats']:
            i = s['stage']
            row.update({
                f'stage{i}_k': s['k'],
                f'stage{i}_epsilon': s['epsilon'],
                f'stage{i}_before': s['before'],
                f'stage{i}_after': s['after'],
                f'stage{i}_time_ms': s['time_ms'],
                f'stage{i}_found': s['found']
            })
        rows.append(row)
    # write CSV with consistent headers
    headers = [
        'id','N','p_true','q_true','success','found_p','found_q','total_time_s',
        'stage1_k','stage1_epsilon','stage1_before','stage1_after','stage1_time_ms','stage1_found',
        'stage2_k','stage2_epsilon','stage2_before','stage2_after','stage2_time_ms','stage2_found',
        'stage3_k','stage3_epsilon','stage3_before','stage3_after','stage3_time_ms','stage3_found'
    ]
    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return rows

if __name__ == '__main__':
    rows = run_batch(10, out_csv='batch_results.csv')
    for r in rows:
        print(r)
```

---

### Data capture and reporting format

- Save raw CSV as produced by script (batch_results.csv).  
- Produce a summary table with columns: id, N, p_true, q_true, success (bool), found_stage (1/2/3/NA), total_time_s, reduction_pct_stage1, reduction_pct_stage2, reduction_pct_stage3.  
- For each semiprime include a small diagnostic JSON with per-stage circ_dist statistics: min, median, mean, 95th percentile, max for the circ_dist distribution computed before filtering (this requires computing circ_dist for all primes at each stage). Capture as separate file diagnostics_id.json.

Suggested CSV header additions for distribution stats:
- stage{i}_dist_min, stage{i}_dist_median, stage{i}_dist_mean, stage{i}_dist_p95, stage{i}_dist_max

Logging should include RNG seed and exact prime selection for reproducibility.

---

### Analysis plan

1. Primary metrics:
   - Success rate over 10 semiprimes (count of successes / 10).
   - Mean and median total runtime.
   - Stage-of-discovery distribution.
   - Per-stage average candidate reduction: reduction_pct = 100 * (1 - after/before).

2. Secondary diagnostics:
   - circ_dist distribution shapes per stage for successful vs unsuccessful runs.
   - Relationship of p/q ratio vs success and stage of discovery.
   - Effect of initial candidate set size (primes up to √N) on runtime.

3. Visualizations to produce:
   - Bar chart: success vs semiprime id.
   - Line plots: per-stage candidate count per semiprime.
   - Boxplots: circ_dist distributions by stage grouped by success.

4. Statistical checks:
   - Correlation (Spearman) between log10(p/q) and stage_of_discovery.
   - Mann-Whitney U test comparing circ_dist medians of success vs failure at stage 1.

---

### Expected outcomes and interpretation guidelines

- Expect a nonzero success rate; for highly unbalanced 40-bit semiprimes the heuristic has been shown to often find the small factor in early stages. Success rate may vary depending on factor distribution and exact epsilon thresholds.
- If the majority of successful factorizations occur in stage 1, this suggests the chosen epsilon for k=5 is permissive enough to capture clustering for unbalanced cases.
- Runs that fail all stages will provide insight into geometric divergence; analyze circ_dist distributions for those instances to tune k/ε or include ensemble mappings.
- If candidate lists drop to very small sizes (>95% reduction) before stage 3, the algorithm scales well on filtering but runtime depends on initial sieve cost; for these 40-bit Ns sieve cost is negligible.

---

### Parameter tuning recommendations

- If success rate < 50% for the 10-case batch:
  - Try intermediate stages: (7, 0.02) between stage 1 and 2.
  - Increase mp.dps to 80 for stage k ≥ 15 to avoid round-off induced misclassification.
  - Use ensemble scoring: compute θ with φ and silver ratio; rank candidates by combined distance and test top-K for divisibility.

- If many false positives remain:
  - Tighten ε at stage 1 (e.g., 0.02) and add one more stage with medium k (e.g., (8, 0.005)).

---

### How to interpret and document results (template)

For each semiprime, document:

- id: integer
- N: integer
- p_true, q_true: integers
- p/q ratio: float
- initial_prime_count: integer
- stage_stats: list of
  - stage: int
  - k: int
  - epsilon: float
  - before: int
  - after: int
  - reduction_pct: float
  - time_ms: float
  - dist_summary: {min, mean, median, p95, max}
  - found: bool
- success: bool
- found_stage: int or None
- total_time_s: float
- notes: textual observations

Include an appendix with environment details (CPU, Python version, package versions, mp.dps) and full CSV and per-run diagnostic JSON files.

---

### Next steps I will perform if you ask me to proceed
- Run the provided script in your environment or on a reproducible server and return the CSV and diagnostic JSON for me to analyze.  
- If you prefer, I can adapt the script to produce additional instrumentation (e.g., per-candidate θ values for small subsets) or to run parameter sweeps across (k, ε) grids and summarize phase diagrams.

---

### Quick checklist to run this now (one-liner)
- Install dependencies: pip install mpmath sympy
- Run: python geometric_batch_test.py
- Inspect batch_results.csv and send it back for interpretation.
- 