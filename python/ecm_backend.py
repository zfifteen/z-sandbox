# python/ecm_backend.py
import shutil
ECM_BIN = shutil.which("ecm")
BACKEND = "gmp-ecm" if ECM_BIN else "pyecm"

def run_ecm_once(N: int, B1: int, curves: int, timeout_sec: int):
    if BACKEND == "gmp-ecm":
        import subprocess, shlex
        cmd = f"ecm -q -one -c {curves} {B1}"
        p = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            out, _ = p.communicate(input=str(N) + "\n", timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            p.kill(); return None
        for line in out.splitlines():
            s = line.strip()
            if s.isdigit():
                f = int(s)
                if 1 < f < N and (N % f) == 0:
                    return f
        return None
    else:
        # pyecm fallback – slower; only for dev boxes without gmp-ecm
        import pyecm
        # pyecm factor() returns a list of prime factors (not guaranteed in one pass)
        fs = pyecm.factors(N, True, False, B1=B1)
        for f in fs:
            if 1 < f < N and (N % f) == 0:
                return f
        return None