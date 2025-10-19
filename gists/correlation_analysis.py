#!/usr/bin/env python3
"""
Compute correlation between spiral radii and zeta zero imaginary parts
"""

import math
from scipy import stats
import mpmath as mp

# Set precision
mp.mp.dps = 50

# Zeta zeros imaginary parts (first 20)
ZETA_ZEROS_IMAG = [
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446248, 59.347045, 60.831778, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704690, 77.144840
]

def compute_spiral_radii(N, num_points=20, k=0.3):
    """Compute radii for spiral candidates"""
    phi = (1 + mp.sqrt(5)) / 2
    zeta_mean = sum(ZETA_ZEROS_IMAG) / len(ZETA_ZEROS_IMAG)
    scale = 0.5 * (zeta_mean / 10.0)
    sqrt_N = mp.sqrt(N)

    radii = []
    for i in range(num_points):
        r = sqrt_N * scale * (1 + mp.log(i + 2)) * (phi ** (i / (5 * k)))
        radii.append(float(r))

    return radii

def analyze_correlation():
    """Analyze correlation between spiral radii and zeta zeros"""
    N = 91  # Use small N for analysis
    radii = compute_spiral_radii(N)

    # Ensure same length
    min_len = min(len(radii), len(ZETA_ZEROS_IMAG))
    radii = radii[:min_len]
    zeta_vals = ZETA_ZEROS_IMAG[:min_len]

    # Compute Pearson correlation
    correlation, p_value = stats.pearsonr(radii, zeta_vals)

    print(f"Correlation analysis for N={N}")
    print(f"Spiral radii (first {min_len}): {radii}")
    print(f"Zeta imaginary parts (first {min_len}): {zeta_vals}")
    print(".4f")
    print(f"P-value: {p_value}")
    print(f"Significant correlation: {p_value < 0.05}")

    # Interpretation
    if abs(correlation) > 0.8:
        strength = "strong"
    elif abs(correlation) > 0.6:
        strength = "moderate"
    elif abs(correlation) > 0.3:
        strength = "weak"
    else:
        strength = "very weak"

    direction = "positive" if correlation > 0 else "negative"
    print(f"Correlation strength: {strength} and {direction}")

if __name__ == '__main__':
    analyze_correlation()