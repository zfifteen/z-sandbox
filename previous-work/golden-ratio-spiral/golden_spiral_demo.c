/**
 * @file golden_spiral_demo.c
 * @brief Main demo program for Golden Ratio Index Scaling and Spiral Search
 *
 * This is a simple wrapper that calls the comprehensive demonstration
 * function from the golden_spiral library.
 *
 * @author Golden Ratio Spiral Implementation Team
 * @version 1.0
 * @date 2025-09-21
 */

#include "golden_spiral.h"

int main(void) {
    /* Run the comprehensive demonstration */
    int result = run_golden_spiral_demo();
    
    if (result == 0) {
        return 0; /* Success */
    } else {
        return 1; /* Error */
    }
}