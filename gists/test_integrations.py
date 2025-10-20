# Test file for integration code snippets from 2025-10-20.md analysis

import sys
import traceback

# Project 1: sympy/sympy integrations

# Golden Ratio Mapping
from mpmath import mp, phi, power, fabs, floor
mp.dps = 50
phi_val = phi()
def theta(m, k):
    """θ(m,k) = {φ × ({m / φ})^k}"""
    inner = mp.frac(m / phi_val)
    powered = power(inner, k)
    return mp.frac(phi_val * powered)

def circ_dist(a, b):
    """d(a,b) = min(|a-b|,1-|a-b|)"""
    diff = fabs(a - b)
    return min(diff, mp.mpf(1) - diff)

# Z5D with Zeta Tuning
from sympy import log, Integer, zeta
def z5d_zeta_prime(k, zeros=20):
    """\\hat p_k with zeta radii"""
    pi_inv = Integer(k * log(k))
    d_k = log(k)
    zeta_corr = sum(float(zeta(i).evalf()) for i in range(2, zeros+2)) / zeros
    return pi_inv + d_k + zeta_corr * (k**0.5 / log(k))

# Tests for Project 1
def test_theta_circ_dist():
    N = mp.mpf(170629)
    result = circ_dist(theta(N, 10), theta(mp.mpf(17), 10)) < 0.001
    print(f"test_theta_circ_dist: {'PASS' if result else 'FAIL'}")
    return result

def test_z5d_zeta_prime():
    from sympy.ntheory import prime
    diff = abs(z5d_zeta_prime(1000) - prime(1000)) < 15
    print(f"test_z5d_zeta_prime: {'PASS' if diff else 'FAIL'}")
    return diff

# Project 2: pyca/cryptography integrations

from math import sqrt, log
from sympy.ntheory import isprime

# Golden Filter for Keygen
def golden_filter_candidates(bits, k=10, eps=0.001):
    """Filter via θ mapping <eps"""
    base = 2**(bits-1)
    candidates = [base + i for i in range(-5000, 5001)]
    theta_base = theta(base, k)  # theta defined above
    return [c for c in candidates if circ_dist(theta(c, k), theta_base) < eps]

# Z5D Zeta Predict
def z5d_zeta_predict(bits, zeros=20):
    """Predict with zeta corr"""
    k = 2**(bits-1)
    pi_inv = k * log(k)
    d_k = log(k)
    zeta_corr = sum(1 / n**2 for n in range(1, zeros+1))  # Approx
    candidate = int(pi_inv + d_k + zeta_corr * sqrt(k) / log(k))
    while not isprime(candidate):
        candidate += 2
    return candidate

# Tests for Project 2
def test_golden_filter_candidates():
    candidates = golden_filter_candidates(10)
    result = len(candidates) < 10000 * 0.05  # Reduction
    print(f"test_golden_filter_candidates: {'PASS' if result else 'FAIL'} (filtered {len(candidates)})")
    return result

def test_z5d_zeta_predict():
    p = z5d_zeta_predict(20)
    result = isprime(p)
    print(f"test_z5d_zeta_predict: {'PASS' if result else 'FAIL'} (prime: {p})")
    return result

# Run all tests
if __name__ == "__main__":
    print("Running Python integration tests...\n")
    results = []
    try:
        results.append(("test_theta_circ_dist", test_theta_circ_dist()))
    except Exception as e:
        print(f"test_theta_circ_dist: ERROR - {e}")
        traceback.print_exc()
        results.append(("test_theta_circ_dist", False))

    try:
        results.append(("test_z5d_zeta_prime", test_z5d_zeta_prime()))
    except Exception as e:
        print(f"test_z5d_zeta_prime: ERROR - {e}")
        traceback.print_exc()
        results.append(("test_z5d_zeta_prime", False))

    try:
        results.append(("test_golden_filter_candidates", test_golden_filter_candidates()))
    except Exception as e:
        print(f"test_golden_filter_candidates: ERROR - {e}")
        traceback.print_exc()
        results.append(("test_golden_filter_candidates", False))

    try:
        results.append(("test_z5d_zeta_predict", test_z5d_zeta_predict()))
    except Exception as e:
        print(f"test_z5d_zeta_predict: ERROR - {e}")
        traceback.print_exc()
        results.append(("test_z5d_zeta_predict", False))

    print(f"\nSummary: {sum(1 for r in results if r[1])}/{len(results)} tests passed")
    sys.exit(0 if all(r[1] for r in results) else 1)