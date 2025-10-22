package unifiedframework;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.*;

/**
 * Empirical validation experiments for GVA factorization approach.
 * Tests distance correlation, scaling behavior, efficiency, and dimensionality effects.
 */
public class GVAExperiments {
    private static final MathContext MC = new MathContext(1000, RoundingMode.HALF_UP);
    private static final Random RNG = new Random(42);

    public static void main(String[] args) {
        System.out.println("=== GVA EMPIRICAL VALIDATION ===\n");

        System.out.println("Experiment 1: Distance Correlation");
        measureDistanceCorrelation();

        System.out.println("\nExperiment 2: Scaling Behavior");
        measureScaling();

        System.out.println("\nExperiment 3: Candidate Efficiency");
        measureCandidateEfficiency();

        System.out.println("\nExperiment 4: Dimensionality Effect");
        measureDimensionalityEffect();

        System.out.println("\nExperiment 5: Known Challenge Cases");
        testKnownSemiprimes();

        System.out.println("\nExperiment 6: 256-bit Semiprime Factorization");
        test256BitSemiprimes();
    }

    /**
     * Experiment 1: Distance Correlation Test
     * Measures if factors are geometrically closer than non-factors in embedding space.
     */
    public static void measureDistanceCorrelation() {
        List<Double> factorDistances = new ArrayList<>();
        List<Double> nonFactorDistances = new ArrayList<>();

        for (int trial = 0; trial < 1; trial++) {
            // Generate 32-bit balanced semiprime
            BigInteger p = BigInteger.probablePrime(32, RNG);
            BigInteger q = BigInteger.probablePrime(32, RNG);
            BigInteger N = p.multiply(q);

            // Embed
            BigDecimal k = Embedding.adaptiveK(new BigDecimal(N));
            BigDecimal[] emb_N = Embedding.embedTorusGeodesic(new BigDecimal(N), k, 7);
            BigDecimal[] emb_p = Embedding.embedTorusGeodesic(new BigDecimal(p), k, 7);

            if (trial == 0) {
                System.out.printf("N=%s, p=%s, k=%.6f\n", N, p, k.doubleValue());
                System.out.printf("emb_N[0]: %s\n", emb_N[0].toString().substring(0,50));
                System.out.printf("emb_p[0]: %s\n", emb_p[0].toString().substring(0,50));
            }

            // TRUE FACTOR distance
            BigDecimal dist_factor = RiemannianDistance.calculate(emb_N, emb_p, new BigDecimal(N));
            factorDistances.add(dist_factor.doubleValue());

            if (trial == 0) {
                System.out.printf("factor distance: %.10f\n", dist_factor.doubleValue());
            }

            // NON-FACTOR distances (10 random primes near p)
            for (int i = 0; i < 10; i++) {
                BigInteger nonFactor = BigInteger.probablePrime(32, RNG);
                BigDecimal[] emb_nf = Embedding.embedTorusGeodesic(new BigDecimal(nonFactor), k, 7);
                BigDecimal dist_nonfactor = RiemannianDistance.calculate(emb_N, emb_nf, new BigDecimal(N));
                nonFactorDistances.add(dist_nonfactor.doubleValue());
            }
        }

        // ANALYSIS
        double factorMean = factorDistances.stream().mapToDouble(d -> d).average().orElse(0);
        double nonFactorMean = nonFactorDistances.stream().mapToDouble(d -> d).average().orElse(0);

        System.out.printf("Factor distances: mean=%.6f, min=%.6f, max=%.6f\n",
            factorMean,
            factorDistances.stream().mapToDouble(d -> d).min().orElse(0),
            factorDistances.stream().mapToDouble(d -> d).max().orElse(0));

        System.out.printf("Non-factor distances: mean=%.6f, min=%.6f, max=%.6f\n",
            nonFactorMean,
            nonFactorDistances.stream().mapToDouble(d -> d).min().orElse(0),
            nonFactorDistances.stream().mapToDouble(d -> d).max().orElse(0));

        // SIGNAL: If factorMean << nonFactorMean, there's something here
        double separationRatio = nonFactorMean / factorMean;
        System.out.printf("Separation ratio: %.2fx\n", separationRatio);
    }

