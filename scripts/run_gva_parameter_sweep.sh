#!/bin/bash
# GVA 200-bit Parameter Sweep Script
# Reproduces the full parameter sweep experiment

set -e

echo "=== GVA 200-bit Parameter Sweep ==="
echo "Testing 9 configurations: dims(13,15,17) × ranges(5000,10000,50000)"
echo "100 trials per configuration = 900 total trials"
echo ""

# Create results directory
mkdir -p results

# Run all parameter combinations
echo "Starting parameter sweep..."

for dims in 13 15 17; do
    for range in 5000 10000 50000; do
        echo "Running: dims=${dims}, range=${range}"
        python3 python/gva_200bit_experiment.py 100 ${dims} ${range}
        echo "Completed: gva_200bit_d${dims}_r${range}_results.csv"
        echo ""
    done
done

echo "Parameter sweep complete!"
echo ""
echo "=== Results Summary ==="

# Count total trials and check for successes
total_trials=0
success_count=0

for file in gva_200bit_*_results.csv; do
    if [[ -f "$file" ]]; then
        trials=$(tail -n +2 "$file" | wc -l)
        successes=$(grep -c "True" "$file")
        total_trials=$((total_trials + trials))
        success_count=$((success_count + successes))

        config=$(basename "$file" .csv | sed 's/gva_200bit_//')
        echo "${config}: ${trials} trials, ${successes} successes"
    fi
done

success_rate=$(echo "scale=2; $success_count * 100 / $total_trials" | bc -l 2>/dev/null || echo "0")

echo ""
echo "TOTAL: ${total_trials} trials, ${success_count} successes (${success_rate}% success rate)"

if [[ $success_count -eq 0 ]]; then
    echo "❌ CONCLUSION: GVA method shows 0% success on 200-bit numbers"
    echo "   Next steps: Test on smaller bit sizes, review algorithm foundations"
else
    echo "✅ CONCLUSION: GVA method shows potential for 200-bit factorization"
    echo "   Next steps: Scale up testing, optimize parameters"
fi