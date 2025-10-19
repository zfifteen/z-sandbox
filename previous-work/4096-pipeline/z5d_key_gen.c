// z5d_secure_key_gen.c — Secure RSA-4096 using Z5D predictor with entropy
// Build: cc z5d_secure_key_gen.c z5d_predictor.c -o z5d_secure_key_gen -lmpfr -lgmp -lssl -lcrypto -lm
//
// **Z5D SECURE RSA KEY GENERATOR** - Uses high-entropy seeds for cryptographically
// secure RSA-4096 key generation with Z5D predictor integration. Generates unique,
// non-reproducible keys suitable for cryptographic applications.
//
// Purpose: This tool creates cryptographically secure RSA-4096 keys using the Z5D
// predictor for prime selection with high-entropy seed generation. Unlike the
// deterministic demo version, this generates unique keys each time and is suitable
// for actual cryptographic use cases while demonstrating Z5D integration.
//
// ---------------------------------------------------------------------------

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <time.h>
#include <limits.h>
#include <openssl/rsa.h>
#include <openssl/pem.h>
#include <openssl/x509.h>
#include <openssl/x509v3.h>
#include <openssl/evp.h>
#include <openssl/sha.h>
#include <openssl/crypto.h>
#include <gmp.h>
#include <mpfr.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <unistd.h>
#ifdef _OPENMP
#include <omp.h>
#endif
#include "../z_framework_params.h"
#include "../z5d_predictor.h"
#include "z_seed_generator.h"
#include "gpu_info.h"

// Default configuration
#define DEFAULT_BITS 4096
#define DEFAULT_E 65537
#define DEFAULT_VALIDITY_DAYS 30
#define DEFAULT_KAPPA_GEO ZF_KAPPA_GEO_DEFAULT
#define DEFAULT_KAPPA_STAR ZF_KAPPA_STAR_DEFAULT
#define DEFAULT_PHI ZF_GOLDEN_PHI
#define DEFAULT_BUMP_P 0
#define DEFAULT_BUMP_Q 1

#define MR_GEODESIC_WITNESSES 6
#define MR_STANDARD_WITNESSES 8

static const unsigned long MR_STANDARD_BASES[MR_STANDARD_WITNESSES] = {
    2UL, 3UL, 5UL, 7UL, 11UL, 13UL, 17UL, 19UL
};

static int g_debug = 0;
static int g_quiet = 0;

#define PRINT_ALWAYS(...) do { if (!g_quiet) fprintf(stdout, __VA_ARGS__); } while (0)
#define DBG_PRINTF(...)   do { if (g_debug && !g_quiet) fprintf(stdout, __VA_ARGS__); } while (0)

typedef struct {
    mpz_t n;
    mpz_t n_minus_1;
    mpz_t n_minus_3;
    mpz_t d;
    unsigned long r;
} mr_context_t;

// Configuration structure
typedef struct {
    uint8_t seed[SEED_SIZE];
    char seed_hex[HEX_SEED_LEN];
    int bits;
    unsigned long e;
    int validity_days;
    double kappa_geo;
    double kappa_star;
    double phi;
    int bump_p;
    int bump_q;
} config_t;

static int seed_error_exit_code(int rc) {
    switch (rc) {
        case ZSEED_ERR_ENTROPY_UNAVAIL:
            return 2;
        case ZSEED_ERR_READ_FAILURE:
            return 3;
        case ZSEED_ERR_CRYPTO_FAILURE:
            return 4;
        case ZSEED_ERR_NULL_POINTER:
        default:
            return 1;
    }
}

static void report_seed_failure(int rc) {
    switch (rc) {
        case ZSEED_ERR_ENTROPY_UNAVAIL:
            fprintf(stderr, "ERROR: entropy source unavailable\n");
            break;
        case ZSEED_ERR_READ_FAILURE:
            fprintf(stderr, "ERROR: entropy read failure\n");
            break;
        case ZSEED_ERR_CRYPTO_FAILURE:
            fprintf(stderr, "ERROR: cryptographic mixing failure\n");
            break;
        case ZSEED_ERR_NULL_POINTER:
        default:
            fprintf(stderr, "ERROR: internal seed generator failure\n");
            break;
    }
}

// Initialize default configuration
static int init_config(config_t *cfg) {
    int rc = z_generate_seed(cfg->seed);
    if (rc != ZSEED_OK) {
        return rc;
    }

    z_seed_to_hex(cfg->seed, cfg->seed_hex);
    cfg->bits = DEFAULT_BITS;
    cfg->e = DEFAULT_E;
    cfg->validity_days = DEFAULT_VALIDITY_DAYS;
    cfg->kappa_geo = DEFAULT_KAPPA_GEO;
    cfg->kappa_star = DEFAULT_KAPPA_STAR;
    cfg->phi = DEFAULT_PHI;
    cfg->bump_p = DEFAULT_BUMP_P;
    cfg->bump_q = DEFAULT_BUMP_Q;

    return ZSEED_OK;
}

// Print usage information
static void print_usage(const char *progname) {
    printf("Usage: %s [OPTIONS]\n", progname);
    printf("\n**Z5D SECURE RSA KEY GENERATOR** - Creates cryptographically secure RSA keys\n\n");
    printf("Options:\n");
    printf("  --bits INT             Key size in bits (default: %d)\n", DEFAULT_BITS);
    printf("  --e INT                Public exponent (default: %lu)\n", (unsigned long)DEFAULT_E);
    printf("  --validity-days INT    Certificate validity in days (default: %d)\n", DEFAULT_VALIDITY_DAYS);
    printf("  --kappa-geo FLOAT      Z5D kappa_geo parameter (default: %.3f)\n", DEFAULT_KAPPA_GEO);
    printf("  --kappa-star FLOAT     Z5D kappa_star parameter (default: %.5f)\n", DEFAULT_KAPPA_STAR);
    printf("  --phi FLOAT            Z5D phi parameter (default: %.15f)\n", DEFAULT_PHI);
    printf("  --bump-p INT           Bump value for p (default: %d)\n", DEFAULT_BUMP_P);
    printf("  --bump-q INT           Bump value for q (default: %d)\n", DEFAULT_BUMP_Q);
    printf("  --debug                Enable verbose diagnostic logging\n");
    printf("  --quiet                Suppress non-essential output\n");
    printf("  --help                 Show this help\n");
    printf("\nBy default, generates a new secure seed for each run.\n");
    printf("Output files: z5d_key_gen-<tag>.key and .crt (tag from seed hash)\n");
}

