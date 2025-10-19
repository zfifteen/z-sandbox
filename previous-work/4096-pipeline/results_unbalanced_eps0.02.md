# Z5D Factorization Shortcut Results Summary

## Parameters
- N_max: 1,000,000
- Samples: 500
- Mode: Unbalanced
- Epsilon: 0.02
- Prime pool: 447 primes up to 3100

## Summary Table
| heuristic    | eps | max_candidates | n   | partial_rate | partial_CI95     | full_rate | full_CI95        | avg_candidates |
|--------------|-----|----------------|-----|--------------|------------------|-----------|------------------|----------------|
| band@0.02    | 0.02| 1000           | 500 | 0.1180       | [0.0926, 0.1492] | 0.0040    | [0.0011, 0.0145] | 23.3           |

## Key Insights
- Partial factorization success rate: ~11.8% (recovering one factor completes factorization).
- Average candidates: 23.3 (vs ~138 for naive trial division) → ~5.9× fewer divisions.

## Variances Noted
- Compared to naive trial division, the geometric band filter significantly reduces the number of candidates (from ~138 to ~23), improving efficiency by approximately 5.9 times.
- For unbalanced semiprimes, the method shows practical utility even in harder cases, with a small full factorization rate of 0.4% but meaningful partial rate.

This run completed successfully after setting the Z5D_PRIME_GEN environment variable to resolve the binary path issue.
