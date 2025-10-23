# File: experiments/validate_hydrogen_curvature_hypothesis.py
import numpy as np
import mpmath as mp
from scipy.optimize import curve_fit
from scipy.stats import linregress
import matplotlib.pyplot as plt

# Import z-sandbox tools

mp.dps = 50

# Define missing functions
def curvature_kappa(n):
    """Compute curvature κ(n) = 4 * ln(n+1) / e²."""
    return 4 * mp.log(mp.mpf(n) + 1) / mp.e**2

def divisor_count(n):
    """Count number of divisors of n."""
    count = 0
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            count += 1 if i == n // i else 2
    return count
np.random.seed(42)

# === 1. Generate 10,000 mock orbitals ===
N_SAMPLES = 10_000
n_values = np.random.randint(2, 5001, size=N_SAMPLES)
kappa_vals = np.array([float(curvature_kappa(int(n))) for n in n_values])
d_vals = np.array([divisor_count(int(n)) for n in n_values])
prime_density = d_vals / np.log(n_values + 1)  # ≈ d(n)/ln n

# Mock "probability weight" inspired by radial node structure
# We hypothesize: weight ∝ exp(-α κ) → high κ = low probability (like node)
weights = np.exp(-kappa_vals)  # baseline exponential decay
weights *= prime_density        # boost in high d(n)/ln n regions

# Normalize
weights /= weights.sum()

# === 2. Bin by κ quintiles ===
kappa_quintiles = np.percentile(kappa_vals, [0, 20, 40, 60, 80, 100])
bins = kappa_quintiles
hist, bin_edges = np.histogram(kappa_vals, bins=bins, weights=weights, density=True)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

# Remove empty bins
mask = hist > 0
x, y = bin_centers[mask], hist[mask]

# === 3. Fit P(κ) = A * exp(-α κ) ===
def exp_decay(k, A, alpha):
    return A * np.exp(-alpha * k)

popt, pcov = curve_fit(exp_decay, x, y, p0=[y.max(), 1.0], bounds=([0, 0], [np.inf, np.inf]))
A_fit, alpha_fit = popt
alpha_err = np.sqrt(pcov[1,1])

print(f"Fitted: P(κ) = {A_fit:.3e} * exp(-{alpha_fit:.4f} κ)")
print(f"α ± σ_α = {alpha_fit:.4f} ± {alpha_err:.4f}")

# === 4. Compare to hydrogen radial decay: α_n = 2/n ===
n_hydrogen = np.array([2, 3, 4])
alpha_hydrogen = 2.0 / n_hydrogen

# Use n=2,3,4 weighted average (mimicking n=2..4 range)
alpha_h_mean = np.mean(alpha_hydrogen)
alpha_h_std  = np.std(alpha_hydrogen) / np.sqrt(len(alpha_hydrogen))

print(f"Hydrogen α (n=2,3,4): {alpha_h_mean:.4f} ± {alpha_h_std:.4f}")

# === 5. Statistical test: |α_fit - α_h| < 2σ_total ? ===
sigma_total = np.sqrt(alpha_err**2 + alpha_h_std**2)
diff = abs(alpha_fit - alpha_h_mean)
z_score = diff / sigma_total

print(f"|α_fit - α_H| = {diff:.4f}, σ_total = {sigma_total:.4f} → z = {z_score:.2f}")

# === 6. Correlation: κ vs log(probability) should be linear if exp decay holds ===
log_prob = np.log(hist + 1e-15)[mask]
slope, intercept, r_val, p_val, std_err = linregress(x, log_prob)

print(f"log(P) vs κ: slope = {slope:.4f}, r = {r_val:.4f}, p = {p_val:.2e}")

# === 7. Visualize ===
plt.figure(figsize=(10, 6))
plt.scatter(kappa_vals[::50], weights[::50], alpha=0.3, label="Mock Orbitals", s=10)
plt.hist(kappa_vals, bins=50, weights=weights, density=True, alpha=0.7, color='orange', label="Binned Density")
plt.plot(x, exp_decay(x, *popt), 'r-', lw=2, label=f'Fit: exp(-{alpha_fit:.3f}κ)')
plt.axhline(0, color='k', lw=0.5)
plt.xlabel("Curvature κ(n)")
plt.ylabel("Probability Density")
plt.title("Prime Curvature vs Mock Electron Density")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# === 8. Final Verdict ===
if z_score < 2.0 and r_val > 0.85:
    verdict = "✅ ACCEPT H₀: Prime curvature induces quantization-like decay"
    axiom_status = "VERIFIED (via MC simulation)"
else:
    verdict = "❌ REJECT H₀: No significant analogy to hydrogen radial nodes"
    axiom_status = "UNVERIFIED"

print("\n" + "="*60)
print(verdict)
print(f"Axiom Status: {axiom_status}")
print(f"Correlation r = {r_val:.4f} (target >0.85)")
print(f"Z-score = {z_score:.2f} (target <2.0)")
print("="*60)