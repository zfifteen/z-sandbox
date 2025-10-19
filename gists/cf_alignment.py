#!/usr/bin/env python3
"""
Continued-Fraction Alignment Module for Geometric Factorization
Refines α values via CF convergents to minimize angular errors for better boundary crossing.
"""

from decimal import Decimal, getcontext, ROUND_HALF_EVEN
import math

def set_precision(prec=120):
    getcontext().prec = prec
    getcontext().rounding = ROUND_HALF_EVEN

# Base α family
BASES = {
    'phi': Decimal('1.6180339887498948'),
    'e':   Decimal('2.7182818284590452'),
    'pi':  Decimal('3.1415926535897932'),
    'sqrt2': Decimal('1.4142135623730951'),
    'silver': Decimal('2.4142135623730951'),
    'sqrt3': Decimal('1.7320508075688772'),
}

def decimal_ln(x: Decimal) -> Decimal:
    return x.ln()

def cf_expansion(x: Decimal, max_terms=20):
    """Simple continued fraction coefficients for x > 0."""
    a = []
    y = x
    for _ in range(max_terms):
        ai = int(y)  # floor
        a.append(ai)
        frac = y - Decimal(ai)
        if frac == 0:
            break
        y = Decimal(1) / frac
    return a

def cf_convergents(a):
    """Return convergents (p, q) from CF coefficients a."""
    # H/K recurrence
    p_prev, p = 1, a[0]
    q_prev, q = 0, 1
    convs = [(p, q)]
    for ai in a[1:]:
        p_prev, p = p, ai*p + p_prev
        q_prev, q = q, ai*q + q_prev
        convs.append((p, q))
    return convs

def refine_alphas_via_cf(N: int, bases=BASES, max_convergents=10, precision=120):
    set_precision(precision)
    lnN = Decimal(N).ln()
    aligned = []
    for name, a0 in bases.items():
        lnA0 = a0.ln()
        ratio = lnN / lnA0  # r = log N / log α0
        coeffs = cf_expansion(ratio, max_terms=max_convergents)
        convs = cf_convergents(coeffs)[:max_convergents]
        for idx, (p, q) in enumerate(convs):
            # α = α0^(p/q)
            exponent = Decimal(p) / Decimal(q)
            alpha = (a0 ** exponent)
            aligned.append({
                'base': name,
                'a0': a0,
                'p': int(p),
                'q': int(q),
                'alpha': alpha,
                'cf_index': idx,
                'ratio': ratio
            })
    return aligned

def theta_mod1_log(x: int, alpha: Decimal) -> float:
    t = (alpha * Decimal(x).ln()) % Decimal(1)
    return float(t)

def circ_dist(a: float, b: float) -> float:
    d = abs(a - b)
    return d if d <= 0.5 else 1.0 - d

def circular_mean(ts):
    """Compute circular mean of angles in [0,1)"""
    if not ts:
        return 0.0
    # Convert to complex, average, get angle
    import cmath
    z = sum(cmath.exp(2j * math.pi * t) for t in ts) / len(ts)
    angle = cmath.phase(z) / (2 * math.pi)
    return angle % 1.0

def renormalize_angles(values, alpha: Decimal):
    """Renormalize angles by subtracting circular mean"""
    ts = [theta_mod1_log(v, alpha) for v in values]
    mu = circular_mean(ts)
    res = [((t - mu) % 1.0) for t in ts]
    return mu, res

def score_candidate_cf(N: int, cand: int, aligned_alphas, window_vals):
    """Score candidate using CF-aligned alphas with renormalization"""
    scores = []
    # Precompute mu for each alpha (in practice, cache this)
    mus = {}
    for info in aligned_alphas:
        a = info['alpha']
        if a not in mus:
            mus[a] = renormalize_angles(window_vals, a)[0]

    for info in aligned_alphas:
        a = info['alpha']
        mu = mus[a]
        tN = (theta_mod1_log(N, a) - mu) % 1.0
        tc = (theta_mod1_log(cand, a) - mu) % 1.0
        score = circ_dist(tN, tc)
        scores.append((score, info))

    # Return best score and which α achieved it
    best = min(scores, key=lambda x: x[0])
    return best[0], best[1], scores