from decimal import Decimal, getcontext
# Set high precision for Decimal
getcontext().prec = 100
import math
import sympy as sp
from mpmath import mp, frac, power, mpf  # For golden ratio heuristic

# Z5D Port (simplified double-precision)
E_FOURTH = 54.59815003314424
CALIBRATIONS = [(-0.00247, 0.04449, 0.3), (-0.00037, -0.11446, 0.3*0.809),
                (-0.0001, -0.15, 0.3*0.5), (-0.00002, -0.10, 0.3*0.333)]
SCALE_THRESHOLDS = [0, 1e7, 1e10, 1e12, float('inf')]

def z5d_predict(k):
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
    lnlnk = math.log(lnk)
    pnt = k * (lnk + lnlnk - 1 + (lnlnk - 2) / lnk)
    if pnt <= 1:
        return 0
    d = (math.log(pnt) / E_FOURTH) ** 2 if math.log(pnt) > 0 else 0
    e = pnt ** (-1/3) if pnt > 0 else 0
    pred = pnt + c * d * pnt + kstar * e * pnt
    return max(pred, pnt) if pred < 0 else pred

# High-precision Z5D using Decimal
def z5d_predict_high_prec(k_str):
    k = Decimal(k_str)
    if k < 1:
        raise ValueError("k >=1")
    ln_k = k.ln()
    pred = (k * ln_k + k) * Decimal(math.e) ** (Decimal(0.3) * ln_k)  # Theta adj, k_exp=0.3
    return pred.quantize(Decimal('1.'), rounding='ROUND_HALF_EVEN')

# Rough pi(x) approx for estimating number of primes <= limit
def approx_pi(limit):
    return limit / math.log(limit) if limit > 1 else 0

# Golden Ratio Heuristic (from discussion, simplified)
mp.dps = 50  # High precision
phi = (1 + mp.sqrt(5)) / 2

def theta(m, k_exp):
    m_over_phi = m / phi
    frac_m = frac(m_over_phi)
    powered = power(frac_m, k_exp)
    return frac(phi * powered)

def circular_dist(a, b):
    diff = abs(a - b)
    return min(diff, 1 - diff)

def factor_with_z5d_heuristic(N, k_exp=10, epsilon=0.001, sample_frac=0.5):
    from math import sqrt
    sqrt_n = int(sqrt(N)) + 1
    full_pi = int(approx_pi(sqrt_n))
    primes = []
    stride = max(1, int(1 / sample_frac))
    for kk in range(1, full_pi + 1, stride):
        pred = z5d_predict(kk)
        # Check range around prediction (error margin ~0.01% * pred)
        margin = max(50, int(0.01 * pred))
        for cand in range(int(pred - margin), int(pred + margin + 1)):
            if sp.isprime(cand):
                primes.append(cand)
    primes = sorted(set(primes))  # Dedup and sort

    theta_n = theta(N, k_exp)
    candidates = []
    for p in primes:
        theta_p = theta(p, k_exp)
        if circular_dist(theta_n, theta_p) < epsilon:
            candidates.append(p)

    for cand in candidates:
        if N % cand == 0:
            return cand, N // cand
    return None, None  # Not found

# Example usage (from discussion)
N = 170629  # 17 * 10037
p, q = factor_with_z5d_heuristic(N)
print(f"Factors: {p}, {q}")
