#!/bin/bash
# Run Java BigDecimal GVA Factorization Demo
# Outputs verification data for 64, 128, 256-bit tests

echo "Running Java GVA Demo..."
cd "$(dirname "$0")/.."
./gradlew gva