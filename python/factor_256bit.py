import os, time
from pathlib import Path
import hashlib
from ecm_backend import run_ecm_once, backend_info
from math import gcd, ceil, sqrt

def is_probable_prime(n, k=12) -> bool:
    if n < 2: return False
    small_primes = [2,3,5,7,11,13,17,19,23,29,31]
    for p in small_primes:
        if n % p == 0:
            return n == p
    # Miller-Rabin (deterministic for 64-bit; probabilistic otherwise)
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

def _compute_sigma_u64(N: int, B1: int) -> int:
    """
    Deterministic curve seed from blake2b(N||B1). Keep within uint64.
    """
    h = hashlib.blake2b(f"{N}:{B1}".encode(), digest_size=16).digest()
    # take lower 8 bytes as unsigned 64-bit
    return int.from_bytes(h[-8:], "little") or 1

ECM_SCHEDULE = [
    # (target_digits, B1, curves)
    (35,   1_000_000,   1800),
    (40,   3_000_000,   5100),
    (45,  11_000_000,  10600),
    (50,  43_000_000,  19300),
]

def factor_256bit(
    N: int,
    per_stage_timeout_sec: int = 1200,
    checkpoint_dir: str | None = None,
    use_sigma: bool = False,
):
    # ... existing code ...
    pass  # Keep existing

def verify_factors(N, p, q):
    return p * q == N and is_probable_prime(p) and is_probable_prime(q)

def pollard_rho(N, max_iterations=10000):
    if N % 2 == 0:
        return 2
    def f(x):
        return (x*x + 1) % N
    x = 2
    y = 2
    d = 1
    for i in range(max_iterations):
        x = f(x)
        y = f(f(y))
        d = gcd(abs(x - y), N)
        if d > 1:
            return d
    return None

def fermat_factorization(N, max_iterations=100):
    if N % 2 == 0:
        return (2, N//2)
    a = ceil(sqrt(N))
    for i in range(max_iterations):
        b2 = a*a - N
        b = int(sqrt(b2))
        if b*b == b2:
            return (a - b, a + b)
        a += 1
    return None

def try_pollard_rho(N, max_iterations=10000):
    factor = pollard_rho(N, max_iterations)
    if factor and factor != N:
        return factor
    return None

def try_fermat(N, max_iterations=100):
    result = fermat_factorization(N, max_iterations)
    if result:
        p, q = result
        if p != q:
            return p
    return None

class FactorizationPipeline:
    def __init__(self, N, timeout_seconds=30):
        self.N = N
        self.timeout = timeout_seconds

    def run(self):
        start = time.time()
        # Try pollard rho
        factor = try_pollard_rho(self.N)
        if factor:
            elapsed = time.time() - start
            return ([factor, self.N // factor], 'pollard_rho', elapsed, {})
        # Try fermat
        factor = try_fermat(self.N)
        if factor:
            elapsed = time.time() - start
            return ([factor, self.N // factor], 'fermat', elapsed, {})
        # No factor found
        elapsed = time.time() - start
        return (None, None, elapsed, {})
