import os, time, json, math
import mpmath as mp

mp.mp.dps = 50

PHI = (1 + mp.sqrt(5)) / 2


def frac(x):
    return x - mp.floor(x)


def theta_prime(n, k=0.3):
    return frac(PHI * (frac(n / PHI) ** k))


def run(n_max=1000, k=0.3):
    rows = []
    for n in range(2, n_max + 1):
        rows.append({"n": n, "theta": float(theta_prime(n, k))})
    return rows


if __name__ == "__main__":
    out_dir = "out/phi_bias"
    os.makedirs(out_dir, exist_ok=True)
    run_id = time.strftime("%Y%m%d_%H%M%S")
    path = f"{out_dir}/{run_id}.jsonl"
    with open(path, "w") as f:
        for r in run(n_max=5000, k=0.3):
            f.write(
                json.dumps(
                    {"ts": time.time(), "exp": "phi_bias", "params": {"k": 0.3}, "row": r}
                )
                + "\n"
            )
    print("wrote", path)
