/**
 * @file golden_spiral.h
 * @brief Golden Ratio Index Scaling and Spiral Search for Prime Discovery
 *
 * This header defines interfaces for the Golden Ratio Index Scaling and Spiral Search
 * implementation, using MPFR high-precision arithmetic throughout.
 *
 * Key Features:
 * - Golden ratio scaling (φ ≈ 1.618) for super-exponential growth prediction
 * - Golden angle spiral search (137.5°) for optimal packing
 * - MPFR-only high-precision arithmetic
 * - Minimized resonance gaps in dense prime fields
 *
 * @author Golden Ratio Spiral Implementation Team
 * @version 1.0
 * @date 2025-09-21
 */

#ifndef GOLDEN_SPIRAL_H
#define GOLDEN_SPIRAL_H

#include <mpfr.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifdef WITH_OPENMP
#include <omp.h>
#endif

/**
 * @brief Default precision for MPFR calculations (256 bits)
 */
#define GOLDEN_SPIRAL_PRECISION 256

/**
 * @brief Maximum number of spiral iterations for search
 */
#define MAX_SPIRAL_ITERATIONS 10000

/**
 * @brief Golden ratio φ = (1 + √5)/2 ≈ 1.618033988749...
 */
extern mpfr_t PHI;

/**
 * @brief Golden angle = 2π/φ² ≈ 137.5077640500... degrees
 */
extern mpfr_t GOLDEN_ANGLE;

/**
 * @brief π constant for trigonometric calculations
 */
extern mpfr_t PI;

/**
 * @brief 2π constant for optimization
 */
extern mpfr_t TWO_PI;

/**
 * @brief Structure to hold spiral search parameters
 */
typedef struct {
    mpfr_t center;           /**< Center point for spiral search */
    mpfr_t r_scale;          /**< Radial scaling factor */
    mpfr_t s_scale;          /**< Secondary scaling factor */
    int max_iterations;      /**< Maximum iterations for search */
    int precision_bits;      /**< MPFR precision in bits */
} spiral_params_t;

/**
 * @brief Structure to hold golden ratio scaling results
 */
typedef struct {
    mpfr_t current_order;    /**< Current order value */
    mpfr_t predicted_next;   /**< Predicted next order using φ scaling */
    mpfr_t scaling_factor;   /**< Actual scaling factor applied */
    mpfr_t adjustment;       /**< Historical adjustment based on regression */
    int is_valid;            /**< Flag indicating if result is valid */
} golden_scaling_result_t;

/**
 * @brief Structure to hold spiral search candidate
 */
typedef struct {
    mpfr_t value;           /**< Candidate value */
    mpfr_t spiral_x;        /**< X coordinate in spiral */
    mpfr_t spiral_y;        /**< Y coordinate in spiral */
    int iteration;          /**< Spiral iteration number */
    int is_candidate;       /**< Flag for potential prime candidate */
} spiral_candidate_t;

/**
 * @brief Initialize the golden spiral system
 *
 * Sets up MPFR constants and initializes the mathematical framework
 * for golden ratio scaling and spiral search.
 *
 * @param precision_bits Precision for MPFR calculations (default: 256)
 * @return 0 on success, -1 on error
 */
int golden_spiral_init(int precision_bits);

/**
 * @brief Cleanup the golden spiral system
 *
 * Frees all allocated MPFR variables and cleans up resources.
 */
void golden_spiral_cleanup(void);

/**
 * @brief Initialize spiral parameters structure
 *
 * @param params Pointer to spiral_params_t structure
 * @param center_value Initial center value for spiral
 * @param r_scale Radial scaling factor
 * @param s_scale Secondary scaling factor
 * @param max_iter Maximum iterations
 * @return 0 on success, -1 on error
 */
int spiral_params_init(spiral_params_t *params, double center_value, 
                       double r_scale, double s_scale, int max_iter);

/**
 * @brief Cleanup spiral parameters structure
 *
 * @param params Pointer to spiral_params_t structure
 */
