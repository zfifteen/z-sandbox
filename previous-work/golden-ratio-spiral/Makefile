# Golden Ratio Index Scaling and Spiral Search - Makefile
# ========================================================
#
# Build system for Golden Ratio Index Scaling and Spiral Search implementation.
# Inherits dependencies from parent Makefile and builds shared libraries.
# Uses parent's sophisticated dependency detection for cross-platform compatibility.
#
# Usage:
#   make          - Build golden spiral executable
#   make test     - Build and run demonstration
#   make clean    - Clean build artifacts
#   make help     - Show this help
#
# @file Makefile
# @version 1.0

# Ensure default goal is 'all' regardless of rule order
.DEFAULT_GOAL := all

# Directories
SRC_DIR := .
PARENT_DIR := ..
BUILD_DIR := build
BIN_DIR := bin

# Platform detection
UNAME_S := $(shell uname -s 2>/dev/null || echo Windows)

# Inherit sophisticated dependency detection from parent Makefile
# This ensures Apple M1/macOS compatibility and proper Homebrew support

# GMP/MPFR configuration (inherited pattern from parent)
PKG_CONFIG_EXISTS := $(shell command -v pkg-config >/dev/null 2>&1 && echo 1 || echo 0)
GMP_AVAILABLE := $(shell if [ "$(PKG_CONFIG_EXISTS)" = "1" ]; then pkg-config --exists gmp && echo 1 || echo 0; \
    else \
        (test -f /usr/include/gmp.h -o -f /usr/local/include/gmp.h -o -f /opt/homebrew/include/gmp.h) && echo 1 || echo 0; \
    fi)
MPFR_AVAILABLE := $(shell if [ "$(PKG_CONFIG_EXISTS)" = "1" ]; then pkg-config --exists mpfr && echo 1 || echo 0; \
    else \
        (test -f /usr/include/mpfr.h -o -f /usr/local/include/mpfr.h -o -f /opt/homebrew/include/mpfr.h) && echo 1 || echo 0; \
    fi)

ifeq ($(GMP_AVAILABLE)$(MPFR_AVAILABLE),11)
    ifeq ($(PKG_CONFIG_EXISTS),1)
        GMP_INCLUDE ?= $(shell pkg-config --cflags gmp 2>/dev/null || echo -I/opt/homebrew/include)
        GMP_LIB ?= $(shell pkg-config --libs gmp 2>/dev/null || echo -L/opt/homebrew/lib )
        MPFR_INCLUDE ?= $(shell pkg-config --cflags mpfr 2>/dev/null || echo -I/opt/homebrew/include)
        MPFR_LIB ?= $(shell pkg-config --libs mpfr 2>/dev/null || echo -L/opt/homebrew/lib -lmpfr)
    else
        GMP_INCLUDE ?= $(shell \
            if test -f /usr/include/gmp.h; then echo -I/usr/include; \
            elif test -f /usr/local/include/gmp.h; then echo -I/usr/local/include; \
            elif test -f /opt/homebrew/include/gmp.h; then echo -I/opt/homebrew/include; \
            else echo ""; fi)
        GMP_LIB ?= $(shell \
            if test -f /usr/lib/libgmp.a -o -f /usr/lib/libgmp.so; then echo -L/usr/lib ; \
            elif test -f /usr/local/lib/libgmp.a -o -f /usr/local/lib/libgmp.so; then echo -L/usr/local/lib ; \
            elif test -f /opt/homebrew/lib/libgmp.a -o -f /opt/homebrew/lib/libgmp.dylib; then echo -L/opt/homebrew/lib ; \
            else echo ""; fi)
        MPFR_INCLUDE ?= $(shell \
            if test -f /usr/include/mpfr.h; then echo -I/usr/include; \
            elif test -f /usr/local/include/mpfr.h; then echo -I/usr/local/include; \
            elif test -f /opt/homebrew/include/mpfr.h; then echo -I/opt/homebrew/include; \
            else echo ""; fi)
        MPFR_LIB ?= $(shell \
            if test -f /usr/lib/libmpfr.a -o -f /usr/lib/libmpfr.so; then echo -L/usr/lib -lmpfr; \
            elif test -f /usr/local/lib/libmpfr.a -o -f /usr/local/lib/libmpfr.so; then echo -L/usr/local/lib -lmpfr; \
            elif test -f /opt/homebrew/lib/libmpfr.a -o -f /opt/homebrew/lib/libmpfr.dylib; then echo -L/opt/homebrew/lib -lmpfr; \
            else echo "-lmpfr"; fi)
    endif
    MPFR_LDFLAGS := $(GMP_LIB) $(MPFR_LIB)
