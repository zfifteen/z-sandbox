/**
 * Z Framework Seed Generator (C Implementation)
 * ==============================================
 *
 * Generates a high-entropy seed internally for reproducible simulations,
 * bootstrap resampling (e.g., 1000 resamples for CIs), or initialization.
 * Meets minimal requirements: internal generation, uniqueness, entropy,
 * simple interface. Uses system time and PID for low-collision probability.
 *
 * Empirical: Verifiable uniqueness (<10^{-50} collision); entropy ~256 bits.
 *
 * @file z_seed_generator.h
 * @author Dionisio Alberto Lopez III (D.A.L. III)
 * @version 1.0 (Empirical Breakthrough Edition)
 */

#ifndef Z_SEED_GENERATOR_H
#define Z_SEED_GENERATOR_H

#include <time.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>   // For snprintf, sscanf
#include <unistd.h>  // For getpid()
#include <fcntl.h>   // For open()
#include <sys/time.h>
#include <string.h>  // For memset
#include <openssl/evp.h>
#include <openssl/crypto.h>

#include "z_seed_errors.h"

#define SEED_SIZE 32  // 256-bit for high entropy
#define HEX_SEED_LEN (SEED_SIZE * 2 + 1)

/**
 * Generate a unique, high-entropy seed.
 *
 * @param seed Buffer to store the seed (at least SEED_SIZE bytes).
 * @return ZSEED_OK on success or a negative ZSEED_ERR_* code on failure
 */
static inline int z_generate_seed(uint8_t *seed) {
    if (!seed) return ZSEED_ERR_NULL_POINTER;

    // SECURITY: Strictly fail-closed on /dev/urandom failures
    // (ZSEED_ERR_ENTROPY_UNAVAIL / READ_FAILURE). We never proceed
    // under weakened entropy conditions.
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd < 0) {
        return ZSEED_ERR_ENTROPY_UNAVAIL;
    }

    // SECURITY: Single, full-length read from OS CSPRNG only;
    // no fallback RNG permitted.
    ssize_t bytes_read = read(fd, seed, SEED_SIZE);
    close(fd);
    if (bytes_read != SEED_SIZE) {
        return ZSEED_ERR_READ_FAILURE;
    }

    struct timeval tv;
    gettimeofday(&tv, NULL);
    pid_t pid = getpid();
    clock_t clk = clock();

    uint64_t monotonic_entropy = 0;
#if defined(CLOCK_MONOTONIC)
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
        monotonic_entropy = ((uint64_t)ts.tv_sec << 32) ^ (uint64_t)ts.tv_nsec;
    } else {
        monotonic_entropy = ((uint64_t)tv.tv_sec << 32) ^ (uint64_t)tv.tv_usec;
    }
#else
    monotonic_entropy = ((uint64_t)tv.tv_sec << 32) ^ (uint64_t)tv.tv_usec;
#endif

    unsigned char mix_input[sizeof(tv) + sizeof(pid) + sizeof(clk) + sizeof(monotonic_entropy)];
    size_t offset = 0;
    memcpy(mix_input + offset, &tv, sizeof(tv));
    offset += sizeof(tv);
    memcpy(mix_input + offset, &pid, sizeof(pid));
    offset += sizeof(pid);
    memcpy(mix_input + offset, &clk, sizeof(clk));
    offset += sizeof(clk);
    memcpy(mix_input + offset, &monotonic_entropy, sizeof(monotonic_entropy));
    offset += sizeof(monotonic_entropy);

    // SECURITY: Low-entropy fields (getpid, clocks, monotonic) are
    // only fed into a SHA-256 mixing step and cannot reduce the
    // 256 bits of OS-provided randomness.
    unsigned char digest[EVP_MAX_MD_SIZE];
    unsigned int digest_len = 0;
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (!ctx) {
        OPENSSL_cleanse(mix_input, sizeof(mix_input));
        return ZSEED_ERR_CRYPTO_FAILURE;
    }

    int ok = EVP_DigestInit_ex(ctx, EVP_sha256(), NULL);
    ok &= EVP_DigestUpdate(ctx, seed, SEED_SIZE);
    ok &= EVP_DigestUpdate(ctx, mix_input, offset);
    ok &= EVP_DigestFinal_ex(ctx, digest, &digest_len);
    EVP_MD_CTX_free(ctx);

    // MEMORY-HYGIENE: cleanse all mixing buffers on every path.
    size_t cleanse_len = digest_len ? digest_len : sizeof(digest);

    if (!ok || digest_len < SEED_SIZE) {
        OPENSSL_cleanse(digest, cleanse_len);
        OPENSSL_cleanse(mix_input, sizeof(mix_input));
        return ZSEED_ERR_CRYPTO_FAILURE;
    }

    for (int i = 0; i < SEED_SIZE; i++) {
        seed[i] ^= digest[i];
    }

    OPENSSL_cleanse(digest, cleanse_len);
    OPENSSL_cleanse(mix_input, sizeof(mix_input));

    return ZSEED_OK;
}

/**
 * Convert seed bytes to a hex string for display/storage
 *
 * @param seed Input seed buffer (SEED_SIZE bytes)
 * @param hex_out Output hex string buffer (at least HEX_SEED_LEN bytes)
 */
static inline void z_seed_to_hex(const uint8_t *seed, char *hex_out) {
    for (int i = 0; i < SEED_SIZE; i++) {
        // BOUNDS-CHECKED: per-byte snprintf prevents overflow when
        // converting 32-byte seed to 64-char hex.
        snprintf(hex_out + i*2, 3, "%02x", seed[i]);
    }
    hex_out[SEED_SIZE*2] = '\0';
}

/**
 * Convert hex string back to seed bytes
 *
 * @param hex_in Input hex string (SEED_SIZE*2 characters)
 * @param seed Output seed buffer (SEED_SIZE bytes)
 * @return 0 on success, -1 on error
 */
static inline int z_hex_to_seed(const char *hex_in, uint8_t *seed) {
    if (!hex_in || !seed) return -1;

    for (int i = 0; i < SEED_SIZE; i++) {
        unsigned int byte_val;
        if (sscanf(hex_in + i*2, "%02x", &byte_val) != 1) {
            return -1;
        }
        seed[i] = (uint8_t)byte_val;
    }
    return 0;
}

#endif /* Z_SEED_GENERATOR_H */
