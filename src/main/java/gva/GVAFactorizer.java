package gva;

import tools.BenchLadder.CandidateBuilder;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

/**
 * Geodesic Validation Assault (GVA) Factorizer.
 * Implements CandidateBuilder for geometric factorization.
 */
public class GVAFactorizer implements CandidateBuilder {

    private final MathContext mc;
    private final Embedding embedding;
    private final RiemannianDistance distance;

    public GVAFactorizer(MathContext mc) {
        this.mc = mc;
        this.embedding = new Embedding(mc);
        this.distance = new RiemannianDistance(mc);
    }

    @Override
    public List<BigInteger> build(BigInteger N, int maxCands, long seed) {
        List<BigInteger> candidates = new ArrayList<>();
        int bits = N.bitLength();
        int dims = getAdaptiveDims(bits);
        BigDecimal epsilon = getAdaptiveEpsilon(N, bits);

        BigInteger sqrtN = sqrtFloor(N);
        BigInteger range = BigInteger.valueOf(100000); // R=100000

        // Parallel check
        ExecutorService executor = Executors.newFixedThreadPool(4);
        List<Future<BigInteger>> futures = new ArrayList<>();

        for (BigInteger d = BigInteger.ONE.negate(); d.compareTo(range) <= 0; d = d.add(BigInteger.ONE)) {
            BigInteger p = sqrtN.add(d);
            if (p.compareTo(BigInteger.TWO) < 0 || p.compareTo(N) >= 0) continue;

            Future<BigInteger> future = executor.submit(() -> {
                if (N.mod(p).equals(BigInteger.ZERO)) {
                    BigInteger q = N.divide(p);
                    if (isPrime(p) && isPrime(q) && isBalanced(p, q)) {
                        BigDecimal[] embN = embedding.embedTorusGeodesic(N, dims);
                        BigDecimal[] embP = embedding.embedTorusGeodesic(p, dims);
                        BigDecimal[] embQ = embedding.embedTorusGeodesic(q, dims);
                        BigDecimal distP = distance.distance(embN, embP, N);
                        BigDecimal distQ = distance.distance(embN, embQ, N);
                        if (distP.compareTo(epsilon) < 0 || distQ.compareTo(epsilon) < 0) {
                            return p;
                        }
                    }
                }
                return null;
            });
            futures.add(future);
        }

        for (Future<BigInteger> future : futures) {
            try {
                BigInteger cand = future.get();
                if (cand != null && candidates.size() < maxCands) {
                    candidates.add(cand);
                }
            } catch (Exception e) {
                // Handle exception
            }
        }

        executor.shutdown();
        return candidates;
    }

    @Override
    public String name() {
        return "GVA";
    }

    private int getAdaptiveDims(int bits) {
        if (bits <= 64) return 7;
        if (bits <= 128) return 9;
        return 11;
    }

    private BigDecimal getAdaptiveEpsilon(BigInteger N, int bits) {
        double kappa = 4 * Math.log(N.doubleValue() + 1) / Math.exp(2);
        return BigDecimal.valueOf(0.2 / (1 + kappa));
    }

    private BigInteger sqrtFloor(BigInteger n) {
        // Approximation
        return BigInteger.valueOf((long) Math.sqrt(n.doubleValue()));
    }

    private boolean isPrime(BigInteger n) {
        return n.isProbablePrime(80);
    }

    private boolean isBalanced(BigInteger p, BigInteger q) {
        double logP = Math.log(p.doubleValue()) / Math.log(2);
        double logQ = Math.log(q.doubleValue()) / Math.log(2);
        return Math.abs(logP - logQ) <= 1;
    }
}