# z-sandbox

**Purpose:** scratchpad for Z-Framework experiments (prime geometry, φ-mappings, Z-triangles, RSA grid filters, imaging demos). Expect messy prototypes, fast iteration, and structured logs.

> ⚠️ Research sandbox — not production-secure. Expect breaking changes.

## Structure
```
/src/                    # Java source (e.g., Domain.java, ZFrameworkValidation.java)
/scripts/                # Python scripts (analyze_domain.py, hologram.py, proof.py)
/data/                   # Datasets (zeta_1000.txt, etc.)
/plots/                 # Generated visualizations
/build/                 # Gradle build artifacts
.github/                # CI/CD workflows
```

## Quick Start
### Java (Z-Framework Validation)
```bash
./gradlew build
java -cp build/classes/java/main unifiedframework.ZFrameworkValidation
```
Validates θ' invariants for primes vs. zeta zeros.

### Python (Analysis & Visualization)
```bash
python analyze_domain.py  # Log magnitude plots
python hologram.py       # 3D helical embeddings
python proof.py          # Symbolic proofs
```

## Experiments
- **Prime Geometry**: θ' mappings, curvature κ(n), fractal patterns.
- **Zeta Zero Correlations**: Helical embeddings, φ-geodesics.
- **RSA Filters**: Grid-based cryptographic experiments.
- **Imaging Demos**: Visualizing Z-triangles.

## Dependencies
- Java 17+ (Gradle for builds)
- Python 3.8+ (matplotlib, sympy, numpy)

## Logs & Changes
See `CHANGELOG.md` for experiment notes.

## Contributing
Messy PRs welcome—focus on Z-Framework insights. Assign zfifteen for reviews.

## License
Research sandbox—see unified-framework for licensing.
