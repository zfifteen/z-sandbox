#!/usr/bin/env python3
"""
Golden Spiral Empirical Validation Script
==========================================

This script validates the golden ratio spiral implementation using mpmath
high-precision arithmetic (dps >= 50, target precision < 1e-16).

Core Axioms Integration:
- Z = A(B / c) : Scaling with c=φ, A=adjustment factor, B=dynamic rate.
- κ(n) = d(n) * ln(n+1) / e² : Curvature for prime density.
- θ'(n,k) = φ * ((n mod φ)/φ)^k : Geometric resolution (k≈0.3).
- Guards: ValueError for |v| >= c, avoid zero-division.

Hypotheses (UNVERIFIED until tested):
1. φ is optimal c for prime exponent scaling (benchmark vs. π, e).
2. κ(n) predicts prime density better than baseline.
3. θ'(n,k) improves spiral angles over fixed golden angle.

Cross-references: zeta_zeros.csv (Riemann), OEIS Mersenne exponents.

Requirements: mpmath, numpy, sympy, pandas.
"""

import mpmath as mp
import numpy as np
import sympy as sp
import pandas as pd
import csv
import os
from math import log, sqrt

# Set mpmath precision (dps >= 50 for < 1e-16)
mp.dps = 50

# Constants
PHI = (1 + mp.sqrt(5)) / 2
E = mp.e
PI = mp.pi
E_SQUARED = E**2
K_DEFAULT = 0.3  # For θ'(n,k)

# Load datasets
ZETA_ZEROS_PATH = 'zeta_zeros.csv'  # Assumed in project root
MERSENNE_EXPONENTS = [2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279, 2203, 2281, 3217, 4253, 4423, 9689, 9941, 11213, 19937, 21701, 23209, 44497, 86243, 110503, 132049, 216091, 756839, 859433, 1257787, 1398269, 2976221, 3021377, 6972593, 13466917, 20996011, 24036583, 25964951, 30402457, 32582657, 37156667, 42643801, 43112609, 57885161, 74207281, 77232917, 82589933, 136279841]  # OEIS A000043

def load_zeta_zeros():
    if os.path.exists(ZETA_ZEROS_PATH):
        return pd.read_csv(ZETA_ZEROS_PATH)['zero'].tolist()[:100]  # First 100 zeros
    else:
        print("Warning: zeta_zeros.csv not found. Using synthetic Riemann zeros.")
        return [0.5 + i*1j for i in range(1, 101)]  # Synthetic for demo

def z_framework_scale(current, c=PHI, a=1.0):
    """Z = A(B / c) scaling: B=dynamic rate (log growth), A=adjustment."""
    b = mp.log(current) / mp.log(10)  # Example dynamic rate
    z = a * (b / c)
    if abs(z) >= c:
        raise ValueError(f"Scaling violation: |Z| >= c ({z} >= {c})")
    return z

def curvature_kappa(n):
    """κ(n) = d(n) * ln(n+1) / e², with zero-division guard."""
    if n <= 0:
        raise ValueError("n must be positive.")
    d_n = sp.divisor_count(n)  # Sympy for divisor function
    ln_term = mp.log(n + 1)
    kappa = float(d_n) * ln_term / E_SQUARED
    return kappa

def geometric_resolution_theta(n, k=K_DEFAULT):
    """θ'(n,k) = φ * ((n mod φ)/φ)^k"""
    mod_phi = mp.fmod(n, PHI)
    ratio = mod_phi / PHI
    theta = PHI * (ratio ** k)
    return theta

def validate_scaling_hypothesis():
    """Hypothesis 1: Test φ as c in Z= A(B/c) for Mersenne scaling."""
    print("HYPOTHESIS 1: φ as optimal c for prime scaling (UNVERIFIED)")
    results = []
    for exp in MERSENNE_EXPONENTS[-5:]:  # Last 5 for growth
        try:
            z_phi = z_framework_scale(exp, c=PHI)
            z_pi = z_framework_scale(exp, c=PI)  # Benchmark vs π
            z_e2 = z_framework_scale(exp, c=E_SQUARED)  # Vs e²
            ratio_phi = (exp * PHI) / exp  # Predicted growth
            results.append((exp, z_phi, z_pi, z_e2, ratio_phi))
            print(f"Exp: {exp}, Z_φ: {z_phi:.6f}, Ratio_φ: {ratio_phi:.6f}")
        except ValueError as e:
            print(f"Guard triggered for {exp}: {e}")
    # Correlation with actual growth (convert to float for numpy)
    actual_ratios = [float(MERSENNE_EXPONENTS[i+1]/MERSENNE_EXPONENTS[i]) for i in range(len(MERSENNE_EXPONENTS)-1)]
    predicted_phi = [float(PHI) for _ in actual_ratios]
    corr = np.corrcoef(actual_ratios, predicted_phi)[0,1]
    print(f"Correlation φ vs actual growth: {corr:.6f}")
    print("Status: UNVERIFIED (guards trigger at large scales; c may need domain adaptation)\n")

def validate_curvature_hypothesis():
    """Hypothesis 2: κ(n) predicts prime density."""
    print("HYPOTHESIS 2: κ(n) for prime density (UNVERIFIED)")
    test_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]  # Small primes
    test_composites = [4, 6, 8, 9, 10, 12, 14, 15, 16]
    kappa_primes = [curvature_kappa(p) for p in test_primes]
    kappa_comps = [curvature_kappa(c) for c in test_composites]
    avg_kappa_primes = np.mean([float(k) for k in kappa_primes])
    avg_kappa_comps = np.mean([float(k) for k in kappa_comps])
    print(f"Avg κ(primes): {avg_kappa_primes:.6f}, Avg κ(comps): {avg_kappa_comps:.6f}")
    # Benchmark vs baseline (random)
    np.random.seed(42)  # Reproducibility
    baseline_primes = np.random.uniform(0, 1, len(test_primes))
    baseline_comps = np.random.uniform(0, 1, len(test_composites))
    print(f"Baseline avg primes: {np.mean(baseline_primes):.6f}, comps: {np.mean(baseline_comps):.6f}")
    print("Status: UNVERIFIED (needs large-scale prime set)\n")

def validate_geometric_hypothesis():
    """Hypothesis 3: θ'(n,k) improves angles."""
    print("HYPOTHESIS 3: θ'(n,k) for spiral angles (UNVERIFIED)")
    fixed_angle = 2 * PI / (PHI ** 2)  # Traditional golden angle
    test_n = [1, 2, 3, 5, 7, 11, 13]
    angles_fixed = [float(fixed_angle * n) for n in test_n]
    angles_theta = [float(geometric_resolution_theta(n)) for n in test_n]
    print("Fixed angles:", angles_fixed)
    print("θ' angles:", angles_theta)
    # Cross-ref zeta zeros for "density"
    zeta_zeros = load_zeta_zeros()
    correlations = []
    for i, zero in enumerate(zeta_zeros[:len(test_n)]):
        dist_fixed = min(abs(zero - a) for a in angles_fixed)
        dist_theta = min(abs(zero - a) for a in angles_theta)
        correlations.append(dist_theta < dist_fixed)
    print(f"θ' closer to zeta zeros: {sum(correlations)}/{len(correlations)}")
    print("Status: UNVERIFIED (needs full spiral simulation)\n")

def main():
    print("Golden Spiral Empirical Validation (mpmath dps=50)\n")
    validate_scaling_hypothesis()
    validate_curvature_hypothesis()
    validate_geometric_hypothesis()
    print("Reproducibility: RNG seed=42, mp.dps=50. Run again for consistency.")

if __name__ == "__main__":
    main()