# ============================================================
# TOPIC 10: Understanding Data
# ============================================================

import numpy as np
import pandas as pd

np.random.seed(42)

# ============================================================
# SECTION 1: Types of Data (Numerical vs Categorical)
# ============================================================

print("--- Types of Data ---")

# NUMERICAL DATA: numbers that represent quantities
#   - Continuous: any value in a range (height, salary, temperature)
#   - Discrete: only whole/counted values (number of children, goals scored)

# CATEGORICAL DATA: groups or labels
#   - Nominal: no natural order (city, gender, blood type, color)
#   - Ordinal: has a natural order (education level, ratings 1-5, shirt size)

data = pd.DataFrame({
    "Name":        ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "Age":         [25, 30, 22, 28, 35],             # Discrete numeric
    "Height_cm":   [165.2, 178.5, 171.0, 160.8, 175.3],  # Continuous numeric
    "Salary":      [45000, 72000, 38000, 90000, 55000],   # Continuous numeric
    "City":        ["Accra", "Kumasi", "Accra", "Tamale", "Kumasi"],  # Nominal
    "Education":   ["BSc", "MSc", "BSc", "PhD", "MSc"],  # Ordinal
    "Rating":      [3, 5, 2, 4, 5],                  # Ordinal (1-5 scale)
})

print(data)
print("\nData types detected by Pandas:")
print(data.dtypes)

# ============================================================
# SECTION 2: Descriptive Statistics
# ============================================================

print("\n--- Descriptive Statistics ---")

# Create a larger dataset to work with
n = 100
df = pd.DataFrame({
    "Score":  np.random.normal(loc=70, scale=15, size=n).clip(0, 100).round(1),
    "Salary": np.random.normal(loc=60000, scale=15000, size=n).clip(25000, 120000).round(-2),
    "Age":    np.random.randint(20, 60, n),
})

print("Dataset preview:")
print(df.head())

print("\ndescribe() — full summary statistics:")
print(df.describe().round(2))

# ============================================================
# SECTION 3: Measures of Central Tendency
# ============================================================

print("\n--- Measures of Central Tendency ---")

scores = df["Score"]

mean   = scores.mean()
median = scores.median()
mode   = scores.mode()[0]  # mode() returns a Series; take first value

print(f"Mean   (average)    : {mean:.2f}")
print(f"Median (middle)     : {median:.2f}")
print(f"Mode   (most common): {mode:.2f}")

print("""
When to use which:
  Mean   → when data is symmetric and has no outliers
  Median → when data is skewed or has outliers (e.g., income)
  Mode   → for categorical data or finding the most common value
""")

# Salary example — mean vs median
salaries = df["Salary"]
print(f"Salary Mean  : ${salaries.mean():,.0f}")
print(f"Salary Median: ${salaries.median():,.0f}")
# If there are outliers (very high earners), mean >> median

# ============================================================
# SECTION 4: Measures of Dispersion
# ============================================================

print("\n--- Measures of Dispersion ---")

# How spread out is the data?

variance = scores.var()
std_dev  = scores.std()
rng      = scores.max() - scores.min()
iqr      = scores.quantile(0.75) - scores.quantile(0.25)

print(f"Range               : {rng:.2f}  (max - min)")
print(f"Variance            : {variance:.2f}  (average squared distance from mean)")
print(f"Standard Deviation  : {std_dev:.2f}  (sqrt of variance — same unit as data)")
print(f"IQR (Q3 - Q1)       : {iqr:.2f}  (middle 50% of data)")

print(f"\nQ1 (25th percentile): {scores.quantile(0.25):.2f}")
print(f"Q2 (50th / median)  : {scores.quantile(0.50):.2f}")
print(f"Q3 (75th percentile): {scores.quantile(0.75):.2f}")
print(f"Min: {scores.min():.2f}   Max: {scores.max():.2f}")

print("""
Interpretation:
  Small std dev → data is clustered close to the mean
  Large std dev → data is spread out / more variable
  IQR is more robust than range (not affected by extreme outliers)
""")

# ============================================================
# SECTION 5: Skewness and Kurtosis
# ============================================================

print("\n--- Skewness and Kurtosis ---")

# SKEWNESS: measures the asymmetry of the distribution
#   = 0   : perfectly symmetric
#   > 0   : right-skewed (long tail on the right, most values on the left)
#   < 0   : left-skewed  (long tail on the left,  most values on the right)

# Create examples
symmetric    = pd.Series(np.random.normal(50, 10, 1000))
right_skewed = pd.Series(np.random.exponential(scale=10, size=1000))   # income-like
left_skewed  = pd.Series(100 - np.random.exponential(scale=10, size=1000))

print("Skewness (how asymmetric the distribution is):")
print(f"  Symmetric distribution : {symmetric.skew():.3f}   (should be near 0)")
print(f"  Right-skewed            : {right_skewed.skew():.3f}   (positive — tail right)")
print(f"  Left-skewed             : {left_skewed.skew():.3f}   (negative — tail left)")

print("""
  Rule of thumb:
    |skewness| < 0.5  → fairly symmetric
    0.5 to 1.0        → moderately skewed
    > 1.0             → highly skewed
""")

# KURTOSIS: measures the "tailedness" — how heavy the tails are
#   Normal distribution kurtosis ≈ 0 (using excess kurtosis)
#   > 0 (Leptokurtic) : heavy tails, more outliers (e.g., finance data)
#   < 0 (Platykurtic) : light tails, fewer outliers

print("Kurtosis (how heavy the tails are / how many outliers):")
print(f"  Normal distribution     : {symmetric.kurtosis():.3f}")
print(f"  Right-skewed (exp)      : {right_skewed.kurtosis():.3f}")

print(f"\nYour dataset — Score column:")
print(f"  Skewness : {df['Score'].skew():.3f}")
print(f"  Kurtosis : {df['Score'].kurtosis():.3f}")

# Full summary in one place
print("\n--- Full Statistical Summary ---")
summary = df["Score"].agg([
    "count", "mean", "median", "std", "var", "min", "max", "skew", "kurt"
]).round(3)
summary.index = ["Count", "Mean", "Median", "Std Dev", "Variance", "Min", "Max", "Skewness", "Kurtosis"]
print(summary.to_string())

print("\n--- End of Understanding Data ---")
