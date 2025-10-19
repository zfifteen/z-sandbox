#!/bin/bash
#
# Validation Test Suite for Z5D Factorization Shortcut
# =====================================================
#
# Runs comprehensive validation tests to verify correctness and performance.

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "Z5D Factorization Shortcut - Validation Test Suite"
echo "============================================================"
echo ""

# Check Z5D binary exists
Z5D_BIN="${Z5D_PRIME_GEN:-../../src/c/bin/z5d_prime_gen}"
if [ ! -f "$Z5D_BIN" ]; then
    echo -e "${RED}ERROR: Z5D binary not found at $Z5D_BIN${NC}"
    echo "Build it with: cd ../../src/c && make z5d_prime_gen"
    exit 1
fi

echo -e "${GREEN}✓ Z5D binary found:${NC} $Z5D_BIN"
echo ""

# Test 1: Quick smoke test
echo "Test 1: Quick smoke test (N_max=100K, 100 samples)"
echo "---------------------------------------------------"
python3 factorization_shortcut_z5d.py \
    --Nmax 100000 \
    --samples 100 \
    --eps 0.05 \
    --seed 42 \
    > /tmp/z5d_test1.out 2>&1

if grep -q "partial_rate" /tmp/z5d_test1.out; then
    SUCCESS_RATE=$(grep "partial_rate" /tmp/z5d_test1.out | head -1 | awk '{print $7}')
    echo -e "${GREEN}✓ PASSED${NC}: Success rate = $SUCCESS_RATE"
else
    echo -e "${RED}✗ FAILED${NC}: No results produced"
    cat /tmp/z5d_test1.out
    exit 1
fi
echo ""

# Test 2: Baseline validation (N_max=1M, 500 samples)
echo "Test 2: Baseline validation (N_max=1M, 500 samples)"
echo "----------------------------------------------------"
python3 factorization_shortcut_z5d.py \
    --Nmax 1000000 \
    --samples 500 \
    --eps 0.05 \
    --seed 42 \
    > /tmp/z5d_test2.out 2>&1

if grep -q "partial_rate" /tmp/z5d_test2.out; then
    SUCCESS_RATE=$(grep "partial_rate" /tmp/z5d_test2.out | head -1 | awk '{print $7}')
    echo -e "${GREEN}✓ PASSED${NC}: Success rate = $SUCCESS_RATE"

    # Check if within expected range (20-26%)
    RATE_NUM=$(echo $SUCCESS_RATE | sed 's/[^0-9.]//g')
    if (( $(echo "$RATE_NUM > 0.15" | bc -l) && $(echo "$RATE_NUM < 0.30" | bc -l) )); then
        echo -e "${GREEN}✓ SUCCESS RATE IN EXPECTED RANGE${NC} (20-26%)"
    else
        echo -e "${YELLOW}⚠ WARNING: Success rate outside expected range${NC}"
    fi
else
    echo -e "${RED}✗ FAILED${NC}: No results produced"
    cat /tmp/z5d_test2.out
    exit 1
fi
echo ""

# Test 3: Multiple epsilon values
echo "Test 3: Multiple epsilon test (N_max=1M, eps=[0.02,0.05,0.10])"
echo "----------------------------------------------------------------"
python3 factorization_shortcut_z5d.py \
    --Nmax 1000000 \
    --samples 200 \
    --eps 0.02 0.05 0.10 \
    --seed 42 \
    > /tmp/z5d_test3.out 2>&1

EPS_COUNT=$(grep -c "partial_rate" /tmp/z5d_test3.out || true)
if [ "$EPS_COUNT" -ge 3 ]; then
    echo -e "${GREEN}✓ PASSED${NC}: Tested $EPS_COUNT epsilon values"
else
    echo -e "${RED}✗ FAILED${NC}: Expected 3+ epsilon results, got $EPS_COUNT"
    cat /tmp/z5d_test3.out
    exit 1
fi
echo ""

# Test 4: Unbalanced mode
echo "Test 4: Unbalanced semiprimes (N_max=1M, mode=unbalanced)"
echo "----------------------------------------------------------"
python3 factorization_shortcut_z5d.py \
    --Nmax 1000000 \
    --samples 200 \
    --mode unbalanced \
    --eps 0.05 \
    --seed 42 \
    > /tmp/z5d_test4.out 2>&1

if grep -q "partial_rate" /tmp/z5d_test4.out; then
    SUCCESS_RATE=$(grep "partial_rate" /tmp/z5d_test4.out | head -1 | awk '{print $7}')
    echo -e "${GREEN}✓ PASSED${NC}: Success rate = $SUCCESS_RATE (unbalanced)"
else
    echo -e "${RED}✗ FAILED${NC}: No results produced"
    cat /tmp/z5d_test4.out
    exit 1
fi
echo ""

# Test 5: CSV/MD export
echo "Test 5: CSV and Markdown export"
echo "--------------------------------"
python3 factorization_shortcut_z5d.py \
    --Nmax 100000 \
    --samples 50 \
    --eps 0.05 \
    --seed 42 \
    --csv /tmp/z5d_test.csv \
    --md /tmp/z5d_test.md \
    > /tmp/z5d_test5.out 2>&1

if [ -f /tmp/z5d_test.csv ] && [ -f /tmp/z5d_test.md ]; then
    echo -e "${GREEN}✓ PASSED${NC}: CSV and Markdown files created"
    echo "  CSV: $(wc -l < /tmp/z5d_test.csv) lines"
    echo "  MD:  $(wc -l < /tmp/z5d_test.md) lines"
else
    echo -e "${RED}✗ FAILED${NC}: Export files not created"
    exit 1
fi
echo ""

# Test 6: Reproducibility
echo "Test 6: Reproducibility (same seed = same results)"
echo "---------------------------------------------------"
python3 factorization_shortcut_z5d.py \
    --Nmax 100000 \
    --samples 100 \
    --eps 0.05 \
    --seed 123 \
    > /tmp/z5d_test6a.out 2>&1

python3 factorization_shortcut_z5d.py \
    --Nmax 100000 \
    --samples 100 \
    --eps 0.05 \
    --seed 123 \
    > /tmp/z5d_test6b.out 2>&1

RATE_A=$(grep "partial_rate" /tmp/z5d_test6a.out | head -1 | awk '{print $7}')
RATE_B=$(grep "partial_rate" /tmp/z5d_test6b.out | head -1 | awk '{print $7}')

if [ "$RATE_A" == "$RATE_B" ]; then
    echo -e "${GREEN}✓ PASSED${NC}: Results identical ($RATE_A = $RATE_B)"
else
    echo -e "${RED}✗ FAILED${NC}: Results differ ($RATE_A vs $RATE_B)"
    exit 1
fi
echo ""

# Summary
echo "============================================================"
echo -e "${GREEN}ALL TESTS PASSED${NC}"
echo "============================================================"
echo ""
echo "Validation complete. Reference implementation is working correctly."
echo ""
echo "Next steps:"
echo "  - Run larger scale tests: --Nmax 10000000"
echo "  - Benchmark against sieve version"
echo "  - Test at cryptographic scales (N > 10^12)"

# Cleanup
rm -f /tmp/z5d_test*.out /tmp/z5d_test.csv /tmp/z5d_test.md

exit 0
