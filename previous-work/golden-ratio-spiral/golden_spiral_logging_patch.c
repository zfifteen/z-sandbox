// golden_spiral_logging_patch.c
// Patch to add structured logging to golden_spiral.c or .h
// Insert this code into the golden_spiral_search function, after finding each candidate.

// Assuming golden_spiral_search loops over iterations, computes value, checks is_candidate.

// Add this after is_candidate check, if true:

#include <time.h>  // For timestamp_ns

// ... existing code ...

int golden_spiral_search(const spiral_params_t *params, 
                        spiral_candidate_t *candidates, 
                        int max_candidates, 
                        int *found_count) {
    // ... existing init ...

    int candidate_index = 0;
    *found_count = 0;

    for (int i = 0; i < params->max_iterations && candidate_index < max_candidates; i++) {
        // Compute spiral coordinates
        mpfr_t x, y;
        mpfr_init2(x, params->precision_bits);
        mpfr_init2(y, params->precision_bits);
        calculate_spiral_coordinates(i, params, x, y);

        // Compute candidate value (assume some formula, e.g., center + x * r_scale + y * s_scale or similar)
        // Adjust based on actual computation in your code
        mpfr_t candidate_val;
        mpfr_init2(candidate_val, params->precision_bits);
        // Example: mpfr_add(candidate_val, params->center, x, MPFR_RNDN);  // Replace with actual
        // For now, placeholder:
        mpfr_set_si(candidate_val, 1000000 + i * 1000, MPFR_RNDN);  // Placeholder, replace with real calc

        int is_cand = is_potential_candidate(candidate_val);

        if (is_cand) {
            // Log the candidate in structured format (CSV or key-value)
            // Use CSV for simplicity
            struct timespec ts;
            clock_gettime(CLOCK_MONOTONIC, &ts);
            long long timestamp_ns = (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;

            // Compute area proxy: assume area = r_scale * s_scale
            mpfr_t area;
            mpfr_init2(area, params->precision_bits);
            mpfr_mul(area, params->r_scale, params->s_scale, MPFR_RNDN);

            // Output line
            char value_str[1024];
            mpfr_snprintf(value_str, sizeof(value_str), "%.0Rf", candidate_val);
            char area_str[256];
            mpfr_snprintf(area_str, sizeof(area_str), "%.6Rf", area);
            char center_str[256];
            mpfr_snprintf(center_str, sizeof(center_str), "%.0Rf", params->center);

            // CSV format: center,it,value,area,radius,scale_x,scale_y,timestamp_ns
            // radius: sqrt(x^2 + y^2)
            mpfr_t radius;
            mpfr_init2(radius, params->precision_bits);
            mpfr_hypot(radius, x, y, MPFR_RNDN);
            char radius_str[256];
            mpfr_snprintf(radius_str, sizeof(radius_str), "%.6Rf", radius);

            char scale_x_str[256];
            mpfr_snprintf(scale_x_str, sizeof(scale_x_str), "%.6Rf", params->r_scale);
            char scale_y_str[256];
            mpfr_snprintf(scale_y_str, sizeof(scale_y_str), "%.6Rf", params->s_scale);

            printf("%s,%d,%s,%s,%s,%s,%s,%lld\n",
                   center_str, i, value_str, area_str, radius_str, scale_x_str, scale_y_str, timestamp_ns);

            // Store in candidates array if needed
            if (candidate_index < max_candidates) {
                spiral_candidate_init(&candidates[candidate_index]);
                mpfr_set(candidates[candidate_index].value, candidate_val, MPFR_RNDN);
                mpfr_set(candidates[candidate_index].spiral_x, x, MPFR_RNDN);
                mpfr_set(candidates[candidate_index].spiral_y, y, MPFR_RNDN);
                candidates[candidate_index].iteration = i;
                candidates[candidate_index].is_candidate = 1;
                candidate_index++;
            }

            mpfr_clear(radius);
            mpfr_clear(area);
        }

        mpfr_clear(x);
        mpfr_clear(y);
        mpfr_clear(candidate_val);
    }

    *found_count = candidate_index;

    // ... existing cleanup ...

    return 0;
}

// Also, add header if CSV:
// printf("center,it,value,area,radius,scale_x,scale_y,timestamp_ns\n");
// At the beginning of the function.

// Note: Replace placeholder candidate_val calculation with actual logic from your code.
// This assumes MPFR for all, adjust as needed.