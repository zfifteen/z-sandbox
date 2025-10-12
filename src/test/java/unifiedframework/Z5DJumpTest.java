package unifiedframework;

import org.junit.jupiter.api.Test;
import java.math.BigDecimal;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for Z5DJump class.
 * Verifies jump calculations and displays data for verification.
 */
public class Z5DJumpTest {

    // === Regression guard helpers ===
    private static boolean approx(double a, double b, double tol) {
        return Math.abs(a - b) <= tol;
    }
    private static void must(boolean cond, String msg) {
        if (!cond) throw new AssertionError(msg);
    }
    // === End: Regression guard helpers ===

    @Test
    public void testGeodesicJumpCalculations() {
        System.out.println("=== Z5DJump Unit Test: Jump Size Verification ===");

        // Test cases with expected approximate jump sizes
        BigDecimal[] testCases = {
            BigDecimal.valueOf(1000),
            BigDecimal.valueOf(10000),
            new BigDecimal("1e12"),
            new BigDecimal("1e18"),
            new BigDecimal("1e100"),
            new BigDecimal("1e500"),
            new BigDecimal("1e1000"),
            new BigDecimal("1e1233")
        };

        String[] descriptions = {
            "k=1000 (small scale)",
            "k=10000 (medium scale)",
            "k=10^12 (large scale)",
            "k=10^18 (very large scale)",
            "k=10^100 (ultra scale)",
            "k=10^500 (extreme scale)",
            "k=10^1000 (ultra-extreme scale)",
            "k=10^1233 (maximum test scale)"
        };

        // Store lnPred values for regression guards
        double[] lnPredValues = new double[testCases.length];

        for (int i = 0; i < testCases.length; i++) {
            BigDecimal k = testCases[i];
            String predStr = Z5dPredictor.z5dPrimeString(k.toString(), Z5DJump.ZF_Z5D_C_CALIBRATED,
                                                       Z5DJump.ZF_KAPPA_STAR_DEFAULT,
                                                       Z5DJump.ZF_KAPPA_GEO_DEFAULT, true);
            double jumpSize = Z5DJump.computeGeodesicJump(k);
            double lnPred;
            try {
                BigDecimal pred = new BigDecimal(predStr);
                lnPred = Z5DJump.approximateLn(pred);
            } catch (NumberFormatException e) {
                lnPred = Z5DJump.parseLnFromScientificString(predStr);
            }
            lnPredValues[i] = lnPred;

            System.out.printf("%-25s: jump_size = %.3f (ln(pred)=%.3f)%n", descriptions[i], jumpSize, lnPred);

            // Basic assertions
            assertTrue(jumpSize > 0, "Jump size must be positive for " + descriptions[i]);
            assertTrue(Double.isFinite(jumpSize), "Jump size must be finite for " + descriptions[i]);
            assertTrue(jumpSize >= 2.0, "Jump size must be at least fallback value for " + descriptions[i]);
        }

        // === Regression guards ===
        double LN10 = Math.log(10.0);
        double kappaGeo = 0.300;


        // Anchor checks
        must(approx(lnPredValues[0], 9.077, 0.5), "ln p_{1e3} out of expected range");
        must(approx(lnPredValues[1], 11.602, 0.5), "ln p_{1e4} out of expected range");
        must(approx(lnPredValues[3], 45.918, 0.5), "ln p_{1e18} out of expected range");

        // Slope sanity: approximate using 1e100 and 1e101
        BigDecimal k100 = new BigDecimal("1e100");
        BigDecimal k101 = new BigDecimal("1e101");
        String predStr100 = Z5dPredictor.z5dPrimeString(k100.toString(), Z5DJump.ZF_Z5D_C_CALIBRATED,
                                                       Z5DJump.ZF_KAPPA_STAR_DEFAULT,
                                                       Z5DJump.ZF_KAPPA_GEO_DEFAULT, true);
        String predStr101 = Z5dPredictor.z5dPrimeString(k101.toString(), Z5DJump.ZF_Z5D_C_CALIBRATED,
                                                       Z5DJump.ZF_KAPPA_STAR_DEFAULT,
                                                       Z5DJump.ZF_KAPPA_GEO_DEFAULT, true);
        double ln100, ln101;
        try {
            ln100 = Z5DJump.approximateLn(new BigDecimal(predStr100));
            ln101 = Z5DJump.approximateLn(new BigDecimal(predStr101));
        } catch (NumberFormatException e) {
            ln100 = Z5DJump.parseLnFromScientificString(predStr100);
            ln101 = Z5DJump.parseLnFromScientificString(predStr101);
        }
        double slope = (ln101 - ln100) / LN10;
        must(slope > 0.9 && slope < 1.3, "slope d ln p / d ln k out of range (regression risk)");

        // Jump-size anchors
        must(approx(kappaGeo * lnPredValues[0], 2.723, 0.5), "jump(1e3) out of range");
        must(approx(kappaGeo * lnPredValues[1], 3.481, 0.5), "jump(1e4) out of range");
        must(approx(kappaGeo * lnPredValues[3], 13.775, 0.5), "jump(1e18) out of expected range");
        // === End: Regression guards ===

        System.out.println("✓ All jump size calculations completed successfully");
        System.out.println("✓ Verification data displayed above");
        System.out.println("✓ Regression guards passed");
    }

    @Test
    public void testCandidateGeneration() {
        System.out.println("=== Z5DJump Unit Test: Candidate Generation ===");

        BigDecimal startK = BigDecimal.valueOf(1000);
        int numCandidates = 5;
        double baseIncrement = 1.0;

        var candidates = Z5DJump.generateJumpedCandidates(startK, numCandidates, baseIncrement);

        System.out.println("Generated candidates:");
        for (int i = 0; i < candidates.size(); i++) {
            System.out.printf("  Candidate %d: %s%n", i + 1, candidates.get(i).toEngineeringString());
        }

        // Assertions
        assertEquals(numCandidates, candidates.size(), "Should generate correct number of candidates");
        assertTrue(candidates.get(0).compareTo(startK) == 0, "First candidate should be start value");

        for (int i = 1; i < candidates.size(); i++) {
            assertTrue(candidates.get(i).compareTo(candidates.get(i-1)) > 0,
                      "Candidates should be monotonically increasing");
        }

        System.out.println("✓ Candidate generation test passed");
    }

    @Test
    public void testJumpSizeScaling() {
        System.out.println("=== Z5DJump Unit Test: Jump Size Scaling Verification ===");

        BigDecimal k1 = BigDecimal.valueOf(1000);
        BigDecimal k2 = new BigDecimal("1e100");

        double jump1 = Z5DJump.computeGeodesicJump(k1);
        double jump2 = Z5DJump.computeGeodesicJump(k2);

        System.out.printf("Jump size for k=1000: %.3f%n", jump1);
        System.out.printf("Jump size for k=10^100: %.3f%n", jump2);
        System.out.printf("Ratio (k2/k1): %.1e%n", k2.divide(k1, java.math.MathContext.DECIMAL128).doubleValue());
        System.out.printf("Jump size ratio: %.3f%n", jump2 / jump1);

        // Jump sizes should increase with scale
        assertTrue(jump2 > jump1, "Jump size should increase with scale");

        System.out.println("✓ Jump size scaling test passed");
    }

    @Test
    public void testDemonstrationOutput() {
        System.out.println("=== Z5DJump Unit Test: Full Demonstration ===");
        // This test runs the full demonstration to display verification data
        Z5DJump.demonstrateJumping();
        System.out.println("✓ Demonstration completed - verification data displayed above");
    }
}