    /**
     * Experiment 2: Scaling Behavior
     * Tests if signal persists as N grows larger.
     */
    public static void measureScaling() {
        int[] bitSizes = {32, 48, 64};

        for (int bits : bitSizes) {
            double totalSeparation = 0;
            int trials = 20;

            for (int t = 0; t < trials; t++) {
                BigInteger p = BigInteger.probablePrime(bits/2, RNG);
                BigInteger q = BigInteger.probablePrime(bits/2, RNG);
                BigInteger N = p.multiply(q);

                // Measure separation at this scale
                BigDecimal k = Embedding.adaptiveK(new BigDecimal(N));
                BigDecimal[] emb_N = Embedding.embedTorusGeodesic(new BigDecimal(N), k, 7);
                BigDecimal[] emb_p = Embedding.embedTorusGeodesic(new BigDecimal(p), k, 7);

                BigDecimal factorDist = RiemannianDistance.calculate(emb_N, emb_p, new BigDecimal(N));

                // Average non-factor distance
                double nonFactorSum = 0;
                for (int i = 0; i < 5; i++) {
                    BigInteger nonFactor = BigInteger.probablePrime(bits/2, RNG);
                    BigDecimal[] emb_nf = Embedding.embedTorusGeodesic(new BigDecimal(nonFactor), k, 7);
                    BigDecimal dist = RiemannianDistance.calculate(emb_N, emb_nf, new BigDecimal(N));
                    nonFactorSum += dist.doubleValue();
                }
                double avgNonFactor = nonFactorSum / 5;

                double ratio = avgNonFactor / factorDist.doubleValue();
                totalSeparation += ratio;
            }

            double avgSeparation = totalSeparation / trials;
            System.out.printf("%d-bit: separation = %.2fx\n", bits, avgSeparation);
        }
    }

    /**
     * Experiment 3: Candidate Efficiency
     * Compares GVA factorization speed vs brute force trial division.
     */
    public static void measureCandidateEfficiency() {
        for (int trial = 0; trial < 10; trial++) {  // Reduced trials for speed
            BigInteger p = BigInteger.probablePrime(24, RNG);  // Smaller for brute force
            BigInteger q = BigInteger.probablePrime(24, RNG);
            BigInteger N = p.multiply(q);

            // GVA approach
            long startGVA = System.nanoTime();
            Optional<BigInteger[]> resultGVA = GVAFactorizer.factorize(N, 1000);
            long timeGVA = System.nanoTime() - startGVA;

            // Brute force baseline (trial division from sqrt(N) down)
            long startBrute = System.nanoTime();
            BigInteger sqrtN = sqrt(new BigDecimal(N)).toBigInteger();
            BigInteger found = null;
            for (BigInteger test = sqrtN; test.compareTo(BigInteger.TWO) > 0; test = test.subtract(BigInteger.ONE)) {
                if (N.mod(test).equals(BigInteger.ZERO)) {
                    found = test;
                    break;
                }
            }
            long timeBrute = System.nanoTime() - startBrute;

            boolean gvaSuccess = resultGVA.isPresent();
            double speedup = gvaSuccess ? (double)timeBrute / timeGVA : 0;

            System.out.printf("Trial %d: GVA=%dms (success=%s), Brute=%dms, Speedup=%.2fx\n",
                trial, timeGVA/1_000_000, gvaSuccess, timeBrute/1_000_000, speedup);
        }
    }

