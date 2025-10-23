import os, time, math, random
from pathlib import Path
import pyecm

def is_probable_prime(n, k=12):
    if n < 2: return False
    # Miller-Rabin (deterministic for 64-bit; probabilistic otherwise)
    small_primes = [2,3,5,7,11,13,17,19,23,29,31]
    for p in small_primes:
        if n % p == 0:
            return n == p
    # write MR quickly
    d, r = n-1, 0
    while d % 2 == 0: d //= 2; r += 1
    def check(a):
        x = pow(a, d, n)
        if x == 1 or x == n-1: return True
        for _ in range(r-1):
            x = (x * x) % n
            if x == n-1: return True
        return False
    for a in [2,325,9375,28178,450775,9780504,1795265022][:k]:
        a %= n
        if a in (0,1): 
            continue
        if not check(a):
            return False
    return True

    """
    Returns a nontrivial factor or None.
    Uses: ecm -q -one -c {curves} {B1}
    """
    cmd = f"ecm -q -one -c {curves} {B1}"
    try:
        proc = subprocess.Popen(
            shlex.split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
    except FileNotFoundError:
        raise RuntimeError("ecm not found. Install GMP-ECM (e.g., brew install gmp-ecm)")

    try:
        out, err = proc.communicate(input=str(N) + "\n", timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        proc.kill()
        return None

    f = parse_ecm_factor(out)
    if f and 1 < f < N and N % f == 0:
        return f
    return None

def run_ecm_once(N: int, B1: int, curves: int, timeout_sec: int) -> int | None:
    """
    Returns a nontrivial factor or None.
    Uses pyecm.ecm
    """
    try:
        factors = pyecm.ecm(N, B1=B1, curves=curves, timeout=timeout_sec)
        if factors:
            for f in factors:
                if 1 < f < N and N % f == 0:
                    return f
    except:
        pass
    return None

ECM_SCHEDULE = [
    # (target_digits, B1, curves)
    (35,   1_000_000,   1800),
    (40,   3_000_000,   5100),
    (45,  11_000_000,  10600),
    (50,  43_000_000,  19300),
]

def factor_256bit(N: int, per_stage_timeout_sec=1200):
    # Guards against false positives
    if N.bit_length() < 250:
        raise ValueError(f"N too small for 256-bit path: {N.bit_length()} bits")

    # quick exit for trivial cases
    if is_probable_prime(N):
        return None, None

    for (_, B1, curves) in ECM_SCHEDULE:
        f = run_ecm_once(N, B1, curves, per_stage_timeout_sec)
        if f:
            p, q = f, N // f
            # Final integrity checks
            if p*q == N and is_probable_prime(p) and is_probable_prime(q) and min(p.bit_length(), q.bit_length()) >= 120:
                return (min(p, q), max(p, q))
            # If integrity failed, keep searching
    return None, None
