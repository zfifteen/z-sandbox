/**
 * @brief Check if a candidate is potentially prime using basic filters and κ(n).
 */
int is_potential_candidate(const mpfr_t candidate) {
    /* Basic primality filters:
     * 1. Must be positive integer
     * 2. Must be odd (except for 2)
     * 3. Not divisible by small primes (3, 5, 7, 11, 13)
     * 4. Curvature κ(n) < 1.0 (empirical threshold from validation)
     */
    
    /* Check if it's a positive integer */
    if (mpfr_sgn(candidate) <= 0 || !mpfr_integer_p(candidate)) {
        return 0;
    }
    
    /* Convert to unsigned long for basic tests */
    if (!mpfr_fits_ulong_p(candidate, MPFR_RNDN)) {
        return 1; /* Too large for basic tests, assume it's potentially prime */
    }
    
    unsigned long val = mpfr_get_ui(candidate, MPFR_RNDN);
    
    /* Check for 2 */
    if (val == 2) return 1;
    
    /* Check if even */
    if (val % 2 == 0) return 0;
    
    /* Check divisibility by small primes */
    if (val % 3 == 0 && val != 3) return 0;
    if (val % 5 == 0 && val != 5) return 0;
    if (val % 7 == 0 && val != 7) return 0;
    if (val % 11 == 0 && val != 11) return 0;
    if (val % 13 == 0 && val != 13) return 0;
    
    /* Check curvature κ(n) < 1.0 */
    double kappa = curvature_kappa(val);
    if (kappa >= 1.0) return 0;
    
    return 1; /* Passed all filters */
}