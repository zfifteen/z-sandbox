import sympy as sp
from mpmath import mp
phi = (1 + mp.sqrt(5)) / 2
def frac(x):
    return x - mp.floor(x)
def theta(m, k):
    a = frac(m / phi)
    b = mp.power(a, k)
    return frac(phi * b)
def circ_dist(a, b):
    diff = mp.fabs(a - b)
    return min(diff, 1 - diff)
def multi_stage_geometric_factorize(N, stages):
    mp.dps = 50
    mp_n = mp.mpf(N)
    sqrt_n = int(N**0.5) + 1
    candidates = list(sp.primerange(2, sqrt_n + 1))
    for k, epsilon in stages:
        th_n = theta(mp_n, k)
        new_cands = []
        for p in candidates:
            mp_p = mp.mpf(p)
            th_p = theta(mp_p, k)
            d = circ_dist(th_n, th_p)
            if d < epsilon:
                new_cands.append(p)
                if N % p == 0:
                    return p, N // p
        candidates = new_cands
    return None

print(multi_stage_geometric_factorize(1099511641871, [(5, 0.05), (10, 0.002), (15, 0.0001)]))
