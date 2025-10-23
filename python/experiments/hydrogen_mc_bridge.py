# File: experiments/hydrogen_mc_bridge.py
import numpy as np, mpmath as mp, matplotlib.pyplot as plt
from monte_carlo import MonteCarloEstimator
def curvature_kappa(n):
    """Compute curvature κ(n) = 4 * ln(n+1) / e²."""
    return 4 * mp.log(mp.mpf(n) + 1) / mp.e**2

mp.dps = 50
mc = MonteCarloEstimator(seed=42)

def sample_hydrogen_210(N=10**6):
    """Sample |ψ₂₁₀|² ∝ ρ² exp(-ρ) |Y₁⁰|² on ℝ³ → spherical shell"""
    rho = np.random.exponential(4.0, N)          # effective scale for n=2
    theta, phi = np.random.uniform(0, np.pi, N), np.random.uniform(0, 2*np.pi, N)
    Y10 = np.sqrt(3/(8*np.pi)) * np.cos(theta)
    weight = rho**2 * np.exp(-rho) * np.abs(Y10)**2
    return np.mean(weight), np.std(weight) / np.sqrt(N)

def sample_via_z5d_curvature(N=10**6):
    """Replace exponential with κ(n)-modulated density"""
    n = np.random.randint(2, 1000, N)
    kappa = np.array([curvature_kappa(int(k)) for k in n], dtype=float)
    weight = kappa * np.log1p(n) / np.exp(1)**2   # mimic radial decay
    return np.mean(weight), np.std(weight) / np.sqrt(N)

# Run & compare
exact_norm = mp.quad(lambda r: r**2 * mp.exp(-r) * (r**2), [0, mp.inf])  # ≈ 8
print("Exact |ψ₂₁₀| radial norm:", exact_norm)
mc_psi, err_psi = sample_hydrogen_210()
print(f"MC ψ₂₁₀: {mc_psi:.6f} ± {err_psi:.6f}")
mc_kappa, err_kappa = sample_via_z5d_curvature()
print(f"MC κ(n)-modulated: {mc_kappa:.6f} ± {err_kappa:.6f}")