# ============================================================
# TOPIC 16: Data Preparation for Machine Learning
# ============================================================
# Install: pip install scikit-learn pandas numpy

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (MinMaxScaler, StandardScaler,
                                    LabelEncoder, OneHotEncoder)
from sklearn.feature_selection import SelectKBest, f_classif

np.random.seed(42)

# ============================================================
# Build the Dataset
# ============================================================

n = 300
df = pd.DataFrame({
    "Age":        np.random.randint(22, 60, n),
    "Experience": np.random.randint(0, 30, n),
    "Salary":     np.random.normal(60000, 15000, n).clip(25000, 120000).round(-2),
    "Score":      np.random.normal(70, 12, n).clip(30, 100).round(1),
    "Gender":     np.random.choice(["Male", "Female"], n),
    "Department": np.random.choice(["Engineering", "Sales", "HR", "Finance"], n),
    "Education":  np.random.choice(["BSc", "MSc", "PhD"], n),
    # Target: 1 = promoted, 0 = not promoted
    "Promoted":   np.random.choice([0, 1], n, p=[0.65, 0.35]),
})

# Boost promotion chance for high salary + experience
df.loc[(df["Salary"] > 75000) & (df["Experience"] > 10), "Promoted"] = 1

print("Original dataset:")
print(df.head(8))
print(f"Shape: {df.shape}")
print(f"\nTarget distribution:")
print(df["Promoted"].value_counts())

# ============================================================
# SECTION 1: Train-Test Split
# ============================================================

print("\n--- Train-Test Split ---")

# Define features (X) and target (y)
# Drop non-numeric columns for now (we'll handle them below)
X_numeric = df[["Age", "Experience", "Salary", "Score"]]
y = df["Promoted"]

# Split: 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X_numeric, y,
    test_size=0.20,       # 20% for testing
    random_state=42,      # Fixed seed for reproducibility
    stratify=y            # Keep same class proportions in train and test
)

print(f"Full dataset     : {len(df)} rows")
print(f"Training set     : {len(X_train)} rows ({len(X_train)/len(df)*100:.0f}%)")
print(f"Test set         : {len(X_test)} rows  ({len(X_test)/len(df)*100:.0f}%)")

print(f"\nClass distribution in train set:")
print(y_train.value_counts(normalize=True).round(3))
print("Class distribution in test set:")
print(y_test.value_counts(normalize=True).round(3))

print("""
WHY split into train and test?
  - We train (teach) the model on the training data.
  - We test how well it generalizes on the TEST data.
  - The model NEVER sees the test data during training.
  - This simulates real-world performance on new/unseen data.
""")

# ============================================================
# SECTION 2: Feature Selection
# ============================================================

print("--- Feature Selection ---")

# Feature selection: choose the most relevant columns for the model.
# Irrelevant features can reduce accuracy and slow down training.

# Check correlation with target
print("Correlation with 'Promoted':")
for col in ["Age", "Experience", "Salary", "Score"]:
    corr = df[col].corr(df["Promoted"])
    print(f"  {col}: {corr:.3f}")

# Statistical test: SelectKBest (F-test for classification)
selector = SelectKBest(score_func=f_classif, k=3)  # keep top 3 features
X_selected = selector.fit_transform(X_numeric, y)

scores = pd.Series(selector.scores_, index=X_numeric.columns)
print("\nFeature importance scores (F-statistic):")
print(scores.sort_values(ascending=False).round(2))
print(f"\nSelected top 3 features: {list(X_numeric.columns[selector.get_support()])}")

# ============================================================
# SECTION 3: Feature Scaling
# ============================================================

print("\n--- Feature Scaling ---")

print("Before scaling — first 3 rows:")
print(X_train.head(3).to_string())

# Min-Max Scaling: rescales to [0, 1]
minmax = MinMaxScaler()
X_train_minmax = pd.DataFrame(minmax.fit_transform(X_train), columns=X_train.columns)
X_test_minmax  = pd.DataFrame(minmax.transform(X_test),  columns=X_test.columns)

