import sympy
import numpy as np
from sklearn.metrics import mutual_info_score
import mpmath as mp

# Set precision for reproducibility
mp.dps = 50

# Generate primes up to 1e6 for analysis
max_p = 10**6
primes_list = list(sympy.primerange(2, max_p))
print(f"Generated {len(primes_list)} primes up to {max_p}")

# Compute gaps
gaps = [primes_list[i+1] - primes_list[i] for i in range(len(primes_list)-1)]
max_gap = max(gaps)
print(f"Max gap: {max_gap}")

# Compute bit lengths and Z = n (Δ_n / Δ_max) for each prime except last
bit_lens = []
log_Zs = []
for i in range(len(primes_list)-1):
    p = primes_list[i]
    p_mp = mp.mpf(p)
    bit_len = int(mp.log(p_mp, 2)) + 1
    bit_lens.append(bit_len)
    
    delta_n = gaps[i]
    Z = p * (delta_n / max_gap)
    log_Z = mp.log(mp.mpf(Z))
    log_Zs.append(float(log_Z))

# Normalize log(Zs)
log_Zs_arr = np.array(log_Zs)
mean_log = np.mean(log_Zs_arr)
std_log = np.std(log_Zs_arr)
norm_log_Zs = (log_Zs_arr - mean_log) / std_log

# Bin normalized log(Zs) into 10 bins for discretization
bins = np.linspace(norm_log_Zs.min(), norm_log_Zs.max(), 11)
binned_norm_log = np.digitize(norm_log_Zs, bins[:-1]) - 1  # 0 to 9

# Compute MI between binned norm log(Z) and bit lengths
mi = mutual_info_score(binned_norm_log, bit_lens)

print(f"Mutual Information: {mi:.6f}")
print(f"Normalized log(Z) range: {norm_log_Zs.min():.3f} to {norm_log_Zs.max():.3f}")
print(f"Bit lengths range: {min(bit_lens)} to {max(bit_lens)}")
print(f"Bins for norm log(Z): {len(np.unique(binned_norm_log))} unique bins")

# Empirical validation: random shuffle bit_lens and recompute MI as baseline
np.random.seed(42)  # For reproducibility
shuffled_bit_lens = np.random.permutation(bit_lens)
mi_shuffled = mutual_info_score(binned_norm_log, shuffled_bit_lens)
print(f"MI with shuffled bit lengths (baseline): {mi_shuffled:.6f}")

# UNVERIFIED hypothesis: Z = n (Δ_n / Δ_max) may reveal prime density patterns via gaps; MI test suggests...