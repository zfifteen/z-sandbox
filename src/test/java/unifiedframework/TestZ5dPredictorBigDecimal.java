package unifiedframework;

import static org.junit.jupiter.api.Assertions.*;

import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * Test suite for BigDecimal arbitrary-precision support in Z5dPredictor. Tests ultra-high scales up
 * to 10^1233 and validates consistency with double-precision methods.
 */
public class TestZ5dPredictorBigDecimal {

  private static final MathContext MC = new MathContext(100, RoundingMode.HALF_UP);
  private static final double RELATIVE_TOLERANCE =
      1e-6; // 10^-6 relative error (adequate for comparison)

  @Test
  @DisplayName("Test BigDecimal PNT matches double PNT for reasonable scales")
  public void testBigDecimalPntMatchesDouble() {
    System.out.println("Testing BigDecimal PNT matches double PNT for reasonable scales");

    double[] testScales = {1000.0, 10000.0, 100000.0, 1000000.0};

    for (double k : testScales) {
      BigDecimal kBD = new BigDecimal(k);

      double doublePnt = Z5dPredictor.z5dBasePntPrime(k);
      BigDecimal bigDecimalPnt = Z5dPredictor.z5dBasePntPrimeBigDecimal(kBD, MC);
      double bigDecimalPntAsDouble = bigDecimalPnt.doubleValue();

      double relativeError = Math.abs(doublePnt - bigDecimalPntAsDouble) / doublePnt;

      System.out.printf(
          "k=%.0f: doublePNT=%.6f, BigDecimalPNT=%.6f, relError=%.10f%n",
          k, doublePnt, bigDecimalPntAsDouble, relativeError);

      assertTrue(
          relativeError < RELATIVE_TOLERANCE,
          String.format("Relative error %.10f exceeds tolerance at k=%.0f", relativeError, k));
    }
  }

  @Test
  @DisplayName("Test BigDecimal Z5D matches double Z5D for reasonable scales")
  public void testBigDecimalZ5dMatchesDouble() {
    System.out.println("Testing BigDecimal Z5D matches double Z5D for reasonable scales");

    double[] testScales = {1000.0, 10000.0, 100000.0, 1000000.0};

    for (double k : testScales) {
      BigDecimal kBD = new BigDecimal(k);

      double doubleZ5d = Z5dPredictor.z5dPrime(k, -0.00247, 0.04449, 0.3, false);
      BigDecimal bigDecimalZ5d =
          Z5dPredictor.z5dPrimeBigDecimal(kBD, -0.00247, 0.04449, 0.3, false, MC);
      double bigDecimalZ5dAsDouble = bigDecimalZ5d.doubleValue();

      double relativeError = Math.abs(doubleZ5d - bigDecimalZ5dAsDouble) / doubleZ5d;

      System.out.printf(
          "k=%.0f: doubleZ5D=%.6f, BigDecimalZ5D=%.6f, relError=%.10f%n",
          k, doubleZ5d, bigDecimalZ5dAsDouble, relativeError);

      assertTrue(
          relativeError < RELATIVE_TOLERANCE,
          String.format("Relative error %.10f exceeds tolerance at k=%.0f", relativeError, k));
    }
  }

  @Test
  @DisplayName("Test BigDecimal handles scales beyond double limit (10^306+)")
  public void testBigDecimalBeyondDoubleLimit() {
    System.out.println("Testing BigDecimal handles scales beyond double limit");

    // Test scales from 10^306 to 10^320 where double overflows
    int[] exponents = {306, 310, 315, 320};

    for (int exp : exponents) {
      String kStr = "1e" + exp;
      BigDecimal k = new BigDecimal(kStr);

      System.out.printf("\nTesting k = 10^%d:%n", exp);

      // Double methods should fail or return Inf/NaN
      double kDouble = Math.pow(10, exp);
      System.out.printf("  k as double: %.2e (isFinite: %b)%n", kDouble, Double.isFinite(kDouble));

      // BigDecimal should succeed
      BigDecimal pnt = Z5dPredictor.z5dBasePntPrimeBigDecimal(k, MC);
      BigDecimal z5d = Z5dPredictor.z5dPrimeBigDecimal(k, 0, 0, 0, true, MC);

      System.out.printf("  PNT (BigDecimal): %s%n", pnt.toString());
      System.out.printf("  Z5D (BigDecimal): %s%n", z5d.toString());

      // Validate results are positive and finite
      assertTrue(pnt.compareTo(BigDecimal.ZERO) > 0, "PNT should be positive");
      assertTrue(z5d.compareTo(BigDecimal.ZERO) > 0, "Z5D should be positive");
      assertTrue(z5d.compareTo(k) > 0, "Z5D should be greater than k");

      // Validate Z5D is close to PNT (within 10%)
      BigDecimal diff = z5d.subtract(pnt).abs();
      BigDecimal relDiff = diff.divide(pnt, MC);
      double relDiffDouble = relDiff.doubleValue();

      System.out.printf("  Relative difference from PNT: %.6f%n", relDiffDouble);
      assertTrue(relDiffDouble < 0.1, "Z5D should be within 10% of PNT");
    }
  }

