package unifiedframework;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;

/**
 * Unit tests for Z5dPredictor class
 */
public class TestZ5dPredictor {

    private static final double DELTA = 1e-6; // Tolerance for floating-point comparisons

    @Test
    @DisplayName("Test basic prediction functionality")
    public void testBasicPrediction() {
        System.out.println("Testing basic prediction functionality");
        // Test with default parameters
        double k = 100000.0;
        double result = Z5dPredictor.z5dPrime(k, -0.00247, 0.04449, 0.3, false);

        System.out.printf("Input k: %.1f%n", k);
        System.out.printf("Result: %.6f%n", result);
        System.out.printf("Is finite: %b%n", Double.isFinite(result));
        System.out.printf("Is positive: %b%n", result > 0);

        // Should return a finite positive value
        assertTrue(Double.isFinite(result));
        assertTrue(result > 0);

        // For k=100000, PNT approximation is around 1299709
        // Z5D should be close but modified by corrections
        double pntApprox = k * (Math.log(k) + Math.log(Math.log(k)) - 1);
        double tolerance = pntApprox * 0.01;
        System.out.printf("PNT approximation: %.6f%n", pntApprox);
        System.out.printf("Tolerance (1%%): %.6f%n", tolerance);
        System.out.printf("Difference from PNT: %.6f%n", Math.abs(result - pntApprox));
        System.out.printf("Within tolerance: %b%n", Math.abs(result - pntApprox) < tolerance);

        assertTrue(Math.abs(result - pntApprox) < pntApprox * 0.01); // Within 1% of PNT
    }

    @Test
    @DisplayName("Test auto-calibration functionality")
    public void testAutoCalibration() {
        System.out.println("Testing auto-calibration functionality");
        double k = 100000.0;

        // Manual calibration
        double manual = Z5dPredictor.z5dPrime(k, -0.00247, 0.04449, 0.3, false);

        // Auto-calibration
        double auto = Z5dPredictor.z5dPrime(k, 0, 0, 0, true);

        System.out.printf("Input k: %.1f%n", k);
        System.out.printf("Manual calibration result: %.6f%n", manual);
        System.out.printf("Auto-calibration result: %.6f%n", auto);
        System.out.printf("Manual is finite: %b%n", Double.isFinite(manual));
        System.out.printf("Auto is finite: %b%n", Double.isFinite(auto));
        System.out.printf("Manual is positive: %b%n", manual > 0);
        System.out.printf("Auto is positive: %b%n", auto > 0);
        System.out.printf("Results equal: %b%n", Math.abs(manual - auto) < DELTA);

        // Both should be finite and positive
        assertTrue(Double.isFinite(manual));
        assertTrue(Double.isFinite(auto));
        assertTrue(manual > 0);
        assertTrue(auto > 0);

        // For this k value, auto and manual should be the same (scale 1)
        assertEquals(manual, auto, DELTA);
    }