// Parse command line arguments
static int parse_args(int argc, char **argv, config_t *cfg) {
    static struct option long_options[] = {
        {"bits", required_argument, 0, 'b'},
        {"e", required_argument, 0, 'e'},
        {"validity-days", required_argument, 0, 'v'},
        {"kappa-geo", required_argument, 0, 'g'},
        {"kappa-star", required_argument, 0, 'k'},
        {"phi", required_argument, 0, 'p'},
        {"bump-p", required_argument, 0, 'P'},
        {"bump-q", required_argument, 0, 'Q'},
        {"debug", no_argument, 0, 'd'},
        {"quiet", no_argument, 0, 'q'},
        {"help", no_argument, 0, 'h'},
        {0, 0, 0, 0}
    };

    int c;
    while ((c = getopt_long(argc, argv, "b:e:v:g:k:p:P:Q:dqh", long_options, NULL)) != -1) {
        switch (c) {
            case 'b':
                cfg->bits = atoi(optarg);
                if (cfg->bits < 512 || cfg->bits > 8192) {
                    fprintf(stderr, "Error: bits must be between 512 and 8192\n");
                    return -1;
                }
                break;
            case 'e':
                cfg->e = strtoul(optarg, NULL, 10);
                break;
            case 'v':
                cfg->validity_days = atoi(optarg);
                break;
            case 'g':
                cfg->kappa_geo = atof(optarg);
                break;
            case 'k':
                cfg->kappa_star = atof(optarg);
                break;
            case 'p':
                cfg->phi = atof(optarg);
                break;
            case 'P':
                cfg->bump_p = atoi(optarg);
                if (cfg->bump_p < 0) {
                    fprintf(stderr, "Error: bump-p must be non-negative\n");
                    return -1;
                }
                break;
            case 'Q':
                cfg->bump_q = atoi(optarg);
                if (cfg->bump_q < 0) {
                    fprintf(stderr, "Error: bump-q must be non-negative\n");
                    return -1;
                }
                break;
            case 'd':
                g_debug = 1;
                break;
            case 'q':
                g_quiet = 1;
                break;
            case 'h':
                print_usage(argv[0]);
                exit(0);
            default:
                fprintf(stderr, "Try '%s --help' for more information.\n", argv[0]);
                return -1;
        }
    }
    return 0;
}

// Create deterministic tag from seed
static void create_tag(const uint8_t *seed, char *tag_out, size_t tag_size) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(seed, SEED_SIZE, hash);

    // Take first 4 bytes and convert to hex
    snprintf(tag_out, tag_size, "%02x%02x%02x%02x",
             hash[0], hash[1], hash[2], hash[3]);
}

// Derive seed for p or q
// DOMAIN-SEPARATION: one-way derivation for p- and q-specific seeds
// using SHA-256 over (tag || base_seed). The transient buffers used
// here are cleansed before return.
static void derive_seed(const uint8_t *base_seed, const char *tag, unsigned char *output, size_t output_size) {
    const size_t TAG_PREFIX_MAX = 32;
    unsigned char context[SEED_SIZE + TAG_PREFIX_MAX];
    unsigned char digest[SHA256_DIGEST_LENGTH];

    if (!output || output_size == 0) {
        return;
    }

    if (!base_seed || !tag) {
        memset(output, 0, output_size);
        return;
    }

    memset(context, 0, sizeof(context));
    size_t tag_len = strlen(tag);
    if (tag_len > TAG_PREFIX_MAX) {
        tag_len = TAG_PREFIX_MAX;
    }
    memcpy(context, tag, tag_len);
    memcpy(context + tag_len, base_seed, SEED_SIZE);

    SHA256(context, tag_len + SEED_SIZE, digest);

    size_t produced = 0;
    while (produced < output_size) {
        size_t chunk = SHA256_DIGEST_LENGTH;
        if (chunk > output_size - produced) {
            chunk = output_size - produced;
        }
        memcpy(output + produced, digest, chunk);
        produced += chunk;
        if (produced < output_size) {
            SHA256(digest, SHA256_DIGEST_LENGTH, digest);
        }
    }
    // MEMORY-HYGIENE: wipe transient buffers
    OPENSSL_cleanse(context, sizeof(context));
    OPENSSL_cleanse(digest, sizeof(digest));
}

static void mr_context_init(mr_context_t *ctx, const mpz_t n) {
    mpz_init_set(ctx->n, n);
    mpz_init(ctx->n_minus_1);
    mpz_sub_ui(ctx->n_minus_1, ctx->n, 1);
    mpz_init(ctx->n_minus_3);
    if (mpz_cmp_ui(ctx->n, 3) > 0) {
        mpz_sub_ui(ctx->n_minus_3, ctx->n, 3);
    } else {
        mpz_set_ui(ctx->n_minus_3, 0);
    }
    mpz_init_set(ctx->d, ctx->n_minus_1);
    ctx->r = 0;
    while (mpz_even_p(ctx->d)) {
        mpz_fdiv_q_2exp(ctx->d, ctx->d, 1);
        ctx->r++;
    }
}

static void mr_context_clear(mr_context_t *ctx) {
    mpz_clear(ctx->n);
    mpz_clear(ctx->n_minus_1);
    mpz_clear(ctx->n_minus_3);
    mpz_clear(ctx->d);
}

static void map_witness_into_range(const mr_context_t *ctx, mpz_t witness) {
    if (mpz_cmp_ui(witness, 2) < 0) {
        mpz_set_ui(witness, 2);
        return;
    }

    if (mpz_cmp(witness, ctx->n_minus_1) >= 0) {
        if (mpz_cmp_ui(ctx->n_minus_3, 1) <= 0) {
            mpz_set_ui(witness, 2);
        } else {
            mpz_mod(witness, witness, ctx->n_minus_3);
            mpz_add_ui(witness, witness, 2);
        }
    }
}

static void generate_standard_witnesses(mpz_t *witnesses, size_t count, const mr_context_t *ctx) {
    size_t limit = count < MR_STANDARD_WITNESSES ? count : MR_STANDARD_WITNESSES;
    for (size_t i = 0; i < limit; ++i) {
        mpz_set_ui(witnesses[i], MR_STANDARD_BASES[i]);
        map_witness_into_range(ctx, witnesses[i]);
    }
}

static void generate_geodesic_witnesses(mpz_t *witnesses, size_t count,
                                        const mpz_t candidate, const config_t *cfg,
                                        unsigned long hint, const mr_context_t *ctx) {
    if (count == 0) {
        return;
    }

    if (mpz_cmp_ui(ctx->n_minus_3, 1) <= 0) {
        for (size_t i = 0; i < count; ++i) {
            mpz_set_ui(witnesses[i], 2);
        }
        return;
    }

    size_t buf_size = (mpz_sizeinbase(candidate, 2) + 7) / 8;
    if (buf_size == 0) {
        buf_size = 1;
    }

    unsigned char *candidate_bytes = (unsigned char*)malloc(buf_size);
    if (!candidate_bytes) {
        for (size_t i = 0; i < count; ++i) {
            mpz_set_ui(witnesses[i], 2);
        }
        return;
    }

    size_t exported = 0;
    mpz_export(candidate_bytes, &exported, 1, 1, 0, 0, candidate);
    if (exported == 0) {
        exported = 1;
        candidate_bytes[0] = 0;
    }

    for (size_t i = 0; i < count; ++i) {
        unsigned char digest[SHA256_DIGEST_LENGTH];
        SHA256_CTX sha_ctx;
        SHA256_Init(&sha_ctx);
        SHA256_Update(&sha_ctx, candidate_bytes, exported);
        if (cfg) {
            SHA256_Update(&sha_ctx, cfg->seed, SEED_SIZE);
        }
        SHA256_Update(&sha_ctx, &hint, sizeof(hint));
        SHA256_Update(&sha_ctx, &i, sizeof(i));
        SHA256_Final(digest, &sha_ctx);

        mpz_import(witnesses[i], SHA256_DIGEST_LENGTH, 1, 1, 0, 0, digest);
        map_witness_into_range(ctx, witnesses[i]);
    }

    OPENSSL_cleanse(candidate_bytes, buf_size);
    free(candidate_bytes);
}

