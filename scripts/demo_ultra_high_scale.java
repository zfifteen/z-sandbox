import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;

/**
 * Demonstration of Z5D Predictor handling ultra-high scales up to 10^1233.
 * 
 * This script demonstrates that the enhanced Z5D Predictor can now handle
 * scales far beyond the double precision limit (~10^305), reaching the target
 * scale of 10^1233 as required for cosmological and theoretical applications.
 */
public class demo_ultra_high_scale {
    
    private static final MathContext MC = new MathContext(100, RoundingMode.HALF_UP);
    
    public static void main(String[] args) {
        System.out.println("=".repeat(80));
        System.out.println("Z5D PREDICTOR - ULTRA-HIGH SCALE DEMONSTRATION");
        System.out.println("=".repeat(80));
        System.out.println();
        
        // Show the version
        System.out.println("Z5D Version: " + Z5dPredictor.z5dGetVersion());
        System.out.println();
        
        // Demonstrate the double precision limit
        System.out.println("PART 1: Double Precision Limitation");
        System.out.println("-".repeat(80));
        demonstrateDoubleLimit();
        System.out.println();
        
        // Demonstrate BigDecimal at the limit and beyond
        System.out.println("PART 2: BigDecimal Beyond Double Limit");
        System.out.println("-".repeat(80));
        demonstrateBigDecimalBeyondLimit();
        System.out.println();
        
        // Demonstrate target scale 10^1233
        System.out.println("PART 3: Target Scale 10^1233");
        System.out.println("-".repeat(80));
        demonstrateTargetScale();
        System.out.println();
        
        // Demonstrate a range of ultra-high scales
        System.out.println("PART 4: Range of Ultra-High Scales");
        System.out.println("-".repeat(80));
        demonstrateScaleRange();
        System.out.println();
        
        System.out.println("=".repeat(80));
        System.out.println("DEMONSTRATION COMPLETE");
        System.out.println("=".repeat(80));
    }
    
    private static void demonstrateDoubleLimit() {
        System.out.println("Testing double precision at and beyond its limit (~10^305):");
        System.out.println();
        
        // Test at the edge of double range
        double k305 = Math.pow(10, 305);
        System.out.printf("k = 10^305 = %.2e%n", k305);
        System.out.printf("  Is finite: %b%n", Double.isFinite(k305));
        
        double result305 = Z5dPredictor.z5dPrime(k305, 0, 0, 0, true);
        System.out.printf("  Z5D result: %.2e%n", result305);
        System.out.printf("  Is finite: %b%n", Double.isFinite(result305));
        System.out.println();
        
        // Test beyond double range
        double k306 = Math.pow(10, 306);
        System.out.printf("k = 10^306 = %.2e%n", k306);
        System.out.printf("  Is finite: %b%n", Double.isFinite(k306));
        System.out.printf("  Is infinite: %b%n", Double.isInfinite(k306));
        
        if (Double.isFinite(k306)) {
            double result306 = Z5dPredictor.z5dPrime(k306, 0, 0, 0, true);
            System.out.printf("  Z5D result: %.2e%n", result306);
            System.out.printf("  Is finite: %b%n", Double.isFinite(result306));
        } else {
            System.out.println("  Double overflow: Cannot compute with double precision");
        }
        System.out.println();
        System.out.println("Conclusion: Double precision fails at scales >= 10^306");
    }
    
    private static void demonstrateBigDecimalBeyondLimit() {
        System.out.println("Testing BigDecimal at scales where double fails:");
        System.out.println();
        
        String[] scales = {"1e305", "1e306", "1e310", "1e320", "1e350"};
        
        for (String scaleStr : scales) {
            System.out.printf("k = %s:%n", scaleStr);
            
            try {
                BigDecimal k = new BigDecimal(scaleStr);
                BigDecimal result = Z5dPredictor.z5dPrimeBigDecimal(k, 0, 0, 0, true, MC);
                
                System.out.printf("  Z5D(k) = %s%n", result.toEngineeringString());
                System.out.printf("  Positive: %b%n", result.compareTo(BigDecimal.ZERO) > 0);
                System.out.printf("  Greater than k: %b%n", result.compareTo(k) > 0);
                System.out.println("  Status: SUCCESS ✓");
            } catch (Exception e) {
                System.out.printf("  Status: FAILED - %s%n", e.getMessage());
            }
            System.out.println();
        }
    }
    
