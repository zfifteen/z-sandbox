package unifiedframework;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

public class TestZ5dTruthPanels {

  @Test
  void k1e6_matchesTruth_tight() {
    double k = 1_000_000d;
    double truth = 15_485_863d; // p_1,000,000
    double z = Z5dPredictor.z5dPrime(k, 0, 0, 0, true);
    double rel = Math.abs(z - truth) / truth;
    System.out.printf("k=%.0f, truth=%.0f, z=%.6f, rel=%.10f%n", k, truth, z, rel);
    assertTrue(rel <= 2e-4, "rel err ≤ 0.02% (was " + rel + ")");
  }

  @Test
  void k1e7_matchesTruth_tight() {
    double k = 10_000_000d;
    double truth = 179_424_673d; // p_10,000,000
    double z = Z5dPredictor.z5dPrime(k, 0, 0, 0, true);
    double rel = Math.abs(z - truth) / truth;
    System.out.printf("k=%.0f, truth=%.0f, z=%.6f, rel=%.10f%n", k, truth, z, rel);
    assertTrue(rel <= 2e-4, "rel err ≤ 0.02% (was " + rel + ")");
  }

  @Test
  void k1e9_matchesTruth_tight() {
    double k = 1_000_000_000d;
    double truth = 22_801_644_371d; // p_1,000,000,000
    double z = Z5dPredictor.z5dPrime(k, 0, 0, 0, true);
    double rel = Math.abs(z - truth) / truth;
    System.out.printf("k=%.0f, truth=%.0f, z=%.6f, rel=%.10f%n", k, truth, z, rel);
    assertTrue(rel <= 2e-4, "rel err ≤ 0.02% (was " + rel + ")");
  }

  @Test
  void k1e10_matchesTruth_tight() {
    double k = 10_000_000_000d;
    double truth = 252_097_800_623d; // p_10,000,000,000
    double z = Z5dPredictor.z5dPrime(k, 0, 0, 0, true);
    double rel = Math.abs(z - truth) / truth;
    System.out.printf("k=%.0f, truth=%.0f, z=%.6f, rel=%.10f%n", k, truth, z, rel);
    assertTrue(rel <= 2e-4, "rel err ≤ 0.02% (was " + rel + ")");
  }

  @Test
  void diverseK_accuracyCheck() {
    // Test diverse k values across calibration boundaries
    double[] ks = {1e4, 5e6, 2e7, 5e9, 2e10};
    for (double k : ks) {
      double z = Z5dPredictor.z5dPrime(k, 0, 0, 0, true);
      // Approximate check: z should be roughly k * ln(k) + k * ln(ln(k))
      double approx = k * Math.log(k) + k * Math.log(Math.log(k));
      double rel = Math.abs(z - approx) / approx;
      System.out.printf("k=%.0f, approx=%.6f, z=%.6f, rel=%.10f%n", k, approx, z, rel);
      assertTrue(rel < 0.1, "Diverse k=" + k + " rel err >10% (was " + rel + ")");
    }
  }
}