  @Test
  @DisplayName("Test BigDecimal handles target scale 10^1233")
  public void testTargetScale1233() {
    System.out.println("Testing BigDecimal at target scale 10^1233");

    String kStr = "1e1233";
    System.out.printf("Testing k = %s%n", kStr);

    BigDecimal k = new BigDecimal(kStr);

    // Compute predictions
    BigDecimal pnt = Z5dPredictor.z5dBasePntPrimeBigDecimal(k, MC);
    BigDecimal z5d = Z5dPredictor.z5dPrimeBigDecimal(k, 0, 0, 0, true, MC);

    System.out.printf("PNT result: %s%n", pnt.toEngineeringString());
    System.out.printf("Z5D result: %s%n", z5d.toEngineeringString());

    // Validate results
    assertTrue(pnt.compareTo(BigDecimal.ZERO) > 0, "PNT should be positive");
    assertTrue(z5d.compareTo(BigDecimal.ZERO) > 0, "Z5D should be positive");
    assertTrue(z5d.compareTo(k) > 0, "Z5D should be greater than k");

    // Validate Z5D is close to PNT (within 10%)
    BigDecimal diff = z5d.subtract(pnt).abs();
    BigDecimal relDiff = diff.divide(pnt, MC);
    double relDiffDouble = relDiff.doubleValue();

    System.out.printf("Relative difference from PNT: %.10f%n", relDiffDouble);
    assertTrue(relDiffDouble < 0.1, "Z5D should be within 10% of PNT");

    System.out.println("SUCCESS: Scale 10^1233 handled correctly!");
  }

  @Test
  @DisplayName("Test BigDecimal string API convenience method")
  public void testStringApiConvenience() {
    System.out.println("Testing BigDecimal string API convenience method");

    String[] testScales = {"1e100", "1e500", "1e1000", "1e1233"};

    for (String kStr : testScales) {
      System.out.printf("\nTesting k = %s:%n", kStr);

      String result = Z5dPredictor.z5dPrimeString(kStr, 0, 0, 0, true);

      System.out.printf("Result: %s%n", result);

      // Validate result is a valid number
      BigDecimal resultBD = new BigDecimal(result);
      assertTrue(resultBD.compareTo(BigDecimal.ZERO) > 0, "Result should be positive");

      BigDecimal k = new BigDecimal(kStr);
      assertTrue(resultBD.compareTo(k) > 0, "Result should be greater than k");
    }
  }

  @Test
  @DisplayName("Test BigDecimal extended result structure")
  public void testBigDecimalExtendedResult() {
    System.out.println("Testing BigDecimal extended result structure");

    BigDecimal k = new BigDecimal("1e500");
    Z5dPredictor.Z5dResultBigDecimal result = new Z5dPredictor.Z5dResultBigDecimal();

    int status =
        Z5dPredictor.z5dPrimeExtendedBigDecimal(k, -0.00247, 0.04449, 0.3, false, result, MC);

    System.out.printf("Status: %d (expected: %d)%n", status, Z5dPredictor.Z5D_SUCCESS);
    System.out.printf("Prediction: %s%n", result.prediction.toEngineeringString());
    System.out.printf("PNT Base: %s%n", result.pntBase.toEngineeringString());
    System.out.printf("D Term: %s%n", result.dTerm.toEngineeringString());
    System.out.printf("E Term: %s%n", result.eTerm.toEngineeringString());
    System.out.printf("C Used: %.6f%n", result.cUsed);
    System.out.printf("K* Used: %.6f%n", result.kStarUsed);
    System.out.printf("Kappa Geo Used: %.6f%n", result.kappaGeoUsed);

    assertEquals(Z5dPredictor.Z5D_SUCCESS, status);
    assertEquals(Z5dPredictor.Z5D_SUCCESS, result.errorCode);
    assertTrue(result.prediction.compareTo(BigDecimal.ZERO) > 0);
    assertTrue(result.pntBase.compareTo(BigDecimal.ZERO) > 0);
    assertTrue(result.dTerm.compareTo(BigDecimal.ZERO) >= 0);
    assertTrue(result.eTerm.compareTo(BigDecimal.ZERO) > 0);
  }

