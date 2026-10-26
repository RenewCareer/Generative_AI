# ============================================================
# TOPIC 13: Matplotlib – Data Visualization
# ============================================================
# Install: pip install matplotlib
# Run this file to generate and save plots.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend for saving files

import os
output_dir = "plots_matplotlib"
os.makedirs(output_dir, exist_ok=True)

np.random.seed(42)

# ============================================================
# SECTION 1: Introduction – The Anatomy of a Matplotlib Plot
# ============================================================

print("--- Introduction to Matplotlib ---")
print("""
Key concepts:
  Figure  : the whole image / canvas (like a page)
  Axes    : the actual plot area within a figure (with x and y axis)
  Plot    : the drawn chart (line, bar, scatter, etc.)

Workflow:
  1. Create a figure:  fig, ax = plt.subplots()
  2. Draw on the axes: ax.plot(x, y)
  3. Add labels:       ax.set_title(), ax.set_xlabel(), ax.set_ylabel()
  4. Show or save:     plt.show()  or  plt.savefig("file.png")
""")

# ============================================================
# SECTION 2: Line Plot
# ============================================================

print("Creating Line Plot...")

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
sales_2023 = [120, 135, 148, 162, 175, 190, 180, 168, 155, 170, 185, 200]
sales_2024 = [130, 142, 160, 172, 188, 202, 195, 180, 170, 185, 200, 220]

fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(months, sales_2023, marker="o", label="2023", color="blue", linewidth=2)
ax.plot(months, sales_2024, marker="s", label="2024", color="orange", linewidth=2, linestyle="--")

ax.set_title("Monthly Sales Comparison (2023 vs 2024)", fontsize=14, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Sales (Units)")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{output_dir}/01_line_plot.png", dpi=100)
plt.close()
print(f"  Saved: {output_dir}/01_line_plot.png")

# ============================================================
# SECTION 3: Bar Chart
# ============================================================

print("Creating Bar Chart...")

departments = ["Engineering", "Sales", "HR", "Finance", "Marketing"]
avg_salary = [85000, 65000, 58000, 72000, 60000]
colors = ["#2196F3", "#FF9800", "#4CAF50", "#9C27B0", "#F44336"]

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(departments, avg_salary, color=colors, edgecolor="white", linewidth=0.8)

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 500,
            f"${height:,.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

ax.set_title("Average Salary by Department", fontsize=14, fontweight="bold")
ax.set_xlabel("Department")
ax.set_ylabel("Average Salary ($)")
ax.set_ylim(0, max(avg_salary) * 1.15)
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig(f"{output_dir}/02_bar_chart.png", dpi=100)
plt.close()
print(f"  Saved: {output_dir}/02_bar_chart.png")

# Horizontal bar chart
fig, ax = plt.subplots(figsize=(8, 5))
sorted_idx = np.argsort(avg_salary)
ax.barh([departments[i] for i in sorted_idx],
         [avg_salary[i] for i in sorted_idx],
         color="steelblue")
ax.set_title("Average Salary by Department (Horizontal)", fontsize=13)
ax.set_xlabel("Average Salary ($)")
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{output_dir}/02b_bar_horizontal.png", dpi=100)
plt.close()
print(f"  Saved: {output_dir}/02b_bar_horizontal.png")

# ============================================================
# SECTION 4: Histogram
# ============================================================

print("Creating Histogram...")

scores = np.random.normal(70, 12, 500)

fig, ax = plt.subplots(figsize=(8, 5))

n, bins, patches = ax.hist(scores, bins=20, color="steelblue",
                            edgecolor="white", alpha=0.8)

# Color bars differently based on score range
for patch, left_edge in zip(patches, bins):
    if left_edge < 50:
        patch.set_facecolor("#F44336")  # Fail: red
    elif left_edge < 70:
        patch.set_facecolor("#FF9800")  # Average: orange
    else:
        patch.set_facecolor("#4CAF50")  # Good: green

ax.axvline(scores.mean(), color="navy", linestyle="--", label=f"Mean = {scores.mean():.1f}", linewidth=2)
ax.axvline(np.median(scores), color="red", linestyle=":", label=f"Median = {np.median(scores):.1f}", linewidth=2)

ax.set_title("Distribution of Student Scores", fontsize=14, fontweight="bold")
ax.set_xlabel("Score")
ax.set_ylabel("Number of Students")
ax.legend()

plt.tight_layout()
plt.savefig(f"{output_dir}/03_histogram.png", dpi=100)
plt.close()
print(f"  Saved: {output_dir}/03_histogram.png")

# ============================================================
# SECTION 5: Scatter Plot
# ============================================================

print("Creating Scatter Plot...")

experience = np.random.randint(0, 30, 150)
salary = 30000 + experience * 2000 + np.random.normal(0, 8000, 150)
departments_list = np.random.choice(["Engineering", "Sales", "HR"], 150)

fig, ax = plt.subplots(figsize=(8, 5))

