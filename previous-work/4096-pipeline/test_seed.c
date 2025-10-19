#include "z_seed_generator.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    uint8_t seed1[SEED_SIZE];
    uint8_t seed2[SEED_SIZE];
    char hex1[HEX_SEED_LEN];
    char hex2[HEX_SEED_LEN];

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
