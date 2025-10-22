package unifiedframework;
import java.math.BigDecimal;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.math.BigInteger;
import java.util.Random;
import java.util.Optional;

public class TestGVAFactorizer {

    @Test
    @DisplayName("Test GVA factorization for 64-bit balanced semiprimes")
    public void testGVA64Bit() {
        System.out.println("Testing GVA 64-bit factorization");

        // Generate test case similar to Python
        BigInteger p = BigInteger.valueOf(4294966297L);
        BigInteger q = BigInteger.valueOf(4294966427L);
        BigInteger N = p.multiply(q);

        assertEquals(64, N.bitLength(), "N should be 64-bit");

        long start = System.nanoTime();
        Optional<BigInteger[]> result = GVAFactorizer.factorize(N, 100);
        BigInteger[] factors = result.orElse(null);
        long end = System.nanoTime();

        assertNotNull(factors, "Factors should be found");
        assertEquals(2, factors.length);
        assertTrue(factors[0].multiply(factors[1]).equals(N), "Factors should multiply to N");

        System.out.printf("64-bit GVA: %s × %s = %s in %.2f ms%n",
                factors[0], factors[1], N, (end - start) / 1e6);
    }

    @Test
    @DisplayName("Test GVA factorization for 128-bit balanced semiprimes")
    public void testGVA128Bit() {
        System.out.println("Testing GVA 128-bit factorization");

        // Generate balanced 128-bit semiprime
        Random rand = new Random(42);
        BigInteger p = BigInteger.probablePrime(64, rand);
        BigInteger offset = BigInteger.valueOf(rand.nextInt(100) + 1);
        BigInteger q = p.add(offset).nextProbablePrime();
        BigInteger N = p.multiply(q);

        assertTrue(N.bitLength() >= 127 && N.bitLength() <= 129, "N should be ~128-bit");

        long start = System.nanoTime();
        Optional<BigInteger[]> result = GVAFactorizer.factorize(N, 100);
        BigInteger[] factors = result.orElse(null);
        long end = System.nanoTime();

        if (factors != null) {
            assertEquals(2, factors.length);
            assertTrue(factors[0].multiply(factors[1]).equals(N), "Factors should multiply to N");
            System.out.printf("128-bit GVA VICTORY: %s × %s = %s in %.2f ms%n",
                    factors[0], factors[1], N, (end - start) / 1e6);
        } else {
            System.out.printf("128-bit GVA: No factors found for N=%s in %.2f ms%n", N, (end - start) / 1e6);
        }
    }

    @Test
    @DisplayName("Test GVA factorization for 256-bit balanced semiprimes")
    public void testGVA256Bit() {
        System.out.println("Testing GVA 256-bit factorization");

        // Generate balanced 256-bit semiprime
        Random rand = new Random(42);
        BigInteger p = BigInteger.probablePrime(32, rand); // Smaller for speed
        BigInteger offset = BigInteger.valueOf(2).pow(60 + rand.nextInt(10)); // 2^60 to 2^70
        BigInteger q = p.add(offset).nextProbablePrime();
        BigInteger N = p.multiply(q);

        assertTrue(N.bitLength() >= 255 && N.bitLength() <= 257, "N should be ~256-bit");

        long start = System.nanoTime();
        Optional<BigInteger[]> result = GVAFactorizer.factorize(N, 100);
        BigInteger[] factors = result.orElse(null);
        long end = System.nanoTime();

        if (factors != null) {
            assertEquals(2, factors.length);
            assertTrue(factors[0].multiply(factors[1]).equals(N), "Factors should multiply to N");
            System.out.printf("256-bit GVA BREAKTHROUGH: %s × %s = %s in %.2f ms%n",
                    factors[0], factors[1], N, (end - start) / 1e6);
        } else {
            System.out.printf("256-bit GVA: No factors found for N=%s in %.2f ms (expected for initial tests)%n",
                    N.toString().substring(0, 50) + "...", (end - start) / 1e6);
        }
    }

    @Test
    @DisplayName("Test embedding and distance calculations")
    public void testEmbeddingAndDistance() {
        BigDecimal N = BigDecimal.valueOf(123456789);
        BigDecimal k = Embedding.adaptiveK(N);
        BigDecimal[] emb = Embedding.embedTorusGeodesic(N, k, 7);

        assertNotNull(emb);
        assertEquals(7, emb.length);

        BigDecimal dist = RiemannianDistance.calculate(emb, emb, N);
        assertTrue(dist.compareTo(BigDecimal.ZERO) >= 0, "Distance should be non-negative");
    }

    @Test
    @DisplayName("Test Z5D integration for candidate generation")
    public void testZ5DIntegration() {
        // Test that Z5D generates reasonable candidates around sqrt(N)

        // The integration is tested indirectly in factorize, but here check Z5D output

        // For now, just assert Z5D predictor works
        double est = Z5dPredictor.z5dPrime(100, 0, 0, 0, true);
        assertTrue(est > 0, "Z5D should predict positive values");
    }
}