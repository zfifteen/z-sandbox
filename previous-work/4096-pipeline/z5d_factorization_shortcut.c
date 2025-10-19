#include "z5d_factorization_shortcut.h"

#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <sys/time.h>

#include <mpfr.h>
#include <gmp.h>
#include <openssl/bn.h>
#include <openssl/rand.h>

static mpfr_t phi_mpfr;
static int phi_initialized = 0;

static void ensure_phi_initialized(void) {
    if (phi_initialized) {
        return;
    }
    mpfr_init2(phi_mpfr, 256);
    mpfr_t tmp;
    mpfr_init2(tmp, 256);
    mpfr_sqrt_ui(tmp, 5, MPFR_RNDN);
    mpfr_add_ui(tmp, tmp, 1, MPFR_RNDN);
    mpfr_div_ui(phi_mpfr, tmp, 2, MPFR_RNDN);
    mpfr_clear(tmp);
    phi_initialized = 1;
}

static double theta_prime_from_mpfr(const mpfr_t value, double k) {
    ensure_phi_initialized();
    mpfr_t tmp, k_mp;
    mpfr_init2(tmp, mpfr_get_prec(value));
    mpfr_set(tmp, value, MPFR_RNDN);
    mpfr_div(tmp, tmp, phi_mpfr, MPFR_RNDN);
    mpfr_frac(tmp, tmp, MPFR_RNDN);

    mpfr_init2(k_mp, mpfr_get_prec(value));
    mpfr_set_d(k_mp, k, MPFR_RNDN);
    mpfr_pow(tmp, tmp, k_mp, MPFR_RNDN);
    mpfr_mul(tmp, tmp, phi_mpfr, MPFR_RNDN);
    mpfr_frac(tmp, tmp, MPFR_RNDN);

    double result = mpfr_get_d(tmp, MPFR_RNDN);
    mpfr_clear(k_mp);
    mpfr_clear(tmp);
    return result;
}

static double theta_prime_from_string(const char *decimal, double k) {
    mpz_t mpz_value;
    mpz_init_set_str(mpz_value, decimal, 10);
    mpfr_t mpfr_value;
    mpfr_init2(mpfr_value, 512);
    mpfr_set_z(mpfr_value, mpz_value, MPFR_RNDN);
    double result = theta_prime_from_mpfr(mpfr_value, k);
    mpfr_clear(mpfr_value);
    mpz_clear(mpz_value);
    return result;
}

static double theta_prime_from_bn(const BIGNUM *bn, double k) {
    char *dec = BN_bn2dec(bn);
    if (!dec) {
        return 0.0;
    }
    double result = theta_prime_from_string(dec, k);
    OPENSSL_free(dec);
    return result;
}

static double circular_distance(double a, double b) {
    double diff = fmod(a - b + 0.5, 1.0) - 0.5;
    return fabs(diff);
}

static double elapsed_seconds(struct timeval start, struct timeval end) {
    return (double)(end.tv_sec - start.tv_sec) + (double)(end.tv_usec - start.tv_usec) / 1e6;
}

int z5d_factorization_shortcut(const char *modulus_decimal,
                               int max_iterations,
                               double epsilon,
                               z5d_factor_stat_t *out_stat) {
    if (!modulus_decimal || !out_stat) {
        return -1;
    }

    out_stat->success = 0;
    out_stat->divisions_tried = 0;
    out_stat->elapsed_seconds = 0.0;
    out_stat->factor_p = NULL;
    out_stat->factor_q = NULL;

    ensure_phi_initialized();

    BN_CTX *ctx = BN_CTX_new();
    if (!ctx) {
        return -1;
    }

    BIGNUM *N = BN_new();
    if (!N || !BN_dec2bn(&N, modulus_decimal)) {
        if (N) BN_free(N);
        BN_CTX_free(ctx);
        return -1;
    }

    mpz_t mpz_N;
    mpz_init_set_str(mpz_N, modulus_decimal, 10);
    mpfr_t mpfr_N;
    mpfr_init2(mpfr_N, 512);
    mpfr_set_z(mpfr_N, mpz_N, MPFR_RNDN);
    double theta_N = theta_prime_from_mpfr(mpfr_N, 0.45);
    mpfr_clear(mpfr_N);
    mpz_clear(mpz_N);

    struct timeval start, end;
    gettimeofday(&start, NULL);

    BIGNUM *candidate = BN_new();
    BIGNUM *remainder = BN_new();
    BIGNUM *quotient = BN_new();
    if (!candidate || !remainder || !quotient) {
        if (candidate) BN_free(candidate);
        if (remainder) BN_free(remainder);
        if (quotient) BN_free(quotient);
        BN_free(N);
        BN_CTX_free(ctx);
        return -1;
    }

    int attempts = 0;
    int success = 0;

    int target_bits = BN_num_bits(N) / 2;
    if (target_bits < 64) {
        target_bits = 64;
    }

    for (int iter = 0; iter < max_iterations; ++iter) {
        if (!BN_generate_prime_ex(candidate, target_bits, 0, NULL, NULL, NULL)) {
            continue;
        }
        attempts++;

        double theta_p = theta_prime_from_bn(candidate, 0.45);
        double dist = circular_distance(theta_p, theta_N);
        if (dist > epsilon) {
            continue;
        }

        if (!BN_mod(remainder, N, candidate, ctx)) {
            continue;
        }

        if (BN_is_zero(remainder)) {
            if (!BN_div(quotient, NULL, N, candidate, ctx)) {
                continue;
            }

            out_stat->factor_p = BN_bn2dec(candidate);
            out_stat->factor_q = BN_bn2dec(quotient);
            success = (out_stat->factor_p && out_stat->factor_q);
            break;
        }
    }

    gettimeofday(&end, NULL);
    out_stat->divisions_tried = attempts;
    out_stat->elapsed_seconds = elapsed_seconds(start, end);
    out_stat->success = success;

    BN_free(candidate);
    BN_free(remainder);
    BN_free(quotient);
    BN_free(N);
    BN_CTX_free(ctx);

    return success ? 1 : 0;
}

void z5d_factorization_free(z5d_factor_stat_t *stat) {
    if (!stat) return;
    if (stat->factor_p) {
        OPENSSL_free(stat->factor_p);
        stat->factor_p = NULL;
    }
    if (stat->factor_q) {
        OPENSSL_free(stat->factor_q);
        stat->factor_q = NULL;
    }
}
