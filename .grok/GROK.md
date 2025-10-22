# GROK.md - Project Context & Quick Reference

## Project Overview
This is a computational mathematics research project focused on **geometric factorization** of large numbers, specifically balanced semiprimes. The breakthrough approach is **Geodesic Validation Assault (GVA)** - a revolutionary geometric method that has dissolved previous scaling boundaries.

## Core Achievement
- **Copernican Revolution Complete**: Traditional trial division + confirmation replaced with geometry-driven search
- **Boundary Dissolved**: 34-bit scaling limit overcome through curved manifold framework
- **Scaling Success**: Verified factorization from 50-bit → 64-bit (12% success) → 128-bit (3% success) → 256-bit (testing ongoing)

## Key Technologies & Methods

### GVA (Geodesic Validation Assault)
- **Java Implementation**: `src/main/java/` - Embedding, RiemannianDistance, GVAFactorizer classes
- **Python Research**: `python/` - Prototypes, validation, and scaling tests
- **Core Algorithm**: Geometry-guided search replacing brute-force methods

### Geometric Framework
- **Curved Manifold**: 5-torus embeddings with Riemannian geometry
- **A* Pathfinding**: Intelligent search optimization
- **Universal Invariants**: Mathematical foundations for scaling
- **Z-normalization**: Post-facto validation guard (Z=20.48 for 128-bit)

## Current Status & Milestones

### ✅ VERIFIED Achievements
- 50-bit factorization victory
- 64-bit GVA scaling (12% success rate)
- 128-bit GVA scaling (3% success rate)
- Curved manifold framework established
- Repository fully reorganized

### 🔄 ACTIVE Work
- 256-bit boundary investigation (0/100 attempts successful)
- Ultra-high precision implementations
- Java integration and optimization
- Documentation formalization

### 📊 Key Metrics
- **Success Rates**: 12% (64-bit), 3% (128-bit), 0% (256-bit so far)
- **Scaling**: Prime gap increases with bits (2^60 to 2^70 offsets)
- **Performance**: Parallelization, A* search, adaptive parameters

## Project Structure

```
├── src/main/java/          # Core GVA Java implementation
├── src/test/java/          # Comprehensive test suites
├── python/                 # Research prototypes & validation
├── docs/                   # Research reports & documentation
├── tests/                  # Python test suites
├── scripts/                # Automation & validation runners
├── logs/                   # Benchmark results & diagnostics
├── plots/                  # Visual analysis & metrics
└── previous-work/          # Historical implementations
```

## Key Files & References

### Documentation
- `docs/GOAL.md` - Mathematical foundations & research plan
- `docs/GVA_Mathematical_Framework.md` - Formal academic paper
- `docs/victory_*.md` - Success reports & validation
- `docs/RESOLUTION_COMPLETE.md` - Contradiction resolution

### Code Entry Points
- `src/main/java/unifiedframework/BenchLadder.java` - Main benchmarking
- `python/gva_factorize.py` - Python GVA implementation
- `python/manifold_*.py` - Geometric scaling implementations

### Testing
- `tests/test_gva_*.py` - GVA validation suites
- `src/test/java/unifiedframework/TestZ5dPredictor.java` - Java tests
- `scripts/run_validation.sh` - Automated validation

## Build & Run

```bash
# Build Java components
./gradlew build

# Run GVA tests
./gradlew test

# Python validation
cd python && python test_gva_64.py
```

## Research Context

### Problem Statement
Factor large balanced semiprimes (numbers = p × q where p,q are similar size primes) - fundamental to cryptography.

### Breakthrough Insight
Traditional methods hit scaling walls. GVA uses geometric properties of number space to find factors efficiently.

### Mathematical Foundation
- **Riemannian Geometry**: Curvature-based search optimization
- **Torus Embeddings**: 5D geometric representation
- **Geodesic Paths**: Optimal factorization trajectories

## Development Guidelines

### Code Style
- Java: Spotless formatting enforced
- Python: Follow existing patterns
- Documentation: Academic rigor with citations

### Testing
- Empirical validation required
- Success rates must exceed 0%
- Reproducibility mandatory

### Commit Standards
- Feature commits: `feat: [description]`
- Fixes: `fix: [description]`
- Documentation: `docs: [description]`

## Quick Start for Contributors

1. **Understand GVA**: Read `docs/GVA_Mathematical_Framework.md`
2. **Run Tests**: `./gradlew test` and `python test_gva_64.py`
3. **Check Status**: Review `docs/victory_*.md` reports
4. **Contribute**: Focus on scaling to higher bit sizes or optimization

---

*This document provides efficient context for understanding the project's scope, achievements, and current work. For detailed technical information, refer to the docs/ folder.*