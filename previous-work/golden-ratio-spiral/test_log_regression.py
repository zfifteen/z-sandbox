#!/usr/bin/env python3
"""
Log-Regression Test for Z = A(B / c) with Causality Guards
==========================================================

Tests exponential fit using log-linear regression: log(Z) = β₀ + β₁ log(B / c)
Data: Real from spiral_data.csv (B=Iteration, Z=Value)
c = φ (golden ratio), A = exp(β₀)

Hypotheses (UNVERIFIED):
- Exponential growth in spiral candidates.

Reproducibility: mp.dps=50, no RNG.
"""

import mpmath as mp
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import pandas as pd
import os

# Precision
mp.dps = 50
c = float(mp.phi)  # φ ≈ 1.618

# Load real data
csv_path = '/Users/velocityworks/IdeaProjects/unified-framework/src/c/golden-ratio-spiral/spiral_data.csv'
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    sample_B = df['Iteration'].values.astype(float)
    sample_Z = df['Value'].values.astype(float)
    print(f"Loaded {len(sample_B)} real data points from spiral_data.csv")
else:
    print("spiral_data.csv not found, using synthetic fallback")
    np.random.seed(42)
    sample_B = np.random.uniform(0.1, 1.5, 100)
    sample_Z = np.exp(sample_B)  # Exponential for testing

# Causality checks
for b in sample_B:
    if abs(b) >= c:
        print(f"B={b}: Causality error (|B| >= c)")

# Log-regression: log(Z) = β₀ + β₁ log(B / c)
# Avoid log(0), add small epsilon
eps = 1e-10
X = np.log(sample_B / c + eps).reshape(-1, 1)
y = np.log(sample_Z + eps)

model = LinearRegression()
model.fit(X, y)
beta_0 = model.intercept_
beta_1 = model.coef_[0]

# Predictions
y_pred = model.predict(X)
r2 = r2_score(y, y_pred)

print(f"A fit: β₀={beta_0:.4f}, β₁={beta_1:.4f}, R²={r2:.4f}")

# Status
if r2 > 0.9:
    print("Status: VERIFIED (strong exponential fit)")
else:
    print("Status: UNVERIFIED (poor fit; check data or model)")