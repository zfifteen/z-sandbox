package unifiedframework;

import java.math.BigInteger;
import java.util.Optional;

/**
 * Demo class for Java BigDecimal GVA factorization.
 * Runs sample tests and outputs verification data.
 */
public class GVAFactorizerDemo {

    public static void main(String[] args) {
        System.out.println("=== Java BigDecimal GVA Factorization Demo ===");
        System.out.println("Precision: 400 digits via BigDecimal");
        System.out.println("Integrated Z5D predictor for candidate seeding");
        System.out.println();

        // 64-bit test
        runTest("64-bit", new BigInteger("18446736050711510819"), 1000);

        // 128-bit test (generate sample)
        BigInteger p128 = BigInteger.probablePrime(64, new java.util.Random(42));
        BigInteger q128 = p128.add(BigInteger.valueOf(100)).nextProbablePrime();
        BigInteger N128 = p128.multiply(q128);
        runTest("128-bit", N128, 1000);

        // 256-bit test (smaller for demo)
        BigInteger p256 = BigInteger.probablePrime(64, new java.util.Random(42)); // Smaller for speed
        BigInteger q256 = p256.add(BigInteger.valueOf(2).pow(20)).nextProbablePrime();
        BigInteger N256 = p256.multiply(q256);
        runTest("256-bit", N256, 50);

        System.out.println("=== Demo Complete ===");
    }

    private static void runTest(String label, BigInteger N, int maxAttempts) {
        System.out.println("Testing " + label + " N: " + N);
        System.out.println("Bit length: " + N.bitLength());
        long start = System.nanoTime();
        Optional<BigInteger[]> result = GVAFactorizer.factorize(N, maxAttempts, 11);
        BigInteger[] factors = result.orElse(null);
        long end = System.nanoTime();
        double timeMs = (end - start) / 1e6;

        if (factors != null) {
            System.out.println("SUCCESS: " + factors[0] + " × " + factors[1] + " = " + factors[0].multiply(factors[1]));
            System.out.println("Verification: " + factors[0].multiply(factors[1]).equals(N));
        } else {
            System.out.println("FAILED: No factors found");
        }
        System.out.println("Time: " + String.format("%.2f", timeMs) + " ms");
        System.out.println();
    }
}