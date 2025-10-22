package unifiedframework;

import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;

/**
 * Torus geodesic embedding for GVA using BigDecimal for high precision.
 * Ports Python embed_torus_geodesic function.
 */
public class Embedding {
    private static final MathContext MC = new MathContext(400, RoundingMode.HALF_UP);
    private static final BigDecimal PHI = BigDecimal.valueOf((1 + Math.sqrt(5)) / 2).setScale(400, RoundingMode.HALF_UP);
    private static final BigDecimal E_SQUARED = BigDecimal.valueOf(Math.exp(2)).setScale(400, RoundingMode.HALF_UP);

    /**
     * Embed N into torus using iterative θ' transformations.
     * Z = A(B / c) with c = e²
     */
    public static BigDecimal[] embedTorusGeodesic(BigDecimal n, BigDecimal k, int dims) {
        BigDecimal x = n.divide(E_SQUARED, MC);
        BigDecimal[] coords = new BigDecimal[dims];
        for (int i = 0; i < dims; i++) {
            BigDecimal frac = fractionalPart(x.divide(PHI, MC));
            x = PHI.multiply(frac.pow(k.intValue(), MC), MC);  // Approximate power
            coords[i] = fractionalPart(x);
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
     * Adaptive k for scaling: 0.3 / log2(log2(N+1))
     */
    public static BigDecimal adaptiveK(BigDecimal n) {
        BigDecimal logLogN = log2(log2(n.add(BigDecimal.ONE, MC), MC), MC);
        return BigDecimal.valueOf(0.3).divide(logLogN, MC);
    }

    /**
     * Log base 2 of BigDecimal.
     */
    private static BigDecimal log2(BigDecimal x, MathContext mc) {
        return BigDecimal.valueOf(Math.log(x.doubleValue()) / Math.log(2)).setScale(400, RoundingMode.HALF_UP);
    }
}