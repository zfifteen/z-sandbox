package gva;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;

/**
 * Spherical Flux Distance Calculator for GVA.
 * 
 * Implements surface flux metric based on differential area elements:
 * dA = sinθ dθ dφ (Jacobian factor from spherical coordinates)
 * 
 * This replaces Euclidean distance with a geometric "flux" measure that
 * accounts for the curvature and density distribution on the torus manifold.
 * 
 * Mathematical basis: E·dA dot product from Gauss's Law
 * → Prime separation as flux: ∑ (Δθ_i · sinθ_i · Δφ_i)
 */
public class SphericalFluxDistance {

  private final MathContext mc;

  public SphericalFluxDistance(MathContext mc) {
    this.mc = mc;
  }

  /**
   * Compute flux-based distance between two embeddings.
   * 
   * Uses differential area element: dA = sinθ dθ dφ
   * Flux = ∑_i (Δθ_i · Δφ_i · sinθ_i)
   * 
   * Normalized by log²N to scale with number size.
   * 
   * @param coords1 First embedding coordinates (alternating θ, φ pairs)
   * @param coords2 Second embedding coordinates (alternating θ, φ pairs)
   * @param N The semiprime being factored (for normalization)
   * @return Flux distance as BigDecimal
   */
  public BigDecimal distance(BigDecimal[] coords1, BigDecimal[] coords2, BigInteger N) {
    if (coords1.length != coords2.length) {
      throw new IllegalArgumentException("Coordinate arrays must have same length");
    }
    if (coords1.length % 2 != 0) {
      throw new IllegalArgumentException("Coordinate array length must be even (θ, φ pairs)");
    }

    BigDecimal flux = BigDecimal.ZERO;
    
    // Process coordinates as (θ, φ) pairs
    for (int i = 0; i < coords1.length; i += 2) {
      // Map [0,1] coordinates to angles
      BigDecimal theta1 = coords1[i].multiply(BigDecimal.valueOf(Math.PI), mc);
      BigDecimal theta2 = coords2[i].multiply(BigDecimal.valueOf(Math.PI), mc);
      BigDecimal phi1 = coords1[i + 1].multiply(BigDecimal.valueOf(2.0 * Math.PI), mc);
      BigDecimal phi2 = coords2[i + 1].multiply(BigDecimal.valueOf(2.0 * Math.PI), mc);
      
      // Compute differences (with torus periodicity for φ)
      BigDecimal dTheta = minAbsDiff(theta1, theta2, Math.PI);
      BigDecimal dPhi = minAbsDiff(phi1, phi2, 2.0 * Math.PI);
      
      // Compute sin(θ) - use average θ for Jacobian
      BigDecimal thetaAvg = theta1.add(theta2).divide(BigDecimal.valueOf(2.0), mc);
      BigDecimal sinTheta = sin(thetaAvg);
      
      // Flux contribution: dθ · dφ · sinθ
      BigDecimal contribution = dTheta.multiply(dPhi, mc).multiply(sinTheta, mc);
      flux = flux.add(contribution, mc);
    }
    
    // Normalize by log²N
    BigDecimal lnN = ln(new BigDecimal(N));
    BigDecimal lnNSquared = lnN.multiply(lnN, mc);
    
    return flux.abs().divide(lnNSquared, mc);
  }

  /**
   * Alternative distance using standard Riemannian metric but with flux weighting.
   * Combines Euclidean-like distance with sinθ weighting.
   */
  public BigDecimal fluxWeightedDistance(BigDecimal[] coords1, BigDecimal[] coords2, BigInteger N) {
    if (coords1.length != coords2.length) {
      throw new IllegalArgumentException("Coordinate arrays must have same length");
    }

    BigDecimal sum = BigDecimal.ZERO;
    
    for (int i = 0; i < coords1.length; i += 2) {
      BigDecimal theta1 = coords1[i].multiply(BigDecimal.valueOf(Math.PI), mc);
      BigDecimal theta2 = coords2[i].multiply(BigDecimal.valueOf(Math.PI), mc);
      BigDecimal phi1 = coords1[i + 1].multiply(BigDecimal.valueOf(2.0 * Math.PI), mc);
      BigDecimal phi2 = coords2[i + 1].multiply(BigDecimal.valueOf(2.0 * Math.PI), mc);
      
      BigDecimal dTheta = minAbsDiff(theta1, theta2, Math.PI);
      BigDecimal dPhi = minAbsDiff(phi1, phi2, 2.0 * Math.PI);
      
      BigDecimal thetaAvg = theta1.add(theta2).divide(BigDecimal.valueOf(2.0), mc);
      BigDecimal sinTheta = sin(thetaAvg);
      
      // Weighted squared distance: (dθ² + dφ²) · sinθ
      BigDecimal distSq = dTheta.multiply(dTheta, mc).add(dPhi.multiply(dPhi, mc), mc);
      BigDecimal weighted = distSq.multiply(sinTheta, mc);
      sum = sum.add(weighted, mc);
    }
    
    return sqrt(sum);
  }

  /**
   * Compute minimum absolute difference considering periodicity.
   */
  private BigDecimal minAbsDiff(BigDecimal a, BigDecimal b, double period) {
    BigDecimal diff = a.subtract(b).abs();
    BigDecimal periodBD = BigDecimal.valueOf(period);
    BigDecimal altDiff = periodBD.subtract(diff);
    return diff.min(altDiff);
  }

  /**
   * Approximate sin(x) using Taylor series for BigDecimal.
   * For better performance, converts to double for angles in radians.
   */
  private BigDecimal sin(BigDecimal x) {
    // For moderate precision, use double sin
    double angle = x.doubleValue();
    return BigDecimal.valueOf(Math.sin(angle));
  }

  /**
   * Natural logarithm approximation for BigDecimal.
   */
  private BigDecimal ln(BigDecimal x) {
    if (x.compareTo(BigDecimal.ZERO) <= 0) {
      throw new ArithmeticException("Logarithm of non-positive number");
    }
    return BigDecimal.valueOf(Math.log(x.doubleValue()));
  }

  /**
   * Square root approximation for BigDecimal.
   */
  private BigDecimal sqrt(BigDecimal x) {
    if (x.compareTo(BigDecimal.ZERO) < 0) {
      throw new ArithmeticException("Square root of negative number");
    }
    return BigDecimal.valueOf(Math.sqrt(x.doubleValue()));
  }
}
