import json, time, math, argparse
from pathlib import Path
from factor_256bit import factor_256bit

LOG = Path("logs/256bit_breakthrough_log.md")
LOG.parent.mkdir(parents=True, exist_ok=True)

def log_row(result):
    with open(LOG, "a") as f:
        f.write(f"- {result}\n")

def run_batch(max_targets=100, timeout_per_stage=1200, single_N=None):
    with open('python/targets_filtered.json', 'r') as f:
        data = json.load(f)
    T = [int(t['N']) for t in data['targets'][:max_targets]]
    print(f"Running {len(T)} targets with per-stage timeout {timeout_per_stage}s")
    for i, N in enumerate(T, 1):
        t0 = time.time()
        result = {"i": i, "bits": N.bit_length(), "N_head": str(N)[:20], "timeout_stage": timeout_per_stage}
        try:
            p, q = factor_256bit(N, per_stage_timeout_sec=timeout_per_stage)
            dt = time.time() - t0
            if p and q:
                result |= {
                    "status": "factored",
                    "p_bits": p.bit_length(),
                    "q_bits": q.bit_length(),
                    "time_sec": round(dt, 3),
                    "integrity": (p*q == N),
                }
            else:
                result |= {"status": "not_factored", "time_sec": round(dt, 3)}
        except Exception as e:
            result |= {"status": "error", "error": str(e)}
        log_row(result)
        print(result)

if __name__ == "__main__":
    run_batch(max_targets=5, timeout_per_stage=30)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--single", help="Run single N")
    parser.add_argument("--timeout-per-stage", type=int, default=1200)
    args = parser.parse_args()
    run_batch(single_N=args.single, timeout_per_stage=args.timeout_per_stage)

