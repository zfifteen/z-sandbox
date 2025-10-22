package unifiedframework;

import java.math.BigDecimal;
import java.util.*;

/**
 * A* pathfinder using Riemannian distance as cost for torus navigation.
 * Ports Python RiemannianAStar class.
 */
public class RiemannianAStar {

    /**
     * Heuristic: straight-line distance in torus.
     */
    private static BigDecimal heuristic(BigDecimal[] current, BigDecimal[] goal) {
        return RiemannianDistance.calculate(current, goal, BigDecimal.ONE); // N not used in heuristic
    }

    /**
     * Generate neighboring points on the torus.
     */
    private static List<BigDecimal[]> getNeighbors(BigDecimal[] point, BigDecimal stepSize) {
        List<BigDecimal[]> neighbors = new ArrayList<>();
        for (int i = 0; i < point.length; i++) {
            for (int delta = -1; delta <= 1; delta += 2) { // -1, 1
                BigDecimal[] neighbor = point.clone();
                neighbor[i] = neighbor[i].add(stepSize.multiply(BigDecimal.valueOf(delta))).remainder(BigDecimal.ONE);
                neighbors.add(neighbor);
            }
        }
        return neighbors;
    }

    /**
     * A* search from start to goal on the torus.
     */
    public static List<BigDecimal[]> findPath(BigDecimal[] start, BigDecimal[] goal, BigDecimal N, int maxIterations) {
        PriorityQueue<Node> frontier = new PriorityQueue<>(Comparator.comparingDouble(n -> n.priority));
        frontier.add(new Node(start, heuristic(start, goal).doubleValue()));

        Map<String, BigDecimal> costSoFar = new HashMap<>();
        Map<String, BigDecimal[]> cameFrom = new HashMap<>();

        costSoFar.put(Arrays.toString(start), BigDecimal.ZERO);
        cameFrom.put(Arrays.toString(start), null);

        int iterations = 0;
        while (!frontier.isEmpty() && iterations < maxIterations) {
            iterations++;
            Node currentNode = frontier.poll();
            BigDecimal[] current = currentNode.point;

            if (RiemannianDistance.calculate(current, goal, N).compareTo(BigDecimal.valueOf(0.001)) < 0) {
                // Reconstruct path
                List<BigDecimal[]> path = new ArrayList<>();
                BigDecimal[] node = current;
                while (node != null) {
                    path.add(node);
                    node = cameFrom.get(Arrays.toString(node));
                }
                Collections.reverse(path);
                return path;
            }

            for (BigDecimal[] neighbor : getNeighbors(current, BigDecimal.valueOf(0.01))) {
                BigDecimal newCost = costSoFar.get(Arrays.toString(current)).add(RiemannianDistance.calculate(current, neighbor, N));
                String neighborKey = Arrays.toString(neighbor);
                if (!costSoFar.containsKey(neighborKey) || newCost.compareTo(costSoFar.get(neighborKey)) < 0) {
                    costSoFar.put(neighborKey, newCost);
                    double priority = newCost.add(heuristic(neighbor, goal)).doubleValue();
                    frontier.add(new Node(neighbor, priority));
                    cameFrom.put(neighborKey, current);
                }
            }
        }
        return null; // No path found
    }

    private static class Node {
        BigDecimal[] point;
        double priority;

        Node(BigDecimal[] point, double priority) {
            this.point = point;
            this.priority = priority;
        }
    }
}