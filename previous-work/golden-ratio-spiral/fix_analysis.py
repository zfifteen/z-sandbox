import mpmath as mp
mp.mp.dps = 50

# Full OEIS A000043: Mersenne prime exponents (known as of 2023; deterministic, reproducible)
EXPS = [
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279, 2203, 2281, 3217, 4253, 4423, 9689, 9941, 11213, 19937, 21701, 23209, 44497, 86243, 110503, 132049, 216091, 756839, 859433, 1257787, 1398269, 2976221, 3021377, 6972593, 13466917, 20996011, 24036583, 25964951, 30402457, 32582657, 37156667, 42643801, 43112609, 57885161, 74207281, 77232917, 82589933
]

def analyze_mersenne_exps(exps):
    if len(exps) < 3:
        raise ValueError("Need ≥3 exponents")
    exps = [mp.mpf(x) for x in exps]
    # Ratio form with c = 2
    r = [exps[i]/exps[i-1] for i in range(1, len(exps))]
    Z_ratio = [ri / mp.mpf(2) for ri in r]     # expect ~1 with structure
    eps_ratio = [mp.log(ri/mp.mpf(2)) for ri in r]  # centered residuals

    # Log2 increment form with c = 1
    lg = [mp.log(exps[i], 2) - mp.log(exps[i-1], 2) for i in range(1, len(exps))]
    Z_log = lg  # c=1

    def stats(x):
        m = sum(x) / len(x)
        v = sum((xi - m)**2 for xi in x) / (len(x)-1)
        return float(m), float(mp.sqrt(v))

    mean_Z_ratio, sd_Z_ratio = stats(Z_ratio)
    mean_eps_ratio, sd_eps_ratio = stats(eps_ratio)
    mean_Z_log, sd_Z_log       = stats(Z_log)

    return {
        "ratio_form": {"mean(Z_ratio)": mean_Z_ratio, "sd(Z_ratio)": sd_Z_ratio,
                       "mean(log residual)": mean_eps_ratio, "sd(log residual)": sd_eps_ratio},
        "log2_increment_form": {"mean(g_i)": mean_Z_log, "sd(g_i)": sd_Z_log}
    }

def parse_spiral_data(filepath):
    DATA = []
    with open(filepath, 'r') as f:
        for line in f:
            if 'center:' in line and 'iterations:' in line and 'value:' in line:
                parts = line.split()
                center = int(parts[1])
                iterations = int(parts[3])
                value = float(parts[5])
                area = float(parts[7]) if len(parts) > 7 else 1.0  # default area=1 if missing
                DATA.append((center, iterations, value, area))
    return DATA

def spiral_refit(rows, use_area=True):
    # Build per-center normalized rate: B = iterations / area (if known)
    # Avoid log(0) and cross-scale pooling without an intercept
    centers = sorted(set(r[0] for r in rows))
    out = {}
    for c in centers:
        S = [(mp.mpf(it), mp.mpf(z), mp.mpf(a) if use_area else mp.mpf(1))
             for (cc,it,z,a) in rows if cc == c]
        if len(S) < 5:  # need minimal sample
            continue
        B = [ (it / a) for (it,z,a) in S ]  # rate proxy
        Z = [ z for (it,z,a) in S ]
        # log-log fit: log Z = beta0 + beta1 * log B
        x = [ mp.log(b) for b in B if b > 0 ]
        y = [ mp.log(z) for (b,z) in zip(B,Z) if b > 0 and z > 0 ]
        n = min(len(x), len(y))
        x, y = x[:n], y[:n]
        # OLS on (x,y) with mpmath
        sx, sy = sum(x), sum(y)
        sxx = sum(xi*xi for xi in x)
        sxy = sum(xi*yi for xi,yi in zip(x,y))
        denom = n*sxx - sx*sx
        if denom == 0:
            beta1 = mp.mpf(0)
        else:
            beta1 = (n*sxy - sx*sy) / denom
        beta0 = (sy - beta1*sx) / n
        # R^2
        yhat = [ beta0 + beta1*xi for xi in x ]
        ybar = sy/n
        ss_tot = sum((yi - ybar)**2 for yi in y)
        ss_res = sum((yi - yh)**2 for yi,yh in zip(y,yhat))
        R2 = 1 - ss_res/ss_tot if ss_tot != 0 else mp.mpf('0')
        out[c] = {"beta0": float(beta0), "beta1": float(beta1), "R2": float(R2), "n": n}
    return out

if __name__ == "__main__":
    print("=== Mersenne Exponents Analysis ===")
    mersenne_result = analyze_mersenne_exps(EXPS)
    print(mersenne_result)
    
    print("\n=== Spiral Candidates Refit ===")
    filepath = "/Users/velocityworks/IdeaProjects/unified-framework/src/c/golden-ratio-spiral/golden_spiral_out.txt"
    DATA = parse_spiral_data(filepath)
    if not DATA:
        print("No data parsed from golden_spiral_out.txt")
    else:
        spiral_result = spiral_refit(DATA, use_area=True)
        print(spiral_result)