# ============================================================
# TOPIC 12: EDA Workflow (Exploratory Data Analysis)
# ============================================================

import numpy as np
import pandas as pd

np.random.seed(0)

# Build a realistic dataset for EDA
n = 200
df = pd.DataFrame({
    "Age":        np.random.randint(22, 60, n),
    "Gender":     np.random.choice(["Male", "Female"], n, p=[0.55, 0.45]),
    "Education":  np.random.choice(["BSc", "MSc", "PhD", "HND"], n, p=[0.45, 0.30, 0.10, 0.15]),
    "Department": np.random.choice(["Engineering", "Sales", "HR", "Finance"], n, p=[0.35, 0.25, 0.20, 0.20]),
    "Experience": np.random.randint(0, 30, n),
    "Salary":     np.random.normal(60000, 18000, n).clip(20000, 130000).round(-2),
    "Performance":np.random.choice([1, 2, 3, 4, 5], n, p=[0.05, 0.10, 0.30, 0.35, 0.20]),
})

# Add some missing values
df.loc[np.random.choice(n, 10, replace=False), "Salary"] = np.nan

# ============================================================
# STEP 1: Asking the Right Questions
# ============================================================

print("=" * 60)
print("EDA WORKFLOW — Employee Salary Dataset")
print("=" * 60)
print("""
Business Questions:
  1. What does the salary distribution look like?
  2. Does salary differ by gender?
  3. Which department pays the most?
  4. Does education level affect salary?
  5. How does experience correlate with salary?
  6. What is the performance distribution?
""")

# ============================================================
# STEP 2: Dataset Overview
# ============================================================

print("--- Dataset Overview ---")
print(f"Shape       : {df.shape[0]} rows x {df.shape[1]} columns")
print(f"Missing vals: {df.isnull().sum().sum()} total")
print(f"\nColumn types:")
print(df.dtypes)
print(f"\nDescriptive stats:")
print(df.describe().round(1))

# Fill missing salary with median before analysis
df["Salary"] = df["Salary"].fillna(df["Salary"].median())

# ============================================================
# STEP 3: Univariate Analysis
# ============================================================

print("\n--- Univariate Analysis (one variable at a time) ---")

# Numeric variables
for col in ["Age", "Salary", "Experience"]:
    series = df[col]
    print(f"\n{col}:")
    print(f"  Mean   : {series.mean():,.1f}")
    print(f"  Median : {series.median():,.1f}")
    print(f"  Std    : {series.std():,.1f}")
    print(f"  Min    : {series.min():,.1f}")
    print(f"  Max    : {series.max():,.1f}")
    print(f"  Skew   : {series.skew():.3f}")

# Categorical variables
for col in ["Gender", "Education", "Department", "Performance"]:
    print(f"\n{col} value counts:")
    vc = df[col].value_counts()
    pct = (df[col].value_counts(normalize=True) * 100).round(1)
    combined = pd.DataFrame({"Count": vc, "Percent %": pct})
    print(combined.to_string())

# ============================================================
# STEP 4: Bivariate Analysis
# ============================================================

print("\n--- Bivariate Analysis (two variables at a time) ---")

# Salary by Gender
print("\nSalary by Gender:")
print(df.groupby("Gender")["Salary"].agg(["mean", "median", "std", "count"]).round(0))

# Salary by Department
print("\nSalary by Department:")
dept_salary = df.groupby("Department")["Salary"].agg(["mean", "median", "count"])
dept_salary.columns = ["Mean Salary", "Median Salary", "Count"]
dept_salary = dept_salary.sort_values("Mean Salary", ascending=False)
print(dept_salary.round(0))

# Salary by Education
print("\nSalary by Education:")
edu_order = ["HND", "BSc", "MSc", "PhD"]
edu_salary = df.groupby("Education")["Salary"].mean().reindex(edu_order)
print(edu_salary.round(0))

# Correlation between numeric variables
print("\nCorrelation Matrix (numeric columns):")
numeric_cols = df[["Age", "Experience", "Salary", "Performance"]]
print(numeric_cols.corr().round(3))

print("""
Interpreting Correlation:
  +1.0  = perfect positive relationship
  -1.0  = perfect negative relationship
   0.0  = no linear relationship
  >0.7  = strong positive
  <-0.7 = strong negative
  0.3 to 0.7 = moderate positive
""")

# Manual correlation check
corr_exp_sal = df["Experience"].corr(df["Salary"])
corr_age_sal = df["Age"].corr(df["Salary"])
print(f"Experience ↔ Salary correlation: {corr_exp_sal:.3f}")
print(f"Age ↔ Salary correlation       : {corr_age_sal:.3f}")

# ============================================================
# STEP 5: Multivariate Analysis
# ============================================================

print("\n--- Multivariate Analysis (3+ variables) ---")

# Salary by Gender AND Department
pivot = df.pivot_table(values="Salary", index="Department", columns="Gender", aggfunc="mean")
print("Mean Salary by Department and Gender:")
print(pivot.round(0))

# Salary by Education AND Department
print("\nMean Salary by Education and Department:")
edu_dept = df.pivot_table(values="Salary", index="Department", columns="Education", aggfunc="mean")
print(edu_dept.round(0).fillna("N/A"))

# Performance by Department
print("\nMean Performance Rating by Department:")
print(df.groupby("Department")["Performance"].mean().round(2).sort_values(ascending=False))

# ============================================================
# STEP 6: Drawing Insights from Data
# ============================================================

print("\n" + "=" * 60)
print("KEY INSIGHTS FROM EDA")
print("=" * 60)

mean_salary = df["Salary"].mean()
median_salary = df["Salary"].median()
skew = df["Salary"].skew()

gender_gap = df.groupby("Gender")["Salary"].mean()
top_dept = df.groupby("Department")["Salary"].mean().idxmax()
top_dept_sal = df.groupby("Department")["Salary"].mean().max()

edu_order_sal = df.groupby("Education")["Salary"].mean().sort_values(ascending=False)

print(f"""
1. SALARY DISTRIBUTION
   - Mean salary: ${mean_salary:,.0f}
   - Median salary: ${median_salary:,.0f}
   - {'Right-skewed' if skew > 0 else 'Left-skewed'} distribution (skew = {skew:.2f})
   - This means a few high earners pull the mean above the median.

2. GENDER PAY
   - Male average:   ${gender_gap.get('Male', 0):,.0f}
   - Female average: ${gender_gap.get('Female', 0):,.0f}
   - Difference: ${abs(gender_gap.get('Male', 0) - gender_gap.get('Female', 0)):,.0f}

3. TOP DEPARTMENT
   - '{top_dept}' has the highest mean salary: ${top_dept_sal:,.0f}

4. EDUCATION AND SALARY
   - Salary ranking by education:
""")
for edu, sal in edu_order_sal.items():
    print(f"     {edu}: ${sal:,.0f}")

print(f"""
5. EXPERIENCE AND SALARY
   - Correlation: {corr_exp_sal:.3f}
   - {'More experience is associated with higher salary.' if corr_exp_sal > 0.3 else 'Experience and salary have a weak correlation here.'}

6. NEXT STEPS
   - Visualize distributions (Matplotlib / Seaborn)
   - Build a salary prediction model (Machine Learning)
   - Investigate the gender pay gap further
""")

print("--- End of EDA Workflow ---")
