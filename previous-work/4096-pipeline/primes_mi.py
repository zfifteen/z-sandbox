import sympy
import numpy as np
from sklearn.metrics import mutual_info_score
import mpmath as mp

# Set precision for reproducibility
mp.dps = 50

# Golden ratio phi
phi = mp.phi

# k for geometric resolution, as per framework (try 0.07 from appetizer)
k = 0.07

# Generate primes up to 1e6 for analysis (adjust as needed for runtime)
max_p = 10**6
primes = list(sympy.primerange(2, max_p))
print(f"Generated {len(primes)} primes up to {max_p}")

# Compute bit lengths and theta' for each prime
bit_lens = []
log_thetas = []
for p in primes:
    p_mp = mp.mpf(p)
    bit_len = int(mp.log(p_mp, 2)) + 1
    bit_lens.append(bit_len)
    
    mod_val = mp.fmod(p_mp, phi)
    normalized = mod_val / phi
    theta_prime = phi * (normalized ** k)
    log_theta = mp.log(theta_prime)
    log_thetas.append(float(log_theta))  # Convert to float for numpy

# Normalize log(thetas)
log_thetas_arr = np.array(log_thetas)
mean_log = np.mean(log_thetas_arr)
std_log = np.std(log_thetas_arr)
norm_log_thetas = (log_thetas_arr - mean_log) / std_log

# Bin normalized log_thetas into 10 bins for discretization
bins = np.linspace(norm_log_thetas.min(), norm_log_thetas.max(), 11)
binned_norm_log = np.digitize(norm_log_thetas, bins[:-1]) - 1  # 0 to 9

# Compute MI between binned norm log(Z) and bit lengths
mi = mutual_info_score(binned_norm_log, bit_lens)

print(f"Mutual Information: {mi:.6f}")
print(f"Normalized log(Z) range: {norm_log_thetas.min():.3f} to {norm_log_thetas.max():.3f}")
print(f"Bit lengths range: {min(bit_lens)} to {max(bit_lens)}")
print(f"Bins for norm log(Z): {len(np.unique(binned_norm_log))} unique bins")

# Empirical validation: random shuffle bit_lens and recompute MI as baseline
np.random.seed(42)  # For reproducibility
shuffled_bit_lens = np.random.permutation(bit_lens)
mi_shuffled = mutual_info_score(binned_norm_log, shuffled_bit_lens)
print(f"MI with shuffled bit lengths (baseline): {mi_shuffled:.6f}")

# Hypothesis: If MI > MI_shuffled significantly, suggests geometric lens reveals pattern in prime bit lengths.
# UNVERIFIED: This is a first empirical test; cross-check with larger prime sets or different k.