void spiral_params_cleanup(spiral_params_t *params);

/**
 * @brief Initialize golden scaling result structure
 *
 * @param result Pointer to golden_scaling_result_t structure
 * @return 0 on success, -1 on error
 */
int golden_scaling_result_init(golden_scaling_result_t *result);

/**
 * @brief Cleanup golden scaling result structure
 *
 * @param result Pointer to golden_scaling_result_t structure
 */
void golden_scaling_result_cleanup(golden_scaling_result_t *result);

/**
 * @brief Initialize spiral candidate structure
 *
 * @param candidate Pointer to spiral_candidate_t structure
 * @return 0 on success, -1 on error
 */
int spiral_candidate_init(spiral_candidate_t *candidate);

/**
 * @brief Cleanup spiral candidate structure
 *
 * @param candidate Pointer to spiral_candidate_t structure
 */
void spiral_candidate_cleanup(spiral_candidate_t *candidate);

/**
 * @brief Perform golden ratio scaling prediction
 *
 * Uses φ ≈ 1.618 to predict the next order based on current order,
 * with historical adjustment based on observed patterns.
 *
 * @param current_order Current prime order
 * @param result Pointer to store scaling result
 * @return 0 on success, -1 on error
 */
int golden_ratio_scale(const mpfr_t current_order, golden_scaling_result_t *result);

/**
 * @brief Perform golden angle spiral search
 *
 * Searches for candidates using golden angle (137.5°) spiral pattern
 * around a predicted center point for optimal packing.
 *
 * @param params Spiral search parameters
 * @param candidates Array to store found candidates
 * @param max_candidates Maximum number of candidates to find
 * @param found_count Pointer to store actual number of candidates found
 * @return 0 on success, -1 on error
 */
int golden_spiral_search(const spiral_params_t *params, 
                        spiral_candidate_t *candidates, 
                        int max_candidates, 
                        int *found_count);

/**
 * @brief Calculate spiral coordinates for iteration i
 *
 * Computes x,y coordinates for the i-th point in the golden spiral.
 *
 * @param iteration Spiral iteration number
 * @param params Spiral parameters
 * @param x Pointer to store x coordinate
 * @param y Pointer to store y coordinate
 * @return 0 on success, -1 on error
 */
int calculate_spiral_coordinates(int iteration, const spiral_params_t *params, 
                                mpfr_t x, mpfr_t y);

/**
 * @brief Estimate historical adjustment for golden ratio scaling
 *
 * Uses regression on log exponents to estimate adjustment factor
 * based on historical gaps between known prime orders.
 *
 * @param current_order Current order
 * @param adjustment Pointer to store calculated adjustment
 * @return 0 on success, -1 on error
 */
int estimate_historical_adjustment(const mpfr_t current_order, mpfr_t adjustment);

/**
 * @brief Check if a candidate is potentially prime using basic filters
 *
 * Applies basic primality filters before more expensive tests.
 *
 * @param candidate Candidate value to check
 * @return 1 if candidate passes basic filters, 0 otherwise
 */
int is_potential_candidate(const mpfr_t candidate);

/**
 * @brief Print spiral search results
 *
 * Displays formatted results of spiral search including candidates found.
 *
 * @param candidates Array of candidates found
 * @param count Number of candidates
 * @param params Search parameters used
 */
void print_spiral_results(const spiral_candidate_t *candidates, int count, 
                         const spiral_params_t *params);

/**
 * @brief Print golden ratio scaling results
 *
 * Displays formatted results of golden ratio scaling prediction.
 *
 * @param result Scaling result to display
 */
void print_scaling_results(const golden_scaling_result_t *result);

/**
 * @brief Run comprehensive demonstration
 *
 * Performs complete demonstration of golden ratio scaling and spiral search
 * capabilities with various test cases and parameter sets.
 *
 * @return 0 on success, -1 on error
 */
int run_golden_spiral_demo(void);

#endif /* GOLDEN_SPIRAL_H */