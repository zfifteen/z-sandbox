import json
import random
import subprocess
import os

random.seed(42)
successes = 0

# Load targets
with open('python/targets_filtered.json', 'r') as f:
    data = json.load(f)
targets = data['targets']

print(f"Loaded {len(targets)} targets")

for i, target in enumerate(targets[:100]):  # Start with 10 for test
    N = str(target['N'])
    print(f"Testing target {i+1}: N={N[:50]}...")
    
    # Run factor_256bit.py (adapt if needed)
    result = subprocess.run(['python3', 'python/factor_256bit.py', N], capture_output=True, timeout=3600)  # 10 min timeout
    output = result.stdout.decode() + result.stderr.decode()
    
    if 'factored' in output.lower() or 'success' in output.lower():
        successes += 1
        print(f"  SUCCESS: Found factors")
    else:
        print(f"  FAILED: No factors found")

print(f"Success rate: {successes}/{len(targets[:100])} = {successes/len(targets[:10])*100}%")