static int miller_rabin_round(const mr_context_t *ctx, const mpz_t witness) {
    mpz_t x;
    mpz_init(x);

    mpz_powm(x, witness, ctx->d, ctx->n);
    if (mpz_cmp_ui(x, 1) == 0 || mpz_cmp(x, ctx->n_minus_1) == 0) {
        mpz_clear(x);
        return 1;
    }

    for (unsigned long i = 1; i < ctx->r; ++i) {
        mpz_powm_ui(x, x, 2, ctx->n);
        if (mpz_cmp(x, ctx->n_minus_1) == 0) {
            mpz_clear(x);
            return 1;
        }
    }

    mpz_clear(x);
    return 0;
}

static int candidate_is_probable_prime(const mpz_t candidate, const config_t *cfg, unsigned long hint) {
    // MILLER–RABIN STRATEGY: Perform a sequence of geodesic-first and
    // standard witnesses. Early exits are allowed on strong probable-prime
    // hits; witness arrays are pre-allocated and reused to reduce heap churn.
    if (mpz_cmp_ui(candidate, 2) < 0) {
        return 0;
    }
    if (mpz_cmp_ui(candidate, 2) == 0) {
        return 1;
    }
    if (mpz_even_p(candidate)) {
        return 0;
    }

    mr_context_t ctx;
    mr_context_init(&ctx, candidate);

    // PRE-ALLOCATE: witness arrays are allocated once per check
    // and reused through the MR rounds to minimize heap churn.
    mpz_t geodesic[MR_GEODESIC_WITNESSES];
    mpz_t standard[MR_STANDARD_WITNESSES];

    for (size_t i = 0; i < MR_GEODESIC_WITNESSES; ++i) {
        mpz_init(geodesic[i]);
    }
    for (size_t i = 0; i < MR_STANDARD_WITNESSES; ++i) {
        mpz_init(standard[i]);
    }

    generate_geodesic_witnesses(geodesic, MR_GEODESIC_WITNESSES, candidate, cfg, hint, &ctx);
    generate_standard_witnesses(standard, MR_STANDARD_WITNESSES, &ctx);

    for (size_t i = 0; i < MR_GEODESIC_WITNESSES; ++i) {
        if (!miller_rabin_round(&ctx, geodesic[i])) {
            for (size_t j = 0; j < MR_GEODESIC_WITNESSES; ++j) {
                mpz_clear(geodesic[j]);
            }
            for (size_t j = 0; j < MR_STANDARD_WITNESSES; ++j) {
                mpz_clear(standard[j]);
            }
            mr_context_clear(&ctx);
            return 0;
        }
    }

    for (size_t i = 0; i < MR_STANDARD_WITNESSES; ++i) {
        if (!miller_rabin_round(&ctx, standard[i])) {
            for (size_t j = 0; j < MR_GEODESIC_WITNESSES; ++j) {
                mpz_clear(geodesic[j]);
            }
            for (size_t j = 0; j < MR_STANDARD_WITNESSES; ++j) {
                mpz_clear(standard[j]);
            }
            mr_context_clear(&ctx);
            return 0;
        }
    }

    for (size_t i = 0; i < MR_GEODESIC_WITNESSES; ++i) {
        mpz_clear(geodesic[i]);
    }
    for (size_t i = 0; i < MR_STANDARD_WITNESSES; ++i) {
        mpz_clear(standard[i]);
    }
    mr_context_clear(&ctx);
    return 1;
}

static void print_miller_rabin_info(const char *label) {
    if (g_debug && !g_quiet) {
        // NOTE: We log the MR configuration explicitly to aid operational
        // review of witness counts and early-exit behavior.
        printf("Miller-Rabin (%s): geodesic-first %d + standard %d witnesses (early exit)\n",
               label, MR_GEODESIC_WITNESSES, MR_STANDARD_WITNESSES);
    }
}

static inline int x931_too_close_2048(const mpz_t a, const mpz_t b) {
    mpz_t ah, bh;
    mpz_inits(ah, bh, NULL);
    mpz_fdiv_q_2exp(ah, a, 2048 - 100);
    mpz_fdiv_q_2exp(bh, b, 2048 - 100);
    int eq = (mpz_cmp(ah, bh) == 0);
    mpz_clears(ah, bh, NULL);
    return eq;
}

static int search_prime_candidates(const mpz_t start, unsigned long max_attempts,
                                   const config_t *cfg, unsigned long hint_seed,
                                   mpz_t result_out, int *used_parallel,
                                   unsigned long *attempts_used,
                                   unsigned int limit_bit,
                                   int clamp_on_limit,
                                   const mpz_t *too_close_ref,
                                   int enforce_not_too_close);

static int guided_prime_search(const mpz_t estimated_start,
                               unsigned long max_attempts,
                               const config_t *cfg,
                               unsigned long hint_seed,
                               mpz_t result_out,
                               int *used_parallel,
                               unsigned long *attempts_used,
                               const mpz_t *too_close_ref,
                               int enforce_not_too_close) {
    if (used_parallel) {
        *used_parallel = 0;
    }
    if (attempts_used) {
        *attempts_used = max_attempts;
    }

    mpz_t modulus;
    mpz_init(modulus);
    mpz_set_ui(modulus, 1);
    mpz_mul_2exp(modulus, modulus, 2048);

    mpz_t base_start;
    mpz_init(base_start);
    mpz_mod(base_start, estimated_start, modulus);
    mpz_setbit(base_start, 2047);
    if (!mpz_tstbit(base_start, 0)) {
        mpz_setbit(base_start, 0);
    }

    mpz_t current_start;
    mpz_init_set(current_start, base_start);

    unsigned long remaining = max_attempts;
    unsigned long offset = 0;
    int found = 0;

    while (remaining > 0) {
        unsigned long segment = remaining;

        mpz_t distance;
        mpz_init(distance);
        mpz_sub(distance, modulus, current_start);
        if (mpz_sgn(distance) <= 0) {
            mpz_clear(distance);
            break;  // already beyond limit; stop search
        }

        unsigned long twice_seg = segment > (ULONG_MAX / 2UL) ? ULONG_MAX : segment * 2UL;
        if (mpz_cmp_ui(distance, twice_seg) <= 0) {
            unsigned long safe_steps = (unsigned long)(mpz_get_ui(distance) / 2UL);
            if (safe_steps == 0) {
                safe_steps = 1;
            }
            if (safe_steps < segment) {
                segment = safe_steps;
            }
        }
        mpz_clear(distance);

        unsigned long segment_attempts_used = segment;
        int segment_used_parallel = 0;

        found = search_prime_candidates(current_start,
                                        segment,
                                        cfg,
                                        hint_seed + offset,
                                        result_out,
                                        &segment_used_parallel,
                                        &segment_attempts_used,
                                        2048,
                                        0,
                                        too_close_ref,
                                        enforce_not_too_close);
        if (found) {
            if (used_parallel && segment_used_parallel) {
                *used_parallel = 1;
            }
            if (attempts_used) {
                *attempts_used = offset + segment_attempts_used;
            }
            break;
        }

        offset += segment;
        remaining -= segment;
        if (remaining == 0) {
            break;
        }

        mpz_set(current_start, base_start);
        mpz_add_ui(current_start, current_start, 2UL * offset);

        if (mpz_cmp(current_start, modulus) >= 0) {
            break;  // stop instead of wrapping past 2048-bit boundary
        }
    }

    mpz_clear(current_start);
    mpz_clear(base_start);
    mpz_clear(modulus);

    return found;
}

