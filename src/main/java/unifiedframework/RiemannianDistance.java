package unifiedframework;

import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;

/**
 * Riemannian distance on torus with domain-specific curvature using BigDecimal.
 * Ports Python riemannian_distance function.
 */
public class RiemannianDistance {
    private static final MathContext MC = new MathContext(400, RoundingMode.HALF_UP);
    private static final BigDecimal E_SQUARED = BigDecimal.valueOf(Math.exp(2)).setScale(400, RoundingMode.HALF_UP);

    /**
     * Calculate Riemannian distance between two coordinate arrays.
     * κ(n) = 4 · ln(n+1) / e²
     */
    public static BigDecimal calculate(BigDecimal[] coords1, BigDecimal[] coords2, BigDecimal N) {
        if (coords1.length != coords2.length) {
            throw new IllegalArgumentException("Coordinate arrays must be same length");
        }

        BigDecimal kappa = BigDecimal.valueOf(4).multiply(log(N.add(BigDecimal.ONE, MC), MC), MC).divide(E_SQUARED, MC);

        BigDecimal total = BigDecimal.ZERO;
        for (int i = 0; i < coords1.length; i++) {
            BigDecimal diff = coords1[i].subtract(coords2[i], MC).abs();
            BigDecimal circDist = diff.min(BigDecimal.ONE.subtract(diff, MC));
            BigDecimal warpedDist = circDist.multiply(BigDecimal.ONE.add(kappa.multiply(circDist, MC), MC), MC);
            total = total.add(warpedDist.pow(2, MC), MC);
        }
        return sqrt(total, MC);
    }

    /**
     * Adaptive threshold ε = 0.2 / (1 + κ)
     */
    public static BigDecimal adaptiveThreshold(BigDecimal N) {
        BigDecimal kappa = BigDecimal.valueOf(4).multiply(log(N.add(BigDecimal.ONE, MC), MC), MC).divide(E_SQUARED, MC);
        return BigDecimal.valueOf(0.2).divide(BigDecimal.ONE.add(kappa, MC), MC);
    }

    /**
     * Natural log of BigDecimal.
     */
    private static BigDecimal log(BigDecimal x, MathContext mc) {
        return BigDecimal.valueOf(Math.log(x.doubleValue())).setScale(400, RoundingMode.HALF_UP);
    }

    /**
     * Square root of BigDecimal.
     */
    private static BigDecimal sqrt(BigDecimal x, MathContext mc) {
        return BigDecimal.valueOf(Math.sqrt(x.doubleValue())).setScale(400, RoundingMode.HALF_UP);
    }
}