# ============================================================
# TOPIC 9: Pandas – Data Analysis
# ============================================================
# Install: pip install pandas openpyxl
# Import convention: import pandas as pd

import pandas as pd
import numpy as np

# ============================================================
# SECTION 1: Introduction to Pandas
# ============================================================

print("--- Introduction to Pandas ---")
# Pandas = Panel Data
# The most important library for data analysis in Python.
# It gives you two key tools:
#   - Series: a single column of data (1D)
#   - DataFrame: a full table with rows and columns (2D)

print("Pandas version:", pd.__version__)

# ============================================================
# SECTION 2: Series and DataFrames
# ============================================================

print("\n--- Series ---")

# A Series is like a NumPy array but with a labeled index
ages = pd.Series([25, 30, 22, 28], index=["Alice", "Bob", "Charlie", "Diana"])
print(ages)
print("Type:", type(ages))
print("Alice's age:", ages["Alice"])
print("Mean age:", ages.mean())

print("\n--- DataFrame ---")

# A DataFrame is a table — like an Excel spreadsheet
data = {
    "Name":    ["Alice", "Bob", "Charlie", "Diana", "Edward"],
    "Age":     [25, 30, 22, 28, 35],
    "City":    ["Accra", "Kumasi", "Tamale", "Cape Coast", "Accra"],
    "Score":   [85.0, 92.0, 78.0, 95.0, 88.0],
    "Passed":  [True, True, True, True, True],
}

df = pd.DataFrame(data)
print(df)
print("\nShape:", df.shape)   # (rows, columns)
print("Columns:", list(df.columns))

# ============================================================
# SECTION 3: Reading Datasets (CSV, Excel)
# ============================================================

print("\n--- Reading Datasets ---")

# First, let's create a CSV to read
df.to_csv("students.csv", index=False)
print("students.csv saved.")

# Read CSV
df_csv = pd.read_csv("students.csv")
print("\nRead from CSV:")
print(df_csv)

# To read Excel: pd.read_excel("file.xlsx")
# To read JSON:  pd.read_json("file.json")
# To read from URL:
#   url = "https://raw.githubusercontent.com/.../data.csv"
#   df = pd.read_csv(url)

# ============================================================
# SECTION 4: Exploring Datasets
# ============================================================

print("\n--- Exploring the Dataset ---")

# Create a bigger dataset for exploration
np.random.seed(42)
n = 50
explore_df = pd.DataFrame({
    "Name": [f"Student_{i}" for i in range(n)],
    "Age": np.random.randint(18, 30, n),
    "Math": np.random.randint(40, 100, n),
    "English": np.random.randint(40, 100, n),
    "Science": np.random.randint(40, 100, n),
    "City": np.random.choice(["Accra", "Kumasi", "Tamale"], n),
})

# Add some missing values
explore_df.loc[[5, 15, 30], "Math"] = np.nan
explore_df.loc[[10, 25], "English"] = np.nan

print("First 5 rows:")
print(explore_df.head())            # First 5 rows

print("\nLast 3 rows:")
print(explore_df.tail(3))           # Last 3 rows

print("\nDataset info:")
explore_df.info()                   # Column names, types, non-null counts

print("\nDescriptive statistics:")
print(explore_df.describe())        # Count, mean, std, min, max, quartiles

print("\nMissing values per column:")
print(explore_df.isnull().sum())    # Count of NaN per column

print("\nUnique values in City:")
print(explore_df["City"].unique())  # ['Accra', 'Kumasi', 'Tamale']
print("Value counts for City:")
print(explore_df["City"].value_counts())

# ============================================================
# SECTION 5: Selecting Rows and Columns
# ============================================================

print("\n--- Selecting Data ---")

# Select a single column (returns Series)
names = explore_df["Name"]
print("Names column (first 5):")
print(names.head())

# Select multiple columns (returns DataFrame)
scores_df = explore_df[["Name", "Math", "English", "Science"]]
print("\nScores only (first 5):")
print(scores_df.head())

# Select by position with iloc [row, col] — integer-based
print("\nRow 0, all columns:")
print(explore_df.iloc[0])

print("\nRows 0-2, columns 0-3:")
print(explore_df.iloc[0:3, 0:4])

# Select by label with loc [row_label, column_name]
print("\nUsing loc — rows 0 to 3, specific columns:")
print(explore_df.loc[0:3, ["Name", "Math", "City"]])

# ============================================================
# SECTION 6: Filtering Data
# ============================================================

print("\n--- Filtering Data ---")

# Filter rows where Math score > 80
high_math = explore_df[explore_df["Math"] > 80]
print(f"Students with Math > 80: {len(high_math)}")
print(high_math[["Name", "Math"]].head())

# Multiple conditions (use & for AND, | for OR)
top_students = explore_df[(explore_df["Math"] > 75) & (explore_df["English"] > 75)]
print(f"\nStudents with Math>75 AND English>75: {len(top_students)}")

# Filter by city
accra_students = explore_df[explore_df["City"] == "Accra"]
print(f"Students from Accra: {len(accra_students)}")

# isin() — filter if value is in a list
selected_cities = explore_df[explore_df["City"].isin(["Accra", "Kumasi"])]
print(f"Students from Accra or Kumasi: {len(selected_cities)}")