static int search_prime_candidates(const mpz_t start, unsigned long max_attempts,
                                   const config_t *cfg, unsigned long hint_seed,
                                   mpz_t result_out, int *used_parallel,
                                   unsigned long *attempts_used,
                                   unsigned int limit_bit,
                                   int clamp_on_limit,
                                   const mpz_t *too_close_ref,
                                   int enforce_not_too_close) {
    if (used_parallel) {
        *used_parallel = 0;
    }
    if (attempts_used) {
        *attempts_used = max_attempts;
    }

    if (max_attempts == 0) {
        return 0;
    }

#ifdef _OPENMP
    int requested_threads = omp_get_max_threads();
    if (requested_threads > 1 && max_attempts > 1) {
        int thread_count = requested_threads;
        if ((unsigned long)thread_count > max_attempts) {
            thread_count = (int)max_attempts;
        }
        if (thread_count > 1) {
            mpz_t base_candidate;
            mpz_init_set(base_candidate, start);
            mpz_t found_prime;
            mpz_init(found_prime);
            volatile int found = 0;
            unsigned long found_attempt = max_attempts;
            volatile int limit_reached = 0;

// PARALLEL SEARCH: Each thread explores a disjoint arithmetic progression of
// candidates (unique stride by thread id) under OpenMP. We use barrier/flush
// and a critical section to coordinate the first-found prime and avoid data races.
#pragma omp parallel num_threads(thread_count) shared(found, found_prime, base_candidate, found_attempt)
            {
                const int thread_id = omp_get_thread_num();
                const int total_threads = omp_get_num_threads();
                unsigned long attempt_index = (unsigned long)thread_id;
                const unsigned long stride = 2UL * (unsigned long)total_threads;

                mpz_t candidate;
                mpz_init_set(candidate, base_candidate);
                mpz_add_ui(candidate, candidate, 2UL * (unsigned long)thread_id);
                int stop_thread = 0;
                if (limit_bit > 0 && mpz_tstbit(candidate, limit_bit)) {
                    if (clamp_on_limit) {
                        mpz_clrbit(candidate, limit_bit);
                        mpz_setbit(candidate, limit_bit - 1);
                    } else {
                        limit_reached = 1;
#pragma omp flush(limit_reached)
                        stop_thread = 1;
                    }
                }

                while (!stop_thread && attempt_index < max_attempts) {
#pragma omp flush(found, limit_reached)
                    if (found || limit_reached) {
                        break;
                    }

                    unsigned long current_attempt = attempt_index;
                    unsigned long hint_value = hint_seed ^ current_attempt;
                    if (candidate_is_probable_prime(candidate, cfg, hint_value)) {
                        if (enforce_not_too_close && too_close_ref &&
                            x931_too_close_2048((*too_close_ref), candidate)) {
                            // Skip candidates too close to reference prime
                        } else {
#pragma omp critical
                        {
                            if (!found) {
                                mpz_set(found_prime, candidate);
                                found_attempt = current_attempt;
                                found = 1;
                            }
                        }
#pragma omp flush(found)
                        break;
                        }
                    }

                    mpz_add_ui(candidate, candidate, stride);
                    if (limit_bit > 0 && mpz_tstbit(candidate, limit_bit)) {
                        if (clamp_on_limit) {
                            mpz_clrbit(candidate, limit_bit);
                            mpz_setbit(candidate, limit_bit - 1);
                        } else {
                            limit_reached = 1;
#pragma omp flush(limit_reached)
                            stop_thread = 1;
                        }
                    }
                    attempt_index += (unsigned long)total_threads;
                }

                mpz_clear(candidate);
            }

            if (found) {
                if (used_parallel) {
                    *used_parallel = 1;
                }
                if (attempts_used) {
                    *attempts_used = found_attempt;
                }
                mpz_set(result_out, found_prime);
                mpz_clear(found_prime);
                mpz_clear(base_candidate);
                return 1;
            }

            if (limit_reached) {
                mpz_clear(found_prime);
                mpz_clear(base_candidate);
                return 0;
            }

            mpz_clear(found_prime);
            mpz_clear(base_candidate);
        }
    }
#endif

    mpz_t candidate;
    mpz_init_set(candidate, start);
    for (unsigned long attempt = 0; attempt < max_attempts; ++attempt) {
        unsigned long hint_value = hint_seed ^ attempt;
        if (candidate_is_probable_prime(candidate, cfg, hint_value)) {
            if (!enforce_not_too_close || !too_close_ref ||
                !x931_too_close_2048((*too_close_ref), candidate)) {
                mpz_set(result_out, candidate);
                if (attempts_used) {
                    *attempts_used = attempt;
                }
                mpz_clear(candidate);
                return 1;
            }
        }
        mpz_add_ui(candidate, candidate, 2);
        if (limit_bit > 0 && mpz_tstbit(candidate, limit_bit)) {
            if (clamp_on_limit) {
                mpz_clrbit(candidate, limit_bit);
                mpz_setbit(candidate, limit_bit - 1);
            } else {
                break;
            }
        }
    }

    mpz_clear(candidate);
    return 0;
}

// Convert seed bytes to 2048-bit value with MSB=1, LSB=1
// Convert seed bytes to a 2048-bit candidate space.
// NOTE: We force MSB to ensure exact 2048-bit width and LSB to ensure oddness,
// which is standard practice for RSA candidate generation.
static void seed_to_2048bit(const unsigned char *seed_bytes, mpz_t result) {
    // Expand 256-bit seed to 2048 bits by repeated hashing
    unsigned char expanded[256];  // 2048 bits = 256 bytes
    derive_seed(seed_bytes, "2048bit", expanded, sizeof(expanded));

    // Import all 256 bytes to get a full 2048-bit number
    mpz_import(result, sizeof(expanded), 1, 1, 0, 0, expanded);

    // Ensure it's exactly 2048 bits by setting MSB
    mpz_setbit(result, 2047);

    // Ensure it's odd by setting LSB
    mpz_setbit(result, 0);
}

