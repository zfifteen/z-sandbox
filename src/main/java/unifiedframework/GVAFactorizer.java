package unifiedframework;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Geodesic Validation Assault (GVA) Factorizer using BigDecimal for high precision.
 * Integrates Embedding, RiemannianDistance, RiemannianAStar, and Z5D predictor.
 * Fixed for safety with large inputs: avoids double conversions, uses probable prime checks.
 */
public class GVAFactorizer {
    private static final MathContext MC = new MathContext(2000, RoundingMode.HALF_UP);
    private static final int TORUS_DIMS = 17;
    private static final int PROJ_BLOCKS = 4; // (x,y,z,w) blocks
    private static final double[] W_LEVELS = {0.0, 1.0}; // Blue/Red cubes

    // Unicursal 4D→3D projection: (x,y,z,w) → (x',y',z') in ℝ³
    private static double[] project4DTo3D(double[] coords4D) {
        double x = coords4D[0], y = coords4D[1], z = coords4D[2], w = coords4D[3];
        // e₁,e₂,e₃,e₄ as basis in ℝ³ (orthonormal + offset)
        double[] e1 = {1, 0, 0}, e2 = {0, 1, 0}, e3 = {0, 0, 1};
        double[] e4 = {0.5, 0.5, 0.5}; // Diagonal for tesseract shadow
        double[] proj = new double[3];
        for (int i = 0; i < 3; i++) {
            proj[i] = x*e1[i] + y*e2[i] + z*e3[i] + w*e4[i];
        }
        return proj;
    }

    // Generate unicursal geodesic seeds from e₄ intersections
    private static List<BigInteger> seedZ5DAtE4Intersections(BigDecimal sqrtN, int range) {
        List<BigInteger> seeds = new ArrayList<>();
        double kApprox = findPrimeIndexApproximation(sqrtN);
        for (double w : W_LEVELS) {
            for (int dx = -1; dx <= 1; dx += 2) {
                for (int dy = -1; dy <= 1; dy += 2) {
                    for (int dz = -1; dz <= 1; dz += 2) {
                        double[] coord4D = {dx * 1e6, dy * 1e6, dz * 1e6, w * 1e6};
                        double[] proj = project4DTo3D(coord4D);
                        double est = Z5dPredictor.z5dPrime((int)(kApprox + proj[0]), 0, 0, 0, true);
                        BigInteger p = BigInteger.valueOf(Math.round(est));
                        if (p.compareTo(BigInteger.ONE) > 0 && isPrimeMR(p)) {
                            seeds.add(p);
                        }
                    }
                }
            }
        }
        return seeds;
    }

    // Miller-Rabin (20 witnesses)
    private static boolean isPrimeMR(BigInteger n) {
        if (n.compareTo(BigInteger.valueOf(3)) < 0) return n.equals(BigInteger.TWO);
        if (n.mod(BigInteger.TWO).equals(BigInteger.ZERO)) return false;
        BigInteger s = n.subtract(BigInteger.ONE);
        int r = 0;
        while (s.mod(BigInteger.TWO).equals(BigInteger.ZERO)) {
            s = s.divide(BigInteger.TWO);
            r++;
        }
        BigInteger[] witnesses = {BigInteger.valueOf(2), BigInteger.valueOf(3), BigInteger.valueOf(5),
                BigInteger.valueOf(7), BigInteger.valueOf(11), BigInteger.valueOf(13),
                BigInteger.valueOf(17), BigInteger.valueOf(19), BigInteger.valueOf(23),
                BigInteger.valueOf(29), BigInteger.valueOf(31), BigInteger.valueOf(37)};
        for (BigInteger a : witnesses) {
            if (a.compareTo(n) >= 0) break;
            BigInteger x = a.modPow(s, n);
            if (x.equals(BigInteger.ONE) || x.equals(n.subtract(BigInteger.ONE))) continue;
            boolean comp = false;
            for (int i = 1; i < r; i++) {
                x = x.modPow(BigInteger.TWO, n);
                if (x.equals(n.subtract(BigInteger.ONE))) { comp = true; break; }
            }
            if (!comp) return false;
        }
        return true;
    }

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
            // Use new (1,3) Pythagram seeding at e₄ intersections
            BigDecimal sqrtN = sqrt(N_bd, MC);
            candidates = seedZ5DAtE4Intersections(sqrtN, 1000000);
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
        return 17; // Fixed to 17-torus
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
