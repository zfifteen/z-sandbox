#!/usr/bin/env python3
import re

def parse_spiral_data(filepath):
    data = []
    with open(filepath, 'r') as f:
        content = f.read()
    # Regex to find lines like [ 1] Value: 1000151, Iteration: 11 ✓
    pattern = r'\[ \d+\] Value: (\d+), Iteration: (\d+) ✓'
    matches = re.findall(pattern, content)
    for match in matches:
        value = int(match[0])
        iteration = int(match[1])
        data.append((iteration, value))
    return data

if __name__ == "__main__":
    filepath = '/Users/velocityworks/IdeaProjects/unified-framework/src/c/golden-ratio-spiral/golden_spiral_out.txt'
    data = parse_spiral_data(filepath)
    print("Parsed data (Iteration, Value):")
    for it, val in data[:10]:  # First 10
        print(f"{it}, {val}")
    # Save to csv
    import csv
    csv_path = '/Users/velocityworks/IdeaProjects/unified-framework/src/c/golden-ratio-spiral/spiral_data.csv'
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Iteration', 'Value'])
        writer.writerows(data)
    print(f"Saved to {csv_path}")