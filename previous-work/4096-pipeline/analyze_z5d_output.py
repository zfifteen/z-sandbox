#!/usr/bin/env python3
"""Analyze z5d_secure_key_gen output and print statistical highlights."""

from __future__ import annotations

import pathlib
import re
from statistics import mean
from decimal import Decimal, getcontext
import argparse
import sys


DEFAULT_OUTPUT = pathlib.Path(__file__).with_name("z5d_secure_key_gen_out.txt")


def new_run() -> dict[str, object | None]:
    return {
        "run_id": None,
        "seed_source": None,
        "bits": None,
        "exponent": None,
        "validity": None,
        "kappa_geo": None,
        "kappa_star": None,
        "phi": None,
        "bump_p": None,
        "bump_q": None,
        "x_p_bits": None,
        "x_q_bits": None,
        "p_bits": None,
        "q_bits": None,
        "k_base_p": None,
        "k_base_q": None,
        "attempts": [],
        "threads": None,
        "total_time_ms": None,
    }


def finalize_run(current: dict[str, object | None], runs: list[dict[str, object | None]]) -> None:
    if current["run_id"] is not None:
        runs.append(current.copy())


def parse_runs(path: pathlib.Path) -> list[dict[str, object | None]]:
    runs: list[dict[str, object | None]] = []
    current = new_run()

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")

            match = re.match(r"=== Run (.+) ===", line)
            if match:
                finalize_run(current, runs)
                current = new_run()
                current["run_id"] = match.group(1)
                continue

            if current["seed_source"] is None:
                match = re.search(r"Seed: [0-9a-f]+ \(([^)]+)\)", line)
                if match:
                    current["seed_source"] = match.group(1)
                    continue

            if current["bits"] is None:
                match = re.search(r"  Bits: (\d+)", line)
                if match:
                    current["bits"] = match.group(1)
                    continue

            if current["exponent"] is None:
                match = re.search(r"  e: (\d+)", line)
                if match:
                    current["exponent"] = match.group(1)
                    continue

            if current["validity"] is None:
                match = re.search(r"  Validity: (\d+)", line)
                if match:
                    current["validity"] = match.group(1)
                    continue

            if current["kappa_geo"] is None:
                match = re.search(
                    r"kappa_geo=([0-9.]+), kappa_star=([0-9.]+), phi=([0-9.]+)",
                    line,
                )
                if match:
                    current["kappa_geo"], current["kappa_star"], current["phi"] = match.groups()
                    continue

            if current["bump_p"] is None:
                match = re.search(r"Bumps: p=(\d+), q=(\d+)", line)
                if match:
                    current["bump_p"], current["bump_q"] = match.groups()
                    continue

            if current["x_p_bits"] is None:
                match = re.search(r"x_p \((\d+)-bit\)", line)
                if match:
                    current["x_p_bits"] = match.group(1)
                    continue

            if current["x_q_bits"] is None:
                match = re.search(r"x_q \((\d+)-bit\)", line)
                if match:
                    current["x_q_bits"] = match.group(1)
                    continue

            if current["p_bits"] is None:
                match = re.match(r"p:\s*(\d+)$", line)
                if match:
                    current["p_bits"] = int(match.group(1)).bit_length()
                    continue

            if current["q_bits"] is None:
                match = re.match(r"q:\s*(\d+)$", line)
                if match:
                    current["q_bits"] = int(match.group(1)).bit_length()
                    continue

            if current["k_base_p"] is None:
                match = re.search(r"k_base_p: (\d+)", line)
                if match:
                    current["k_base_p"] = match.group(1)
                    continue

            if current["k_base_q"] is None:
                match = re.search(r"k_base_q: (\d+)", line)
                if match:
                    current["k_base_q"] = match.group(1)
                    continue

            match = re.search(r"Found prime after (\d+) attempts \(parallel\)", line)
            if match:
                attempts = current["attempts"]
                assert isinstance(attempts, list)
                attempts.append(int(match.group(1)))
                continue

            if current["threads"] is None:
                match = re.search(r"OpenMP parallel candidate search enabled \((\d+) threads\)", line)
                if match:
                    current["threads"] = match.group(1)
                    continue

            if current["total_time_ms"] is None:
                match = re.search(r"Total generation time: (\d+) ms", line)
                if match:
                    current["total_time_ms"] = match.group(1)

    finalize_run(current, runs)
    return runs


