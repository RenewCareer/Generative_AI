# ============================================================
# TOPIC 17: First ML Models (Beginner Level)
# ============================================================
# Install: pip install scikit-learn pandas numpy matplotlib

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
                              accuracy_score, classification_report)

np.random.seed(42)
output_dir = "plots_models"
os.makedirs(output_dir, exist_ok=True)

# ============================================================
# BUILD DATASETS
# ============================================================

# Regression dataset: predict salary from experience
n = 200
experience = np.random.randint(0, 30, n)
salary = 30000 + experience * 2500 + np.random.normal(0, 6000, n)
salary = salary.clip(20000, 120000)
reg_df = pd.DataFrame({"Experience": experience, "Salary": salary})

# Classification dataset: predict if promoted (1) or not (0)
clf_df = pd.DataFrame({
    "Age":        np.random.randint(22, 55, n),
    "Experience": np.random.randint(0, 25, n),
    "Salary":     np.random.normal(60000, 15000, n).clip(25000, 120000),
    "Score":      np.random.normal(72, 12, n).clip(30, 100),
    "Promoted":   np.random.choice([0, 1], n, p=[0.60, 0.40]),
})
# Add signal: high salary + high experience → more likely promoted
clf_df.loc[(clf_df["Salary"] > 72000) & (clf_df["Experience"] > 8), "Promoted"] = 1

print("Datasets built successfully.")

# ============================================================
# SECTION 1: Linear Regression
# ============================================================

print("\n" + "=" * 55)
print("MODEL 1: LINEAR REGRESSION")
print("=" * 55)
print("""
Goal       : Predict a continuous numeric value (salary)
How it works: Fits the best straight line through the data
              y = slope * x + intercept
Use cases  : House price, stock price, temperature, salary
""")

X_reg = reg_df[["Experience"]]
y_reg = reg_df["Salary"]

X_train, X_test, y_train, y_test = train_test_split(
    X_reg, y_reg, test_size=0.2, random_state=42)

model_lr = LinearRegression()
model_lr.fit(X_train, y_train)  # Training step

print(f"Learned equation:")
print(f"  Salary = {model_lr.coef_[0]:,.0f} x Experience + {model_lr.intercept_:,.0f}")

y_pred = model_lr.predict(X_test)

mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2   = r2_score(y_test, y_pred)

print(f"\nEvaluation on test set:")
print(f"  MAE  (Mean Absolute Error)  : ${mae:,.0f}")
print(f"  RMSE (Root Mean Sq Error)   : ${rmse:,.0f}")
print(f"  R²   (Explained Variance)   : {r2:.3f}")
print("""
  MAE  = average prediction error in dollars
  RMSE = penalizes large errors more than MAE
  R²   = 1.0 is perfect; 0.0 = no better than guessing the mean
""")

# Predict for new employees
new_emp = [[2], [10], [20], [28]]
preds = model_lr.predict(new_emp)
print("Predictions for new employees:")
for yrs, sal in zip([x[0] for x in new_emp], preds):
    print(f"  {yrs:>2} years → ${sal:,.0f}")

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(X_reg, y_reg, alpha=0.4, color="steelblue", label="Data")
x_line = np.linspace(0, 30, 100).reshape(-1, 1)
ax.plot(x_line, model_lr.predict(x_line), color="red", linewidth=2, label="Linear Regression")
ax.set_title("Linear Regression: Experience vs Salary")
ax.set_xlabel("Years of Experience")
ax.set_ylabel("Salary ($)")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{output_dir}/01_linear_regression.png", dpi=100)
plt.close()
print(f"Plot saved: {output_dir}/01_linear_regression.png")

# ============================================================
# SECTION 2: Logistic Regression (Classification)
# ============================================================

print("\n" + "=" * 55)
print("MODEL 2: LOGISTIC REGRESSION")
print("=" * 55)
print("""
Goal       : Predict a CATEGORY (0 or 1, yes or no, spam or not)
How it works: Like linear regression, but passes output through
              a sigmoid function to produce a probability (0 to 1).
              Predicts class 1 if probability ≥ 0.5.
Use cases  : Email spam detection, medical diagnosis, churn prediction
""")

X_clf = clf_df[["Age", "Experience", "Salary", "Score"]]
y_clf = clf_df["Promoted"]

X_tr, X_te, y_tr, y_te = train_test_split(
    X_clf, y_clf, test_size=0.2, random_state=42, stratify=y_clf)

scaler = StandardScaler()
X_tr_scaled = scaler.fit_transform(X_tr)
X_te_scaled  = scaler.transform(X_te)

