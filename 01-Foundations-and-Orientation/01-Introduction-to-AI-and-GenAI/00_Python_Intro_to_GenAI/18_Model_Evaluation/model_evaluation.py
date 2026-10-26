# ============================================================
# TOPIC 18: Model Evaluation (Basics)
# ============================================================
# Install: pip install scikit-learn pandas numpy matplotlib seaborn

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, ConfusionMatrixDisplay,
    mean_absolute_error, mean_squared_error, r2_score
)
from sklearn.linear_model import LinearRegression

np.random.seed(42)
output_dir = "plots_evaluation"
os.makedirs(output_dir, exist_ok=True)

# Build datasets
n = 400
X_clf = pd.DataFrame({
    "Age":        np.random.randint(22, 55, n),
    "Experience": np.random.randint(0, 25, n),
    "Salary":     np.random.normal(60000, 15000, n).clip(25000, 120000),
    "Score":      np.random.normal(72, 12, n).clip(30, 100),
})
y_clf = (X_clf["Salary"] > 65000).astype(int)
y_clf[np.random.choice(n, 40)] = 1 - y_clf[np.random.choice(n, 40)]  # Add noise

X_tr, X_te, y_tr, y_te = train_test_split(X_clf, y_clf, test_size=0.2,
                                            random_state=42, stratify=y_clf)
sc = StandardScaler()
X_tr_s = sc.fit_transform(X_tr)
X_te_s  = sc.transform(X_te)

# ============================================================
# SECTION 1: Accuracy, Precision, Recall, F1-Score
# ============================================================

print("=" * 60)
print("MODEL EVALUATION METRICS")
print("=" * 60)
print("""
Four key classification metrics:

  ACCURACY  = (Correct predictions) / (Total predictions)
              Simple but misleading when classes are unbalanced.

  PRECISION = Of all predicted POSITIVE, how many are truly positive?
              "When we say Yes, how often are we right?"
              → Important when false positives are costly
                (e.g., flagging a healthy person as sick)

  RECALL    = Of all truly POSITIVE, how many did we catch?
              "How many real positives did we find?"
              → Important when false negatives are costly
                (e.g., missing a cancer patient)

  F1-SCORE  = Harmonic mean of Precision and Recall
              Best single metric when you need balance of both.
              F1 = 2 * (Precision * Recall) / (Precision + Recall)
""")

model = LogisticRegression(random_state=42)
model.fit(X_tr_s, y_tr)
y_pred = model.predict(X_te_s)

acc  = accuracy_score(y_te, y_pred)
prec = precision_score(y_te, y_pred)
rec  = recall_score(y_te, y_pred)
f1   = f1_score(y_te, y_pred)

print("--- Logistic Regression Results ---")
print(f"  Accuracy  : {acc:.2%}")
print(f"  Precision : {prec:.2%}")
print(f"  Recall    : {rec:.2%}")
print(f"  F1-Score  : {f1:.2%}")

# Manual calculation to explain
print("""
Manual example with small numbers:
  Suppose you have 100 patients; 20 actually have the disease.
  Your model predicts 18 have disease:
    - 15 correct (True Positive)
    - 3 incorrect — healthy people flagged (False Positive)
    - 5 missed real cases (False Negative)
    - 77 correctly called healthy (True Negative)

  Precision = 15 / (15+3) = 83%  (of flagged, 83% are real)
  Recall    = 15 / (15+5) = 75%  (caught 75% of real cases)
  Accuracy  = (15+77)/100 = 92%  (seems great, but we missed 5 sick!)
""")

# ============================================================
# SECTION 2: Confusion Matrix
# ============================================================

print("--- Confusion Matrix ---")
print("""
A Confusion Matrix shows all 4 combinations of predicted vs actual:

               Predicted NO    Predicted YES
  Actual NO  |  True Negative | False Positive |
  Actual YES |  False Negative | True Positive |

  True Positive  (TP): Correctly predicted YES
  True Negative  (TN): Correctly predicted NO
  False Positive (FP): Predicted YES but actually NO  (Type I Error)
  False Negative (FN): Predicted NO  but actually YES (Type II Error)
""")

cm = confusion_matrix(y_te, y_pred)
tn, fp, fn, tp = cm.ravel()

print(f"Confusion Matrix:")
print(f"  True Negatives  (TN): {tn}")
print(f"  False Positives (FP): {fp}")
print(f"  False Negatives (FN): {fn}")
print(f"  True Positives  (TP): {tp}")

# Plot confusion matrix
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                               display_labels=["Class 0", "Class 1"])
disp.plot(ax=axes[0], colorbar=False, cmap="Blues")
axes[0].set_title("Confusion Matrix — Logistic Regression")

# Annotated version
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=axes[1],
            xticklabels=["Pred: No", "Pred: Yes"],
            yticklabels=["Actual: No", "Actual: Yes"])
for i, label in enumerate([f"TN={tn}", f"FP={fp}", f"FN={fn}", f"TP={tp}"]):
    row, col = divmod(i, 2)
    axes[1].text(col + 0.5, row + 0.75, label,
                 ha="center", va="center", color="gray", fontsize=8)
axes[1].set_title("Confusion Matrix with Labels")

plt.tight_layout()
plt.savefig(f"{output_dir}/01_confusion_matrix.png", dpi=100)
plt.close()
print(f"Plot saved: {output_dir}/01_confusion_matrix.png")

# ============================================================
# SECTION 3: Metrics for Regression
# ============================================================