def summarize_runs(runs: list[dict[str, object | None]]) -> None:
    print(f"Total runs analyzed: {len(runs)}\n")

    if not runs:
        return

    def consistent(field: str) -> str:
        values = {run[field] for run in runs if run[field] is not None}
        if not values:
            return "unknown"
        if len(values) == 1:
            return values.pop()  # type: ignore[return-value]
        return f"mixed ({', '.join(sorted(str(v) for v in values))})"

    print("Configuration")
    print(f"- Entropy source: {consistent('seed_source')}")
    print(f"- RSA parameters: {consistent('bits')}-bit modulus, e={consistent('exponent')}")
    print(f"- Validity window: {consistent('validity')} days")
    print(
        f"- Z5D settings: kappa_geo={consistent('kappa_geo')}, "
        f"kappa_star={consistent('kappa_star')}, phi={consistent('phi')}"
    )
    print(f"- Bump offsets: p={consistent('bump_p')}, q={consistent('bump_q')}\n")

    print("Prime Material")
    print(f"- x_p width: {consistent('x_p_bits')} bits")
    print(f"- x_q width: {consistent('x_q_bits')} bits")
    print(f"- p bit-length: {consistent('p_bits')} bits")
    print(f"- q bit-length: {consistent('q_bits')} bits\n")

    getcontext().prec = 6
    if all(run.get("k_base_p") and run.get("k_base_q") for run in runs):
        ratios = [
            Decimal(str(run["k_base_p"])) / Decimal(str(run["k_base_q"]))  # type: ignore[arg-type]
            for run in runs
            if run.get("k_base_p") and run.get("k_base_q")
        ]
        if ratios:
            print("Prime Index Ratio")
            print(
                f"- k_base_p / k_base_q: min={min(ratios)}, "
                f"avg={sum(ratios) / len(ratios)}, max={max(ratios)}\n"
            )

    attempts_p = [
        (run["attempts"][0] if run.get("attempts") and len(run["attempts"]) >= 1 else None)
        for run in runs
    ]
    attempts_q = [
        (run["attempts"][1] if run.get("attempts") and len(run["attempts"]) >= 2 else None)
        for run in runs
    ]
    total_attempts = [
        (run["attempts"][0] + run["attempts"][1]
         if run.get("attempts") and len(run["attempts"]) >= 2 else None)
        for run in runs
    ]
    times = [int(run["total_time_ms"]) for run in runs if run.get("total_time_ms")]

    def stats(values: list[int | None]) -> tuple[str, str, str] | None:
        actual = [v for v in values if v is not None]
        if not actual:
            return None
        return (str(min(actual)), f"{mean(actual):.2f}", str(max(actual)))

    print("Search Effort & Timing")

    p_stats = stats(attempts_p)
    if p_stats:
        print(f"- Attempts to find p: min={p_stats[0]}, avg={p_stats[1]}, max={p_stats[2]}")

    q_stats = stats(attempts_q)
    if q_stats:
        print(f"- Attempts to find q: min={q_stats[0]}, avg={q_stats[1]}, max={q_stats[2]}")

    total_stats = stats(total_attempts)
    if total_stats:
        print(
            f"- Combined attempts: min={total_stats[0]}, avg={total_stats[1]}, max={total_stats[2]}"
        )

    if times:
        print(
            f"- Total generation time (ms): min={min(times)}, "
            f"avg={sum(times)/len(times):.2f}, max={max(times)}"
        )

        throughputs = [
            (total_attempts[i] / (times[i] / 1000.0))
            for i in range(len(runs))
            if total_attempts[i] is not None and times[i] > 0
        ]
        if throughputs:
            print(
                f"- Attempt throughput (attempts/sec): "
                f"min={min(throughputs):.1f}, avg={sum(throughputs)/len(throughputs):.1f}, "
                f"max={max(throughputs):.1f}"
            )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Summarize z5d key generator logs")
    parser.add_argument(
        "logfile",
        nargs="?",
        default=DEFAULT_OUTPUT,
        help="Path to log file (default: %(default)s)",
    )
    args = parser.parse_args(argv)

    log_path = pathlib.Path(args.logfile).expanduser()
    if not log_path.exists():
        print(f"error: log file not found: {log_path}", file=sys.stderr)
        sys.exit(1)

    runs = parse_runs(log_path)
    summarize_runs(runs)


if __name__ == "__main__":
    main()