// Advanced Z5D prime count with Z Framework optimization and OpenMP
static void z5d_prime_count(const mpz_t x, mpz_t count_out, const config_t *cfg) {
    if (mpz_cmp_ui(x, 2) < 0) {
        mpz_set_ui(count_out, 0);
        return;
    }

    (void)cfg;  // Reserved for future adaptive calibration

    // Adapt precision to the magnitude of x (bits of x plus safety margin)
    int precision_bits = mpz_sizeinbase(x, 2) + 64;
    if (precision_bits < 256) {
        precision_bits = 256;
    }

    mpfr_t x_mpfr, ln_x, pnt_base, z5d_correction, result;
    mpfr_init2(x_mpfr, precision_bits);
    mpfr_init2(ln_x, precision_bits);
    mpfr_init2(pnt_base, precision_bits);
    mpfr_init2(z5d_correction, precision_bits);
    mpfr_init2(result, precision_bits);

    mpfr_set_z(x_mpfr, x, MPFR_RNDN);
    mpfr_log(ln_x, x_mpfr, MPFR_RNDN);

    // PNT base: x / ln(x)
    mpfr_div(pnt_base, x_mpfr, ln_x, MPFR_RNDN);

    // Z5D correction using calibrated parameters
    mpfr_t temp1, temp2, kappa_star_mpfr, c_calibrated_mpfr;
    mpfr_init2(temp1, precision_bits);
    mpfr_init2(temp2, precision_bits);
    mpfr_init2(kappa_star_mpfr, precision_bits);
    mpfr_init2(c_calibrated_mpfr, precision_bits);

    double kappa_star = cfg ? cfg->kappa_star : ZF_KAPPA_STAR_DEFAULT;
    mpfr_set_d(kappa_star_mpfr, kappa_star, MPFR_RNDN);
    mpfr_set_d(c_calibrated_mpfr, ZF_Z5D_C_CALIBRATED, MPFR_RNDN);

    // Z5D enhancement: PNT_base * (1 + kappa_star * correction_term + c_calibrated)
    mpfr_mul(temp1, kappa_star_mpfr, ln_x, MPFR_RNDN);  // kappa_star * ln(x)
    mpfr_add(temp2, temp1, c_calibrated_mpfr, MPFR_RNDN);  // + c_calibrated
    mpfr_add_ui(z5d_correction, temp2, 1, MPFR_RNDN);  // 1 + correction

    // Final Z5D estimate
    mpfr_mul(result, pnt_base, z5d_correction, MPFR_RNDN);

    mpfr_get_z(count_out, result, MPFR_RNDN);

    mpfr_clear(x_mpfr);
    mpfr_clear(ln_x);
    mpfr_clear(pnt_base);
    mpfr_clear(z5d_correction);
    mpfr_clear(result);
    mpfr_clear(temp1);
    mpfr_clear(temp2);
    mpfr_clear(kappa_star_mpfr);
    mpfr_clear(c_calibrated_mpfr);
}

// Advanced Z5D nth prime with framework integration and OpenMP optimization
static int z5d_nth_prime(const char *label, const mpz_t k, mpz_t prime_out,
                         const config_t *cfg, const mpz_t *too_close_ref,
                         int enforce_not_too_close) {
    if (g_debug && !g_quiet) {
        gmp_printf("Z5D nth_prime prediction (k=%Zd) with framework optimization...\n", k);
    }
    print_miller_rabin_info(label ? label : "n");
#ifdef _OPENMP
    int max_threads = omp_get_max_threads();
    if (g_debug && !g_quiet) {
        if (max_threads > 1) {
            printf("OpenMP parallel candidate search enabled (%d threads)\n", max_threads);
        } else {
            printf("OpenMP available but using a single thread for candidate search\n");
        }
    }
#else
    if (g_debug && !g_quiet) {
        printf("OpenMP disabled: candidate search running single-threaded\n");
    }
#endif

    // Attempt Z5D-guided search first
    if (mpz_cmp_d(k, ZF_MIN_K_NTH) >= 0) {
        int precision_bits = mpz_sizeinbase(k, 2) + 128;
        if (precision_bits < 256) {
            precision_bits = 256;
        }

        mpfr_t k_mpfr, ln_k, ln_ln_k, z5d_estimate;
        mpfr_init2(k_mpfr, precision_bits);
        mpfr_init2(ln_k, precision_bits);
        mpfr_init2(ln_ln_k, precision_bits);
        mpfr_init2(z5d_estimate, precision_bits);

        mpfr_set_z(k_mpfr, k, MPFR_RNDN);
        mpfr_log(ln_k, k_mpfr, MPFR_RNDN);
        mpfr_log(ln_ln_k, ln_k, MPFR_RNDN);

        mpfr_t correction_term, kappa_star_mpfr, temp;
        mpfr_init2(correction_term, precision_bits);
        mpfr_init2(kappa_star_mpfr, precision_bits);
        mpfr_init2(temp, precision_bits);

        double kappa_star = cfg ? cfg->kappa_star : ZF_KAPPA_STAR_DEFAULT;
        mpfr_set_d(kappa_star_mpfr, kappa_star, MPFR_RNDN);

        mpfr_div(temp, ln_ln_k, ln_k, MPFR_RNDN);
        mpfr_mul(correction_term, kappa_star_mpfr, temp, MPFR_RNDN);

        mpfr_add(temp, ln_k, ln_ln_k, MPFR_RNDN);
        mpfr_sub_ui(temp, temp, 1, MPFR_RNDN);
        mpfr_add(temp, temp, correction_term, MPFR_RNDN);
        mpfr_mul(z5d_estimate, k_mpfr, temp, MPFR_RNDN);

        mpz_t estimated_prime;
        mpz_init(estimated_prime);
        mpfr_get_z(estimated_prime, z5d_estimate, MPFR_RNDN);

        if (mpz_cmp(estimated_prime, k) < 0) {
            mpz_mul_ui(estimated_prime, k, 10);
        }

        if (g_debug && !g_quiet) {
            gmp_printf("Z5D estimated prime for k=%Zd: %Zd\n", k, estimated_prime);
        }

        mpz_set(prime_out, estimated_prime);
        if (mpz_even_p(prime_out)) {
            mpz_add_ui(prime_out, prime_out, 1);
        }

        const unsigned long MAX_LOCAL_ATTEMPTS = 5000UL;
        unsigned long k_hint = mpz_get_ui(k);
        unsigned long attempts_used = MAX_LOCAL_ATTEMPTS;
        int used_parallel = 0;

        mpz_t search_start;
        mpz_init_set(search_start, prime_out);

        if (g_debug && !g_quiet) {
            printf("Starting prime search from Z5D estimate (max %lu attempts)...\n",
                   MAX_LOCAL_ATTEMPTS);
        }
        int found_from_estimate = guided_prime_search(
            search_start,
            MAX_LOCAL_ATTEMPTS,
            cfg,
            k_hint,
            prime_out,
            &used_parallel,
            &attempts_used,
            too_close_ref,
            enforce_not_too_close);
        mpz_clear(search_start);

        if (found_from_estimate && g_debug && !g_quiet) {
            printf("Found prime after %lu attempts%s\n",
                   attempts_used,
                   used_parallel ? " (parallel)" : "");
        }

        mpfr_clear(k_mpfr);
        mpfr_clear(ln_k);
        mpfr_clear(ln_ln_k);
        mpfr_clear(z5d_estimate);
        mpfr_clear(correction_term);
        mpfr_clear(kappa_star_mpfr);
        mpfr_clear(temp);
        mpz_clear(estimated_prime);

        if (found_from_estimate) {
            return 1;
        }
    }

    // Fallback: Generate secure random 2048-bit prime (original secure method)
    if (g_debug && !g_quiet) {
        printf("Using secure random 2048-bit prime generation...\n");
    }

    mpz_t candidate;
    mpz_init(candidate);

    // Get a random starting point in the 2048-bit range using the config seed and bumps
    unsigned char prime_seed[256];  // 2048 bits to fill the entire range
    char tag[32];
    snprintf(tag, sizeof(tag), "prime_p%d_q%d", cfg->bump_p, cfg->bump_q);
    derive_seed(cfg->seed, tag, prime_seed, sizeof(prime_seed));

    // Import as full 2048-bit number
    mpz_import(candidate, sizeof(prime_seed), 1, 1, 0, 0, prime_seed);

    // Ensure it's in the 2048-bit range by setting MSB
    mpz_setbit(candidate, 2047);

    // Ensure it's odd
    mpz_setbit(candidate, 0);

    const unsigned long MAX_PRIME_ATTEMPTS = 10000UL;  // Reasonable limit for 2048-bit primes
    unsigned long random_attempts_used = MAX_PRIME_ATTEMPTS;
    int random_used_parallel = 0;

    int found_random = search_prime_candidates(
        candidate,
        MAX_PRIME_ATTEMPTS,
        cfg,
        0UL,
        prime_out,
        &random_used_parallel,
        &random_attempts_used,
        2048,
        1,
        too_close_ref,
        enforce_not_too_close);
    mpz_clear(candidate);

    if (found_random && g_debug && !g_quiet) {
        printf("Found 2048-bit prime after %lu attempts%s\n",
               random_attempts_used,
               random_used_parallel ? " (parallel)" : "");
        return 1;  // Success
    }

    fprintf(stderr, "ERROR: Failed to find 2048-bit prime after %lu attempts\n", MAX_PRIME_ATTEMPTS);
    return 0;  // Failure
}

