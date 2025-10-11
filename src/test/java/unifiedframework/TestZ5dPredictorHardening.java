package unifiedframework;

import static org.junit.jupiter.api.Assertions.*;

import java.util.Random;
import org.junit.jupiter.api.Test;

/**
 * Hardening tests for Z5d predictor: monotonicity, tight accuracy guards, randomized domain
 * fuzzing, and deviation vs PNT baseline.
 *
 * <p>Assumptions: - Z5dPredictor.prime(double k) -> double - Z5dPredictor.basePntPrime(double k) ->
 * double (PNT baseline)
 *
 * <p>Adjust method names if your API differs.
 */
public class TestZ5dPredictorHardening {

  private static double z5dPrime(double k) {
    return Z5dPredictor.z5dPrime(k, -0.00247, 0.04449, 0.3, false);
  }

  private static double pnt(double k) {
    return Z5dPredictor.z5dBasePntPrime(k);
  }

  @Test
  void monotoneInK_onGrid() {
    System.out.println("Testing monotonicity in k on grid");
    double[] ks = {1e3, 3e3, 1e4, 3e4, 1e5, 3e5, 1e6};
    System.out.print("Test k values: [");
    for (int i = 0; i < ks.length; i++) {
      System.out.printf("%.0f", ks[i]);
      if (i < ks.length - 1) System.out.print(", ");
    }
    System.out.println("]");

    double prev = -1.0;
    for (double k : ks) {
      double v = z5dPrime(k);
      boolean isFinitePositive = Double.isFinite(v) && v > 0.0;
      System.out.printf(
          "k=%.0f: value=%.6f, finite=%b, positive=%b, valid=%b%n",
          k, v, Double.isFinite(v), v > 0.0, isFinitePositive);

      assertTrue(isFinitePositive, "finite/positive @k=" + k);

      if (prev > 0.0) {
        boolean isIncreasing = v > prev;
        System.out.printf("  vs prev (%.6f): increasing=%b%n", prev, isIncreasing);
        assertTrue(isIncreasing, "monotone increasing @k=" + k);
      }
      prev = v;
    }
  }

  @Test
  void deviationVsPnt_isTiny_at100k() {
    System.out.println("Testing deviation vs PNT baseline at k=100k");
    double k = 1e5;
    double z = z5dPrime(k);
    double b = pnt(k);
    System.out.printf("k=%.0f: Z5D=%.6f, PNT=%.6f%n", k, z, b);

    boolean pntValid = Double.isFinite(b) && b > 0.0;
    System.out.printf("PNT valid: %b%n", pntValid);
    assertTrue(pntValid);

    double rel = Math.abs(z - b) / b;
    double threshold = 4e-4; // 0.04%
    System.out.printf("Relative deviation: %.6f (threshold: %.6f)%n", rel, threshold);
    System.out.printf("Within threshold: %b%n", rel <= threshold);

    // Bound deviation vs PNT baseline; conservative 0.04%
    assertTrue(rel <= threshold, "rel dev vs PNT ≤ 0.04% (rel=" + rel + ")");
  }

  @Test
  void accuracyVsTruth_panelAt100k() {
    System.out.println("Testing accuracy vs truth at k=100k");
    // Small truth panel at k=100000
    double k = 1e5;
    double trueP = 1_299_709d; // p_100000
    double z = z5dPrime(k);
    System.out.printf("k=%.0f: predicted=%.6f, true=%.6f%n", k, z, trueP);

    double absError = Math.abs(z - trueP);
    double rel = absError / trueP;
    double threshold = 1.5e-4; // 0.015%

    System.out.printf("Absolute error: %.6f%n", absError);
    System.out.printf("Relative error: %.6f (threshold: %.6f)%n", rel, threshold);
    System.out.printf("Within threshold: %b%n", rel <= threshold);

    // Tight to observed regime (~1e-4): 0.015% guard
    assertTrue(rel <= threshold, "rel err ≤ 0.015% (rel=" + rel + ")");
  }

  @Test
  void randomizedDomainFuzz_noNaNs() {
    System.out.println("Testing randomized domain fuzzing (no NaNs)");
    Random r = new Random(42);
    System.out.printf("Testing %d random k values in range [1e3, 1e11]%n", 2000);

    int passed = 0;
    int failed = 0;

    for (int i = 0; i < 2000; i++) {
      double k = Math.pow(10.0, 3.0 + 8.0 * r.nextDouble()); // [1e3, 1e11]
      double z = z5dPrime(k);
      boolean isValid = Double.isFinite(z) && z > 0.0;

      if (isValid) {
        passed++;
      } else {
        failed++;
        System.out.printf(
            "  FAILED @k=%.6e: value=%.6f, finite=%b, positive=%b%n",
            k, z, Double.isFinite(z), z > 0.0);
      }
    }

    System.out.printf("Results: %d passed, %d failed%n", passed, failed);
    assertTrue(failed == 0, "All values should be finite and positive");
  }

  @Test
  void increasingVsK_baselineComparison() {
    System.out.println("Testing PNT baseline monotonicity");
    // Weak check that PNT growth is monotone over a grid
    double[] ks = {1e4, 3e4, 1e5, 3e5};
    System.out.print("Test k values: [");
    for (int i = 0; i < ks.length; i++) {
      System.out.printf("%.0f", ks[i]);
      if (i < ks.length - 1) System.out.print(", ");
    }
    System.out.println("]");

    double prev = -1.0;
    for (double k : ks) {
      double b = pnt(k);
      boolean isValid = Double.isFinite(b) && b > 0.0;
      System.out.printf(
          "k=%.0f: PNT=%.6f, finite=%b, positive=%b, valid=%b%n",
          k, b, Double.isFinite(b), b > 0.0, isValid);

      assertTrue(isValid);

      if (prev > 0.0) {
        boolean isIncreasing = b > prev;
        System.out.printf("  vs prev (%.6f): increasing=%b%n", prev, isIncreasing);
        assertTrue(isIncreasing, "PNT monotone @k=" + k);
      }
      prev = b;
    }
  }
}