model_log = LogisticRegression(random_state=42)
model_log.fit(X_tr_scaled, y_tr)

y_pred_log = model_log.predict(X_te_scaled)
acc = accuracy_score(y_te, y_pred_log)

print(f"Test Accuracy: {acc:.2%}")
print("\nDetailed Classification Report:")
print(classification_report(y_te, y_pred_log, target_names=["Not Promoted", "Promoted"]))
print("""
Precision = Of all predicted promoted, how many truly were promoted?
Recall    = Of all truly promoted, how many did we correctly catch?
F1-score  = Balance between Precision and Recall
""")

# Feature importance
feature_names = X_clf.columns
coefs = pd.Series(model_log.coef_[0], index=feature_names).abs().sort_values(ascending=False)
print("Feature importance (coefficient magnitude):")
print(coefs.round(3))

# ============================================================
# SECTION 3: K-Nearest Neighbors (KNN)
# ============================================================

print("\n" + "=" * 55)
print("MODEL 3: K-NEAREST NEIGHBORS (KNN)")
print("=" * 55)
print("""
Goal       : Classify a data point based on its 'k' nearest neighbors
How it works:
  1. For a new data point, find the k most similar training examples.
  2. Take a majority vote: whichever class has most neighbors wins.
Use cases  : Recommendation systems, anomaly detection, image recognition
Tip        : k=1 can overfit; try k=5 or k=7 to start.
""")

model_knn = KNeighborsClassifier(n_neighbors=5)
model_knn.fit(X_tr_scaled, y_tr)

y_pred_knn = model_knn.predict(X_te_scaled)
acc_knn = accuracy_score(y_te, y_pred_knn)
print(f"Test Accuracy with k=5: {acc_knn:.2%}")

# Try different k values
print("\nTrying different k values:")
k_values = [1, 3, 5, 7, 11, 15, 21]
for k in k_values:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_tr_scaled, y_tr)
    acc = accuracy_score(y_te, knn.predict(X_te_scaled))
    print(f"  k={k:>2}: accuracy = {acc:.2%}")

# ============================================================
# SECTION 4: Decision Trees
# ============================================================

print("\n" + "=" * 55)
print("MODEL 4: DECISION TREE")
print("=" * 55)
print("""
Goal       : Classify by asking a series of yes/no questions
How it works:
  - Splits data at each node using the feature that best separates classes.
  - Continues until all leaves are 'pure' or a stopping rule is met.
Use cases  : Very interpretable — great for explaining decisions.
             Medical triage, loan approval, fraud detection.
Tip        : Deep trees overfit. Use max_depth to control complexity.
""")

model_dt = DecisionTreeClassifier(max_depth=4, random_state=42)
model_dt.fit(X_tr, y_tr)  # No scaling needed for Decision Trees

y_pred_dt = model_dt.predict(X_te)
acc_dt = accuracy_score(y_te, y_pred_dt)
print(f"Test Accuracy: {acc_dt:.2%}")

# Print the tree in text form
print("\nDecision Tree Rules (depth=4):")
tree_rules = export_text(model_dt, feature_names=list(X_clf.columns))
print(tree_rules)

# Feature importance
fi = pd.Series(model_dt.feature_importances_, index=X_clf.columns)
fi = fi.sort_values(ascending=False)
print("Feature Importance from Decision Tree:")
print(fi.round(3))

# ============================================================
# SECTION 5: Model Training and Prediction Summary
# ============================================================

print("\n" + "=" * 55)
print("MODEL COMPARISON SUMMARY")
print("=" * 55)

summary = {
    "Logistic Regression": accuracy_score(y_te, y_pred_log),
    "KNN (k=5)":           accuracy_score(y_te, y_pred_knn),
    "Decision Tree":       accuracy_score(y_te, y_pred_dt),
}

print(f"\n{'Model':<25} {'Accuracy':>10}")
print("-" * 38)
for name, acc in sorted(summary.items(), key=lambda x: -x[1]):
    bar = "█" * int(acc * 30)
    print(f"{name:<25} {acc:>8.2%}  {bar}")

print("""
Notes:
  - Accuracy alone is not always the best metric (see Topic 18)
  - Results vary by dataset — no single best algorithm
  - Try multiple models and compare

General Guidelines:
  Linear Regression   → predict a number
  Logistic Regression → binary classification (simple, interpretable)
  KNN                 → non-linear, needs scaling, slow on large data
  Decision Tree       → easy to explain, no scaling needed, can overfit
""")

print("--- End of First ML Models ---")
