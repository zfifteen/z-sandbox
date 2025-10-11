import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;

/**
 * Simple example demonstrating the new BigDecimal API for ultra-high scale
 * prime counting predictions.
 * 
 * This example shows three ways to use the enhanced Z5D Predictor:
 * 1. Traditional double precision (for scales up to ~10^305)
 * 2. BigDecimal API with BigDecimal objects
 * 3. String-based convenience API (easiest for ultra-high scales)
 */
public class UltraHighScaleExample {
    
    public static void main(String[] args) {
        System.out.println("Z5D Predictor - Ultra-High Scale Examples");
        System.out.println("==========================================\n");
        
        // Example 1: Traditional double precision (backward compatible)
        example1_DoublePrecision();
        
        // Example 2: BigDecimal API
        example2_BigDecimalAPI();
        
        // Example 3: String-based convenience API (recommended for ultra-high scales)
        example3_StringAPI();
        
        // Example 4: Detailed results with extended API
        example4_ExtendedResults();
    }
    
    private static void example1_DoublePrecision() {
        System.out.println("Example 1: Traditional Double Precision");
        System.out.println("---------------------------------------");
        
        double k = 1e6; // One million
        double prediction = Z5dPredictor.z5dPrime(k, 0, 0, 0, true);
        
        System.out.printf("π(10^6) ≈ %.0f%n", prediction);
        System.out.println();
    }
    
    private static void example2_BigDecimalAPI() {
        System.out.println("Example 2: BigDecimal API");
        System.out.println("-------------------------");
        
        MathContext mc = new MathContext(100, RoundingMode.HALF_UP);
        BigDecimal k = new BigDecimal("1e500");
        
        BigDecimal prediction = Z5dPredictor.z5dPrimeBigDecimal(k, 0, 0, 0, true, mc);
        
        System.out.printf("π(10^500) ≈ %s%n", prediction.toEngineeringString());
        System.out.println();
    }
    
    private static void example3_StringAPI() {
        System.out.println("Example 3: String-Based Convenience API (Recommended)");
        System.out.println("-----------------------------------------------------");
        
        // Easy to use - just pass k as a string
        String k = "1e1233"; // Target cosmological scale
        String prediction = Z5dPredictor.z5dPrimeString(k, 0, 0, 0, true);
        
        System.out.printf("π(10^1233) ≈ %s%n", prediction);
        System.out.println();
        
        // More examples at different scales
        System.out.println("Additional scale examples:");
        String[] scales = {"1e100", "1e500", "1e1000", "1e2000"};
        for (String scale : scales) {
            String result = Z5dPredictor.z5dPrimeString(scale, 0, 0, 0, true);
            System.out.printf("  π(%s) ≈ %s%n", scale, 
                result.substring(0, Math.min(30, result.length())) + "...");
        }
        System.out.println();
    }
    
    private static void example4_ExtendedResults() {
        System.out.println("Example 4: Extended Results (Detailed Components)");
        System.out.println("-------------------------------------------------");
        
        MathContext mc = new MathContext(100, RoundingMode.HALF_UP);
        BigDecimal k = new BigDecimal("1e800");
        
        Z5dPredictor.Z5dResultBigDecimal result = new Z5dPredictor.Z5dResultBigDecimal();
        int status = Z5dPredictor.z5dPrimeExtendedBigDecimal(k, 0, 0, 0, true, result, mc);
        
        if (status == Z5dPredictor.Z5D_SUCCESS) {
            System.out.println("For k = 10^800:");
            System.out.printf("  Z5D Prediction:     %s%n", 
                result.prediction.toEngineeringString());
            System.out.printf("  PNT Baseline:       %s%n", 
                result.pntBase.toEngineeringString());
            System.out.printf("  Dilation term (d):  %s%n", 
                result.dTerm.toEngineeringString());
            System.out.printf("  Curvature term (e): %s%n", 
                result.eTerm.toEngineeringString());
            System.out.printf("  Calibration c:      %.6f%n", result.cUsed);
            System.out.printf("  Calibration k*:     %.6f%n", result.kStarUsed);
            
            // Calculate relative difference from PNT
            BigDecimal relDiff = result.prediction.subtract(result.pntBase)
                .abs().divide(result.pntBase, mc);
            System.out.printf("  Rel. diff from PNT: %.6f%%%n", relDiff.doubleValue() * 100);
        }
        System.out.println();
    }
}
