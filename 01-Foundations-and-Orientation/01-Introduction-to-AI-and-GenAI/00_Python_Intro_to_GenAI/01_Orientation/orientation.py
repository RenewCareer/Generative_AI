# ============================================================
# TOPIC 1: Orientation & Environment Setup
# ============================================================
# Python is a beginner-friendly programming language widely used
# in Data Science, Machine Learning, and Generative AI.
# It is popular because:
#   - It has simple, readable syntax (reads almost like English)
#   - It has thousands of powerful libraries (NumPy, Pandas, TensorFlow)
#   - It is free and open source
#   - It has a huge community with lots of tutorials and support

# ============================================================
# SECTION 1: Your First Python Program
# ============================================================

# The print() function displays output to the screen
print("Hello, World!")
print("Welcome to Python for Data Science & GenAI!")

# You can print numbers too
print(42)
print(3.14)

# You can print multiple things at once using commas
print("My name is", "Alice", "and I am", 25, "years old")

# ============================================================
# SECTION 2: Python as a Calculator
# ============================================================

# Python can do math right away - no setup needed
print("\n--- Python as a Calculator ---")
print(5 + 3)      # Addition
print(10 - 4)     # Subtraction
print(6 * 7)      # Multiplication
print(15 / 4)     # Division (gives decimal)
print(15 // 4)    # Floor division (gives whole number)
print(15 % 4)     # Modulus (remainder)
print(2 ** 10)    # Power (2 to the power of 10)

# ============================================================
# SECTION 3: Understanding Scripts vs Notebooks
# ============================================================

# A SCRIPT (.py file) like this one:
#   - Runs top to bottom all at once
#   - Good for automation and production code
#   - Run it with: python orientation.py

# A NOTEBOOK (.ipynb file - Jupyter Notebook):
#   - Runs one cell at a time
#   - Good for learning, exploring data, and visualization
#   - Mixes code, output, and text together

# ============================================================
# SECTION 4: Checking Your Python Version
# ============================================================

import sys  # sys is a built-in module (no installation needed)

print("\n--- Python Version Info ---")
print("Python version:", sys.version)
print("Python version number:", sys.version_info.major, ".", sys.version_info.minor)

# For Data Science, Python 3.8 or above is recommended

# ============================================================
# SECTION 5: Checking if Key Libraries Are Installed
# ============================================================

print("\n--- Checking Installed Libraries ---")

# We try to import each library and report if it's available
libraries = ["numpy", "pandas", "matplotlib", "seaborn", "sklearn"]

for lib in libraries:
    try:
        __import__(lib)
        print(f"  {lib} -- INSTALLED")
    except ImportError:
        print(f"  {lib} -- NOT FOUND (install with: pip install {lib})")

# ============================================================
# SECTION 6: How to Install Libraries (Reference)
# ============================================================

# To install a library, open your terminal / command prompt and type:
#
#   pip install numpy
#   pip install pandas
#   pip install matplotlib seaborn scikit-learn
#
# With Anaconda, you can also use:
#   conda install numpy
#
# To install everything at once (recommended for this course):
#   pip install numpy pandas matplotlib seaborn scikit-learn jupyter

print("\n--- Setup Complete! ---")
print("You are ready to start learning Python for Data Science & GenAI.")
