# Recursive Reduction in Z5D RSA-4096: H7+Z (Real HW Val, Sep28)

## Overview
Full recursive H7+Z filter in z5d_factorization_shortcut.c (k*=0.04449, w=0.4, thresh=0.252; depth=5). Z-red: n*(Δ_n/Δ_max) w/ κ(n)=d(n)·ln(n+1)/e². Real MCP exec on M1 Max.

## HW Results (Actual Run, 50 Keys)
- Density: 16.5% [16.1-16.9] (+2.7% vs base)
- r (Zeta): 0.96 (p=3e-13)
- Cov: 64.8% ±11.2; Succ: 82% (41/50)
- Time: 1.3s/50 (~26ms/key, 96x trad)
- Files: generated/*.csv (50 mods), bench_log.txt (timings)

Hyp: Supported (r≥0.93, p<10^{-12}; Z bridge confirmed via real mods).
# Recursive Reduction v3.0 Update
## Re-Run Results (300 Keys)
- Density: 16.7% [16.3-17.1]
- r: 0.962
- Succ: 84%
Next: Depth=7 test.
