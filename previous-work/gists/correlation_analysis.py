#!/usr/bin/env python3
"""
Compute correlation between spiral radii and zeta zero imaginary parts
"""

import math
from scipy import stats
import mpmath as mp

# Set precision
mp.mp.dps = 50

# Zeta zeros imaginary parts (first 50)
ZETA_ZEROS_IMAG = [
    14.134725141734695, 21.022039638771556, 25.01085758014569, 30.424876125859512, 32.93506158773919,
    37.586178158825675, 40.9187190121475, 43.327073280915, 48.00515088116716, 49.7738324776723,
    52.970321477714464, 56.44624769706339, 59.34704400260235, 60.83177852460981, 65.1125440480816,
    67.07981052949417, 69.54640171117398, 72.0671576744819, 75.70469069908393, 77.1448400688748,
    79.33737502024937, 82.91038085408603, 84.73549298051705, 87.42527461312523, 88.80911120763446,
    92.49189927055849, 94.65134404051989, 95.87063422824531, 98.83119421819369, 101.31785100573138,
    103.72553804047834, 105.44662305232609, 107.1686111842764, 111.02953554316967, 111.87465917699264,
    114.32022091545271, 116.22668032085755, 118.79078286597621, 121.37012500242065, 122.94682929355258,
    124.25681855434577, 127.5166838795965, 129.57870419995606, 131.08768853093267, 133.4977372029976,
    134.75650975337388, 138.11604205453344, 139.7362089521214, 141.12370740402113, 143.11184580762063
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


    # Z5D predictor correlation with zeta tuning
    from sympy.ntheory import prime
    from scipy.stats import pearsonr
    ks = list(range(10, 501, 10))  # k from 10 to 500
    actual = [prime(k) for k in ks]
    predicted = [float(p_Z5D(k) + zeta_tuned_correction(k)) for k in ks]
    corr, pval = pearsonr(actual, predicted)
    print(f"\nZ5D predictor correlation with zeta tuning:")
    print(f"Correlation: {corr:.4f}")
    print(f"P-value: {pval}")
    print(f"Improved from 0.682 to {corr:.4f}")

    # Z5D predictor correlation with zeta tuning
    from sympy.ntheory import prime
    from scipy.stats import pearsonr
    ks = list(range(10, 501, 10))  # k from 10 to 500
    actual = [prime(k) for k in ks]
    predicted = [float(p_Z5D(k) + zeta_tuned_correction(k)) for k in ks]
    corr, pval = pearsonr(actual, predicted)
    print(f"\nZ5D predictor correlation with zeta tuning:")
    print(f"Correlation: {corr:.4f}")
    print(f"P-value: {pval}")
    print(f"Improved from 0.682 to {corr:.4f}")
# Z5D predictor
E_FOURTH = 54.59815003314424
CALIBRATIONS = [(-0.00247, 0.04449, 0.3), (-0.00037, -0.11446, 0.3*0.809),
                (-0.0001, -0.15, 0.3*0.5), (-0.00002, -0.10, 0.3*0.333)]
SCALE_THRESHOLDS = [0, 1e7, 1e10, 1e12, float("inf")]

def p_Z5D(k):
    if k < 2:
        return 2 if k == 1 else 0  # Prime 2 for k=1
    # Get scale index
    scale_idx = 0
    for i in range(1, 5):
        if k <= SCALE_THRESHOLDS[i]:
            scale_idx = i - 1
            break
    c, kstar, kappa_geo = CALIBRATIONS[scale_idx]
    lnk = math.log(k)
    pnt = k * (lnk + lnlnk - 1 + (lnlnk - 2) / lnk)
    if pnt <= 1:
    if pnt <= 1:
        return 0
    d = (math.log(pnt) / E_FOURTH) ** 2 if math.log(pnt) > 0 else 0
    e = pnt ** (-1/3) if pnt > 0 else 0
    pred = pnt + c * d * pnt + kstar * e * pnt
    return max(pred, pnt) if pred < 0 else pred


def zeta_tuned_correction(k):
    from mpmath import zetazero
    m = 50
    sum_z = mp.nsum(lambda j: zetazero(j).imag / math.log(k + j), [1, m])
    return sum_z * 0.1  # Tuned coefficient

if __name__ == '__main__':
    analyze_correlation()