else
    GMP_INCLUDE := 
    GMP_LIB := 
    MPFR_INCLUDE := 
    MPFR_LIB := 
    MPFR_LDFLAGS := 
    $(error "MPFR/GMP not found - required for Golden Ratio Spiral implementation")
endif

# OpenMP configuration for macOS (inherited pattern from parent)
ifeq ($(UNAME_S),Darwin)
    # Use Homebrew's keg-only paths for libomp on macOS
    OPENMP_LIB_DIR := /opt/homebrew/opt/libomp/lib
    OPENMP_INCLUDE_DIR := /opt/homebrew/opt/libomp/include
    OPENMP_LIB := -lomp

    # Test for libomp directory existence to determine availability
    ifeq ($(wildcard $(OPENMP_LIB_DIR)),)
        OMP_AVAILABLE := 0
    else
        OMP_AVAILABLE := 1
    endif

    ifeq ($(OMP_AVAILABLE),1)
        # Apple Clang requires -Xpreprocessor for OpenMP directives
        OPENMP_CFLAGS := -Xpreprocessor -fopenmp -I$(OPENMP_INCLUDE_DIR) -Wno-pedantic
        OPENMP_LDFLAGS := -L$(OPENMP_LIB_DIR) $(OPENMP_LIB)
        $(info "OpenMP detected via Homebrew for macOS.")
    else
        OPENMP_CFLAGS :=
        OPENMP_LDFLAGS :=
        $(warning "OpenMP (libomp) not found in Homebrew prefix. Build will be single-threaded.")
    endif
else
    # Configuration for Linux and other platforms
    OPENMP_CFLAGS := -fopenmp
    OPENMP_LDFLAGS := -fopenmp
    OMP_AVAILABLE := 1
    $(info "OpenMP configuration for non-macOS platform.")
endif

# Compiler and flags (using same defaults as parent)
CC := clang  # Explicitly use Clang for macOS compatibility
CFLAGS := -std=c99 -Wall -Wextra -O3 -g $(GMP_INCLUDE) $(MPFR_INCLUDE) $(OPENMP_CFLAGS)
LDFLAGS := -lm $(MPFR_LDFLAGS) $(OPENMP_LDFLAGS)

# Add OpenMP definition if available
ifneq ($(OPENMP_CFLAGS),)
    CFLAGS += -DWITH_OPENMP
endif

# Platform-specific configuration
UNAME_M := $(shell uname -m 2>/dev/null || echo Unknown)

ifeq ($(UNAME_S),Darwin)
    # macOS optimizations - only apply ARM flags on ARM systems
    ifeq ($(UNAME_M),arm64)
        CFLAGS += -march=armv8.5-a -mcpu=apple-m1
    endif
else ifeq ($(UNAME_S),Linux)
    # Linux optimizations
    CFLAGS += -fPIC
    # Add additional optimization flags for Linux
    CFLAGS += -march=native -mtune=native
endif

# Target executable
TARGET := $(BIN_DIR)/golden_spiral_demo
MAIN_SOURCE := $(SRC_DIR)/golden_spiral_demo.c

# Golden spiral library
GOLDEN_LIB_SOURCE := $(SRC_DIR)/golden_spiral.c
GOLDEN_LIB_OBJECT := $(BUILD_DIR)/golden_spiral.o

GOLDEN_HEADERS := $(SRC_DIR)/golden_spiral.h

