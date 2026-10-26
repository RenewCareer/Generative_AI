# ============================================================
# TOPIC 8: NumPy – Numerical Computing
# ============================================================
# Install: pip install numpy
# Import convention: import numpy as np

import numpy as np

# ============================================================
# SECTION 1: Introduction to NumPy
# ============================================================

print("--- What is NumPy? ---")
# NumPy = Numerical Python
# It provides the 'array' — a powerful, fast container for numbers.
# It is the foundation of Pandas, Matplotlib, and Scikit-Learn.
# Operations on NumPy arrays are much faster than Python lists.

print("NumPy version:", np.__version__)

# ============================================================
# SECTION 2: Arrays vs Lists
# ============================================================

print("\n--- Arrays vs Lists ---")

# Python list
py_list = [1, 2, 3, 4, 5]

# NumPy array (1D)
np_array = np.array([1, 2, 3, 4, 5])

print("Python list:", py_list)
print("NumPy array:", np_array)
print("Type:", type(np_array))        # <class 'numpy.ndarray'>
print("Data type:", np_array.dtype)   # int64 (or similar)

# Key difference: array operations work on ALL elements at once
py_doubled = [x * 2 for x in py_list]     # List: need a loop
np_doubled = np_array * 2                  # NumPy: direct operation!
print("List doubled:", py_doubled)
print("Array doubled:", np_doubled)

# Create arrays in different ways
zeros = np.zeros(5)           # [0. 0. 0. 0. 0.]
ones = np.ones(5)             # [1. 1. 1. 1. 1.]
range_arr = np.arange(0, 10, 2)  # [0 2 4 6 8]  (start, stop, step)
linspace = np.linspace(0, 1, 5)  # 5 evenly spaced values between 0 and 1
random_arr = np.random.rand(5)   # 5 random floats between 0 and 1
full_arr = np.full(4, 7)        # [7 7 7 7]

print("\nzeros:", zeros)
print("ones:", ones)
print("arange(0,10,2):", range_arr)
print("linspace(0,1,5):", linspace)
print("random:", np.round(random_arr, 3))
print("full(4,7):", full_arr)

# ============================================================
# SECTION 3: Array Indexing and Slicing
# ============================================================

print("\n--- Indexing and Slicing ---")

arr = np.array([10, 20, 30, 40, 50, 60, 70])

# Indexing (same as lists — starts at 0)
print("First element:", arr[0])    # 10
print("Last element:", arr[-1])    # 70
print("Third element:", arr[2])    # 30

# Slicing [start:stop:step]
print("First 3:", arr[:3])         # [10 20 30]
print("Last 3:", arr[-3:])         # [50 60 70]
print("Every 2nd:", arr[::2])      # [10 30 50 70]
print("Reversed:", arr[::-1])      # [70 60 50 40 30 20 10]

# 2D Array (Matrix)
matrix = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
])

print("\n2D array (matrix):")
print(matrix)
print("Shape:", matrix.shape)    # (3, 3) — 3 rows, 3 cols
print("Dimensions:", matrix.ndim) # 2
print("Size:", matrix.size)       # 9 total elements

# Indexing 2D: [row, column]
print("Row 0, Col 1:", matrix[0, 1])    # 2
print("Row 2, Col 2:", matrix[2, 2])    # 9

# Slicing 2D: [rows, columns]
print("First 2 rows:\n", matrix[:2, :])    # rows 0 and 1
print("Last column:\n", matrix[:, -1])     # all rows, last column
print("Middle value:", matrix[1, 1])        # 5

# Boolean indexing (very powerful for data filtering!)
arr = np.array([5, 12, 8, 20, 3, 17, 9])
mask = arr > 10                        # Creates array of True/False
print("\nOriginal:", arr)
print("Mask (>10):", mask)
print("Values > 10:", arr[mask])       # [12 20 17]

# Shorthand
print("Values <= 8:", arr[arr <= 8])   # [5 8 3]

# ============================================================
# SECTION 4: Mathematical Operations
# ============================================================

print("\n--- Mathematical Operations ---")

a = np.array([1, 2, 3, 4, 5])
b = np.array([10, 20, 30, 40, 50])

# Element-wise operations
print("a + b:", a + b)         # [11 22 33 44 55]
print("a * b:", a * b)         # [10 40 90 160 250]
print("b / a:", b / a)         # [10. 10. 10. 10. 10.]
print("a ** 2:", a ** 2)       # [1  4  9  16  25]
print("sqrt(b):", np.sqrt(b))  # square root of each

# Aggregate functions
print("\nSum:", np.sum(a))
print("Mean:", np.mean(a))
print("Median:", np.median(a))
print("Std Dev:", np.std(a))
print("Variance:", np.var(a))
print("Min:", np.min(a))
print("Max:", np.max(a))
print("Cumulative sum:", np.cumsum(a))  # [1 3 6 10 15]

# Matrix multiplication (dot product)
m1 = np.array([[1, 2], [3, 4]])
m2 = np.array([[5, 6], [7, 8]])
print("\nMatrix multiplication:")
print(np.dot(m1, m2))

# Universal functions (ufuncs) — fast element-wise math
angles = np.array([0, 30, 45, 60, 90])
angles_rad = np.deg2rad(angles)
print("\nSin of angles:", np.round(np.sin(angles_rad), 3))
print("Exp:", np.exp([1, 2, 3]))         # e^1, e^2, e^3
print("Log:", np.round(np.log([1, 10, 100]), 2))

# ============================================================
# SECTION 5: Broadcasting
# ============================================================

print("\n--- Broadcasting ---")

# Broadcasting allows operations between arrays of different shapes
# NumPy automatically "stretches" the smaller array to match

arr = np.array([1, 2, 3, 4, 5])
print("arr + 10:", arr + 10)   # 10 is broadcast to [10,10,10,10,10]
print("arr * 3:", arr * 3)
print("arr ** 2:", arr ** 2)

# Broadcasting with 2D arrays
matrix = np.array([[1, 2, 3],
                   [4, 5, 6],
                   [7, 8, 9]])

row_to_add = np.array([10, 20, 30])  # 1D added to each row
print("\nMatrix + row_to_add:")
print(matrix + row_to_add)

# Normalizing data (a common data preprocessing step)
data = np.array([150, 200, 180, 220, 170])
normalized = (data - data.mean()) / data.std()
print("\nOriginal data:", data)
print("Normalized:", np.round(normalized, 3))

# ============================================================
# SECTION 6: Handling Missing Values
# ============================================================

print("\n--- Handling Missing Values ---")

# NumPy uses NaN (Not a Number) for missing numeric values
data_with_nan = np.array([10, 20, np.nan, 40, np.nan, 60])
print("Data:", data_with_nan)

# Regular functions don't ignore NaN:
print("np.mean (fails):", np.mean(data_with_nan))    # Returns nan

# Use nan-safe functions:
print("np.nanmean:", np.nanmean(data_with_nan))       # 26.0
print("np.nansum:", np.nansum(data_with_nan))          # 130.0
print("np.nanstd:", np.round(np.nanstd(data_with_nan), 2))
print("np.nanmax:", np.nanmax(data_with_nan))

# Check which values are NaN
nan_mask = np.isnan(data_with_nan)
print("NaN positions:", nan_mask)    # [False False True False True False]
print("Count of NaNs:", np.sum(nan_mask))  # 2

# Replace NaN with a value (e.g., the mean)
mean_val = np.nanmean(data_with_nan)
data_filled = np.where(np.isnan(data_with_nan), mean_val, data_with_nan)
print("After filling NaN with mean:", data_filled)

print("\n--- End of NumPy ---")