    @Test
    @DisplayName("Test input validation")
    public void testValidation() {
        System.out.println("Testing input validation");

        // Valid inputs
        int validK = Z5dPredictor.z5dValidateK(100000.0);
        int validKappa = Z5dPredictor.z5dValidateKappaGeo(0.3);
        System.out.printf("z5dValidateK(100000.0): %d (expected: %d)%n", validK, Z5dPredictor.Z5D_SUCCESS);
        System.out.printf("z5dValidateKappaGeo(0.3): %d (expected: %d)%n", validKappa, Z5dPredictor.Z5D_SUCCESS);
        assertEquals(Z5dPredictor.Z5D_SUCCESS, validK);
        assertEquals(Z5dPredictor.Z5D_SUCCESS, validKappa);

        // Invalid inputs
        int invalidK1 = Z5dPredictor.z5dValidateK(1.0); // Too small
        int invalidK2 = Z5dPredictor.z5dValidateK(-1.0); // Negative
        int invalidK3 = Z5dPredictor.z5dValidateK(Double.NaN); // NaN
        int invalidK4 = Z5dPredictor.z5dValidateK(Double.MAX_VALUE); // Too large

        System.out.printf("z5dValidateK(1.0): %d (expected: %d)%n", invalidK1, Z5dPredictor.Z5D_ERROR_INVALID_K);
        System.out.printf("z5dValidateK(-1.0): %d (expected: %d)%n", invalidK2, Z5dPredictor.Z5D_ERROR_INVALID_K);
        System.out.printf("z5dValidateK(NaN): %d (expected: %d)%n", invalidK3, Z5dPredictor.Z5D_ERROR_DOMAIN);
        System.out.printf("z5dValidateK(MAX_VALUE): %d (expected: %d)%n", invalidK4, Z5dPredictor.Z5D_ERROR_OVERFLOW);

        assertEquals(Z5dPredictor.Z5D_ERROR_INVALID_K, invalidK1);
        assertEquals(Z5dPredictor.Z5D_ERROR_INVALID_K, invalidK2);
        assertEquals(Z5dPredictor.Z5D_ERROR_DOMAIN, invalidK3);
        assertEquals(Z5dPredictor.Z5D_ERROR_OVERFLOW, invalidK4);

        int invalidKappa1 = Z5dPredictor.z5dValidateKappaGeo(-0.1); // Too small
        int invalidKappa2 = Z5dPredictor.z5dValidateKappaGeo(20.0); // Too large
        int invalidKappa3 = Z5dPredictor.z5dValidateKappaGeo(Double.NaN); // NaN

        System.out.printf("z5dValidateKappaGeo(-0.1): %d (expected: %d)%n", invalidKappa1, Z5dPredictor.Z5D_ERROR_INVALID_KAPPA_GEO);
        System.out.printf("z5dValidateKappaGeo(20.0): %d (expected: %d)%n", invalidKappa2, Z5dPredictor.Z5D_ERROR_INVALID_KAPPA_GEO);
        System.out.printf("z5dValidateKappaGeo(NaN): %d (expected: %d)%n", invalidKappa3, Z5dPredictor.Z5D_ERROR_DOMAIN);

        assertEquals(Z5dPredictor.Z5D_ERROR_INVALID_KAPPA_GEO, invalidKappa1);
        assertEquals(Z5dPredictor.Z5D_ERROR_INVALID_KAPPA_GEO, invalidKappa2);
        assertEquals(Z5dPredictor.Z5D_ERROR_DOMAIN, invalidKappa3);
    }

    @Test
    @DisplayName("Test calibration selection")
    public void testCalibrationSelection() {
        System.out.println("Testing calibration selection");

        // Test different scales
        Z5dPredictor.Z5dCalibration cal1 = Z5dPredictor.z5dGetOptimalCalibration(1000.0); // Scale 1
        Z5dPredictor.Z5dCalibration cal2 = Z5dPredictor.z5dGetOptimalCalibration(1e8);   // Scale 1
        Z5dPredictor.Z5dCalibration cal3 = Z5dPredictor.z5dGetOptimalCalibration(1e11);  // Scale 4

        System.out.printf("Calibration for k=1000: c=%.5f, k*=%.5f, kappa=%.5f%n", cal1.c, cal1.kStar, cal1.kappaGeoFactor);
        System.out.printf("Calibration for k=1e8: c=%.5f, k*=%.5f, kappa=%.5f%n", cal2.c, cal2.kStar, cal2.kappaGeoFactor);
        System.out.printf("Calibration for k=1e11: c=%.5f, k*=%.5f, kappa=%.5f%n", cal3.c, cal3.kStar, cal3.kappaGeoFactor);

        // Check that different scales return different calibrations
        System.out.printf("cal1.c != cal2.c: %b%n", cal1.c != cal2.c);
        System.out.printf("cal1.kStar != cal2.kStar: %b%n", cal1.kStar != cal2.kStar);
        System.out.printf("cal2.c != cal3.c: %b%n", cal2.c != cal3.c);

        assertNotEquals(cal1.c, cal2.c);
        assertNotEquals(cal1.kStar, cal2.kStar);
        assertNotEquals(cal2.c, cal3.c);

        // All should be finite
        System.out.printf("All cal1 values finite: %b%n", Double.isFinite(cal1.c) && Double.isFinite(cal1.kStar) && Double.isFinite(cal1.kappaGeoFactor));
        assertTrue(Double.isFinite(cal1.c));
        assertTrue(Double.isFinite(cal1.kStar));
        assertTrue(Double.isFinite(cal1.kappaGeoFactor));
    }

