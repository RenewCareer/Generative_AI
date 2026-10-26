# ============================================================
# TOPIC 14: Seaborn – Statistical Data Visualization
# ============================================================
# Install: pip install seaborn matplotlib
# Seaborn is built ON TOP of Matplotlib.
# It creates beautiful statistical charts with less code.

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os

output_dir = "plots_seaborn"
os.makedirs(output_dir, exist_ok=True)

np.random.seed(42)

# Set a global Seaborn theme (once is enough)
sns.set_theme(style="whitegrid", palette="muted")

# ============================================================
# Build a Realistic Dataset
# ============================================================

n = 300
df = pd.DataFrame({
    "Age":        np.random.randint(22, 60, n),
    "Gender":     np.random.choice(["Male", "Female"], n, p=[0.55, 0.45]),
    "Education":  np.random.choice(["BSc", "MSc", "PhD"], n, p=[0.50, 0.35, 0.15]),
    "Department": np.random.choice(["Engineering", "Sales", "HR", "Finance"], n),
    "Experience": np.random.randint(0, 30, n),
    "Salary":     np.random.normal(65000, 18000, n).clip(25000, 130000).round(-2),
    "Score":      np.random.normal(72, 12, n).clip(30, 100).round(1),
    "Performance":np.random.choice([1, 2, 3, 4, 5], n, p=[0.05, 0.10, 0.30, 0.35, 0.20]),
})
# Add salary boost by experience
df["Salary"] = (df["Salary"] + df["Experience"] * 1200).clip(25000, 140000).round(-2)

# ============================================================
# SECTION 1: Distribution Plots
# ============================================================

print("Creating Distribution Plots...")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("Distribution Plots", fontsize=15, fontweight="bold")

# histplot: histogram with optional KDE (density curve)
sns.histplot(df["Salary"], bins=25, kde=True, ax=axes[0], color="steelblue")
axes[0].set_title("Salary Distribution")
axes[0].set_xlabel("Salary ($)")

# kdeplot: smooth density curve
sns.kdeplot(df["Score"], ax=axes[1], fill=True, color="coral", alpha=0.6)
axes[1].set_title("Score Density")
axes[1].set_xlabel("Score")

# Multiple KDE lines (comparing groups)
for gender, color in zip(["Male", "Female"], ["steelblue", "coral"]):
    sns.kdeplot(df[df["Gender"] == gender]["Salary"],
                ax=axes[2], fill=True, label=gender, alpha=0.4, color=color)
axes[2].set_title("Salary Distribution by Gender")
axes[2].legend()

plt.tight_layout()
plt.savefig(f"{output_dir}/01_distribution_plots.png", dpi=100)
plt.close()
print(f"  Saved: {output_dir}/01_distribution_plots.png")

# ============================================================
# SECTION 2: Box Plots and Violin Plots
# ============================================================

print("Creating Box and Violin Plots...")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Box plot: shows median, IQR, and outliers
sns.boxplot(data=df, x="Department", y="Salary", ax=axes[0], palette="Set2")
axes[0].set_title("Salary by Department — Box Plot")
axes[0].set_xlabel("Department")
axes[0].set_ylabel("Salary ($)")
axes[0].tick_params(axis="x", rotation=15)

# Violin plot: combines box plot + KDE density
sns.violinplot(data=df, x="Department", y="Salary", ax=axes[1],
               palette="Set3", inner="quartile")
axes[1].set_title("Salary by Department — Violin Plot")
axes[1].set_xlabel("Department")
axes[1].set_ylabel("Salary ($)")
axes[1].tick_params(axis="x", rotation=15)

plt.tight_layout()
plt.savefig(f"{output_dir}/02_box_violin_plots.png", dpi=100)
plt.close()
print(f"  Saved: {output_dir}/02_box_violin_plots.png")

# ============================================================
# SECTION 3: Bar Plot (with error bars)
# ============================================================

print("Creating Bar Plot...")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# barplot: mean + confidence interval automatically
sns.barplot(data=df, x="Department", y="Salary", hue="Gender",
            ax=axes[0], palette=["steelblue", "coral"], errorbar="sd")
axes[0].set_title("Mean Salary by Dept & Gender")
axes[0].tick_params(axis="x", rotation=15)
axes[0].legend(title="Gender")

