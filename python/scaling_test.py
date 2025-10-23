import json, time, argparse, importlib, datetime
from pathlib import Path
from factor_256bit import factor_256bit, ECM_SCHEDULE
from ecm_backend import backend_info
from targets import load_256bit_targets  # your generator/loader

LOG = Path("logs/256bit_breakthrough_log.md")
LOG.parent.mkdir(parents=True, exist_ok=True)

def _append_log(row: dict) -> None:
    with open(LOG, "a") as f:
        f.write(json.dumps(row) + "\n")

def _maybe_theta_gate(N: int):
    """
    Try to call a theta-gate if available:
    - manifold_128bit.theta_gate(N) or
    - manifold_128bit.theta_prime_gate(N) or
    returns None if unavailable.
    """
    try:
        m = importlib.import_module("manifold_128bit")
        for fn in ("theta_gate", "theta_prime_gate"):
            if hasattr(m, fn):
                return getattr(m, fn)(N)
    except Exception:
        pass
    return None

def run_batch(timeout_per_stage=1200, max_targets=100, checkpoint_dir=None, use_sigma=False, single_N=None):
    # Run metadata header (once)
    meta = backend_info()
    meta.update({
        "meta": "RUN",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "schedule_B1": [B1 for _, B1, _ in ECM_SCHEDULE],
        "schedule_curves": [curves for *_, curves in ECM_SCHEDULE],
        "timeout_per_stage": timeout_per_stage,
        "use_sigma": bool(use_sigma),
        "checkpoint_dir": checkpoint_dir or "checkpoints",
    })
    _append_log(meta)

    if single_N is not None:
        T = [single_N]
    else:
        T = load_256bit_targets(max_targets)

    for i, N in enumerate(T, 1):
        t0 = time.time()
        theta_gate = _maybe_theta_gate(N)
        result = {
            "i": i,
            "bits": N.bit_length(),
            "N_head": str(N)[:20],
            "timeout_stage": timeout_per_stage,
            "theta_gate": theta_gate,
        }
        try:
            p, q = factor_256bit(N, per_stage_timeout_sec=timeout_per_stage, checkpoint_dir=checkpoint_dir, use_sigma=use_sigma)
            dt = time.time() - t0
            if p and q:
                result.update({
                    "status": "factored",
                    "time_sec": round(dt, 3),
                    "p_bits": p.bit_length(),
                    "q_bits": q.bit_length(),
                    "min_factor_bits": min(p.bit_length(), q.bit_length()),
                    "integrity": (p*q == N),
                })
            else:
                result.update({"status": "not_factored", "time_sec": round(dt, 3)})
        except Exception as e:
            result.update({"status": "error", "error": str(e)})
        _append_log(result)

def _parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout-per-stage", type=int, default=1200)
    ap.add_argument("--count", type=int, default=100)
    ap.add_argument("--single", type=int, default=None, help="Run a single N (decimal)")
    ap.add_argument("--checkpoint-dir", type=str, default=None)
    ap.add_argument("--use-sigma", action="store_true", help="Enable deterministic -sigma seeding")
    return ap.parse_args()

if __name__ == "__main__":
    args = _parse_args()
    run_batch(
        timeout_per_stage=args.timeout_per_stage,
        max_targets=args.count,
        checkpoint_dir=args.checkpoint_dir,
        use_sigma=args.use_sigma,
        single_N=args.single,
    )