    @Test
    @DisplayName("Test edge cases and error handling")
    public void testEdgeCases() {
        System.out.println("Testing edge cases and error handling");

        // Invalid k values should return NaN
        double result1 = Z5dPredictor.z5dPrime(1.0, 0, 0, 0, false);
        double result2 = Z5dPredictor.z5dPrime(-1.0, 0, 0, 0, false);
        double result3 = Z5dPredictor.z5dPrime(Double.NaN, 0, 0, 0, false);

        System.out.printf("z5dPrime(1.0): %.6f (isNaN: %b)%n", result1, Double.isNaN(result1));
        System.out.printf("z5dPrime(-1.0): %.6f (isNaN: %b)%n", result2, Double.isNaN(result2));
        System.out.printf("z5dPrime(NaN): %.6f (isNaN: %b)%n", result3, Double.isNaN(result3));

        assertTrue(Double.isNaN(result1));
        assertTrue(Double.isNaN(result2));
        assertTrue(Double.isNaN(result3));

        // Base PNT function should handle edge cases
        double base1 = Z5dPredictor.z5dBasePntPrime(1.0);
        double base3 = Z5dPredictor.z5dBasePntPrime(Double.NaN);

        System.out.printf("z5dBasePntPrime(1.0): %.6f (isNaN: %b)%n", base1, Double.isNaN(base1));
        System.out.printf("z5dBasePntPrime(NaN): %.6f (isNaN: %b)%n", base3, Double.isNaN(base3));

        assertTrue(Double.isNaN(base1));
        assertTrue(Double.isNaN(base3));

        // Valid k should work
        double result = Z5dPredictor.z5dBasePntPrime(100000.0);
        System.out.printf("z5dBasePntPrime(100000.0): %.6f (finite: %b, positive: %b)%n", result, Double.isFinite(result), result > 0);

        assertTrue(Double.isFinite(result));
        assertTrue(result > 0);
    }

    @Test
    @DisplayName("Test extended prediction results")
    public void testExtendedPrediction() {
        System.out.println("Testing extended prediction results");

        double k = 100000.0;
        Z5dPredictor.Z5dResult result = new Z5dPredictor.Z5dResult();

        int status = Z5dPredictor.z5dPrimeExtended(k, -0.00247, 0.04449, 0.3, false, result);

        System.out.printf("Input k: %.1f%n", k);
        System.out.printf("Return status: %d (expected: %d)%n", status, Z5dPredictor.Z5D_SUCCESS);
        System.out.printf("Result error code: %d (expected: %d)%n", result.errorCode, Z5dPredictor.Z5D_SUCCESS);
        System.out.printf("Prediction: %.6f (finite: %b, positive: %b)%n", result.prediction, Double.isFinite(result.prediction), result.prediction > 0);
        System.out.printf("PNT Base: %.6f (finite: %b, positive: %b)%n", result.pntBase, Double.isFinite(result.pntBase), result.pntBase > 0);
        System.out.printf("D Term: %.6f (finite: %b, >=0: %b)%n", result.dTerm, Double.isFinite(result.dTerm), result.dTerm >= 0);
        System.out.printf("E Term: %.6f (finite: %b, >=0: %b)%n", result.eTerm, Double.isFinite(result.eTerm), result.eTerm >= 0);
        System.out.printf("Curvature Proxy: %.6f (finite: %b)%n", result.curvatureProxy, Double.isFinite(result.curvatureProxy));
        System.out.printf("C Used: %.6f (finite: %b)%n", result.cUsed, Double.isFinite(result.cUsed));
        System.out.printf("K* Used: %.6f (finite: %b)%n", result.kStarUsed, Double.isFinite(result.kStarUsed));
        System.out.printf("Kappa Geo Used: %.6f (finite: %b)%n", result.kappaGeoUsed, Double.isFinite(result.kappaGeoUsed));

        assertEquals(Z5dPredictor.Z5D_SUCCESS, status);
        assertEquals(Z5dPredictor.Z5D_SUCCESS, result.errorCode);
        assertTrue(Double.isFinite(result.prediction));
        assertTrue(result.prediction > 0);
        assertTrue(Double.isFinite(result.pntBase));
        assertTrue(result.pntBase > 0);
        assertTrue(Double.isFinite(result.dTerm));
        assertTrue(result.dTerm >= 0);
        assertTrue(Double.isFinite(result.eTerm));
        assertTrue(result.eTerm >= 0);
        assertTrue(Double.isFinite(result.curvatureProxy));
        assertTrue(Double.isFinite(result.cUsed));
        assertTrue(Double.isFinite(result.kStarUsed));
        assertTrue(Double.isFinite(result.kappaGeoUsed));
    }