# Object files
MAIN_OBJECT := $(BUILD_DIR)/golden_spiral_demo.o

# Create directories
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

# Default target
all: $(TARGET)

# Build the golden spiral library object
$(GOLDEN_LIB_OBJECT): $(GOLDEN_LIB_SOURCE) $(GOLDEN_HEADERS) | $(BUILD_DIR)
	@echo "🔧 Compiling golden spiral library..."
	$(CC) $(CFLAGS) -c $(GOLDEN_LIB_SOURCE) -o $(GOLDEN_LIB_OBJECT)

# Build the main demo object
$(MAIN_OBJECT): $(MAIN_SOURCE) $(GOLDEN_HEADERS) | $(BUILD_DIR)
	@echo "🔧 Compiling main demo..."
	$(CC) $(CFLAGS) -c $(MAIN_SOURCE) -o $(MAIN_OBJECT)

# Build the main executable
$(TARGET): $(GOLDEN_LIB_OBJECT) $(MAIN_OBJECT) | $(BIN_DIR)
	@echo "🔗 Linking golden spiral demo executable..."
	$(CC) $(GOLDEN_LIB_OBJECT) $(MAIN_OBJECT) $(LDFLAGS) -o $(TARGET)
	@echo "✅ Built golden spiral demo: $(TARGET)"

# Test target (build and run demo)
test: $(TARGET)
	@echo "🧪 Running golden spiral demonstration..."
	@echo ""
	./$(TARGET)

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf $(BUILD_DIR) $(BIN_DIR)
	@echo "✅ Clean completed"

# Show build information
info:
	@echo "🔍 Golden Ratio Spiral Build Configuration:"
	@echo "  Platform: $(UNAME_S) $(UNAME_M)"
	@echo "  CC: $(CC)"
	@echo "  CFLAGS: $(CFLAGS)"
	@echo "  LDFLAGS: $(LDFLAGS)"
	@echo "  GMP Include: $(GMP_INCLUDE)"
	@echo "  MPFR Include: $(MPFR_INCLUDE)"
	@echo "  MPFR/GMP Available: $(GMP_AVAILABLE)/$(MPFR_AVAILABLE)"
	@echo "  OpenMP: $(if $(OPENMP_CFLAGS),Enabled ($(OPENMP_CFLAGS)),Disabled)"
	@echo "  Target: $(TARGET)"
	@echo "  Dependencies: Inherited from parent Makefile"

# Help target
help:
	@echo "Golden Ratio Index Scaling and Spiral Search - Build System"
	@echo "=========================================================="
	@echo ""
	@echo "Available targets:"
	@echo "  all        - Build golden spiral demo executable (default)"
	@echo "  test       - Build and run demonstration"
	@echo "  clean      - Clean build artifacts"
	@echo "  info       - Show build configuration"
	@echo "  help       - Show this help"
	@echo ""
	@echo "Build options:"
	@echo "  make debug  - Build with debug flags"
	@echo ""
	@echo "Dependencies:"
	@echo "  - MPFR library (libmpfr-dev)"
	@echo "  - GMP library (libgmp-dev)"
	@echo "  - OpenMP (optional, for parallel processing)"
	@echo ""
	@echo "Example usage:"
	@echo "  make test   # Build and run golden spiral demo"

# Debug build option
debug: CFLAGS += -DDEBUG -g3 -O0
debug: $(TARGET)

# Check if parent shared library exists and try to build it
shared:
	@echo "🔍 Checking for parent shared library..."
	@if [ -f "$(PARENT_DIR)/Makefile" ]; then \
		echo "📦 Building parent shared library..."; \
		cd $(PARENT_DIR) && $(MAKE) shared 2>/dev/null || echo "⚠️  Parent shared library build not available"; \
	else \
		echo "⚠️  Parent Makefile not found"; \
	fi

# Phony targets
.PHONY: all test clean info help debug shared

# Dependencies tracking (optional)
-include $(BUILD_DIR)/*.d