dept_colors = {"Engineering": "blue", "Sales": "orange", "HR": "green"}
for dept, color in dept_colors.items():
    mask = departments_list == dept
    ax.scatter(experience[mask], salary[mask],
               c=color, label=dept, alpha=0.6, edgecolors="white", s=60)

# Add trend line
z = np.polyfit(experience, salary, 1)
p = np.poly1d(z)
x_line = np.linspace(0, 30, 100)
ax.plot(x_line, p(x_line), color="red", linestyle="--", linewidth=1.5, label="Trend line")

ax.set_title("Experience vs. Salary by Department", fontsize=14, fontweight="bold")
ax.set_xlabel("Years of Experience")
ax.set_ylabel("Salary ($)")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{output_dir}/04_scatter_plot.png", dpi=100)
plt.close()
print(f"  Saved: {output_dir}/04_scatter_plot.png")

# ============================================================
# SECTION 6: Subplots – Multiple Charts in One Figure
# ============================================================

print("Creating Subplots...")

ages = np.random.randint(22, 60, 200)
salaries = np.random.normal(60000, 15000, 200)
performance = np.random.choice([1, 2, 3, 4, 5], 200)
genders = np.random.choice(["Male", "Female"], 200)

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Employee Dashboard", fontsize=16, fontweight="bold")

# Plot 1: Age histogram
axes[0, 0].hist(ages, bins=15, color="skyblue", edgecolor="white")
axes[0, 0].set_title("Age Distribution")
axes[0, 0].set_xlabel("Age")
axes[0, 0].set_ylabel("Count")

# Plot 2: Salary histogram
axes[0, 1].hist(salaries, bins=20, color="salmon", edgecolor="white")
axes[0, 1].axvline(salaries.mean(), color="darkred", linestyle="--", label=f"Mean: ${salaries.mean():,.0f}")
axes[0, 1].set_title("Salary Distribution")
axes[0, 1].set_xlabel("Salary ($)")
axes[0, 1].legend()

# Plot 3: Performance bar chart
perf_counts = pd.Series(performance).value_counts().sort_index()
axes[1, 0].bar(perf_counts.index, perf_counts.values, color="mediumseagreen", edgecolor="white")
axes[1, 0].set_title("Performance Ratings")
axes[1, 0].set_xlabel("Rating (1-5)")
axes[1, 0].set_ylabel("Count")

# Plot 4: Gender pie chart
gender_counts = pd.Series(genders).value_counts()
axes[1, 1].pie(gender_counts, labels=gender_counts.index,
               autopct="%1.1f%%", colors=["steelblue", "lightcoral"], startangle=90)
axes[1, 1].set_title("Gender Distribution")

plt.tight_layout()
plt.savefig(f"{output_dir}/05_subplots.png", dpi=100)
plt.close()
print(f"  Saved: {output_dir}/05_subplots.png")

# ============================================================
# SECTION 7: Plot Customization
# ============================================================

print("Creating Customized Plot...")

x = np.linspace(0, 2 * np.pi, 200)

fig, ax = plt.subplots(figsize=(10, 5))

# Multiple styled lines
ax.plot(x, np.sin(x), color="#E91E63", linewidth=2.5, label="sin(x)", linestyle="-")
ax.plot(x, np.cos(x), color="#2196F3", linewidth=2.5, label="cos(x)", linestyle="--")
ax.plot(x, np.sin(x) * np.cos(x), color="#4CAF50", linewidth=2, label="sin(x)·cos(x)", linestyle=":")

# Reference line
ax.axhline(y=0, color="gray", linewidth=0.8, linestyle="-")
ax.axvline(x=np.pi, color="gray", linewidth=0.8, linestyle="--", label="x = π")

# Fill under sin(x) where positive
ax.fill_between(x, 0, np.sin(x), where=(np.sin(x) > 0), alpha=0.1, color="#E91E63")

# Annotations
ax.annotate("Max sin(x)", xy=(np.pi / 2, 1), xytext=(np.pi / 2 + 0.5, 1.1),
            arrowprops=dict(arrowstyle="->", color="black"), fontsize=9)

# Axis labels and title
ax.set_title("Trigonometric Functions", fontsize=14, fontweight="bold")
ax.set_xlabel("x (radians)", fontsize=11)
ax.set_ylabel("y", fontsize=11)

# Custom x ticks
ax.set_xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
ax.set_xticklabels(["0", "π/2", "π", "3π/2", "2π"])

ax.legend(loc="upper right")
ax.grid(True, alpha=0.2)

# Set background color
ax.set_facecolor("#f8f9fa")

plt.tight_layout()
plt.savefig(f"{output_dir}/06_customized_plot.png", dpi=100)
plt.close()
print(f"  Saved: {output_dir}/06_customized_plot.png")

print(f"\nAll Matplotlib plots saved to '{output_dir}/' folder.")
print("--- End of Matplotlib ---")
