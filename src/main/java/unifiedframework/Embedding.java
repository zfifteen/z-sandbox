package unifiedframework;

import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;

/**
 * Torus geodesic embedding for GVA using BigDecimal for high precision.
 * Ports Python embed_torus_geodesic function.
 */
public class Embedding {
    private static final MathContext MC = new MathContext(2000, RoundingMode.HALF_UP);
    private static final BigDecimal PHI = BigDecimal.valueOf((1 + Math.sqrt(5)) / 2).setScale(400, RoundingMode.HALF_UP);
    private static final BigDecimal E_SQUARED = BigDecimal.valueOf(Math.exp(2)).setScale(400, RoundingMode.HALF_UP);

    /**
     * Embed N into torus using iterative θ' transformations.
     * Z = A(B / c) with c = e², plus curvature perturbation.
     */
    public static BigDecimal[] embedTorusGeodesic(BigDecimal n, BigDecimal k, int dims) {
        BigDecimal x = n.divide(E_SQUARED, MC);
        BigDecimal[] coords = new BigDecimal[dims];
        for (int i = 0; i < dims; i++) {
            BigDecimal frac = fractionalPart(x.divide(PHI, MC));
            x = PHI.multiply(frac.pow(k.intValue(), MC), MC);  // Approximate power
            BigDecimal perturbation = BigDecimal.valueOf(0.01).multiply(BigDecimal.valueOf(Math.sin(k.doubleValue() * i + n.doubleValue() * 1e-15)), MC);
            coords[i] = fractionalPart(x).add(perturbation, MC);
        }
        return coords;
    }

    /**
     * Fractional part of BigDecimal.
     */
    private static BigDecimal fractionalPart(BigDecimal x) {
        return x.subtract(new BigDecimal(x.toBigInteger())).setScale(400, RoundingMode.HALF_UP);
    }

    /**
     * Adaptive k for scaling: 0.3 / log2(log2(N+1)), boosted with Pythagram w-weight
     */
    public static BigDecimal adaptiveK(BigDecimal n, double w) {
        BigDecimal logLogN = log2(log2(n.add(BigDecimal.ONE, MC), MC), MC);
        BigDecimal k0 = BigDecimal.valueOf(0.3).divide(logLogN, MC);
        return k0.multiply(BigDecimal.valueOf(1 + 0.1 * w), MC);
    }

    /**
     * Adaptive k for scaling: 0.3 / log2(log2(N+1)) (legacy)
     */
    public static BigDecimal adaptiveK(BigDecimal n) {
        return adaptiveK(n, 0.0);
    }

    /**
     * Log base 2 of BigDecimal.
     */
    private static BigDecimal log2(BigDecimal x, MathContext mc) {
        return BigDecimal.valueOf(Math.log(x.doubleValue()) / Math.log(2)).setScale(400, RoundingMode.HALF_UP);
    }
}