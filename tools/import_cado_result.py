#!/usr/bin/env python3
"""
Import CADO-NFS factorization results into rsa_challenges.csv

Usage: python tools/import_cado_result.py <rsa_id> <cado_output_file>

This script reads the CADO-NFS output file, extracts the factors,
and updates the corresponding row in src/test/resources/rsa_challenges.csv.
"""

import sys
import csv
import re

def extract_factors(cado_file):
    """Extract p and q from CADO-NFS output."""
    with open(cado_file, 'r') as f:
        content = f.read()
    # Look for lines like "p = 123..." or similar
    p_match = re.search(r'p\s*=\s*(\d+)', content)
    q_match = re.search(r'q\s*=\s*(\d+)', content)
    if p_match and q_match:
        return p_match.group(1), q_match.group(1)
    return None, None

def update_csv(rsa_id, p, q):
    """Update the CSV with factors."""
    rows = []
    with open('src/test/resources/rsa_challenges.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['id'] == rsa_id:
                row['factor1'] = p
                row['factor2'] = q
                row['notes'] = 'factored'
            rows.append(row)
    with open('src/test/resources/rsa_challenges.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'dec_value', 'factor1', 'factor2', 'notes'])
        writer.writeheader()
        writer.writerows(rows)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python tools/import_cado_result.py <rsa_id> <cado_output_file>")
        sys.exit(1)
    rsa_id = sys.argv[1]
    cado_file = sys.argv[2]
    p, q = extract_factors(cado_file)
    if p and q:
        update_csv(rsa_id, p, q)
        print(f"Updated {rsa_id} with factors {p} and {q}")
    else:
        print("Failed to extract factors from", cado_file)