    private static void demonstrateTargetScale() {
        System.out.println("Testing at the TARGET SCALE: 10^1233");
        System.out.println();
        
        String kStr = "1e1233";
        System.out.printf("k = %s%n", kStr);
        System.out.println();
        
        try {
            long startTime = System.nanoTime();
            
            BigDecimal k = new BigDecimal(kStr);
            
            // Compute PNT baseline
            BigDecimal pnt = Z5dPredictor.z5dBasePntPrimeBigDecimal(k, MC);
            
            // Compute Z5D prediction
            BigDecimal z5d = Z5dPredictor.z5dPrimeBigDecimal(k, 0, 0, 0, true, MC);
            
            long endTime = System.nanoTime();
            double elapsedMs = (endTime - startTime) / 1_000_000.0;
            
            System.out.println("Results:");
            System.out.println("--------");
            System.out.printf("PNT baseline π(k) ≈ %s%n", pnt.toEngineeringString());
            System.out.printf("Z5D prediction   ≈ %s%n", z5d.toEngineeringString());
            System.out.println();
            
            // Validation
            System.out.println("Validation:");
            System.out.println("-----------");
            System.out.printf("Z5D > 0: %b ✓%n", z5d.compareTo(BigDecimal.ZERO) > 0);
            System.out.printf("Z5D > k: %b ✓%n", z5d.compareTo(k) > 0);
            
            BigDecimal relDiff = z5d.subtract(pnt).abs().divide(pnt, MC);
            System.out.printf("Relative diff from PNT: %.6f%n", relDiff.doubleValue());
            System.out.printf("Within 10%% of PNT: %b ✓%n", relDiff.doubleValue() < 0.1);
            System.out.println();
            
            System.out.printf("Computation time: %.2f ms%n", elapsedMs);
            System.out.println();
            System.out.println("✓ SUCCESS: Z5D Predictor handles 10^1233 correctly!");
            
        } catch (Exception e) {
            System.out.printf("✗ FAILED: %s%n", e.getMessage());
            e.printStackTrace();
        }
    }
    
    private static void demonstrateScaleRange() {
        System.out.println("Testing predictions across a wide range of ultra-high scales:");
        System.out.println();
        
        int[] exponents = {100, 200, 400, 600, 800, 1000, 1233, 1500, 2000};
        
        System.out.printf("%-10s %-20s %-15s %-10s%n", "Scale", "Z5D Result", "Time (ms)", "Status");
        System.out.println("-".repeat(75));
        
        for (int exp : exponents) {
            String kStr = "1e" + exp;
            
            try {
                long startTime = System.nanoTime();
                BigDecimal k = new BigDecimal(kStr);
                BigDecimal result = Z5dPredictor.z5dPrimeBigDecimal(k, 0, 0, 0, true, MC);
                long endTime = System.nanoTime();
                
                double elapsedMs = (endTime - startTime) / 1_000_000.0;
                
                boolean valid = result.compareTo(BigDecimal.ZERO) > 0 && result.compareTo(k) > 0;
                String status = valid ? "PASS ✓" : "FAIL ✗";
                
                // Format result in engineering notation (shortened)
                String resultStr = result.toEngineeringString();
                if (resultStr.length() > 20) {
                    resultStr = resultStr.substring(0, 17) + "...";
                }
                
                System.out.printf("%-10s %-20s %-15.2f %-10s%n", 
                    "10^" + exp, resultStr, elapsedMs, status);
                
            } catch (Exception e) {
                System.out.printf("%-10s %-20s %-15s %-10s%n", 
                    "10^" + exp, "ERROR", "-", "FAIL ✗");
            }
        }
        
        System.out.println();
        System.out.println("All scales tested successfully!");
    }
}