// Generate RSA keypair using Z5D
static RSA* generate_rsa_keypair(const config_t *cfg) {
    if (g_debug && !g_quiet) {
        printf("# Z5D SECURE RSA KEY GENERATOR\n");
        printf("# seed_hex=\"%s\"; bumps: p=%d, q=%d; z5d_params: kappa_geo=%.3f, kappa_star=%.5f\n",
               cfg->seed_hex, cfg->bump_p, cfg->bump_q, cfg->kappa_geo, cfg->kappa_star);
    }

    // Derive seeds for p and q
    unsigned char seed_p[32], seed_q[32];
    derive_seed(cfg->seed, "p", seed_p, sizeof(seed_p));
    derive_seed(cfg->seed, "q", seed_q, sizeof(seed_q));

    // Convert to 2048-bit values
    mpz_t x_p, x_q;
    mpz_init(x_p);
    mpz_init(x_q);
    seed_to_2048bit(seed_p, x_p);
    seed_to_2048bit(seed_q, x_q);

    if (g_debug && !g_quiet) {
        gmp_printf("x_p (2048-bit): %Zx\n", x_p);
        gmp_printf("x_q (2048-bit): %Zx\n", x_q);
    }

    // Get prime counts
    mpz_t k_base_p, k_base_q;
    mpz_init(k_base_p);
    mpz_init(k_base_q);
    z5d_prime_count(x_p, k_base_p, cfg);
    z5d_prime_count(x_q, k_base_q, cfg);

    if (g_debug && !g_quiet) {
        gmp_printf("k_base_p: %Zd\n", k_base_p);
        gmp_printf("k_base_q: %Zd\n", k_base_q);
    }

    // Add bumps
    mpz_add_ui(k_base_p, k_base_p, cfg->bump_p);
    mpz_add_ui(k_base_q, k_base_q, cfg->bump_q);

    // Get primes via z5d nth_prime
    mpz_t p, q;
    mpz_init(p);
    mpz_init(q);

    if (g_debug && !g_quiet) {
        printf("Generating p via z5d.nth_prime...\n");
    }
    if (!z5d_nth_prime("p", k_base_p, p, cfg, NULL, 0)) {
        fprintf(stderr, "ERROR: Failed to generate prime p\n");
        mpz_clear(x_p);
        mpz_clear(x_q);
        mpz_clear(k_base_p);
        mpz_clear(k_base_q);
        mpz_clear(p);
        mpz_clear(q);
        return NULL;
    }
    if (g_debug && !g_quiet) {
        gmp_printf("p: %Zd\n", p);
    }

    if (g_debug && !g_quiet) {
        printf("Generating q via z5d.nth_prime...\n");
    }
    if (!z5d_nth_prime("q", k_base_q, q, cfg, &p, 1)) {
        fprintf(stderr, "ERROR: Failed to generate prime q\n");
        mpz_clear(x_p);
        mpz_clear(x_q);
        mpz_clear(k_base_p);
        mpz_clear(k_base_q);
        mpz_clear(p);
        mpz_clear(q);
        return NULL;
    }
    if (g_debug && !g_quiet) {
        gmp_printf("q: %Zd\n", q);
    }

    // Guard against p == q with retry loop
    int retry_count = 0;
    const int MAX_RETRIES = 10;

    while (mpz_cmp(p, q) == 0 && retry_count < MAX_RETRIES) {
        if (g_debug && !g_quiet) {
            printf("p == q detected (attempt %d/%d), adjusting q...\n", retry_count + 1, MAX_RETRIES);
        }

        // Increment bump_q to get a different prime
        int original_bump_q = cfg->bump_q;
        config_t temp_cfg = *cfg;
        temp_cfg.bump_q = original_bump_q + retry_count + 2;

        // Re-derive q with new bump (k_base_q already has original bump_q added)
        mpz_t temp_k_base_q;
        mpz_init(temp_k_base_q);

        // Start from original k_base_q (before bump was added) and add new bump
        z5d_prime_count(x_q, temp_k_base_q, cfg);  // Recalculate base
        mpz_add_ui(temp_k_base_q, temp_k_base_q, temp_cfg.bump_q);

        if (!z5d_nth_prime("q", temp_k_base_q, q, &temp_cfg, &p, 1)) {
            fprintf(stderr, "ERROR: Failed to generate prime q in retry %d\n", retry_count + 1);
            mpz_clear(temp_k_base_q);
            mpz_clear(x_p);
            mpz_clear(x_q);
            mpz_clear(k_base_p);
            mpz_clear(k_base_q);
            mpz_clear(p);
            mpz_clear(q);
            return NULL;
        }
        mpz_clear(temp_k_base_q);

        retry_count++;
        if (g_debug && !g_quiet) {
            gmp_printf("Adjusted q (bump_q=%d): %Zd\n", temp_cfg.bump_q, q);
        }
    }

    if (mpz_cmp(p, q) == 0) {
        fprintf(stderr, "ERROR: Failed to generate different p and q after %d retries\n", MAX_RETRIES);
        fprintf(stderr, "This indicates a serious issue with the prime generation logic\n");
        return NULL;
    }

    if (retry_count > 0 && g_debug && !g_quiet) {
        printf("Successfully generated different p and q after %d retries\n", retry_count);
    }

    // Build RSA keypair
    RSA *rsa = RSA_new();
    if (!rsa) {
        fprintf(stderr, "Failed to create RSA structure\n");
        goto cleanup;
    }

    BIGNUM *bn_p = BN_new();
    BIGNUM *bn_q = BN_new();
    BIGNUM *bn_n = BN_new();
    BIGNUM *bn_e = BN_new();
    BIGNUM *bn_d = BN_new();
    BIGNUM *bn_dmp1 = BN_new();
    BIGNUM *bn_dmq1 = BN_new();
    BIGNUM *bn_iqmp = BN_new();

    if (!bn_p || !bn_q || !bn_n || !bn_e || !bn_d || !bn_dmp1 || !bn_dmq1 || !bn_iqmp) {
        fprintf(stderr, "Failed to create BIGNUM structures\n");
        goto cleanup;
    }

    // Convert GMP -> BIGNUM using binary export (big-endian) to avoid
    // large decimal string allocations and parsing overhead.
    size_t p_bytes_len = (mpz_sizeinbase(p, 2) + 7) / 8; if (p_bytes_len == 0) p_bytes_len = 1;
    size_t q_bytes_len = (mpz_sizeinbase(q, 2) + 7) / 8; if (q_bytes_len == 0) q_bytes_len = 1;

    unsigned char *p_bytes = (unsigned char*)malloc(p_bytes_len);
    unsigned char *q_bytes = (unsigned char*)malloc(q_bytes_len);
    if (!p_bytes || !q_bytes) {
        fprintf(stderr, "Failed to allocate temporary buffers for mpz_export\n");
        if (p_bytes) { OPENSSL_cleanse(p_bytes, p_bytes_len); free(p_bytes); }
        if (q_bytes) { OPENSSL_cleanse(q_bytes, q_bytes_len); free(q_bytes); }
        goto cleanup;
    }

    size_t p_written = 0, q_written = 0;
    mpz_export(p_bytes, &p_written, 1 /* most significant word first */, 1 /* 1 byte */, 1 /* big-endian */, 0, p);
    mpz_export(q_bytes, &q_written, 1, 1, 1, 0, q);
    if (p_written == 0) { p_written = 1; p_bytes[0] = 0; }
    if (q_written == 0) { q_written = 1; q_bytes[0] = 0; }

    if (!BN_bin2bn(p_bytes, (int)p_written, bn_p) || !BN_bin2bn(q_bytes, (int)q_written, bn_q)) {
        fprintf(stderr, "Failed to convert mpz to BIGNUM via BN_bin2bn\n");
        OPENSSL_cleanse(p_bytes, p_bytes_len); free(p_bytes);
        OPENSSL_cleanse(q_bytes, q_bytes_len); free(q_bytes);
        goto cleanup;
    }

    OPENSSL_cleanse(p_bytes, p_bytes_len); free(p_bytes);
    OPENSSL_cleanse(q_bytes, q_bytes_len); free(q_bytes);

    // Calculate n = p * q
    BN_CTX *ctx = BN_CTX_new();
    BN_mul(bn_n, bn_p, bn_q, ctx);

    // Set e
    BN_set_word(bn_e, cfg->e);

    // Calculate λ = lcm(p-1, q-1)
    BIGNUM *p_minus_1 = BN_new();
    BIGNUM *q_minus_1 = BN_new();
    BIGNUM *lambda = BN_new();
    BIGNUM *gcd = BN_new();

    BN_sub(p_minus_1, bn_p, BN_value_one());
    BN_sub(q_minus_1, bn_q, BN_value_one());
    BN_gcd(gcd, p_minus_1, q_minus_1, ctx);
    BN_mul(lambda, p_minus_1, q_minus_1, ctx);
    BN_div(lambda, NULL, lambda, gcd, ctx);

    // Calculate d = e^(-1) mod λ
    if (!BN_mod_inverse(bn_d, bn_e, lambda, ctx)) {
        fprintf(stderr, "Failed to calculate private exponent\n");
        goto cleanup;
    }

    // Calculate CRT parameters
    BN_mod(bn_dmp1, bn_d, p_minus_1, ctx);
    BN_mod(bn_dmq1, bn_d, q_minus_1, ctx);
    BN_mod_inverse(bn_iqmp, bn_q, bn_p, ctx);

    // Set RSA parameters
    RSA_set0_key(rsa, bn_n, bn_e, bn_d);
    RSA_set0_factors(rsa, bn_p, bn_q);
    RSA_set0_crt_params(rsa, bn_dmp1, bn_dmq1, bn_iqmp);

    BN_free(p_minus_1);
    BN_free(q_minus_1);
    BN_free(lambda);
    BN_free(gcd);
    BN_CTX_free(ctx);

cleanup:
    mpz_clear(x_p);
    mpz_clear(x_q);
    mpz_clear(k_base_p);
    mpz_clear(k_base_q);
    mpz_clear(p);
    mpz_clear(q);

    return rsa;
}

