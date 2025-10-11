import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV
df = pd.read_csv('../ladder_results.csv')
# Filter out header rows
df = df[df['id'] != 'id'].copy()
df['success'] = df['success'].replace({'true': 1, 'false': 0})
# Convert numeric columns
numeric_cols = ['id', 'digits', 'cand_count', 'time_ms', 'tries_to_hit', 'reduction_pct']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna()

# Group by digits and builder, compute averages
grouped = df.groupby(['digits', 'builder']).agg({
    'success': 'mean',
    'time_ms': 'mean',
    'reduction_pct': 'mean',
    'tries_to_hit': 'mean'
}).reset_index()

# Plot reduction_pct vs digits
plt.figure(figsize=(10, 6))
for builder in grouped['builder'].unique():
    subset = grouped[grouped['builder'] == builder]
    plt.plot(subset['digits'], subset['reduction_pct'], label=builder, marker='o')

plt.xlabel('Digits')
plt.ylabel('Reduction %')
plt.title('Reduction % vs Digits')
plt.legend()
plt.grid(True)
plt.savefig('../plots/reduction_vs_digits.png')
plt.show()

# Plot time_ms vs digits
plt.figure(figsize=(10, 6))
for builder in grouped['builder'].unique():
    subset = grouped[grouped['builder'] == builder]
    plt.plot(subset['digits'], subset['time_ms'], label=builder, marker='o')

plt.xlabel('Digits')
plt.ylabel('Time (ms)')
plt.title('Time vs Digits')
plt.legend()
plt.grid(True)
plt.savefig('../plots/time_vs_digits.png')
plt.show()

# Plot success rate vs digits
plt.figure(figsize=(10, 6))
for builder in grouped['builder'].unique():
    subset = grouped[grouped['builder'] == builder]
    plt.plot(subset['digits'], subset['success'], label=builder, marker='o')

plt.xlabel('Digits')
plt.ylabel('Success Rate')
plt.title('Success Rate vs Digits')
plt.legend()
plt.grid(True)
plt.savefig('../plots/success_vs_digits.png')
plt.show()