print("\n--- Regression Evaluation Metrics ---")
print("""
For regression (predicting numbers), use:

  MAE  (Mean Absolute Error)  : Average absolute difference
  RMSE (Root Mean Sq Error)   : Penalizes large errors more
  R²   (R-squared)            : % of variance explained (0 to 1)
                                 1.0 = perfect, 0.0 = baseline guess
""")

exp = np.random.randint(0, 30, 200).reshape(-1, 1)
sal = 28000 + exp.ravel() * 2400 + np.random.normal(0, 5000, 200)
X_r_tr, X_r_te, y_r_tr, y_r_te = train_test_split(exp, sal, test_size=0.2, random_state=42)

reg_model = LinearRegression()
reg_model.fit(X_r_tr, y_r_tr)
y_r_pred = reg_model.predict(X_r_te)

mae  = mean_absolute_error(y_r_te, y_r_pred)
rmse = np.sqrt(mean_squared_error(y_r_te, y_r_pred))
r2   = r2_score(y_r_te, y_r_pred)

print(f"Linear Regression — Salary Prediction:")
print(f"  MAE  : ${mae:,.0f}")
print(f"  RMSE : ${rmse:,.0f}")
print(f"  R²   : {r2:.3f}")

# ============================================================
# SECTION 4: Overfitting vs Underfitting
# ============================================================

print("\n--- Overfitting vs Underfitting ---")
print("""
UNDERFITTING (High Bias):
  - Model is too simple; misses the real pattern in the data.
  - Bad performance on BOTH training AND test data.
  - Cause: too few features, model too simple, too few training steps.

OVERFITTING (High Variance):
  - Model is too complex; memorizes the training data including noise.
  - Great on training data, poor on test data.
  - Cause: model too complex, too little data, too many features.

GOOD FIT:
  - Model generalizes well.
  - Similar performance on training and test data.

           Underfitting     Good Fit      Overfitting
Train Acc:     Low            High           Very High
Test Acc :     Low            High           Low
Gap      :     Small          Small          Large
""")

print("Demonstrating with Decision Trees at different depths:")
print(f"\n{'Depth':<8} {'Train Acc':>10} {'Test Acc':>10} {'Gap':>8}")
print("-" * 40)
for depth in [1, 2, 3, 5, 8, 15, None]:
    dt = DecisionTreeClassifier(max_depth=depth, random_state=42)
    dt.fit(X_tr_s, y_tr)
    train_acc = accuracy_score(y_tr, dt.predict(X_tr_s))
    test_acc  = accuracy_score(y_te, dt.predict(X_te_s))
    gap       = train_acc - test_acc
    label = str(depth) if depth else "None (full)"
    print(f"{label:<8} {train_acc:>10.2%} {test_acc:>10.2%} {gap:>8.2%}")

print("""
Observation:
  depth=1   → underfitting (too simple)
  depth=3-5 → good balance
  depth=None → overfitting (memorizes everything, test drops)
""")

# ============================================================
# SECTION 5: Cross-Validation
# ============================================================

print("--- Cross-Validation ---")
print("""
Cross-Validation: more reliable evaluation than a single train/test split.

  K-Fold CV (e.g., k=5):
    1. Split data into 5 equal "folds"
    2. Train on 4 folds, test on 1 fold
    3. Repeat 5 times (each fold is the test set once)
    4. Average the 5 scores

  Result: more stable estimate of real-world performance.
""")

from sklearn.model_selection import cross_val_score

models = {
    "Logistic Regression": LogisticRegression(random_state=42),
    "Decision Tree (d=3)": DecisionTreeClassifier(max_depth=3, random_state=42),
    "Decision Tree (d=8)": DecisionTreeClassifier(max_depth=8, random_state=42),
}

print(f"\n{'Model':<25} {'CV Mean':>9} {'CV Std':>9} {'95% CI':>18}")
print("-" * 65)
for name, mdl in models.items():
    cv_scores = cross_val_score(mdl, sc.fit_transform(X_clf), y_clf,
                                 cv=5, scoring="accuracy")
    mean = cv_scores.mean()
    std  = cv_scores.std()
    print(f"{name:<25} {mean:>9.2%} {std:>9.3f}  [{mean-2*std:.2%}, {mean+2*std:.2%}]")

# Plot train vs test accuracy across depths
depths = range(1, 16)
train_accs, test_accs = [], []
for d in depths:
    dt = DecisionTreeClassifier(max_depth=d, random_state=42)
    dt.fit(X_tr_s, y_tr)
    train_accs.append(accuracy_score(y_tr, dt.predict(X_tr_s)))
    test_accs.append(accuracy_score(y_te, dt.predict(X_te_s)))

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(depths, train_accs, "o-", label="Training Accuracy", color="blue")
ax.plot(depths, test_accs,  "s-", label="Test Accuracy",     color="red")
ax.axvline(x=3, linestyle="--", color="green", alpha=0.7, label="Sweet spot (~depth 3)")
ax.fill_between(depths, train_accs, test_accs, alpha=0.1, color="gray", label="Overfit gap")
ax.set_title("Overfitting vs Underfitting — Decision Tree Depth", fontsize=13)
ax.set_xlabel("Max Tree Depth")
ax.set_ylabel("Accuracy")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{output_dir}/02_overfit_underfit.png", dpi=100)
plt.close()
print(f"\nPlot saved: {output_dir}/02_overfit_underfit.png")

print("\n--- End of Model Evaluation ---")