    /**
     * Experiment 4: Embedding Dimensionality
     * Tests effect of different embedding dimensions on factorization success.
     */
    public static void measureDimensionalityEffect() {
        int[] dimOptions = {3, 5, 7, 9, 11};

        // Fixed test case
        BigInteger p = BigInteger.probablePrime(20, RNG);
        BigInteger q = BigInteger.probablePrime(20, RNG);
        BigInteger N = p.multiply(q);

        for (int dims : dimOptions) {
            int successes = 0;
            double totalSeparation = 0;
            int trials = 10;

            for (int t = 0; t < trials; t++) {
                BigDecimal k = Embedding.adaptiveK(new BigDecimal(N));
                BigDecimal[] emb_N = Embedding.embedTorusGeodesic(new BigDecimal(N), k, dims);
                BigDecimal[] emb_p = Embedding.embedTorusGeodesic(new BigDecimal(p), k, dims);

                BigDecimal factorDist = RiemannianDistance.calculate(emb_N, emb_p, new BigDecimal(N));

                // Non-factor distances
                double nonFactorSum = 0;
                for (int i = 0; i < 3; i++) {
                    BigInteger nonFactor = BigInteger.probablePrime(20, RNG);
                    BigDecimal[] emb_nf = Embedding.embedTorusGeodesic(new BigDecimal(nonFactor), k, dims);
                    BigDecimal dist = RiemannianDistance.calculate(emb_N, emb_nf, new BigDecimal(N));
                    nonFactorSum += dist.doubleValue();
                }
                double avgNonFactor = nonFactorSum / 3;
                double ratio = avgNonFactor / factorDist.doubleValue();
                totalSeparation += ratio;

                // Try factorization
                Optional<BigInteger[]> result = GVAFactorizer.factorize(N, 100);
                if (result.isPresent()) successes++;
            }

            double successRate = (double)successes / trials * 100;
            double avgSeparation = totalSeparation / trials;
            System.out.printf("%d dims: success=%.1f%%, separation=%.2fx\n",
                dims, successRate, avgSeparation);
        }
    }

    /**
     * Experiment 5: Known Challenge Cases
     * Tests on known small semiprimes.
     */
    private static void testKnownSemiprimes() {
        String[] challenges = {
            "15",    // 3 × 5
            "21",    // 3 × 7
            "33",    // 3 × 11
            "143",   // 11 × 13
            "1147",  // 31 × 37
            "46441"  // 211 × 220
        };

        for (String nStr : challenges) {
            BigInteger N = new BigInteger(nStr);
            long start = System.nanoTime();
            Optional<BigInteger[]> result = GVAFactorizer.factorize(N, 10000);
            long elapsed = (System.nanoTime() - start) / 1_000_000;

            if (result.isPresent()) {
                BigInteger[] factors = result.get();
                System.out.printf("%s = %s × %s (%dms)\n",
                    nStr, factors[0], factors[1], elapsed);
            } else {
                System.out.printf("%s = FAILED (%dms)\n", nStr, elapsed);
            }
        }
    }

    /**
    /**
     * Experiment 6: 256-bit Semiprime Factorization
     * Tests the refined Z5D seeding on large 256-bit balanced semiprimes.
     */
    private static void test256BitSemiprimes() {
        int trials = 5; // Adjust for time
        int successes = 0;
        long totalTime = 0;

        for (int t = 0; t < trials; t++) {
            // Generate 128-bit primes for 256-bit product
            BigInteger p = BigInteger.probablePrime(128, RNG);
            BigInteger q = BigInteger.probablePrime(128, RNG);
            BigInteger N = p.multiply(q);

            System.out.printf("Trial %d: N has %d bits\n", t+1, N.bitLength());

            long start = System.nanoTime();
            Optional<BigInteger[]> result = GVAFactorizer.factorize(N, 10000); // Increased attempts
            long elapsed = (System.nanoTime() - start) / 1_000_000; // ms
            totalTime += elapsed;

            if (result.isPresent()) {
                BigInteger[] factors = result.get();
                System.out.printf("SUCCESS: %s × %s (%dms)\n", factors[0], factors[1], elapsed);
                successes++;
            } else {
                System.out.printf("FAILED (%dms)\n", elapsed);
            }
        }

        double successRate = (double) successes / trials * 100;
        double avgTime = (double) totalTime / trials / 1000; // seconds
        System.out.printf("\n256-bit Results: %.1f%% success, %.2fs average time\n", successRate, avgTime);
    }
    /** Square root for BigDecimal.
     */
    private static BigDecimal sqrt(BigDecimal x) {
        return BigDecimal.valueOf(Math.sqrt(x.doubleValue()));
    }
}