# countplot: counts per category
sns.countplot(data=df, x="Department", hue="Education",
              ax=axes[1], palette="Set1")
axes[1].set_title("Employee Count by Dept & Education")
axes[1].tick_params(axis="x", rotation=15)
axes[1].legend(title="Education", fontsize=8)

plt.tight_layout()
plt.savefig(f"{output_dir}/03_bar_plots.png", dpi=100)
plt.close()
print(f"  Saved: {output_dir}/03_bar_plots.png")

# ============================================================
# SECTION 4: Heatmaps
# ============================================================

print("Creating Heatmap...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Correlation heatmap — the most commonly used heatmap in data science
numeric_df = df[["Age", "Experience", "Salary", "Score", "Performance"]]
corr_matrix = numeric_df.corr()

sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm",
            center=0, square=True, ax=axes[0],
            linewidths=0.5, cbar_kws={"shrink": 0.8})
axes[0].set_title("Correlation Heatmap")

# Pivot table heatmap — salary by dept and education
pivot = df.pivot_table(values="Salary", index="Department", columns="Education", aggfunc="mean")
sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd",
            ax=axes[1], linewidths=0.5, cbar_kws={"shrink": 0.8})
axes[1].set_title("Mean Salary by Dept & Education")

plt.tight_layout()
plt.savefig(f"{output_dir}/04_heatmaps.png", dpi=100)
plt.close()
print(f"  Saved: {output_dir}/04_heatmaps.png")

# ============================================================
# SECTION 5: Pair Plot
# ============================================================

print("Creating Pair Plot (this may take a moment)...")

# pairplot: scatter plot for every pair of numeric variables
# diagonal shows the distribution of each variable
pair_df = df[["Age", "Experience", "Salary", "Score", "Gender"]].sample(100, random_state=1)

pair_grid = sns.pairplot(pair_df, hue="Gender",
                          palette={"Male": "steelblue", "Female": "coral"},
                          diag_kind="kde", plot_kws={"alpha": 0.5, "s": 25})
pair_grid.figure.suptitle("Pair Plot — Numeric Variables by Gender",
                            y=1.02, fontsize=14, fontweight="bold")

plt.savefig(f"{output_dir}/05_pair_plot.png", dpi=90, bbox_inches="tight")
plt.close()
print(f"  Saved: {output_dir}/05_pair_plot.png")

# ============================================================
# SECTION 6: Scatter Plots & Visualizing Relationships
# ============================================================

print("Creating Relationship Plots...")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# scatterplot with color and size encoding
sns.scatterplot(data=df, x="Experience", y="Salary",
                hue="Department", size="Performance",
                sizes=(30, 150), alpha=0.7, ax=axes[0], palette="tab10")
axes[0].set_title("Experience vs Salary\n(color=Dept, size=Performance)")
axes[0].legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=7)

# regplot: scatter + regression line
sns.regplot(data=df, x="Experience", y="Salary",
            ax=axes[1], scatter_kws={"alpha": 0.3, "color": "steelblue"},
            line_kws={"color": "red", "linewidth": 2})
axes[1].set_title("Experience vs Salary — Regression Line")

plt.tight_layout()
plt.savefig(f"{output_dir}/06_scatter_relationship.png", dpi=100)
plt.close()
print(f"  Saved: {output_dir}/06_scatter_relationship.png")

# ============================================================
# Bonus: Strip and Swarm Plots
# ============================================================

print("Creating Strip and Swarm Plots...")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# stripplot: scatter where one axis is categorical
sns.stripplot(data=df, x="Department", y="Salary",
              hue="Gender", ax=axes[0], dodge=True,
              alpha=0.4, palette=["steelblue", "coral"])
axes[0].set_title("Salary Strip Plot by Department")
axes[0].tick_params(axis="x", rotation=15)

# swarmplot: like stripplot but points don't overlap
subset = df.sample(100, random_state=0)
sns.swarmplot(data=subset, x="Performance", y="Score",
              ax=axes[1], palette="viridis", size=4)
axes[1].set_title("Score by Performance Rating (Swarm)")

plt.tight_layout()
plt.savefig(f"{output_dir}/07_strip_swarm.png", dpi=100)
plt.close()
print(f"  Saved: {output_dir}/07_strip_swarm.png")

print(f"\nAll Seaborn plots saved to '{output_dir}/' folder.")
print("--- End of Seaborn ---")
