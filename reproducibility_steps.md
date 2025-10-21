# Reproducibility Steps for Benchmark Results

## Objective
Reproduce the benchmark results for semiprime factorization using geometric methods in the z-sandbox repository.

## Environment Setup
- **Commit Hash**: Use the latest commit or specify: `d619e5f` (from `git log --oneline -1`)
- **Java Version**: OpenJDK 17.0.x (verify with `java -version`)
- **Operating System**: macOS (or specify your OS)
- **Heap Size**: Default (or set `-Xmx4g` if needed)

## Steps to Reproduce
1. **Navigate to Repository Root**:
   ```
   cd /path/to/z-sandbox
   ```

2. **Compile the Benchmark Tool**:
   ```
   javac src/main/java/tools/BenchLadder.java
   ```

3. **Run the Benchmark**:
   ```
   java -cp src/main/java tools.BenchLadder --ladder --digits 200
   ```
   - `--ladder`: Enables ladder benchmark mode, which generates `ladder_results.csv`
   - `--digits`: Specifies the number of digits for semiprimes (e.g., 200)

4. **Verify Output**:
   - Check that `ladder_results.csv` is created in the working directory.
   - Expected first few lines:
     ```
     id,digits,builder,cand_count,time_ms,success,tries_to_hit,reduction_pct
     0,200,ZNeighborhood,10002,8,true,5692,30.08
     1,200,ZNeighborhood,10002,4,true,2382,30.13
     ...
     ```
   - The file contains multiple runs with varying digits (automatically incremented in ladder mode).

## Notes on Discrepancies
- The original protocol mentioned `--digits 200-260 --trials 5 --log ladder_results.csv`, but the actual code uses `--ladder --digits <start>` and writes to a hardcoded file name.
- If results differ, compare:
  - Commit hash
  - Java version
  - OS details
  - Full command used
- Attach a snippet of your generated CSV for comparison.

## Provenance Check
- View commit history for the CSV:
  ```
  git log --oneline -- ladder_results.csv
  ```
- Compare with committed version (if exists):
  ```
  diff ladder_results.csv path/to/committed/version
  ```

This ensures the benchmark can be reproduced step-by-step.