#!/usr/bin/env python3
"""
spiral_refit.py - Per-center log-log OLS regression for spiral candidates.

Parses golden_spiral_out.txt (CSV or key=value format), groups by center,
fits ln(Z) = beta0 + beta1 * ln(B), where B = it / area (rate-normalized).
Uses mpmath for high precision (dps=50).

Outputs:
- spiral_refit_results.csv: center,n,beta0,beta1,R2
- spiral_refit_results.json: same data as dict.

Requires: mpmath, numpy, scipy (for OLS).

Usage: python spiral_refit.py golden_spiral_out.txt
"""

import sys
import json
import csv
from collections import defaultdict
import mpmath as mp
import numpy as np
from scipy import stats

mp.dps = 50  # High precision

def parse_line(line, is_csv=False):
    """Parse a line into dict."""
    if is_csv:
        # Assume header-less or with header; parse as CSV
        reader = csv.reader([line])
        row = next(reader)
        if len(row) < 4:
            return None
        return {
            'center': row[0],
            'it': row[1],
            'value': row[2],
            'area': row[3],
            'radius': row[4] if len(row) > 4 else '0',
            'scale_x': row[5] if len(row) > 5 else '0',
            'scale_y': row[6] if len(row) > 6 else '0',
            'timestamp_ns': row[7] if len(row) > 7 else '0'
        }
    else:
        # Key=value format
        parts = line.split()
        data = {}
        for part in parts:
            if '=' in part:
                k, v = part.split('=', 1)
                data[k] = v
        if 'center' in data and 'it' in data and 'value' in data and 'area' in data:
            return data
    return None

def fit_per_center(data):
    """Fit per center, return results."""
    results = []
    for center, rows in data.items():
        if len(rows) < 2:
            continue  # Need at least 2 points for OLS
        X = []
        Y = []
        for row in rows:
            try:
                it = float(row['it'])
                value = float(row['value'])
                area = float(row['area'])
                if area == 0:
                    continue
                B = it / area
                if B <= 0 or value <= 0:
                    continue
                X.append(mp.log(B))
                Y.append(mp.log(value))
            except (ValueError, KeyError):
                continue
        if len(X) < 2:
            continue
        # OLS: Y = beta0 + beta1 * X
        X_arr = np.array([float(x) for x in X])
        Y_arr = np.array([float(y) for y in Y])
        slope, intercept, r_value, p_value, std_err = stats.linregress(X_arr, Y_arr)
        r_squared = r_value ** 2
        results.append({
            'center': center,
            'n': len(X),
            'beta0': float(intercept),
            'beta1': float(slope),
            'R2': float(r_squared)
        })
    return results

def main():
    if len(sys.argv) != 2:
        print("Usage: python spiral_refit.py <output_file>")
        sys.exit(1)
    filename = sys.argv[1]
    data = defaultdict(list)
    is_csv = False
    with open(filename, 'r') as f:
        first_line = f.readline().strip()
        if ',' in first_line and 'center' in first_line:
            is_csv = True
        else:
            # Rewind
            f.seek(0)
        for line in f:
            line = line.strip()
            if not line:
                continue
            parsed = parse_line(line, is_csv)
            if parsed:
                data[parsed['center']].append(parsed)

    results = fit_per_center(data)

    # Write CSV
    with open('spiral_refit_results.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['center', 'n', 'beta0', 'beta1', 'R2'])
        writer.writeheader()
        writer.writerows(results)

    # Write JSON
    with open('spiral_refit_results.json', 'w') as jsonfile:
        json.dump(results, jsonfile, indent=2)

    print(f"Processed {len(results)} centers. Results in spiral_refit_results.csv and .json")

if __name__ == '__main__':
    main()