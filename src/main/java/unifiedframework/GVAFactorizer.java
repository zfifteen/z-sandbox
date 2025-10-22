package unifiedframework;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.List;
import java.util.Optional;

/**
 * Geodesic Validation Assault (GVA) Factorizer using BigDecimal for high precision.
 * Integrates Embedding, RiemannianDistance, RiemannianAStar, and Z5D predictor.
 * Fixed for safety with large inputs: avoids double conversions, uses probable prime checks.
 */
public class GVAFactorizer {
    private static final MathContext MC = new MathContext(1000, RoundingMode.HALF_UP);


    /**
     * Factorize balanced semiprime N using GVA.
     * Returns Optional containing factors if found.
     */
    public static Optional<BigInteger[]> factorize(BigInteger N, int maxAttempts) {
        if (N == null || N.compareTo(BigInteger.ONE) <= 0) return Optional.empty();
        BigDecimal N_bd = new BigDecimal(N);
        int dims = getDimsForBitSize(N.bitLength());

        // Embed N
        BigDecimal k = Embedding.adaptiveK(N_bd);
        BigDecimal[] emb_N = Embedding.embedTorusGeodesic(N_bd, k, dims);

        List<BigInteger> candidates;
        if (N.bitLength() < 100) {
            // For smaller N, use brute force around sqrt(N) with safe limits
            BigDecimal sqrtN = sqrt(N_bd, MC);
            BigInteger start = sqrtN.toBigInteger().subtract(BigInteger.valueOf(1000));
            if (start.compareTo(BigInteger.TWO) < 0) start = BigInteger.TWO;
            BigInteger end = start.add(BigInteger.valueOf(2000));
            candidates = new java.util.ArrayList<>();
            for (BigInteger candidate = start; candidate.compareTo(end) <= 0; candidate = candidate.add(BigInteger.ONE)) {
                if (isPrime(candidate)) {
                    candidates.add(candidate);
                }
            }
        } else {
            // Use Z5D to estimate prime index near sqrt(N)
            BigDecimal sqrtN = sqrt(N_bd, MC);
            double kApprox = findPrimeIndexApproximation(sqrtN);
            // Generate candidate primes using Z5D predictions around kApprox
            candidates = generateCandidatesWithZ5D(kApprox, 1000); // +/- 100000 around estimate
        }


        BigDecimal epsilon = RiemannianDistance.adaptiveThreshold(N_bd);

        for (BigInteger p : candidates) {
            if (p.compareTo(BigInteger.ONE) <= 0 || p.compareTo(N) >= 0) continue;
            if (!N.mod(p).equals(BigInteger.ZERO)) continue;
            BigInteger q = N.divide(p);
            if (!isPrime(q)) continue;

            // Check balance
            if (!isBalanced(p, q)) continue;

            // Embed factors and check distance
            BigDecimal[] emb_p = Embedding.embedTorusGeodesic(new BigDecimal(p), k, dims);
            BigDecimal[] emb_q = Embedding.embedTorusGeodesic(new BigDecimal(q), k, dims);
            BigDecimal dist_p = RiemannianDistance.calculate(emb_N, emb_p, N_bd);
            BigDecimal dist_q = RiemannianDistance.calculate(emb_N, emb_q, N_bd);
            BigDecimal minDist = dist_p.min(dist_q);

            if (minDist.compareTo(epsilon) < 0) {
                return Optional.of(new BigInteger[]{p, q});
            }

            // Optional: Try A* to find path to factor embedding
            List<BigDecimal[]> path = RiemannianAStar.findPath(emb_N, emb_p, N_bd, 10000);
            if (path != null && path.size() > 1) {
                // Inverse embedding would be needed here, but simplified
            }
        }

        return Optional.empty(); // No factors found
    }

    /**
     * Estimate prime index k where p(k) ≈ value.
     * Uses BigDecimal for large values to avoid double overflow.
     */
    private static double findPrimeIndexApproximation(BigDecimal value) {
        if (value.compareTo(BigDecimal.valueOf(Double.MAX_VALUE)) < 0) {
            double v = value.doubleValue();
            return v / Math.log(v);
        } else {
            // For astronomically large values fallback to bitLength-based approximation
            int bits = value.toBigInteger().bitLength();
            double denom = (bits - 1) * Math.log(2);
            return Math.pow(2.0, bits - 1) / denom;
        }
    }

    /**
     * Generate candidate primes around prime index k using Z5D.
     * Protected from double/long overflow and large loops.
     */
    private static List<BigInteger> generateCandidatesWithZ5D(double k, int range) {
        List<BigInteger> candidates = new java.util.ArrayList<>();
        int start = Math.max(2, (int) Math.max(2, Math.floor(k - range)));
        int end = (int) Math.ceil(k + range);
        for (int i = start; i <= end; i++) {
            double est = Z5dPredictor.z5dPrime(i, 0, 0, 0, true);
            if (!Double.isFinite(est) || est <= 2) continue;
            BigInteger candidate = BigInteger.valueOf((long) Math.round(est));
            if (candidate.bitLength() > 62) continue; // avoid bad casts
            if (isPrime(candidate)) candidates.add(candidate);
        }
        return candidates;
    }

    /**
     * Check if p and q are balanced: |log2(p/q)| ≤ 1
     * Uses bitLength for safety on large inputs.
     */
    private static boolean isBalanced(BigInteger p, BigInteger q) {
        int bitDiff = Math.abs(p.bitLength() - q.bitLength());
        if (bitDiff > 1) return false;
        // For bitDiff 0 or 1, refine by checking p <= 2*q and q <= 2*p
        return (p.compareTo(q.shiftLeft(1)) <= 0) && (q.compareTo(p.shiftLeft(1)) <= 0);
    }

    /**
     * Probable primality check using BigInteger.isProbablePrime.
     */
    private static boolean isPrime(BigInteger n) {
        if (n == null) return false;
        return n.isProbablePrime(50); // 2^-50 error probability
    }

    /**
     * Get dimensions for embedding based on bit size.
     */
    private static int getDimsForBitSize(int bits) {
        if (bits <= 64) return 7;
        if (bits <= 128) return 9;
        return 15; // For 256-bit+
    }

    /**
     * Square root for BigDecimal using Newton's method with relative tolerance.
     */
    private static BigDecimal sqrt(BigDecimal x, MathContext mc) {
        if (x.signum() < 0) throw new ArithmeticException("sqrt of negative");
        if (x.signum() == 0) return BigDecimal.ZERO;
        int precision = mc.getPrecision();
        BigDecimal two = BigDecimal.valueOf(2);
        BigDecimal guess = BigDecimal.ONE.movePointRight((x.precision() + x.scale()) / 2);
        MathContext mcIter = new MathContext(Math.max(precision + 10, 50), mc.getRoundingMode());
        BigDecimal prev;
        do {
            prev = guess;
            guess = prev.add(x.divide(prev, mcIter)).divide(two, mcIter);
        } while (prev.subtract(guess).abs().compareTo(BigDecimal.ONE.movePointLeft(precision)) > 0);
        return guess.round(mc);
    }
}
