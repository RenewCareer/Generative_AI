# ============================================================
# TOPIC 5: Functions & Modular Programming
# ============================================================

# ============================================================
# SECTION 1: Defining and Calling Functions
# ============================================================

print("--- Defining Functions ---")

# A function is a reusable block of code
# Define with: def function_name():
#              (indented code block)

def greet():
    print("Hello! Welcome to Python.")

# Call the function (run it)
greet()
greet()  # Can call it as many times as you want

# ============================================================
# SECTION 2: Function Arguments and Return Values
# ============================================================

print("\n--- Arguments and Return Values ---")

# Arguments: inputs you pass to the function
def greet_person(name):
    print(f"Hello, {name}!")

greet_person("Alice")
greet_person("Bob")

# Multiple arguments
def add(a, b):
    result = a + b
    return result  # return sends a value back to the caller

total = add(5, 3)
print("5 + 3 =", total)

# A function can return multiple values (as a tuple)
def get_min_max(numbers):
    return min(numbers), max(numbers)

data = [4, 2, 9, 1, 7]
lowest, highest = get_min_max(data)
print(f"Min: {lowest}, Max: {highest}")

# Without return, a function returns None
def no_return():
    x = 10  # does work but returns nothing

result = no_return()
print("No return value:", result)   # None

# ============================================================
# SECTION 3: Default and Keyword Arguments
# ============================================================

print("\n--- Default Arguments ---")

# Default argument: used if the caller doesn't provide a value
def introduce(name, language="Python"):
    print(f"Hi, I'm {name} and I code in {language}.")

introduce("Alice")               # uses default "Python"
introduce("Bob", "JavaScript")   # overrides default

# Keyword arguments: pass by name (order doesn't matter)
def describe_student(name, age, city):
    print(f"{name} is {age} years old and lives in {city}.")

describe_student("Alice", 22, "Accra")
describe_student(age=25, city="Kumasi", name="Bob")  # keyword order irrelevant

# Default + keyword together
def power(base, exponent=2):
    return base ** exponent

print(power(3))         # 3^2 = 9 (uses default)
print(power(3, 3))      # 3^3 = 27
print(power(base=2, exponent=8))  # 2^8 = 256

# ============================================================
# SECTION 4: Lambda Functions (Anonymous Functions)
# ============================================================

print("\n--- Lambda Functions ---")

# Lambda: a short one-line function with no name
# Syntax: lambda arguments: expression

# Normal function:
def square(x):
    return x ** 2

# Same thing as a lambda:
square_lambda = lambda x: x ** 2

print(square(5))          # 25
print(square_lambda(5))   # 25

# Lambda with two arguments
multiply = lambda a, b: a * b
print(multiply(4, 7))     # 28

# Lambda is commonly used with built-in functions like sorted(), map(), filter()

# sorted() with a custom key
students = [("Alice", 85), ("Bob", 72), ("Charlie", 91)]
sorted_by_score = sorted(students, key=lambda s: s[1], reverse=True)
print("Sorted by score:", sorted_by_score)

# map(): apply a function to every item in a list
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))
print("Doubled:", doubled)  # [2, 4, 6, 8, 10]

# filter(): keep only items that match a condition
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print("Even numbers:", even_numbers)  # [2, 4]

# ============================================================
# SECTION 5: Scope (Local vs Global Variables)
# ============================================================

print("\n--- Scope ---")

# GLOBAL variable: defined outside any function, accessible everywhere
global_message = "I am global"

def show_global():
    print(global_message)  # Can read global variable

show_global()

# LOCAL variable: defined inside a function, only exists there
def my_function():
    local_var = "I am local"
    print(local_var)

my_function()
# print(local_var)  <-- This would cause: NameError: name 'local_var' is not defined

# When a local variable has the same name as a global, local wins inside the function
name = "Global Name"

def test_scope():
    name = "Local Name"   # This is a NEW local variable
    print("Inside function:", name)

test_scope()
print("Outside function:", name)   # Still "Global Name"

# Use global keyword to MODIFY a global variable from inside a function
counter = 0

def increment():
    global counter
    counter += 1

increment()
increment()
increment()
print("Counter:", counter)  # 3

# ============================================================
# SECTION 6: Importing Modules
# ============================================================

print("\n--- Importing Modules ---")

# Python has many built-in modules you can import

import math
print("Square root of 16:", math.sqrt(16))
print("Value of pi:", math.pi)
print("Ceiling of 4.2:", math.ceil(4.2))
print("Floor of 4.9:", math.floor(4.9))

import random
print("Random number (1-10):", random.randint(1, 10))
print("Random float (0-1):", round(random.random(), 4))

my_list = [1, 2, 3, 4, 5]
random.shuffle(my_list)
print("Shuffled list:", my_list)

import datetime
today = datetime.date.today()
print("Today's date:", today)

# Import specific functions from a module
from math import sqrt, factorial
print("sqrt(25):", sqrt(25))
print("5!:", factorial(5))

# Import with alias (shorter name)
import math as m
print("m.pi:", m.pi)

# ============================================================
# SECTION 7: Creating Reusable Python Scripts
# ============================================================

print("\n--- Reusable Functions ---")

# Good functions do ONE thing and do it well
# They can be tested and reused across many projects

def calculate_bmi(weight_kg, height_m):
    """Calculate BMI given weight in kg and height in meters."""
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)

def classify_bmi(bmi):
    """Return BMI category as a string."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

# Using the functions together
weight = 70
height = 1.75
bmi = calculate_bmi(weight, height)
category = classify_bmi(bmi)
print(f"Weight: {weight}kg, Height: {height}m")
print(f"BMI: {bmi} — Category: {category}")

# The if __name__ == "__main__" block:
# Code inside this block only runs when you execute THIS file directly.
# It does NOT run when another file imports this module.
# This is the standard way to write scripts in Python.

if __name__ == "__main__":
    print("\n--- Running as main script ---")
    print("This block only runs when you run this file directly.")
    print("It is skipped when another script imports this file.")

print("\n--- End of Functions ---")