  @Test
  @DisplayName("Test BigDecimal smoke test across wide range of scales")
  public void testBigDecimalSmokeTest() {
    System.out.println("Testing BigDecimal smoke test across wide range");
    System.out.println("Testing scales from 10^3 to 10^1233");

    // Test exponentially spaced scales
    int[] exponents = {3, 10, 50, 100, 200, 305, 306, 400, 600, 800, 1000, 1233};

    boolean allPassed = true;
    for (int exp : exponents) {
      String kStr = "1e" + exp;
      BigDecimal k = new BigDecimal(kStr);

      try {
        BigDecimal pnt = Z5dPredictor.z5dBasePntPrimeBigDecimal(k, MC);
        BigDecimal z5d = Z5dPredictor.z5dPrimeBigDecimal(k, 0, 0, 0, true, MC);

        boolean positive = z5d.compareTo(BigDecimal.ZERO) > 0;
        boolean greaterThanK = z5d.compareTo(k) > 0;

        BigDecimal relDiff = z5d.subtract(pnt).abs().divide(pnt, MC);
        boolean closeToPnt = relDiff.doubleValue() < 0.1;

        System.out.printf(
            "Scale 10^%d: positive=%b, >k=%b, close_to_PNT=%b",
            exp, positive, greaterThanK, closeToPnt);

        if (positive && greaterThanK && closeToPnt) {
          System.out.println(" -> PASSED");
        } else {
          System.out.println(" -> FAILED");
          allPassed = false;
        }
      } catch (Exception e) {
        System.out.printf("Scale 10^%d: EXCEPTION - %s -> FAILED%n", exp, e.getMessage());
        allPassed = false;
      }
    }

    assertTrue(allPassed, "All smoke tests should pass");
    System.out.println("BigDecimal smoke test COMPLETE");
  }

  @Test
  @DisplayName("Test BigDecimal mathematical consistency")
  public void testBigDecimalMathematicalConsistency() {
    System.out.println("Testing BigDecimal mathematical consistency");

    // Test that predictions increase monotonically with k
    String[] scales = {"1e100", "1e200", "1e500", "1e1000"};
    BigDecimal prevResult = BigDecimal.ZERO;

    for (String kStr : scales) {
      BigDecimal k = new BigDecimal(kStr);
      BigDecimal result = Z5dPredictor.z5dPrimeBigDecimal(k, 0, 0, 0, true, MC);

      System.out.printf("k=%s: result=%s%n", kStr, result.toEngineeringString());

      if (prevResult.compareTo(BigDecimal.ZERO) > 0) {
        boolean increasing = result.compareTo(prevResult) > 0;
        System.out.printf("  Increasing from previous: %b%n", increasing);
        assertTrue(increasing, "Results should increase monotonically");
      }

      prevResult = result;
    }
  }

  @Test
  @DisplayName("Test BigDecimal auto-calibration for ultra-high scales")
  public void testBigDecimalAutoCalibration() {
    System.out.println("Testing BigDecimal auto-calibration for ultra-high scales");

    BigDecimal k = new BigDecimal("1e1000");

    // With auto-calibration
    BigDecimal withAuto = Z5dPredictor.z5dPrimeBigDecimal(k, 0, 0, 0, true, MC);

    // Without auto-calibration (use default params)
    BigDecimal withoutAuto = Z5dPredictor.z5dPrimeBigDecimal(k, -0.00247, 0.04449, 0.3, false, MC);

    System.out.printf("With auto-calibration: %s%n", withAuto.toEngineeringString());
    System.out.printf("Without auto-calibration: %s%n", withoutAuto.toEngineeringString());

    // Both should be positive and finite
    assertTrue(withAuto.compareTo(BigDecimal.ZERO) > 0);
    assertTrue(withoutAuto.compareTo(BigDecimal.ZERO) > 0);

    // They might differ slightly due to calibration
    BigDecimal diff = withAuto.subtract(withoutAuto).abs();
    BigDecimal relDiff = diff.divide(withAuto, MC);

    System.out.printf("Relative difference: %.10f%n", relDiff.doubleValue());

    // Should be reasonably close (within 20% since calibration differs)
    assertTrue(relDiff.doubleValue() < 0.2, "Results should be reasonably close");
  }

  @Test
  @DisplayName("Verify BigDecimal fixes the overflow at 10^306")
  public void testBigDecimalFixesOverflow() {
    System.out.println("Verifying BigDecimal fixes overflow at 10^306");

    // At 10^306, double arithmetic overflows
    double kDouble = Math.pow(10, 306);
    System.out.printf(
        "10^306 as double: %.2e (isInfinite: %b)%n", kDouble, Double.isInfinite(kDouble));

    double doubleResult = Z5dPredictor.z5dPrime(kDouble, 0, 0, 0, true);
    System.out.printf(
        "Double Z5D result: %.2e (isNaN: %b)%n", doubleResult, Double.isNaN(doubleResult));

    // BigDecimal should handle it fine
    String kStr = "1e306";
    BigDecimal k = new BigDecimal(kStr);
    BigDecimal bigDecimalResult = Z5dPredictor.z5dPrimeBigDecimal(k, 0, 0, 0, true, MC);

    System.out.printf("BigDecimal Z5D result: %s%n", bigDecimalResult.toEngineeringString());

    assertTrue(
        bigDecimalResult.compareTo(BigDecimal.ZERO) > 0, "BigDecimal result should be positive");
    assertTrue(bigDecimalResult.compareTo(k) > 0, "BigDecimal result should be greater than k");

    System.out.println("SUCCESS: BigDecimal handles 10^306 correctly where double fails!");
  }
}
