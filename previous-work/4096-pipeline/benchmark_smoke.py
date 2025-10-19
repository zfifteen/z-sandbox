#!/usr/bin/env python3
"""
Quick-and-dirty keygen smoke benchmark.

Runs a couple of iterations of:
  1. Z5D RSA key generator (this directory's binary)
  2. Stock OpenSSL `genpkey` for RSA-4096

Records wall-clock durations so we can check whether the Z5D harness
appears faster before investing in larger sample sizes.
"""

from __future__ import annotations

import subprocess
import tempfile
import time
from pathlib import Path
from statistics import mean
from typing import Iterable, List, Tuple


HERE = Path(__file__).resolve().parent
Z5D_BIN = HERE / "z5d_secure_key_gen"
OPENSSL_BIN = Path("/usr/bin/openssl")

# Small sample to keep the smoke test cheap.
DEFAULT_ITERATIONS = 20


def run_timed(cmd: Iterable[str]) -> Tuple[float, subprocess.CompletedProcess[str]]:
    start = time.perf_counter()
    proc = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        cwd=str(HERE),
        check=False,
    )
    elapsed = time.perf_counter() - start
    return elapsed, proc


def run_z5d(iterations: int) -> List[float]:
    durations: List[float] = []
    for _ in range(iterations):
        elapsed, proc = run_timed([str(Z5D_BIN)])
        durations.append(elapsed)
        if proc.returncode != 0:
            raise RuntimeError(
                f"z5d_secure_key_gen failed (status {proc.returncode}):\n{proc.stderr}"
            )
    return durations


def run_openssl(iterations: int) -> List[float]:
    durations: List[float] = []
    for i in range(iterations):
        with tempfile.NamedTemporaryFile(prefix=f"openssl_key_{i}_", suffix=".pem", delete=False) as tmp:
            out_path = Path(tmp.name)
        cmd = [
            str(OPENSSL_BIN),
            "genpkey",
            "-algorithm",
            "RSA",
            "-pkeyopt",
            "rsa_keygen_bits:4096",
            "-out",
            str(out_path),
        ]
        elapsed, proc = run_timed(cmd)
        durations.append(elapsed)
        if proc.returncode != 0:
            raise RuntimeError(
                f"openssl genpkey failed (status {proc.returncode}):\n{proc.stderr}"
            )
        out_path.unlink(missing_ok=True)
    return durations


def summarize(label: str, durations: List[float]) -> None:
    if not durations:
        print(f"{label}: no samples")
        return
    print(f"{label}: {len(durations)} runs")
    print(f"  min   {min(durations):.3f}s")
    print(f"  max   {max(durations):.3f}s")
    print(f"  mean  {mean(durations):.3f}s")


def main(argv: Iterable[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark Z5D vs OpenSSL RSA keygen.")
    parser.add_argument(
        "-n",
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help="number of runs per generator (default: %(default)s)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.iterations <= 0:
        raise SystemExit("Iterations must be positive")

    if not Z5D_BIN.exists():
        raise SystemExit(f"Missing Z5D binary at {Z5D_BIN}")
    if not OPENSSL_BIN.exists():
        raise SystemExit(f"Missing OpenSSL binary at {OPENSSL_BIN}")

    print(f"Running Z5D benchmark ({args.iterations} runs)...")
    z5d_times = run_z5d(args.iterations)
    summarize("Z5D", z5d_times)
    print("Runs:", " ".join(f"{t:.2f}s" for t in z5d_times))

    print(f"\nRunning OpenSSL benchmark ({args.iterations} runs)...")
    openssl_times = run_openssl(args.iterations)
    summarize("OpenSSL", openssl_times)
    print("Runs:", " ".join(f"{t:.2f}s" for t in openssl_times))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
