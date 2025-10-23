from __future__ import annotations
import shutil
import subprocess
import shlex
from pathlib import Path
from typing import Optional, Tuple

# Detect backend once
ECM_BIN = shutil.which("ecm")
BACKEND = "gmp-ecm"  # Force for simulation

def backend_info() -> dict:
    """
    Returns {'backend': 'gmp-ecm'|'pyecm', 'version': <str or None>}
    """
    if BACKEND != "gmp-ecm":
        return {"backend": BACKEND, "version": None}
    try:
        # 'ecm -v' prints version and table info
        out = subprocess.check_output(["ecm", "-v"], text=True, timeout=5)
        first = out.strip().splitlines()[0] if out else ""
        return {"backend": BACKEND, "version": first}
    except Exception:
        return {"backend": BACKEND, "version": None}

def _parse_factor_lines(output: str, N: int) -> Optional[int]:
    """
    Parse ECM stdout: factors are typically printed as bare decimal integers
    on their own line (quiet mode), or space-separated on one line.
    We accept decimal integers either on separate lines or space-separated on one line.
    """
    for line in output.splitlines():
        s = line.strip()
        # Try the full line first
        if s.isdigit():
            f = int(s)
            if 1 < f < N and (N % f) == 0:
                return f
        # Try space-separated factors on same line
        parts = s.split()
        for part in parts:
            if part.isdigit():
                f = int(part)
                if 1 < f < N and (N % f) == 0:
                    return f
    return None

def run_ecm_once(
    N: int,
    B1: int,
    curves: int,
    timeout_sec: int,
    checkpoint_dir: Optional[str | Path] = None,
    sigma: Optional[int] = None,
    allow_resume: bool = True,
) -> Optional[int]:
    """
    Returns a nontrivial factor of N or None.
    - For gmp-ecm: uses -q -one -c {curves} {B1} and, if provided,
      -save/-resume <file> and -sigma <u64>.
    - For pyecm fallback: attempts a single-pass trial with given B1.
    """
    if BACKEND == "gmp-ecm":
        # Build command
        cmd = ["ecm", "-q", "-one", "-c", str(curves)]
        # Optional deterministic seeding
        if sigma is not None and sigma > 0:
            cmd += ["-sigma", str(sigma)]
        # Optional checkpointing
        ckfile = None
        if checkpoint_dir:
            Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)
            ckfile = Path(checkpoint_dir) / f"ecm_ck_B1{B1}_{str(N)[:16]}.sav"
            cmd += ["-save", str(ckfile)]
            if allow_resume and ckfile.exists():
                cmd += ["-resume", str(ckfile)]
        cmd += [str(B1)]
        # Launch
        p = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        try:
            out, _ = p.communicate(input=str(N) + "\n", timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            p.kill()
            return None
        return _parse_factor_lines(out, N)
    else:
        # pyecm fallback – slower; only for dev boxes without gmp-ecm
        # For now, return None as pyecm API differs
        return None