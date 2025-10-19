#!/usr/bin/env python3
"""
Boundary Analysis: Understand why factorization fails at 35+ bits
Collects data on successful 34-bit and failed 35-bit cases for comparison.
"""

import csv
import time
from geometric_factorization import generate_semiprime, geometric_factor, FactorizationParams
from geometric_factorization import theta, circular_distance

def collect_boundary_data(num_cases=20):
    """Collect data on 34-bit successes and 35-bit failures."""
    data = []

    print("Collecting boundary analysis data...")

    # 34-bit successes
    print("\nGenerating 34-bit successes...")
    success_count = 0
    for i in range(num_cases * 2):  # Try more to get enough successes
        if success_count >= num_cases:
            break
        N, p, q = generate_semiprime(34, 1000 + i)
        params = FactorizationParams(max_time=10.0)
        start_time = time.time()
        result = geometric_factor(N, params)
        elapsed = time.time() - start_time

        if result.success:
            success_count += 1
            record = {
                'bit_size': 34,
                'success': True,
                'N': N,
                'p': p,
                'q': q,
                'attempts': result.attempts,
                'elapsed': elapsed,
                'theta_N': theta(N, 0.45),  # Use default k
                'theta_p': theta(p, 0.45),
                'theta_q': theta(q, 0.45),
                'dist_N_p': circular_distance(theta(N, 0.45), theta(p, 0.45)),
                'dist_N_q': circular_distance(theta(N, 0.45), theta(q, 0.45)),
                'candidates_pre': result.candidate_counts.get('k=0.45_eps=0.02_pre', 0),
                'candidates_post': result.candidate_counts.get('k=0.45_eps=0.02_post', 0),
            }
            data.append(record)
            print(f"  ✓ {success_count}/{num_cases}: {N} = {p}×{q}")

    # 35-bit failures
    print("\nGenerating 35-bit failures...")
    failure_count = 0
    for i in range(num_cases * 2):
        if failure_count >= num_cases:
            break
        N, p, q = generate_semiprime(35, 2000 + i)
        params = FactorizationParams(max_time=10.0)
        start_time = time.time()
        result = geometric_factor(N, params)
        elapsed = time.time() - start_time

        if not result.success:
            failure_count += 1
            record = {
                'bit_size': 35,
                'success': False,
                'N': N,
                'p': p,
                'q': q,
                'attempts': result.attempts,
                'elapsed': elapsed,
                'theta_N': theta(N, 0.45),
                'theta_p': theta(p, 0.45),
                'theta_q': theta(q, 0.45),
                'dist_N_p': circular_distance(theta(N, 0.45), theta(p, 0.45)),
                'dist_N_q': circular_distance(theta(N, 0.45), theta(q, 0.45)),
                'candidates_pre': result.candidate_counts.get('k=0.45_eps=0.02_pre', 0),
                'candidates_post': result.candidate_counts.get('k=0.45_eps=0.02_post', 0),
            }
            data.append(record)
            print(f"  ✗ {failure_count}/{num_cases}: {N} = {p}×{q}")

    return data

def save_data_to_csv(data, filename='boundary_data.csv'):
    """Save collected data to CSV."""
    if not data:
        print("No data to save!")
        return

    fieldnames = data[0].keys()
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Data saved to {filename} ({len(data)} records)")

if __name__ == "__main__":
    data = collect_boundary_data(20)
    save_data_to_csv(data)
    print("\nBoundary analysis data collection complete!")
    print(f"Collected {len([d for d in data if d['success']])} successes and {len([d for d in data if not d['success']])} failures")