# ============================================================
# SECTION 7: Sorting and Ranking
# ============================================================

print("\n--- Sorting ---")

# Sort by one column
sorted_df = explore_df.sort_values("Math", ascending=False)
print("Top 5 by Math score:")
print(sorted_df[["Name", "Math"]].head())

# Sort by multiple columns
sorted_df2 = explore_df.sort_values(["City", "Math"], ascending=[True, False])
print("\nSorted by City (A-Z) then Math (high-low):")
print(sorted_df2[["Name", "City", "Math"]].head(8))

# Rank (1 = best if ascending=False)
explore_df["Math_Rank"] = explore_df["Math"].rank(ascending=False, method="min")
print("\nTop 5 by rank:")
print(explore_df[["Name", "Math", "Math_Rank"]].sort_values("Math_Rank").head())

# ============================================================
# SECTION 8: Handling Missing Values
# ============================================================

print("\n--- Handling Missing Values ---")

print("Missing values before:")
print(explore_df[["Math", "English"]].isnull().sum())

# Option 1: Drop rows with any missing values
df_dropped = explore_df.dropna()
print(f"\nRows after dropping NaN: {len(df_dropped)} (was {len(explore_df)})")

# Option 2: Fill with a fixed value
df_filled_zero = explore_df.fillna(0)
print("Filled with 0:", df_filled_zero[["Math", "English"]].isnull().sum())

# Option 3: Fill with the column mean (most common for numeric data)
mean_math = explore_df["Math"].mean()
mean_english = explore_df["English"].mean()
explore_df["Math"] = explore_df["Math"].fillna(round(mean_math, 1))
explore_df["English"] = explore_df["English"].fillna(round(mean_english, 1))
print("After filling with mean:", explore_df[["Math", "English"]].isnull().sum())

# ============================================================
# SECTION 9: Data Type Conversion
# ============================================================

print("\n--- Data Types ---")

print("Data types:")
print(explore_df.dtypes)

# Convert a column to a different type
explore_df["Age"] = explore_df["Age"].astype(int)
explore_df["Math"] = explore_df["Math"].astype(float)

# Create a categorical column
explore_df["City"] = explore_df["City"].astype("category")
print("\nAfter type conversion:")
print(explore_df[["Age", "Math", "City"]].dtypes)

# ============================================================
# SECTION 10: GroupBy and Aggregation
# ============================================================

print("\n--- GroupBy & Aggregation ---")

# GroupBy: split data into groups, apply a function, combine results
# This is like pivot tables in Excel

city_stats = explore_df.groupby("City")["Math"].mean()
print("Average Math score by City:")
print(city_stats)

# Multiple aggregations at once
city_summary = explore_df.groupby("City").agg(
    Student_Count=("Name", "count"),
    Avg_Math=("Math", "mean"),
    Avg_English=("English", "mean"),
    Avg_Science=("Science", "mean")
).round(1)
print("\nFull city summary:")
print(city_summary)

# ============================================================
# SECTION 11: Merging and Joining Datasets
# ============================================================

print("\n--- Merging DataFrames ---")

# Create two separate tables to merge
students = pd.DataFrame({
    "student_id": [1, 2, 3, 4, 5],
    "name": ["Alice", "Bob", "Charlie", "Diana", "Edward"],
    "city_id": [1, 2, 1, 3, 2],
})

cities = pd.DataFrame({
    "city_id": [1, 2, 3],
    "city_name": ["Accra", "Kumasi", "Tamale"],
    "region": ["Greater Accra", "Ashanti", "Northern"],
})

# Inner join (only matching records)
merged = pd.merge(students, cities, on="city_id", how="inner")
print("Merged (inner join):")
print(merged)

# Left join (all students, even if no matching city)
left_merged = pd.merge(students, cities, on="city_id", how="left")
print("\nLeft join:")
print(left_merged)

# Concatenate (stack DataFrames vertically)
df_part1 = students.iloc[:3]
df_part2 = students.iloc[3:]
combined = pd.concat([df_part1, df_part2], ignore_index=True)
print("\nConcatenated:")
print(combined)

# ============================================================
# SECTION 12: Exploratory Data Analysis (EDA) Quick Summary
# ============================================================

print("\n--- Quick EDA on Student Data ---")

print(f"Dataset shape: {explore_df.shape}")
print(f"Columns: {list(explore_df.columns)}")
print(f"\nMath:    mean={explore_df['Math'].mean():.1f}, std={explore_df['Math'].std():.1f}")
print(f"English: mean={explore_df['English'].mean():.1f}, std={explore_df['English'].std():.1f}")
print(f"Science: mean={explore_df['Science'].mean():.1f}, std={explore_df['Science'].std():.1f}")

explore_df["Total"] = explore_df["Math"] + explore_df["English"] + explore_df["Science"]
explore_df["Average"] = (explore_df["Total"] / 3).round(1)
top = explore_df.nlargest(3, "Average")[["Name", "Math", "English", "Science", "Average"]]
print("\nTop 3 students overall:")
print(top.to_string(index=False))

# Clean up files
import os
for f in ["students.csv"]:
    if os.path.exists(f):
        os.remove(f)

print("\n--- End of Pandas ---")
