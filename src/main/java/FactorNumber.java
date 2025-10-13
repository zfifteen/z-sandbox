import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;

public class FactorNumber {

    public static void main(String[] args) {
        BigInteger N = new BigInteger("137524771864208156028430259349934309717");
        System.out.println("Factoring: " + N);

        // Check if even
        if (N.mod(BigInteger.TWO).equals(BigInteger.ZERO)) {
            BigInteger factor = BigInteger.TWO;
            BigInteger quotient = N.divide(factor);
            System.out.println("Factor: " + factor + " * " + quotient);
            return;
        }

        // Trial division with small primes
        List<BigInteger> smallPrimes = generateSmallPrimes(10000000); // up to 10^7
        for (BigInteger p : smallPrimes) {
            if (N.mod(p).equals(BigInteger.ZERO)) {
                BigInteger quotient = N.divide(p);
                System.out.println("Factor: " + p + " * " + quotient);
                return;
            }
        }

        // If no small factors, try larger
        // For simplicity, assume it's a semiprime and try to find factors around sqrt(N)
        BigInteger sqrtN = sqrtFloor(N);
        System.out.println("sqrt(N) ≈ " + sqrtN);

        // Generate candidates around sqrt(N) using simple method
        BigInteger start = sqrtN.subtract(BigInteger.valueOf(100000000));
        BigInteger end = sqrtN.add(BigInteger.valueOf(100000000));
        for (BigInteger i = start; i.compareTo(end) <= 0; i = i.add(BigInteger.TWO)) {
            if (N.mod(i).equals(BigInteger.ZERO)) {
                BigInteger quotient = N.divide(i);
                System.out.println("Factor: " + i + " * " + quotient);
                return;
            }
        }

        System.out.println("No factors found with trial division up to " + end);

        // Check if prime
        if (N.isProbablePrime(100)) {
            System.out.println("The number is probably prime.");
        } else {
            System.out.println("The number is composite but no factors found.");
        }
    }

    private static BigInteger sqrtFloor(BigInteger n) {
        if (n.signum() < 0) throw new ArithmeticException("sqrt of negative");
        if (n.signum() == 0) return BigInteger.ZERO;
        BigInteger x = BigInteger.ONE.shiftLeft((n.bitLength() + 1) >>> 1);
        while (true) {
            BigInteger xn = x.add(n.divide(x)).shiftRight(1);
            if (xn.equals(x) || xn.equals(x.subtract(BigInteger.ONE))) {
                if (xn.multiply(xn).compareTo(n) > 0) return xn.subtract(BigInteger.ONE);
                return xn;
            }
            x = xn;
        }
    }

    private static List<BigInteger> generateSmallPrimes(int limit) {
        List<BigInteger> primes = new ArrayList<>();
        boolean[] isComposite = new boolean[limit + 1];
        for (int i = 2; i <= limit; i++) {
            if (!isComposite[i]) {
                primes.add(BigInteger.valueOf(i));
                for (int j = i * 2; j <= limit; j += i) {
                    isComposite[j] = true;
                }
            }
        }
        return primes;
    }
}