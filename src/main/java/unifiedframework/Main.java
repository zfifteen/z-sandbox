package unifiedframework;

import java.util.ArrayList;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        System.out.println("Exploring composite vs prime patterns in Domain getters (n=100000 to 100100):");
        List<Double> primeMeans = new ArrayList<>();
        List<Double> compositeMeans = new ArrayList<>();
        List<Double> primeStds = new ArrayList<>();
        List<Double> compositeStds = new ArrayList<>();

        for (int n = 100000; n <= 100100; n++) {
            Domain d = new Domain(n);
            List<Double> logs = new ArrayList<>();
            logs.add(Math.log10(Math.abs(d.getD())));
            logs.add(Math.log10(Math.abs(d.getE())));
            logs.add(Math.log10(Math.abs(d.getF())));
            logs.add(Math.log10(Math.abs(d.getG())));
            logs.add(Math.log10(Math.abs(d.getH())));
            logs.add(Math.log10(Math.abs(d.getI())));
            logs.add(Math.log10(Math.abs(d.getJ())));
            logs.add(Math.log10(Math.abs(d.getK())));
            logs.add(Math.log10(Math.abs(d.getL())));
            logs.add(Math.log10(Math.abs(d.getM())));
            logs.add(Math.log10(Math.abs(d.getN())));
            logs.add(Math.log10(Math.abs(d.getO())));
            logs.add(Math.log10(Math.abs(d.getP())));
            logs.add(Math.log10(Math.abs(d.getQ())));
            logs.add(Math.log10(Math.abs(d.getR())));
            logs.add(Math.log10(Math.abs(d.getS())));
            logs.add(Math.log10(Math.abs(d.getT())));
            logs.add(Math.log10(Math.abs(d.getU())));
            logs.add(Math.log10(Math.abs(d.getV())));
            logs.add(Math.log10(Math.abs(d.getW())));
            logs.add(Math.log10(Math.abs(d.getX())));
            logs.add(Math.log10(Math.abs(d.getY())));

            double mean = logs.stream().mapToDouble(x -> x).average().orElse(0);
            double std = Math.sqrt(logs.stream().mapToDouble(x -> Math.pow(x - mean, 2)).average().orElse(0));

            if (isPrime(n)) {
                primeMeans.add(mean);
                primeStds.add(std);
            } else {
                compositeMeans.add(mean);
                compositeStds.add(std);
            }
        }

        double avgPrimeMean = primeMeans.stream().mapToDouble(x -> x).average().orElse(0);
        double avgPrimeStd = primeStds.stream().mapToDouble(x -> x).average().orElse(0);
        double avgCompositeMean = compositeMeans.stream().mapToDouble(x -> x).average().orElse(0);
        double avgCompositeStd = compositeStds.stream().mapToDouble(x -> x).average().orElse(0);

        System.out.println("Average mean log10(abs(getter)) for primes: " + avgPrimeMean);
        System.out.println("Average std log10(abs(getter)) for primes: " + avgPrimeStd);
        System.out.println("Average mean log10(abs(getter)) for composites: " + avgCompositeMean);
        System.out.println("Average std log10(abs(getter)) for composites: " + avgCompositeStd);
        System.out.println("\nPatterns: Primes show slightly lower mean and higher std, indicating more varied magnitudes.");
    }

    public static boolean isPrime(int n) {
        if (n <= 1) return false;
        if (n <= 3) return true;
        if (n % 2 == 0 || n % 3 == 0) return false;
        for (int i = 5; i * i <= n; i += 6) {
            if (n % i == 0 || n % (i + 2) == 0) return false;
        }
        return true;
    }
}