    @Test
    @DisplayName("Test accuracy validation")
    public void testAccuracyValidation() {
        System.out.println("Testing accuracy validation");

        double[] kValues = {100000.0, 100003.0, 100008.0};
        double[] truePrimes = {1299709.0, 1299733.0, 1299767.0}; // Approximate actual primes
        double[] meanError = new double[1];
        double[] maxError = new double[1];

        System.out.print("K values: [");
        for (int i = 0; i < kValues.length; i++) {
            System.out.printf("%.1f", kValues[i]);
            if (i < kValues.length - 1) System.out.print(", ");
        }
        System.out.println("]");

        System.out.print("True primes: [");
        for (int i = 0; i < truePrimes.length; i++) {
            System.out.printf("%.1f", truePrimes[i]);
            if (i < truePrimes.length - 1) System.out.print(", ");
        }
        System.out.println("]");

        int status = Z5dPredictor.z5dValidateAccuracy(kValues, truePrimes, kValues.length,
                                                    -0.00247, 0.04449, 0.3, false,
                                                    meanError, maxError);

        System.out.printf("Return status: %d (expected: %d)%n", status, Z5dPredictor.Z5D_SUCCESS);
        System.out.printf("Mean relative error: %.6f (should be >= 0)%n", meanError[0]);
        System.out.printf("Max relative error: %.6f (should be >= 0)%n", maxError[0]);
        System.out.printf("Mean <= Max: %b%n", meanError[0] <= maxError[0]);

        assertEquals(Z5dPredictor.Z5D_SUCCESS, status);
        assertTrue(meanError[0] >= 0);
        assertTrue(maxError[0] >= 0);
        assertTrue(meanError[0] <= maxError[0]); // Mean should be <= max
    }

    @Test
    @DisplayName("Test mathematical consistency")
    public void testMathematicalConsistency() {
        System.out.println("Testing mathematical consistency");

        double k = 100000.0;

        // Base PNT should be close to PNT approximation
        double pnt = Z5dPredictor.z5dBasePntPrime(k);
        double expectedPnt = k * (Math.log(k) + Math.log(Math.log(k)) - 1 +
                                 (Math.log(Math.log(k)) - 2) / Math.log(k));

        System.out.printf("Input k: %.1f%n", k);
        System.out.printf("Calculated PNT: %.6f%n", pnt);
        System.out.printf("Expected PNT: %.6f%n", expectedPnt);
        System.out.printf("Difference: %.6f%n", Math.abs(pnt - expectedPnt));
        System.out.printf("Tolerance (1%%): %.6f%n", expectedPnt * 0.01);
        System.out.printf("Within tolerance: %b%n", Math.abs(pnt - expectedPnt) < expectedPnt * 0.01);

        assertEquals(expectedPnt, pnt, expectedPnt * 0.01); // Within 1%

        // Z5D result should be related to PNT but modified
        double z5d = Z5dPredictor.z5dPrime(k, -0.00247, 0.04449, 0.3, false);

        double difference = Math.abs(z5d - pnt);
        double tolerance = Math.abs(pnt * 0.1);

        System.out.printf("Z5D result: %.6f%n", z5d);
        System.out.printf("Difference from PNT: %.6f%n", difference);
        System.out.printf("Tolerance (10%%): %.6f%n", tolerance);
        System.out.printf("Within tolerance: %b%n", difference < tolerance);

        assertTrue(Math.abs(z5d - pnt) < Math.abs(pnt * 0.1)); // Within 10% of PNT
    }

