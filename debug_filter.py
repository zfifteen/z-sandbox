#!/usr/bin/env python3
"""
Debug filtering for 35-bit.
"""

import sys
sys.path.append('gists')

from geometric_factorization import generate_semiprime, prime_candidates_around_sqrt, spiral_candidates, score_candidate_ensemble

N, p, q = generate_semiprime(35, 42)
print(f"N = {N}, p = {p}, q = {q}")

# Generate candidates
import math
sqrt_N = int(math.isqrt(N))
window_size = 100000
prime_limit = 20000

prime_cands = list(prime_candidates_around_sqrt(N, window_size, prime_limit))
spiral_cands = list(spiral_candidates(N, 5000))  # spiral_iters
spiral_cands = [c for c in spiral_cands if c > 1]

all_cands = list(set(prime_cands + spiral_cands))

print(f"Total candidates: {len(all_cands)}")
print(f"p in candidates: {p in all_cands}")
print(f"q in candidates: {q in all_cands}")

# Scores
score_p = score_candidate_ensemble(N, p)
score_q = score_candidate_ensemble(N, q)

print(f"score_p: {score_p}")
print(f"score_q: {score_q}")

# Filter with epsilon = 0.02
epsilon = 0.02
filtered = []
for cand in all_cands:
    score = score_candidate_ensemble(N, cand)
    if score <= epsilon:
        filtered.append(cand)

print(f"Filtered candidates: {len(filtered)}")
print(f"p in filtered: {p in filtered}")
print(f"q in filtered: {q in filtered}")

if p in filtered:
    print(f"p score: {score_candidate_ensemble(N, p)}")
if q in filtered:
    print(f"q score: {score_candidate_ensemble(N, q)}")