package unifiedframework;

import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.stream.Collectors;

public class ZetaZerosHelper {
    private static final String ZETA_FILE_PATH = "/Users/velocityworks/IdeaProjects/unified-framework/data/zeta_1000.txt";

    public static List<BigDecimal> loadZetaZeros() {
        try {
            return Files.lines(Paths.get(ZETA_FILE_PATH))
                    .map(line -> line.split("\\s+")[1])  // Split by space, take second part (value)
                    .map(BigDecimal::new)
                    .collect(Collectors.toList());
        } catch (IOException e) {
            throw new RuntimeException("Failed to load zeta zeros from " + ZETA_FILE_PATH, e);
        }
    }

    public static void main(String[] args) {
        List<BigDecimal> zeros = loadZetaZeros();
        System.out.println("Loaded " + zeros.size() + " zeta zeros.");
        if (!zeros.isEmpty()) {
            System.out.println("First zero: " + zeros.get(0));
            System.out.println("Last zero: " + zeros.get(zeros.size() - 1));
        }
    }
}