    @Test
    @DisplayName("Test different scale behaviors")
    public void testScaleBehaviors() {
        System.out.println("Testing different scale behaviors");

        // Test that different scales produce reasonable results
        double[] testKs = {1000.0, 10000.0, 100000.0, 1000000.0};

        System.out.print("Test k values: [");
        for (int i = 0; i < testKs.length; i++) {
            System.out.printf("%.1f", testKs[i]);
            if (i < testKs.length - 1) System.out.print(", ");
        }
        System.out.println("]");

        for (double k : testKs) {
            double result = Z5dPredictor.z5dPrime(k, 0, 0, 0, true); // Auto-calibrate
            System.out.printf("k=%.1f: result=%.6f, finite=%b, positive=%b, >k=%b%n",
                            k, result, Double.isFinite(result), result > 0, result > k);

            assertTrue(Double.isFinite(result));
            assertTrue(result > 0);
            assertTrue(result > k); // Should be larger than k for reasonable k values
        }
    }


    @Test
    @DisplayName("Test prediction performance across scales")
    public void testPredictionPerformance() {
        System.out.println("Testing prediction performance across scales");
        System.out.println("==================================================");

        // Define scales from 10^5 to 10^18
        double[] scales = new double[14]; // 10^5 to 10^18
        for (int i = 0; i < scales.length; i++) {
            scales[i] = Math.pow(10, 5 + i);
        }

        int predictionsPerScale = 1000;
        String csvFileName = "z5d_performance_log.csv";

        // CSV header
        String csvHeader = "Timestamp,Scale,Prediction_Number,Prediction_Value,Time_ns,Time_ms,Total_Time_ns,Total_Time_ms\n";

        // Statistics collectors
        java.util.List<Double> allTimesMs = new java.util.ArrayList<>();
        java.util.Map<Double, java.util.List<Double>> scaleTimes = new java.util.HashMap<>();
        java.util.Map<Double, Double> scaleTotalTimes = new java.util.HashMap<>();

        long testStartTime = System.nanoTime();

        try (java.io.FileWriter csvWriter = new java.io.FileWriter(csvFileName)) {
            csvWriter.write(csvHeader);

            for (double scale : scales) {
                System.out.printf("\nTesting scale: %.0e (%s)%n", scale, formatScale(scale));
                System.out.println("Progress: [");

                java.util.List<Double> scaleTimeList = new java.util.ArrayList<>();
                long scaleStartTime = System.nanoTime();

                for (int i = 0; i < predictionsPerScale; i++) {
                    long predictionStart = System.nanoTime();

                    // Make prediction with auto-calibration
                    double result = Z5dPredictor.z5dPrime(scale, 0, 0, 0, true);

                    long predictionEnd = System.nanoTime();
                    long predictionTimeNs = predictionEnd - predictionStart;
                    double predictionTimeMs = predictionTimeNs / 1_000_000.0;

                    // Log to CSV
                    String timestamp = java.time.Instant.now().toString();
                    csvWriter.write(String.format("%s,%.0f,%d,%.6f,%d,%.6f,%d,%.6f%n",
                        timestamp, scale, i + 1, result, predictionTimeNs, predictionTimeMs,
                        predictionEnd - scaleStartTime, (predictionEnd - scaleStartTime) / 1_000_000.0));

                    scaleTimeList.add(predictionTimeMs);
                    allTimesMs.add(predictionTimeMs);

                    // Progress indicator
                    if ((i + 1) % 100 == 0) {
                        System.out.print("█");
                    }
                }

                long scaleEndTime = System.nanoTime();
                double scaleTotalTimeMs = (scaleEndTime - scaleStartTime) / 1_000_000.0;

                System.out.printf("] Complete%n");
                System.out.printf("Scale %.0e: %d predictions in %.2f ms%n", scale, predictionsPerScale, scaleTotalTimeMs);

                scaleTimes.put(scale, scaleTimeList);
                scaleTotalTimes.put(scale, scaleTotalTimeMs);
            }

            long testEndTime = System.nanoTime();
            double totalTestTimeMs = (testEndTime - testStartTime) / 1_000_000.0;

            // Calculate aggregate statistics
            System.out.println("\n" + "=".repeat(60));
            System.out.println("AGGREGATE PERFORMANCE STATISTICS");
            System.out.println("=".repeat(60));

            double[] allTimesArray = allTimesMs.stream().mapToDouble(Double::doubleValue).toArray();
            java.util.Arrays.sort(allTimesArray);

            double minTime = allTimesArray[0];
            double maxTime = allTimesArray[allTimesArray.length - 1];
            double meanTime = allTimesMs.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
            double medianTime = allTimesArray.length % 2 == 0 ?
                (allTimesArray[allTimesArray.length / 2 - 1] + allTimesArray[allTimesArray.length / 2]) / 2.0 :
                allTimesArray[allTimesArray.length / 2];
            double p95Time = allTimesArray[(int) (allTimesArray.length * 0.95)];
            double p99Time = allTimesArray[(int) (allTimesArray.length * 0.99)];

            System.out.printf("Total predictions: %,d%n", allTimesMs.size());
            System.out.printf("Total test time: %.2f ms%n", totalTestTimeMs);
            System.out.printf("Effective avg time per prediction (total/count): %.3f ��s%n", (totalTestTimeMs / allTimesMs.size()) * 1000);
            System.out.printf("Median individual prediction time: %.3f \u00B5s%n", medianTime * 1000);
            System.out.printf("Min individual prediction time: %.3f \u00B5s%n", minTime * 1000);
            System.out.printf("Max individual prediction time: %.3f \u00B5s%n", maxTime * 1000);
            System.out.printf("95th percentile individual time: %.3f \u00B5s%n", p95Time * 1000);
            System.out.printf("99th percentile individual time: %.3f \u00B5s%n", p99Time * 1000);
            System.out.printf("Predictions per second (effective): %.0f%n", (allTimesMs.size() / (totalTestTimeMs / 1000.0)));

            System.out.println("\nPER-SCALE BREAKDOWN:");
            System.out.println("-".repeat(60));
            System.out.printf("%-10s %-10s %-12s %-12s %-12s%n", "Scale", "Count", "Total Time", "Avg Time (ms)", "Pred/sec");
            System.out.println("-".repeat(60));

            for (double scale : scales) {
                java.util.List<Double> times = scaleTimes.get(scale);
                double totalTime = scaleTotalTimes.get(scale);
                double avgTime = totalTime / predictionsPerScale;
                double predsPerSec = predictionsPerScale / (totalTime / 1000.0);

                System.out.printf("%-10s %-10d %-12.2f %-12.4f %-12.0f%n",
                    formatScale(scale), predictionsPerScale, totalTime, avgTime, predsPerSec);
            }

            System.out.println("\n" + "=".repeat(60));
            System.out.printf("Detailed timestamped logs saved to: %s%n", csvFileName);
            System.out.println("=".repeat(60));

            csvWriter.flush();

        } catch (java.io.IOException e) {
            System.err.println("Error writing to CSV file: " + e.getMessage());
            fail("Failed to write performance log");
        }
    }

    private String formatScale(double scale) {
        int exponent = (int) Math.log10(scale);
        return String.format("10^%d", exponent);
    }

}
