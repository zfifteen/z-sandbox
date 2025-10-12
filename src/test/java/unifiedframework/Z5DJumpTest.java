package unifiedframework;

import org.junit.jupiter.api.Test;
import java.math.BigDecimal;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for Z5DJump class.
 * Verifies jump calculations and displays data for verification.
 */
public class Z5DJumpTest {

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

        for (int i = 0; i < testCases.length; i++) {
            BigDecimal k = testCases[i];
            double jumpSize = Z5DJump.computeGeodesicJump(k);

            System.out.printf("%-25s: jump_size = %.3f%n", descriptions[i], jumpSize);

            // Basic assertions
            assertTrue(jumpSize > 0, "Jump size must be positive for " + descriptions[i]);
            assertTrue(Double.isFinite(jumpSize), "Jump size must be finite for " + descriptions[i]);
            assertTrue(jumpSize >= 2.0, "Jump size must be at least fallback value for " + descriptions[i]);
        }

        System.out.println("✓ All jump size calculations completed successfully");
        System.out.println("✓ Verification data displayed above");
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