# ============================================================
# TOPIC 2: Python Fundamentals (Core Foundations)
# ============================================================

# ============================================================
# SECTION 1: Python Syntax and Indentation Rules
# ============================================================

# Python uses INDENTATION (spaces) to define blocks of code
# Unlike other languages that use { }, Python uses spaces/tabs
# Standard is 4 spaces per level

print("--- Indentation Example ---")

# Correct indentation:
if True:
    print("This is inside the if block")   # 4 spaces in
    print("Still inside the if block")     # 4 spaces in
print("This is outside the if block")      # Back to 0 spaces

# Python reads line by line — no semicolons needed at line end
# One statement per line (usually)

# You CAN write multiple statements on one line using semicolons
# but this is NOT recommended for beginners — keep it one per line
x = 5; y = 10  # possible but avoid this style

# ============================================================
# SECTION 2: Variables and Data Types
# ============================================================

print("\n--- Variables and Data Types ---")

# A variable stores a value. No need to declare a type first.
name = "Alice"          # str  (text / string)
age = 25                # int  (whole number)
height = 5.7            # float (decimal number)
is_student = True       # bool (True or False)

print(name)
print(age)
print(height)
print(is_student)

# Check the type of a variable using type()
print(type(name))       # <class 'str'>
print(type(age))        # <class 'int'>
print(type(height))     # <class 'float'>
print(type(is_student)) # <class 'bool'>

# Variable names:
# - Must start with a letter or underscore
# - Cannot start with a number
# - Cannot contain spaces (use underscores: my_variable)
# - Case-sensitive: name and Name are different variables

# ============================================================
# SECTION 3: Type Casting (Converting Between Types)
# ============================================================

print("\n--- Type Casting ---")

# Convert string to integer
age_str = "30"
age_int = int(age_str)
print("String to int:", age_int, type(age_int))

# Convert integer to float
num = 7
num_float = float(num)
print("Int to float:", num_float, type(num_float))

# Convert float to int (cuts off decimal — does NOT round)
price = 9.99
price_int = int(price)
print("Float to int:", price_int)  # Output: 9

# Convert number to string (useful when building messages)
score = 95
message = "Your score is: " + str(score)
print(message)

# Convert string to list of characters
word = "hello"
letters = list(word)
print("String to list:", letters)  # ['h', 'e', 'l', 'l', 'o']

# ============================================================
# SECTION 4: Input and Output Operations
# ============================================================

print("\n--- Input and Output ---")

# OUTPUT: print() displays values
print("Hello!")                          # simple print
print("Name:", name, "Age:", age)        # multiple values
print(f"My name is {name} and I am {age} years old.")  # f-string (recommended)

# Formatting with f-strings (most modern and readable way)
pi = 3.14159
print(f"Pi rounded to 2 decimal places: {pi:.2f}")
print(f"Pi rounded to 4 decimal places: {pi:.4f}")

# INPUT: input() reads text from the user
# Uncomment the lines below to try it interactively:

# user_name = input("What is your name? ")
# print(f"Hello, {user_name}! Welcome to Python.")

# NOTE: input() always returns a STRING, so convert if needed:
# user_age = int(input("How old are you? "))

# ============================================================
# SECTION 5: Comments and Code Readability
# ============================================================

print("\n--- Comments ---")

# This is a single-line comment — Python ignores this line

# Use comments to explain WHY your code does something,
# not just WHAT it does.

# Good comment:
salary = 50000
tax_rate = 0.2
# Ghana PAYE rate for this income bracket is 20%
tax = salary * tax_rate

# Bad comment (just repeats the code — not helpful):
# multiply salary by tax_rate
tax = salary * tax_rate  # noqa

# Multi-line comments use triple quotes (also used for docstrings)
"""
This is a multi-line comment (or docstring).
You can write as many lines as you need.
Python ignores this block.
"""

# Printing a clean separator to organize output
print("-" * 40)
print("End of Python Fundamentals")
print("-" * 40)
