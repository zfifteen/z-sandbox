#!/usr/bin/env python3
"""
Fix candidate generation for large N by expanding search range.
"""

# Since str_replace_editor is broken, create a patch

patch = """
        # Enable ultra precision and increase iterations for larger N
        if bit_size >= 35:
            params.ultra_precision = True
            params.spiral_iters = min(5000, params.spiral_iters * 2)  # Increase spiral iterations
            params.search_window = 100000  # Much larger window for 35+ bits
            params.prime_limit = 20000     # More primes
        elif bit_size >= 32:
            params.spiral_iters = min(4000, params.spiral_iters * 1.5)
            params.search_window = 50000
            params.prime_limit = 10000
"""

print("Add this to the adaptive scaling section:")
print(patch)