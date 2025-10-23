#!/usr/bin/env python3
"""
Demo: High-Value Follow-Ups for Monte Carlo Benchmark

This script demonstrates the 5 follow-ups implemented:
1. Factorization builders (Z5D) in benchmark
2. Replay recipe for reproducing results
3. QMC/stratified modes in factor sampler
4. Deprecation warning (shown in imports)
5. CI guardrail with candidates/sec metric
"""

import sys
import warnings
sys.path.insert(0, 'python')

from monte_carlo import FactorizationMonteCarloEnhancer
from z5d_predictor import get_factor_candidates

print("=" * 80)
print("Demo: High-Value Follow-Ups for Monte Carlo Benchmark")
print("=" * 80)

# Follow-up #4: Deprecation Warning
print("\n1. Deprecation Warning (Follow-up #4)")
print("-" * 80)
print("Importing HyperRotationMonteCarloAnalyzer from old path:")
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    from monte_carlo import HyperRotationMonteCarloAnalyzer
    analyzer = HyperRotationMonteCarloAnalyzer(seed=42)
    if w:
        print(f"✓ Warning issued: {w[0].message}")
    else:
        print("Note: Warning may not show in non-interactive mode")

print("\nNew recommended import:")
print("  from security.hyper_rotation import HyperRotationMonteCarloAnalyzer")

# Follow-up #3: QMC/Stratified Modes
print("\n\n2. Variance Reduction Modes in Factor Sampler (Follow-up #3)")
print("-" * 80)

N = 899  # 29 × 31
enhancer = FactorizationMonteCarloEnhancer(seed=42)

import time
for mode in ["uniform", "stratified", "qmc"]:
    start = time.time()
    candidates = enhancer.biased_sampling_with_phi(N, num_samples=500, mode=mode)
    elapsed = time.time() - start
    cand_per_sec = len(candidates) / elapsed if elapsed > 0 else 0
    
    found_29 = 29 in candidates
    found_31 = 31 in candidates
    
    print(f"\n{mode.upper()} mode:")
    print(f"  Candidates: {len(candidates)}")
    print(f"  Time: {elapsed:.4f}s")
    print(f"  Rate: {cand_per_sec:.0f} candidates/sec")
    print(f"  Found 29: {found_29}, Found 31: {found_31}")

# Follow-up #1: Z5D Builder Comparison
print("\n\n3. Factorization Builders Comparison (Follow-up #1)")
print("-" * 80)

# Small test case that Z5D can handle
N_large = 11541040183  # 106661 × 108203
print(f"\nTesting on N = {N_large} (106661 × 108203)")

print("\nZ5D Builder:")
start = time.time()
try:
    z5d_candidates_data = get_factor_candidates(N_large)
    z5d_candidates = [c for c, _, _ in z5d_candidates_data]
    elapsed = time.time() - start
    
    found = False
    factor_idx = None
    for idx, c in enumerate(z5d_candidates):
        if N_large % c == 0:
            print(f"  ✓ Found factor: {c} at index {idx}")
            found = True
            factor_idx = idx
            break
    
    print(f"  Candidates: {len(z5d_candidates)}")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Rate: {len(z5d_candidates)/elapsed:.0f} candidates/sec")
    
    if not found:
        print(f"  Factor not found in candidates")
except Exception as e:
    print(f"  Error: {e}")

print("\nMonte Carlo φ-biased (QMC mode):")
start = time.time()
mc_candidates = enhancer.biased_sampling_with_phi(N_large, num_samples=1000, mode='qmc')
elapsed = time.time() - start

found = False
for c in mc_candidates:
    if N_large % c == 0:
        print(f"  ✓ Found factor: {c}")
        found = True
        break

print(f"  Candidates: {len(mc_candidates)}")
print(f"  Time: {elapsed:.2f}s")
print(f"  Rate: {len(mc_candidates)/elapsed:.0f} candidates/sec")

if not found:
    print(f"  Factor not found (expected for large N)")

# Follow-up #2: Replay Recipe
print("\n\n4. Replay Recipe (Follow-up #2)")
print("-" * 80)
print("""
To replay exact results from benchmark CSV:

# Extract from CSV
seed = 42
mode = 'qmc'
N = 899
samples = 500

# Replay
from monte_carlo import FactorizationMonteCarloEnhancer
enhancer = FactorizationMonteCarloEnhancer(seed=seed)
candidates = enhancer.biased_sampling_with_phi(N, num_samples=samples, mode=mode)

# Verify
print(f"Replayed: {len(candidates)} candidates")
""")

# Follow-up #5: CI Guardrail
print("\n5. CI Performance Guardrail (Follow-up #5)")
print("-" * 80)

# Simulate CI benchmark
print("\nSimulating CI benchmark on N=899:")

enhancer_ci = FactorizationMonteCarloEnhancer(seed=42)

start = time.time()
candidates_uniform = enhancer_ci.biased_sampling_with_phi(N=899, num_samples=500, mode='uniform')
elapsed_uniform = time.time() - start
rate_uniform = len(candidates_uniform) / elapsed_uniform if elapsed_uniform > 0 else 0

start = time.time()
candidates_qmc = enhancer_ci.biased_sampling_with_phi(N=899, num_samples=500, mode='qmc')
elapsed_qmc = time.time() - start
rate_qmc = len(candidates_qmc) / elapsed_qmc if elapsed_qmc > 0 else 0

print(f"\nPerformance Metrics:")
print(f"  Uniform mode: {rate_uniform:.0f} candidates/sec")
print(f"  QMC mode: {rate_qmc:.0f} candidates/sec")
print(f"  Baseline expectation: >1000 cand/s")

if rate_uniform < 100 or rate_qmc < 100:
    print(f"\n⚠ WARNING: Performance below threshold!")
else:
    print(f"\n✓ Performance within expected range")

print("\n" + "=" * 80)
print("Demo Complete!")
print("=" * 80)
print("\nAll 5 follow-ups demonstrated:")
print("  1. ✓ Z5D builder comparison")
print("  2. ✓ Replay recipe")
print("  3. ✓ QMC/stratified modes")
print("  4. ✓ Deprecation warning")
print("  5. ✓ CI performance guardrail")
