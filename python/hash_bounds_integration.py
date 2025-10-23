import json
import numpy as np
import mpmath as mp
mp.dps = 32

# Load data (assume JSON lines in file)
with open('python/hash_bounds_out.txt', 'r') as f:
    records = [json.loads(line.strip()) for line in f if line.strip()]

valid = [r for r in records if r.get('frac_true') is not None]

# Bootstrap (1000 resamples) for CI
def bootstrap_ci(data, stat=np.mean, n_resamples=1000, ci=95):
    np.random.seed(42)  # Reproducibility
    resamples = np.random.choice(data, (n_resamples, len(data)), replace=True)
    stats = np.apply_along_axis(stat, 1, resamples)
    lower = np.percentile(stats, (100 - ci) / 2)
    upper = np.percentile(stats, 100 - (100 - ci) / 2)
    return lower, upper

frac_errors = [r['frac_error_abs'] for r in valid]
mean_frac = np.mean(frac_errors)
ci_lower, ci_upper = bootstrap_ci(frac_errors)
print(f"Mean frac error: {mean_frac}, 95% CI: [{ci_lower}, {ci_upper}]")

# Filter for GVA: reject > upper CI
gva_candidates = [r for r in valid if r['frac_error_abs'] <= ci_upper]

# Precision check example with mpmath
if valid:
    pred = mp.mpf(valid[0]['prediction'])
    true = mp.mpf(valid[0]['prime_true'])
    rel_err = abs((pred - true) / true)
    print(f"Relative error check: {rel_err}")
    # Note: Precision target UNVERIFIED; adjust dps if needed

print(f"Filtered GVA candidates: {len(gva_candidates)} out of {len(valid)}")