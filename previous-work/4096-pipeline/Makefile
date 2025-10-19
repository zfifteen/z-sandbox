# Makefile for z5d_secure_key_gen — Z5D RSA-4096 Secure Key Generator
#
# **Z5D SECURE RSA KEY GENERATOR** - Creates cryptographically secure RSA keys
# using Z5D predictor with high-entropy seed generation.

CC = clang
CFLAGS = -Wall -Wextra -Wno-deprecated-declarations -O3 -std=c99 -mcpu=apple-m1 -ffast-math -fstrict-aliasing -funroll-loops -DZ5D_USE_AMX=1
OPENSSL_PREFIX = $(shell brew --prefix openssl 2>/dev/null || echo "/usr/local/opt/openssl")
GMP_PREFIX = $(shell brew --prefix gmp 2>/dev/null || echo "/usr/local/opt/gmp")
MPFR_PREFIX = $(shell brew --prefix mpfr 2>/dev/null || echo "/usr/local/opt/mpfr")
LIBOMP_PREFIX = $(shell brew --prefix libomp 2>/dev/null || echo "/opt/homebrew/opt/libomp")
INCLUDES = -I../ $(shell pkg-config --cflags openssl) -I$(GMP_PREFIX)/include -I$(MPFR_PREFIX)/include
LDFLAGS = -L$(OPENSSL_PREFIX)/lib -L$(GMP_PREFIX)/lib -L$(MPFR_PREFIX)/lib
LIBS = -lmpfr -lgmp $(shell pkg-config --libs openssl) -lm

LIBOMP_LIB_PATH := $(LIBOMP_PREFIX)/lib
LIBOMP_INCLUDE_PATH := $(LIBOMP_PREFIX)/include

ifneq ("$(wildcard $(LIBOMP_LIB_PATH))","")
OPENMP_CFLAGS := -Xpreprocessor -fopenmp -I$(LIBOMP_INCLUDE_PATH)
OPENMP_LDFLAGS := -L$(LIBOMP_LIB_PATH) -lomp
CFLAGS += $(OPENMP_CFLAGS)
LDFLAGS += $(OPENMP_LDFLAGS)
OPENMP_ENABLED := 1
else
$(warning "libomp not found via Homebrew — building without OpenMP support")
OPENMP_ENABLED := 0
endif

# Source files
MAIN_SRC = z5d_key_gen.c
Z5D_SRC = ../z5d_predictor.c
OBJC_SRC = gpu_info.m
OBJC_OBJ = $(OBJC_SRC:.m=.o)
SOURCES = $(MAIN_SRC) $(Z5D_SRC)

GRID_TEST_SRC = z5d_grid_test.c
GRID_HELPER_SRC = z5d_factorization_shortcut.c
GRID_TEST_OBJS = z5d_grid_test.o z5d_factorization_shortcut.o
GRID_TEST_TARGET = z5d_grid_test

# Target binaries
TARGET = z5d_secure_key_gen
LEGACY_TARGET = insecure_example_key_gen

# Default target
all: $(TARGET) $(GRID_TEST_TARGET)

# Build the main target
$(TARGET): $(SOURCES) $(OBJC_OBJ)
	$(CC) $(CFLAGS) $(INCLUDES) $(LDFLAGS) -o $@ $^ $(LIBS) -framework Metal -framework Foundation

$(GRID_TEST_TARGET): $(GRID_TEST_OBJS)
	$(CC) $(CFLAGS) $(INCLUDES) $(LDFLAGS) -o $@ $^ $(LIBS)

z5d_grid_test.o: z5d_grid_test.c z5d_factorization_shortcut.h
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

z5d_factorization_shortcut.o: z5d_factorization_shortcut.c z5d_factorization_shortcut.h
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

$(OBJC_OBJ): $(OBJC_SRC) gpu_info.h
	$(CC) -fobjc-arc -ObjC $(INCLUDES) -c $< -o $@

# Build legacy target for compatibility
$(LEGACY_TARGET): $(SOURCES)
	$(CC) $(CFLAGS) $(INCLUDES) $(LDFLAGS) -o $@ $^ $(LIBS)

# Test with secure entropy
test: $(TARGET)
	@echo "=== Testing Z5D Secure Key Generator ==="
	./$(TARGET)
	@echo ""
	@echo "=== Generated files ==="
	@ls -la generated/z5d_key_gen-*.key generated/z5d_key_gen-*.crt 2>/dev/null || echo "No output files found"

# Unit test harness for seed generation
test-seed:
	$(CC) $(CFLAGS) $(INCLUDES) test_seed.c -o test_seed $(LDFLAGS) -lcrypto
	./test_seed
	rm -f test_seed

# Demo seed generation
demo-seed:
	@echo "=== Z5D Seed Generator Demo ==="
	@echo '#include "z_seed_generator.h"' > seed_demo.c
	@echo 'int main() { uint8_t seed[SEED_SIZE]; char hex[HEX_SEED_LEN]; if(z_generate_seed(seed)==ZSEED_OK) { z_seed_to_hex(seed,hex); printf("Generated seed: %s\\n", hex); } return 0; }' >> seed_demo.c
	@$(CC) $(CFLAGS) $(INCLUDES) -o seed_demo seed_demo.c $(LDFLAGS) $(LIBS)
	@./seed_demo
	@rm -f seed_demo seed_demo.c

# Clean build artifacts and generated keys
clean:
	rm -f $(TARGET) $(LEGACY_TARGET) $(GRID_TEST_TARGET) seed_demo test_seed
	rm -f $(GRID_TEST_OBJS)
	rm -f z5d_key_gen-*.key z5d_key_gen-*.crt
	rm -f insecure_example_key_gen-*.key insecure_example_key_gen-*.crt
	rm -f $(OBJC_OBJ)

# Show help
help:
	@echo "Available targets:"
	@echo "  all          Build the z5d_secure_key_gen tool"
	@echo "  test         Build and test with secure entropy"
	@echo "  test-seed    Run seed generator unit test harness"
	@echo "  demo-seed    Demo the seed generator"
	@echo "  clean        Remove build artifacts and generated keys"
	@echo "  help         Show this help"
	@echo ""
	@echo "Usage: ./z5d_secure_key_gen [OPTIONS]"
	@echo "Run './z5d_secure_key_gen --help' for option details"

.PHONY: all test test-seed demo-seed clean help
