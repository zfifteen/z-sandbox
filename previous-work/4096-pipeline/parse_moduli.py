import re
import sys
from gmpy2 import mpz  # For big integer multiplication, install if needed: pip install gmpy2

def main(log_file, output_csv):
    with open(log_file, 'r') as f:
        content = f.read()

    runs = re.split(r'=== Run \d+ ===', content)

    moduli = []
    for run in runs[1:]:  # Skip the first empty
        p_match = re.search(r'p:\s*(\d+)', run)
        q_match = re.search(r'q:\s*(\d+)', run)
        if p_match and q_match:
            p = mpz(p_match.group(1))
            q = mpz(q_match.group(1))
            n = p * q
            moduli.append(hex(n)[2:].upper())  # Hex without 0x, uppercase

    with open(output_csv, 'w') as f:
        f.write('modulus\n')
        for mod in moduli:
            f.write(mod + '\n')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python parse_moduli.py <log_file> <output_csv>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])