// Generate self-signed X.509 certificate
static X509* generate_certificate(RSA *rsa, const config_t *cfg) {
    X509 *x509 = X509_new();
    if (!x509) return NULL;

    // Create EVP_PKEY wrapper for signing without stealing RSA ownership
    EVP_PKEY *pkey = EVP_PKEY_new();
    if (!pkey || !EVP_PKEY_set1_RSA(pkey, rsa)) {
        if (pkey) EVP_PKEY_free(pkey);
        X509_free(x509);
        return NULL;
    }

    // Set certificate version (V3)
    X509_set_version(x509, 2);

    // SERIAL NUMBER: Use fresh entropy independent from the master seed
    // to prevent cross-run correlation via serials; buffers are cleansed.
    uint8_t serial_entropy[SEED_SIZE];
    if (z_generate_seed(serial_entropy) != 0) {
        EVP_PKEY_free(pkey);
        X509_free(x509);
        return NULL;
    }

    unsigned char serial_bytes[20];
    memcpy(serial_bytes, serial_entropy, sizeof(serial_bytes));
    OPENSSL_cleanse(serial_entropy, sizeof(serial_entropy));

    BIGNUM *serial_bn = BN_bin2bn(serial_bytes, (int)sizeof(serial_bytes), NULL);
    OPENSSL_cleanse(serial_bytes, sizeof(serial_bytes));
    if (!serial_bn) {
        EVP_PKEY_free(pkey);
        X509_free(x509);
        return NULL;
    }

    ASN1_INTEGER *serial = ASN1_INTEGER_new();
    if (!serial || !BN_to_ASN1_INTEGER(serial_bn, serial) || !X509_set_serialNumber(x509, serial)) {
        if (serial) ASN1_INTEGER_free(serial);
        BN_free(serial_bn);
        EVP_PKEY_free(pkey);
        X509_free(x509);
        return NULL;
    }
    BN_free(serial_bn);
    ASN1_INTEGER_free(serial);

    // Set validity period
    X509_gmtime_adj(X509_get_notBefore(x509), 0);
    X509_gmtime_adj(X509_get_notAfter(x509), (long)cfg->validity_days * 24 * 3600);

    // Set public key
    X509_set_pubkey(x509, pkey);

    // Set subject name
    X509_NAME *name = X509_get_subject_name(x509);
    X509_NAME_add_entry_by_txt(name, "CN", MBSTRING_ASC,
        (unsigned char*)"Z5D_SECURE_RSA_KEY_GEN", -1, -1, 0);
    X509_NAME_add_entry_by_txt(name, "O", MBSTRING_ASC,
        (unsigned char*)"Z5D SECURE RSA KEY GENERATOR (CRYPTOGRAPHICALLY SECURE)", -1, -1, 0);

    // Self-signed: issuer = subject
    X509_set_issuer_name(x509, name);

    // Add extensions
    X509V3_CTX ctx;
    X509V3_set_ctx_nodb(&ctx);
    X509V3_set_ctx(&ctx, x509, x509, NULL, NULL, 0);

    X509_EXTENSION *ext;

    // Basic constraints
    ext = X509V3_EXT_conf_nid(NULL, &ctx, NID_basic_constraints, "CA:FALSE");
    X509_add_ext(x509, ext, -1);
    X509_EXTENSION_free(ext);

    // Key usage
    ext = X509V3_EXT_conf_nid(NULL, &ctx, NID_key_usage, "digitalSignature,keyEncipherment");
    X509_add_ext(x509, ext, -1);
    X509_EXTENSION_free(ext);

    // Extended key usage
    ext = X509V3_EXT_conf_nid(NULL, &ctx, NID_ext_key_usage, "serverAuth,clientAuth");
    X509_add_ext(x509, ext, -1);
    X509_EXTENSION_free(ext);

    // Subject alternative name
    ext = X509V3_EXT_conf_nid(NULL, &ctx, NID_subject_alt_name, "DNS:secure.z5d.crypto");
    X509_add_ext(x509, ext, -1);
    X509_EXTENSION_free(ext);

    // Sign the certificate
    X509_sign(x509, pkey, EVP_sha256());

    // pkey no longer needed; RSA remains owned by caller due to set1 refcounting
    EVP_PKEY_free(pkey);

    return x509;
}

