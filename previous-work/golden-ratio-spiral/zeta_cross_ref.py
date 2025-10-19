#!/usr/bin/env python3
"""
zeta_cross_ref.py - Cross-reference Mersenne residuals with Riemann zeta zeros.

Computes εᵢ = ln((pᵢ/pᵢ₋₁)/2) residuals from Mersenne exponents.
Correlates with gaps between consecutive zeta zeros (using Im(ρ) or t).

Outputs Pearson correlation coefficient ρ in zeta_cross_ref.json.

Requires: mpmath, numpy, scipy, pandas.

Usage: python zeta_cross_ref.py mersenne_exps.txt zeta_zeros.csv

UNVERIFIED: Use canonical datasets for validation.
"""

import sys
import json
import mpmath as mp
import numpy as np
import pandas as pd
from scipy import stats

mp.dps = 50

def compute_mersenne_residuals(exps_file):
    """Compute εᵢ = ln((pᵢ/pᵢ₋₁)/2)"""
    with open(exps_file, 'r') as f:
        exps = [int(line.strip()) for line in f if line.strip()]
    exps.sort()
    residuals = []
    for i in range(1, len(exps)):
        p_i = mp.mpf(2) ** exps[i]
        p_im1 = mp.mpf(2) ** exps[i-1]
        ratio = p_i / p_im1
        eps = mp.log(ratio / 2)
        residuals.append(float(eps))
    return residuals

def load_zeta_zeros(csv_file):
    """Load zeta zeros, compute gaps in Im(ρ) or t."""
    df = pd.read_csv(csv_file)
    # Assume column 't' or 'gamma' for Im(ρ)
    if 't' in df.columns:
        zeros = df['t'].values
    elif 'gamma' in df.columns:
        zeros = df['gamma'].values
    else:
        raise ValueError("CSV must have 't' or 'gamma' column")
    zeros = np.sort(zeros)
    gaps = np.diff(zeros)
    return gaps

def correlate(residuals, gaps):
    """Compute Pearson r."""
    if len(residuals) != len(gaps):
        min_len = min(len(residuals), len(gaps))
        residuals = residuals[:min_len]
        gaps = gaps[:min_len]
    if len(residuals) < 2:
        return None
    r, p = stats.pearsonr(residuals, gaps)
    return {'n_samples': len(residuals), 'pearson_r': float(r), 'p_value': float(p)}

def main():
    if len(sys.argv) != 3:
        print("Usage: python zeta_cross_ref.py <mersenne_exps.txt> <zeta_zeros.csv>")
        sys.exit(1)
    exps_file = sys.argv[1]
    csv_file = sys.argv[2]

    residuals = compute_mersenne_residuals(exps_file)
    gaps = load_zeta_zeros(csv_file)
    result = correlate(residuals, gaps)

    if result:
        with open('zeta_cross_ref.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Correlation computed: r={result['pearson_r']:.6f}, p={result['p_value']:.6f}, n={result['n_samples']}")
    else:
        print("Insufficient data for correlation.")

if __name__ == '__main__':
    main()