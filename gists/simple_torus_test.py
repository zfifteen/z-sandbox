#!/usr/bin/env python3
"""Simple test of 2D torus approach on boundary case."""

from torus_factorization import theta_mod1_log, residualize, torus_score
from decimal import Decimal

# Test case
N = 22170092047
p, q = 94793, 233879

# Simple window
window_vals = [N, p, q, N//2, N//3]  # Small window for testing

# Test torus scoring
alpha = Decimal('1.6180339887498948')  # φ
beta = Decimal('2.7182818284590452')   # e

print(f"Testing torus on N={N}, factors p={p}, q={q}")

# Score true factors
score_p, (dist_a_p, dist_b_p) = torus_score(N, p, window_vals, alpha, beta)
score_q, (dist_a_q, dist_b_q) = torus_score(N, q, window_vals, alpha, beta)

print(f"p score: {score_p:.4f} (dist_a: {dist_a_p:.4f}, dist_b: {dist_b_p:.4f})")
print(f"q score: {score_q:.4f} (dist_a: {dist_a_q:.4f}, dist_b: {dist_b_q:.4f})")

# Compare with random candidate
import random
rand_cand = random.choice(window_vals)
if rand_cand in [p, q, N]:
    rand_cand = N + 1000  # Make it different

score_rand, _ = torus_score(N, rand_cand, window_vals, alpha, beta)
print(f"Random candidate score: {score_rand:.4f}")

if min(score_p, score_q) < score_rand:
    print("✓ Torus approach shows potential - true factors score better")
else:
    print("✗ Torus approach may not help - true factors not distinguished")