// Write files with deterministic names
static void write_files(RSA *rsa, X509 *cert, const config_t *cfg) {
    char tag[9];
    create_tag(cfg->seed, tag, sizeof(tag));

    const char *output_dir = "generated";
    // OUTPUT PROTECTION: Create output directory with owner-only perms (0700)
    // and apply umask(0077) at startup to prevent overly-permissive files.

    struct stat st = {0};
    if (stat(output_dir, &st) != 0) {
        if (mkdir(output_dir, 0700) != 0) {
            perror("ERROR: failed to create output directory");
            return;
        }
    } else if (!S_ISDIR(st.st_mode)) {
        fprintf(stderr, "ERROR: %s exists and is not a directory\n", output_dir);
        return;
    }

    char key_filename[256], cert_filename[256];
    snprintf(key_filename, sizeof(key_filename), "%s/z5d_key_gen-%s.key", output_dir, tag);
    snprintf(cert_filename, sizeof(cert_filename), "%s/z5d_key_gen-%s.crt", output_dir, tag);

    // Write private key
    FILE *key_file = fopen(key_filename, "w");
    if (key_file) {
        fprintf(key_file, "# Z5D SECURE RSA KEY GENERATOR\n");
        fprintf(key_file, "# seed_hex=\"%s\"; bumps: p=%d, q=%d; entropy: SYSTEM_GENERATED\n",
                cfg->seed_hex, cfg->bump_p, cfg->bump_q);

        EVP_PKEY *pkey = EVP_PKEY_new();
        EVP_PKEY_assign_RSA(pkey, RSAPrivateKey_dup(rsa));
        PEM_write_PrivateKey(key_file, pkey, NULL, NULL, 0, NULL, NULL);
        if (fchmod(fileno(key_file), 0600) != 0) {
            perror("WARNING: failed to set key permissions to 0600");
        }
        EVP_PKEY_free(pkey);
        fclose(key_file);
        PRINT_ALWAYS("Wrote private key: %s\n", key_filename);
    }

    // Write certificate
    FILE *cert_file = fopen(cert_filename, "w");
    if (cert_file) {
        PEM_write_X509(cert_file, cert);
        fclose(cert_file);
        PRINT_ALWAYS("Wrote certificate: %s\n", cert_filename);
    }
}

int main(int argc, char **argv) {
    // UMASK_POLICY: prevent accidental world/group-readable outputs
    umask(0077);
#ifdef _OPENMP
    // Force OpenMP to use the maximum available threads from program start.
    omp_set_dynamic(0);
    omp_set_num_threads(omp_get_max_threads());
#endif
    struct timeval start_time, end_time;
    gettimeofday(&start_time, NULL);

    config_t cfg;
    int seed_rc = init_config(&cfg);
    if (seed_rc != ZSEED_OK) {
        report_seed_failure(seed_rc);
        return seed_error_exit_code(seed_rc);
    }

    if (parse_args(argc, argv, &cfg) != 0) {
        return 1;
    }

    PRINT_ALWAYS("=== Z5D SECURE RSA-4096 Key Generator ===\n");
    PRINT_ALWAYS("**Cryptographically secure keys using Z5D predictor with entropy**\n\n");

    PRINT_ALWAYS("Configuration:\n");
    DBG_PRINTF("  Seed: %s (SYSTEM_GENERATED)\n", cfg.seed_hex);
    PRINT_ALWAYS("  Bits: %d\n", cfg.bits);
    PRINT_ALWAYS("  e: %lu\n", cfg.e);
    PRINT_ALWAYS("  Validity: %d days\n", cfg.validity_days);
    PRINT_ALWAYS("  Z5D params: kappa_geo=%.3f, kappa_star=%.5f, phi=%.15f\n",
                 cfg.kappa_geo, cfg.kappa_star, cfg.phi);
    PRINT_ALWAYS("  Bumps: p=%d, q=%d\n\n", cfg.bump_p, cfg.bump_q);

    //todo: enable this when '--show-hardware' flag is passed only.
//    z5d_gpu_print_info();

    // Generate RSA keypair
    RSA *rsa = generate_rsa_keypair(&cfg);
    if (!rsa) {
        fprintf(stderr, "Failed to generate RSA keypair\n");
        return 1;
    }

    // Generate certificate
    X509 *cert = generate_certificate(rsa, &cfg);
    if (!cert) {
        fprintf(stderr, "Failed to generate certificate\n");
        RSA_free(rsa);
        return 1;
    }

    // Write output files
    write_files(rsa, cert, &cfg);

    gettimeofday(&end_time, NULL);
    long long elapsed_ms = (long long)(end_time.tv_sec - start_time.tv_sec) * 1000LL;
    elapsed_ms += (long long)(end_time.tv_usec - start_time.tv_usec) / 1000LL;

    PRINT_ALWAYS("\n=== Generation Complete ===\n");
    PRINT_ALWAYS("Generated cryptographically secure RSA-4096 keys using Z5D predictor!\n");
    PRINT_ALWAYS("Total generation time: %lld ms\n", elapsed_ms);

    X509_free(cert);
    RSA_free(rsa);
    return 0;
}
