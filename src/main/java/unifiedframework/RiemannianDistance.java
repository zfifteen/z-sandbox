package unifiedframework;

import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;

/**
 * Riemannian distance on torus with domain-specific curvature using BigDecimal.
 * Ports Python riemannian_distance function.
 */
public class RiemannianDistance {
    private static final MathContext MC = new MathContext(2000, RoundingMode.HALF_UP);
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
     * Square root of BigDecimal using Newton's method.
     */
    private static BigDecimal sqrt(BigDecimal x, MathContext mc) {
        if (x.compareTo(BigDecimal.ZERO) <= 0) return BigDecimal.ZERO;
        BigDecimal guess = BigDecimal.valueOf(Math.sqrt(x.doubleValue()));
        for (int i = 0; i < 10; i++) {  // 10 iterations for precision
            guess = guess.add(x.divide(guess, mc), mc).divide(BigDecimal.valueOf(2), mc);
        }
        return guess;
    }

    /**
     * Calculate flux-based distance using spherical surface integration.
     * 
     * Uses differential area element: dA = sinθ dθ dφ
     * Flux = ∑_i (Δθ_i · Δφ_i · sinθ_i)
     * 
     * This is based on Gauss's Law analogy where prime separation is measured
     * as "flux" through the manifold surface rather than Euclidean distance.
     * 
     * @param coords1 First coordinate array (alternating θ, φ pairs expected)
     * @param coords2 Second coordinate array
     * @param N The semiprime for normalization
     * @return Flux distance normalized by log²N
     */
    public static BigDecimal calculateFlux(BigDecimal[] coords1, BigDecimal[] coords2, BigDecimal N) {
        if (coords1.length != coords2.length) {
            throw new IllegalArgumentException("Coordinate arrays must be same length");
        }

        gva.SphericalFluxDistance fluxCalc = new gva.SphericalFluxDistance(MC);
        
        // If coordinates are in [0,1] range (standard torus coordinates),
        // we can interpret pairs as (θ, φ) coordinates
        if (coords1.length % 2 == 0) {
            return fluxCalc.distance(coords1, coords2, N.toBigInteger());
        } else {
            // Fall back to standard Riemannian distance with flux weighting
            BigDecimal kappa = BigDecimal.valueOf(4).multiply(log(N.add(BigDecimal.ONE, MC), MC), MC).divide(E_SQUARED, MC);
            
            BigDecimal total = BigDecimal.ZERO;
            for (int i = 0; i < coords1.length; i++) {
                BigDecimal diff = coords1[i].subtract(coords2[i], MC).abs();
                BigDecimal circDist = diff.min(BigDecimal.ONE.subtract(diff, MC));
                
                // Apply flux-like weighting: approximate sinθ contribution
                BigDecimal theta = coords1[i].multiply(BigDecimal.valueOf(Math.PI), MC);
                BigDecimal sinTheta = BigDecimal.valueOf(Math.sin(theta.doubleValue()));
                
                BigDecimal warpedDist = circDist.multiply(sinTheta.add(BigDecimal.ONE, MC), MC);
                warpedDist = warpedDist.multiply(BigDecimal.ONE.add(kappa.multiply(circDist, MC), MC), MC);
                total = total.add(warpedDist.pow(2, MC), MC);
            }
            
            BigDecimal lnN = log(N, MC);
            return sqrt(total, MC).divide(lnN.multiply(lnN, MC), MC);
        }
    }

    /**
     * Hybrid distance calculation that combines Riemannian and flux metrics.
     * 
     * Provides a weighted combination:
     * d_hybrid = α·d_riemannian + (1-α)·d_flux
     * 
     * @param coords1 First coordinate array
     * @param coords2 Second coordinate array
     * @param N The semiprime
     * @param alpha Weight for Riemannian component (0 = pure flux, 1 = pure Riemannian)
     * @return Combined distance metric
     */
    public static BigDecimal calculateHybrid(BigDecimal[] coords1, BigDecimal[] coords2, BigDecimal N, double alpha) {
        BigDecimal dRiemann = calculate(coords1, coords2, N);
        BigDecimal dFlux = calculateFlux(coords1, coords2, N);
        
        BigDecimal alphaWeight = BigDecimal.valueOf(alpha);
        BigDecimal oneMinusAlpha = BigDecimal.ONE.subtract(alphaWeight, MC);
        
        return dRiemann.multiply(alphaWeight, MC).add(dFlux.multiply(oneMinusAlpha, MC), MC);
    }
}