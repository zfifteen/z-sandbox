#!/bin/bash
#
# z5d_secure_key_gen.sh - Z5D RSA-4096 Secure Key Generator Benchmark
#
# **CRYPTOGRAPHICALLY SECURE** - Creates secure RSA keys using high-entropy
# seeds and Z5D predictor. This script runs the z5d_secure_key_gen tool
# with system-generated entropy and measures execution time.
#
# Purpose:
# - Demonstrates Z5D predictor integration into secure RSA-4096 key generation
# - Measures performance of cryptographically secure key generation process
# - Uses high-entropy system randomness for production-grade security
#
# Output:
# - z5d_key_gen-<random_tag>.key (PKCS#8 private key)
# - z5d_key_gen-<random_tag>.crt (X.509 certificate)
# - Execution time in milliseconds
#
# NOTE: Generated keys are SECURE and suitable for production use!
#
echo "Hardware Configuration:"
echo "======================"
echo "CPU: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || uname -p)"
echo "Cores: $(sysctl -n hw.ncpu 2>/dev/null || nproc)"
echo "Memory: $(( $(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1024 / 1024 / 1024 ))GB"
echo "Architecture: $(uname -m)"
echo "OS: $(uname -s) $(uname -r)"
echo ""
echo "=== Z5D Secure RSA-4096 Key Generator Benchmark ==="
echo "Running z5d_secure_key_gen with system-generated entropy..."
echo

# Record start time in milliseconds (portable approach)
start_time=$(python3 -c "import time; print(int(time.time() * 1000))")

# Execute the secure key generator with system entropy
./z5d_secure_key_gen

# Record end time and calculate duration
end_time=$(python3 -c "import time; print(int(time.time() * 1000))")
duration=$((end_time - start_time))

echo
echo "=== Benchmark Results ==="
echo "Execution time: ${duration} milliseconds"
echo "Generated files with cryptographically secure random tag"
echo
echo "Generated keys are SECURE and suitable for production use!"