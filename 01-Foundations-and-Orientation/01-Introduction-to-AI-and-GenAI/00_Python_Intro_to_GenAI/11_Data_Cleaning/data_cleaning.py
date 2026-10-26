# ============================================================
# TOPIC 11: Data Cleaning
# ============================================================

import numpy as np
import pandas as pd

# Build a messy, realistic dataset to clean
print("--- Messy Dataset (Before Cleaning) ---")

raw_data = pd.DataFrame({
    "Name":      ["Alice", "bob", "CHARLIE", "diana", "  Eve  ", "Frank", "Alice", "Grace", None, "Henry"],
    "Age":       [25, 30, -5, 28, 200, 35, 25, 22, 29, np.nan],
    "Salary":    [45000, 72000, 38000, np.nan, 55000, 90000, 45000, 38000, 61000, 70000],
    "City":      ["Accra", "kumasi", "Tamale", "ACCRA", "Accra", "Kumasi", "Accra", np.nan, "Tamale", "Kumasi"],
    "Score":     [85, 92, 78, 95, 88, 91, 85, 200, 74, -10],
    "Join_Date": ["2022-01-15", "2021-05-20", "2023-03-10", "2020-07-04",
                  "invalid_date", "2022-11-30", "2022-01-15", "2023-08-22", "2021-12-01", "2022-06-15"],
})

print(raw_data.to_string())
print(f"\nShape: {raw_data.shape}")

# ============================================================
# SECTION 1: Detecting Missing Values
# ============================================================

print("\n--- Detecting Missing Values ---")

print("Missing values per column:")
print(raw_data.isnull().sum())

print(f"\nTotal missing: {raw_data.isnull().sum().sum()}")
print(f"Percent missing per column:")
print((raw_data.isnull().mean() * 100).round(1))

# Visual check — which cells are missing
print("\nMissing value map (True = missing):")
print(raw_data.isnull())

# ============================================================
# SECTION 2: Removing Duplicates
# ============================================================

print("\n--- Removing Duplicates ---")

print(f"Rows before removing duplicates: {len(raw_data)}")
print(f"Duplicate rows detected: {raw_data.duplicated().sum()}")

# Show the duplicate rows
duplicates = raw_data[raw_data.duplicated()]
print("Duplicate rows:")
print(duplicates)

# Remove duplicates (keep first occurrence)
df = raw_data.drop_duplicates()
print(f"Rows after removing duplicates: {len(df)}")
df = df.reset_index(drop=True)  # Reset row numbers after removing rows

# ============================================================
# SECTION 3: Fixing Text Formatting
# ============================================================

print("\n--- Text Formatting ---")

# Remove whitespace from Name
df["Name"] = df["Name"].str.strip()

# Standardize to Title Case
df["Name"] = df["Name"].str.title()

# Standardize City to Title Case
df["City"] = df["City"].str.strip().str.title()

print("Names after cleanup:", df["Name"].tolist())
print("Cities after cleanup:", df["City"].tolist())

# Fill missing Name with placeholder
df["Name"] = df["Name"].fillna("Unknown")

# ============================================================
# SECTION 4: Outlier Detection
# ============================================================

print("\n--- Outlier Detection ---")

# Method 1: Logical bounds — domain knowledge
# Age should be between 0 and 100; Score between 0 and 100
print("Age outliers (outside 0–100):")
age_outliers = df[(df["Age"] < 0) | (df["Age"] > 100)]
print(age_outliers[["Name", "Age"]])

print("\nScore outliers (outside 0–100):")
score_outliers = df[(df["Score"] < 0) | (df["Score"] > 100)]
print(score_outliers[["Name", "Score"]])

# Method 2: IQR (Interquartile Range) method — statistical approach
def detect_outliers_iqr(series, label=""):
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = series[(series < lower) | (series > upper)]
    print(f"{label}: Q1={Q1:.1f}, Q3={Q3:.1f}, IQR={IQR:.1f}, bounds=[{lower:.1f}, {upper:.1f}]")
    print(f"  Outlier values: {outliers.tolist()}")
    return lower, upper

print("\nIQR-based outlier detection:")
sal_lo, sal_hi = detect_outliers_iqr(df["Salary"].dropna(), "Salary")

# Fix outliers: cap to valid bounds (don't just delete — you lose data)
df["Age"] = df["Age"].clip(lower=0, upper=100)
df["Score"] = df["Score"].clip(lower=0, upper=100)
print("\nAfter clipping Age and Score:")
print(df[["Name", "Age", "Score"]])

# ============================================================
# SECTION 5: Filling Missing Values
# ============================================================

print("\n--- Filling Missing Values ---")

print("Before filling:")
print(df[["Age", "Salary", "City"]].isnull().sum())

# Fill numeric columns with median (more robust than mean for skewed data)
df["Age"] = df["Age"].fillna(df["Age"].median())
df["Salary"] = df["Salary"].fillna(df["Salary"].median())

# Fill categorical column with mode (most common value)
df["City"] = df["City"].fillna(df["City"].mode()[0])

print("After filling:")
print(df[["Age", "Salary", "City"]].isnull().sum())

# ============================================================
# SECTION 6: Data Normalization (Scaling)
# ============================================================

print("\n--- Data Normalization ---")

# Normalization: rescale numeric values to a standard range
# This is important before machine learning algorithms.

# Min-Max Scaling: scales to range [0, 1]
def min_max_scale(series):
    return (series - series.min()) / (series.max() - series.min())

# Z-score Standardization: mean=0, std=1
def z_score_scale(series):
    return (series - series.mean()) / series.std()

df["Salary_MinMax"] = min_max_scale(df["Salary"]).round(3)
df["Salary_ZScore"] = z_score_scale(df["Salary"]).round(3)

print("Salary before and after normalization:")
print(df[["Name", "Salary", "Salary_MinMax", "Salary_ZScore"]].to_string(index=False))

print(f"\nOriginal Salary range: [{df['Salary'].min():,.0f}, {df['Salary'].max():,.0f}]")
print(f"Min-Max range:         [{df['Salary_MinMax'].min()}, {df['Salary_MinMax'].max()}]")
print(f"Z-Score range:         [{df['Salary_ZScore'].min():.2f}, {df['Salary_ZScore'].max():.2f}]")

# ============================================================
# SECTION 7: Feature Formatting (Dates, Encoding)
# ============================================================

print("\n--- Feature Formatting ---")

# Parse and validate dates
df["Join_Date"] = pd.to_datetime(df["Join_Date"], errors="coerce")
# errors='coerce' turns invalid dates into NaT (Not a Time)

print("Join dates after parsing:")
print(df[["Name", "Join_Date"]])
print(f"Invalid dates: {df['Join_Date'].isnull().sum()}")

# Extract date parts
df["Join_Year"]  = df["Join_Date"].dt.year
df["Join_Month"] = df["Join_Date"].dt.month
print("\nExtracted year and month:")
print(df[["Name", "Join_Date", "Join_Year", "Join_Month"]].head())

# ============================================================
# SECTION 8: Final Clean Dataset
# ============================================================

print("\n--- Final Cleaned Dataset ---")

clean_cols = ["Name", "Age", "Salary", "City", "Score", "Join_Date"]
final_df = df[clean_cols].copy()
final_df["Age"] = final_df["Age"].astype(int)

print(final_df.to_string(index=False))
print(f"\nFinal shape: {final_df.shape}")
print("Remaining missing values:")
print(final_df.isnull().sum())

print("\n--- End of Data Cleaning ---")
