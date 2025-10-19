# Proof-of-Concept Priorities — Seed Generator

Scope: tighten correctness, clarity, and hygiene for the seed generator without production infra (no Kubernetes/HSM/audit pipelines yet). Deliver crisp error semantics, buffer safety, minimal secure wiping, a tiny test harness, and README pointers.

---

## 1) Clear Error Semantics & Exit Codes

Add a dedicated error code header and wire return/exit mapping.

Files:
- `z_seed_errors.h` (new)
- `z_seed_generator.h` (update to return codes)
- `z5d_key_gen.c` or calling CLI (map codes to exit codes)

Error codes (header `z_seed_errors.h`):

```c
#define ZSEED_OK                    0
#define ZSEED_ERR_NULL_POINTER     -1
#define ZSEED_ERR_ENTROPY_UNAVAIL  -2
#define ZSEED_ERR_READ_FAILURE     -3
#define ZSEED_ERR_CRYPTO_FAILURE   -4
```

z_generate_seed changes:
- Return `ZSEED_ERR_NULL_POINTER` if `seed == NULL`.
- Return `ZSEED_ERR_ENTROPY_UNAVAIL` when `/dev/urandom` cannot open.
- Return `ZSEED_ERR_READ_FAILURE` if bytes read != `SEED_SIZE`.
- Return `ZSEED_ERR_CRYPTO_FAILURE` if any OpenSSL step fails or digest too short.
- Return `ZSEED_OK` on success.

Caller mapping (example):

```c
int rc = z_generate_seed(buf);
if (rc != ZSEED_OK) {
    switch (rc) {
        case ZSEED_ERR_ENTROPY_UNAVAIL:
            fprintf(stderr, "ERROR: entropy source unavailable\n");
            return EXIT_FAILURE + 2; // 2
        case ZSEED_ERR_READ_FAILURE:
            fprintf(stderr, "ERROR: entropy read failure\n");
            return EXIT_FAILURE + 3; // 3
        case ZSEED_ERR_CRYPTO_FAILURE:
            fprintf(stderr, "ERROR: cryptographic mixing failure\n");
            return EXIT_FAILURE + 4; // 4
        case ZSEED_ERR_NULL_POINTER:
        default:
            fprintf(stderr, "ERROR: internal error\n");
            return EXIT_FAILURE + 1; // 1
    }
}
```

Acceptance criteria:
- z_generate_seed consistently returns the above codes.
- CLI or calling site sets distinct exit codes (0 success; 1 generic; 2 entropy unavailable; 3 read failure; 4 crypto failure).
- README updated with the mapping.

---

## 2) Buffer-Safe Hex Conversion

Replace `sprintf` with `snprintf` and expose a constant for required hex buffer length.

Definitions (in `z_seed_generator.h` next to `SEED_SIZE`):

```c
#define SEED_SIZE      32
#define HEX_SEED_LEN  (SEED_SIZE * 2 + 1)
```

Implementation:

```c
static inline void z_seed_to_hex(const uint8_t *seed, char *hex_out) {
    for (int i = 0; i < SEED_SIZE; i++) {
        snprintf(hex_out + i*2, 3, "%02x", seed[i]);
    }
    hex_out[SEED_SIZE*2] = '\0';
}
```

Documentation:
- README: “Allocate at least `HEX_SEED_LEN` bytes for hex output (65 for 32-byte seeds).”

Acceptance criteria:
- No unbounded `sprintf` in hex conversion.
- `HEX_SEED_LEN` is defined and used consistently.

---

## 3) Minimal Secure-Wipe

Demonstrate hygiene by clearing sensitive intermediates before returning.

Add (near return path in `z_seed_generator.h`):

```c
OPENSSL_cleanse(digest, digest_len);
OPENSSL_cleanse(mix_input, sizeof(mix_input));
```

Notes:
- Include `<openssl/crypto.h>` if not already transitively included.
- If portability is a concern later, optionally gate a fallback `secure_bzero` using `volatile`.

Acceptance criteria:
- Digest buffer and mixing buffer are wiped on all paths after use.

---

## 4) Simple Unit-Test Harness

Add a tiny test to verify success, uniqueness, and hex formatting.

Files:
- `test_seed.c` (new)

Content:

```c
#include "z_seed_generator.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>

int main(void) {
    uint8_t seed1[SEED_SIZE], seed2[SEED_SIZE];
    char hex1[HEX_SEED_LEN], hex2[HEX_SEED_LEN];

    assert(z_generate_seed(seed1) == ZSEED_OK);
    assert(z_generate_seed(seed2) == ZSEED_OK);
    assert(memcmp(seed1, seed2, SEED_SIZE) != 0);

    z_seed_to_hex(seed1, hex1);
    z_seed_to_hex(seed2, hex2);
    assert(strlen(hex1) == SEED_SIZE * 2);
    assert(strcmp(hex1, hex2) != 0);

    printf("POC seed-gen tests passed\n");
    return 0;
}
```

Makefile target:

```make
test-seed:
	cc -Wall -Wextra -O2 -o test_seed test_seed.c -lcrypto
	./test_seed
```

Notes:
- The seed utilities are header-only `static inline`; compiling `test_seed.c` is sufficient.

Acceptance criteria:
- `make test-seed` builds and runs, printing “POC seed-gen tests passed”.

---

## 5) Concise README Addendum

Add in README:
- Exit Codes: 0 success; 1 generic error; 2 entropy unavailable; 3 read failure; 4 crypto failure.
- Buffer Sizes: `HEX_SEED_LEN = 65` for 32-byte seed.
- Test Instructions: `make test-seed`.

Acceptance criteria:
- README includes the above, matching implementation.

---

## Next POC Milestones

1) Entropy Policy Guard
- Clarify and enforce that only system entropy is accepted; user-provided seeds should be rejected with actionable errors.
- Validation: CLI rejects `--seed` attempts; regression test ensures future changes cannot reintroduce deterministic pathways.

2) Integration Example
- Show piping generated hex into RSA generator POC.
- Validation: demo script produces a valid keypair; note timing and seed provenance.

3) Performance Logging
- Time seed generation path; print/log duration for comparison within the pipeline.
- Validation: wall-clock timings emitted; seed-gen is negligible relative to key generation.

---

## Implementation Checklist

- [x] Add `z_seed_errors.h` with error codes.
- [x] Update `z_seed_generator.h` to return specific codes.
- [x] Replace `sprintf` with `snprintf` and define `HEX_SEED_LEN`.
- [x] Add `OPENSSL_cleanse` for `digest` and `mix_input`.
- [x] Create `test_seed.c` and `make test-seed` target.
- [x] Update README with exit codes, buffer sizes, and test command.
- [ ] Optional: add regression harness verifying CLI rejects `--seed` attempts.
- [ ] Optional: add integration example and simple perf logging.

---

## Notes / Alignment

- Style: maintain 4-space indentation, K&R braces; keep headers minimal.
- Build: ensure `make test` remains green; add `test-seed` as a local harness.
- Security: no secrets or large binaries; tests are self-contained and fast.