print("\nAfter Min-Max Scaling (first 3 rows):")
print(X_train_minmax.head(3).round(4).to_string())

# Standard Scaling: mean=0, std=1
scaler = StandardScaler()
X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
X_test_scaled  = pd.DataFrame(scaler.transform(X_test),  columns=X_test.columns)

print("\nAfter Standard Scaling (first 3 rows):")
print(X_train_scaled.head(3).round(4).to_string())

print("""
WHY scale features?
  - Some algorithms (Logistic Regression, KNN, SVM) are sensitive to scale.
  - If 'Salary' ranges from 25000-120000 and 'Score' from 30-100,
    salary will dominate just because it's a bigger number.
  - Scaling puts all features on equal footing.

IMPORTANT RULE:
  - Fit the scaler on TRAINING data only.
  - Then TRANSFORM both train and test with the same fitted scaler.
  - This prevents 'data leakage' (accidentally using test info during training).
""")

# ============================================================
# SECTION 4: Encoding Categorical Variables
# ============================================================

print("--- Encoding Categorical Variables ---")
print("ML models need NUMBERS — they cannot use text like 'Male' or 'Engineering'.")

# Method 1: Label Encoding — assigns an integer to each category
# Good for: ordinal categories (BSc < MSc < PhD)
print("\nLabel Encoding — Education:")
le = LabelEncoder()
df["Education_Encoded"] = le.fit_transform(df["Education"])
mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(f"  Mapping: {mapping}")
print(df[["Education", "Education_Encoded"]].drop_duplicates().sort_values("Education_Encoded"))

# Method 2: One-Hot Encoding — creates a binary column per category
# Good for: nominal categories (no natural order) like Department, Gender
print("\nOne-Hot Encoding — Department:")
ohe_df = pd.get_dummies(df["Department"], prefix="Dept")
print(ohe_df.head(6))
print("Columns created:", list(ohe_df.columns))

# Full encoding example
print("\nFull Encoding Pipeline:")
df_encoded = df.copy()

# Encode Gender (binary: 0 or 1)
df_encoded["Gender_Enc"] = (df_encoded["Gender"] == "Male").astype(int)

# One-hot encode Department (drop first to avoid dummy variable trap)
dept_dummies = pd.get_dummies(df_encoded["Department"], prefix="Dept", drop_first=True)
df_encoded = pd.concat([df_encoded, dept_dummies], axis=1)

# Label encode Education (it has an order: BSc < MSc < PhD)
edu_map = {"BSc": 0, "MSc": 1, "PhD": 2}
df_encoded["Education_Enc"] = df_encoded["Education"].map(edu_map)

# Drop original categorical columns
df_encoded = df_encoded.drop(columns=["Name"] if "Name" in df_encoded.columns else [])
df_encoded = df_encoded.drop(columns=["Gender", "Department", "Education",
                                       "Education_Encoded"])

print("Final encoded columns:")
print(list(df_encoded.columns))
print("\nFirst 3 rows (all numeric now):")
print(df_encoded.head(3).to_string())

# ============================================================
# SECTION 5: Putting It All Together
# ============================================================

print("\n--- Complete Preparation Pipeline ---")

# Define features and target
features = ["Age", "Experience", "Salary", "Score",
            "Gender_Enc", "Education_Enc"] + [c for c in df_encoded.columns if c.startswith("Dept_")]
target = "Promoted"

X_all = df_encoded[features]
y_all = df_encoded[target]

# Train-test split
X_tr, X_te, y_tr, y_te = train_test_split(X_all, y_all,
                                            test_size=0.2, random_state=42, stratify=y_all)

# Scale numeric features
numeric_features = ["Age", "Experience", "Salary", "Score"]
sc = StandardScaler()
X_tr[numeric_features] = sc.fit_transform(X_tr[numeric_features])
X_te[numeric_features]  = sc.transform(X_te[numeric_features])

print(f"Training set: {X_tr.shape}")
print(f"Test set    : {X_te.shape}")
print(f"Features    : {list(X_tr.columns)}")
print("\nData is ready for a machine learning model!")

print("\n--- End of Data Preparation ---")
