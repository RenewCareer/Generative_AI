# ============================================================
# TOPIC 6: Error Handling & Debugging
# ============================================================

# ============================================================
# SECTION 1: Common Python Errors
# ============================================================

print("--- Common Python Errors (What They Mean) ---")

# 1. SyntaxError: code is written incorrectly — Python can't even read it
#    Example: if x == 5   <-- missing colon at end
#    Fix: check for typos, missing colons, unclosed brackets

# 2. NameError: you used a variable that doesn't exist
#    Example: print(my_var)  -- if my_var was never defined

# 3. TypeError: wrong type of data used in an operation
#    Example: "hello" + 5   -- can't add string and int directly

# 4. IndexError: trying to access an index that doesn't exist
#    Example: my_list[10] -- if list only has 5 items

# 5. KeyError: trying to access a key that doesn't exist in a dictionary
#    Example: my_dict["missing_key"]

# 6. ZeroDivisionError: dividing by zero
#    Example: 10 / 0

# 7. ValueError: correct type but wrong value
#    Example: int("hello")  -- "hello" can't be converted to int

# 8. AttributeError: calling a method that doesn't exist on an object
#    Example: "hello".sort()  -- strings don't have a .sort() method

print("Common errors listed above — see comments for details.")

# ============================================================
# SECTION 2: try–except Blocks
# ============================================================

print("\n--- try-except ---")

# Without error handling (this would crash):
# result = 10 / 0   <-- ZeroDivisionError

# WITH try-except, the program handles the error gracefully:
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Error: Cannot divide by zero!")

# Another example: invalid type conversion
try:
    number = int("abc")
except ValueError:
    print("Error: 'abc' cannot be converted to an integer.")

# The try block contains code that might fail
# The except block contains what to do if it fails
# If no error occurs, the except block is SKIPPED

print("Program continues after the try-except block.")

# ============================================================
# SECTION 3: Handling Multiple Exceptions
# ============================================================

print("\n--- Multiple Exceptions ---")

def safe_divide(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("  Cannot divide by zero.")
        return None
    except TypeError:
        print("  Both arguments must be numbers.")
        return None

print(safe_divide(10, 2))     # 5.0
print(safe_divide(10, 0))     # Error message
print(safe_divide(10, "x"))   # Error message

# Catch multiple exceptions in one line
def convert_to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        print(f"  Cannot convert '{value}' to integer.")
        return 0

print(convert_to_int("42"))       # 42
print(convert_to_int("hello"))    # Error message
print(convert_to_int(None))       # Error message

# Using 'as' to get the error message
try:
    my_list = [1, 2, 3]
    print(my_list[10])
except IndexError as e:
    print(f"IndexError caught: {e}")

# Generic exception (catches any error — use as last resort)
try:
    x = 1 / 0
except Exception as e:
    print(f"Unexpected error: {type(e).__name__}: {e}")

# ============================================================
# SECTION 4: else and finally in try-except
# ============================================================

print("\n--- else and finally ---")

# else: runs if NO exception occurred
# finally: runs ALWAYS (whether or not there was an error)

def read_number(value):
    try:
        result = int(value)
    except ValueError:
        print(f"  '{value}' is not a valid number.")
    else:
        print(f"  Successfully converted: {result}")  # Runs only on success
    finally:
        print("  (This always runs — cleanup code goes here)")

read_number("25")
print()
read_number("abc")

# ============================================================
# SECTION 5: Raising Errors (raise)
# ============================================================

print("\n--- Raising Errors ---")

# You can raise your own errors to enforce rules in your code
def get_age(age):
    if not isinstance(age, int):
        raise TypeError("Age must be an integer.")
    if age < 0 or age > 150:
        raise ValueError(f"Age {age} is not realistic.")
    return age

try:
    print(get_age(25))
    print(get_age(-5))
except ValueError as e:
    print(f"ValueError: {e}")

try:
    print(get_age("twenty"))
except TypeError as e:
    print(f"TypeError: {e}")

# ============================================================
# SECTION 6: Debugging Logic Errors
# ============================================================

print("\n--- Debugging Logic Errors ---")

# Logic errors don't crash Python — but they give wrong answers
# These are the hardest bugs to find

# BUGGY version:
def average_buggy(numbers):
    total = 0
    for n in numbers:
        total = total + n
    return total / 10  # BUG: hardcoded 10 instead of len(numbers)

# FIXED version:
def average_fixed(numbers):
    if len(numbers) == 0:
        return 0
    total = sum(numbers)
    return total / len(numbers)

data = [10, 20, 30]
print("Buggy average:", average_buggy(data))   # 6.0 (wrong!)
print("Fixed average:", average_fixed(data))   # 20.0 (correct)

# Debugging tips:
# 1. Add print() statements to see values at different points
# 2. Check your logic step by step
# 3. Test with small, simple inputs first
# 4. Use Python's built-in debugger (pdb) or VS Code debugger

# ============================================================
# SECTION 7: Writing Robust Code
# ============================================================

print("\n--- Robust Code Example ---")

# Robust code validates input, handles errors, and gives useful messages

def calculate_average(scores):
    """
    Calculate average from a list of scores.
    Returns None if the list is empty or contains invalid values.
    """
    if not isinstance(scores, list):
        raise TypeError("Input must be a list.")
    if len(scores) == 0:
        print("Warning: empty list provided.")
        return None

    clean_scores = []
    for i, score in enumerate(scores):
        try:
            clean_scores.append(float(score))
        except (ValueError, TypeError):
            print(f"  Skipping invalid value at index {i}: {score!r}")

    if len(clean_scores) == 0:
        return None

    return sum(clean_scores) / len(clean_scores)


# Test with messy real-world data
messy_data = [85, 90, "N/A", 78, None, 95, "88", 72]
avg = calculate_average(messy_data)
print(f"Average score: {avg:.2f}")

# Test with edge cases
print("Empty list:", calculate_average([]))
print("Good data:", calculate_average([70, 80, 90]))

print("\n--- End of Error Handling ---")
