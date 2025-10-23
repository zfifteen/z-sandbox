import os, time
from pathlib import Path
import hashlib
from ecm_backend import run_ecm_once, backend_info

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
    # Guards against false positives
    if N.bit_length() < 250:
        raise ValueError(f"N too small for 256-bit path: {N.bit_length()} bits")

    # quick exit for trivial cases
    # Optional P-1 sweep for easy wins
    # (placeholder; GMP-ECM supports -pm1)
    pass  # Skip for now    if is_probable_prime(N):
        return None, None

    # Resolve checkpoint directory (env overrides)
    if checkpoint_dir is None:
        checkpoint_dir = os.environ.get("ECM_CKDIR", "checkpoints")
    # Resolve sigma mode (env overrides)
    if not use_sigma:
        use_sigma = os.environ.get("ECM_SIGMA", "0") == "1"

    for (_, B1, curves) in ECM_SCHEDULE:
        sigma = _compute_sigma_u64(N, B1) if use_sigma else None
        f = run_ecm_once(
            N, B1, curves, per_stage_timeout_sec,
            checkpoint_dir=checkpoint_dir,
            sigma=sigma,
            allow_resume=True,
        )
        if f:
            p, q = f, N // f
            # Final integrity checks
            if p*q == N and is_probable_prime(p) and is_probable_prime(q) and min(p.bit_length(), q.bit_length()) >= 120:
                return (min(p, q), max(p, q))
            # If integrity failed, keep searching
    return None, None
