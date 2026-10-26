# ============================================================
# TOPIC 3: Python Data Structures
# ============================================================

# ============================================================
# SECTION 1: Numbers (int, float, complex)
# ============================================================

print("--- Numbers ---")

# int: whole numbers (no decimal point)
apples = 10
temperature = -5
big_number = 1_000_000  # underscores make large numbers readable

# float: numbers with a decimal point
price = 19.99
weight = 72.5
scientific = 1.5e3  # 1.5 x 10^3 = 1500.0

# complex: numbers with a real and imaginary part (rarely used in basic DS)
z = 3 + 4j

print("int:", apples, type(apples))
print("float:", price, type(price))
print("complex:", z, type(z))

# Useful number functions
print(abs(-45))        # Absolute value: 45
print(round(3.7))      # Round: 4
print(round(3.14159, 2))  # Round to 2 decimal places: 3.14
print(max(10, 20, 5))  # Maximum: 20
print(min(10, 20, 5))  # Minimum: 5

# ============================================================
# SECTION 2: Strings and String Methods
# ============================================================

print("\n--- Strings ---")

# A string is a sequence of characters enclosed in quotes
greeting = "Hello, World!"
name = 'Alice'
paragraph = """This is a
multi-line string."""

print(greeting)
print(len(greeting))       # Length: 13

# Accessing characters (indexing — starts at 0)
print(greeting[0])         # 'H'
print(greeting[-1])        # '!' (last character)

# Slicing (extracting a portion)
print(greeting[0:5])       # 'Hello'
print(greeting[7:])        # 'World!'
print(greeting[:5])        # 'Hello'

# String methods
text = "  python for data science  "
print(text.strip())          # Remove whitespace: 'python for data science'
print(text.upper())          # UPPERCASE
print(text.lower())          # lowercase
print(text.title())          # Title Case
print(text.strip().replace("python", "PYTHON"))  # Replace

sentence = "Data Science is fun and data is everywhere"
print(sentence.split(" "))            # Split into list of words
print(sentence.count("data"))         # Count occurrences (case-sensitive)
print(sentence.find("Science"))       # Index where word starts
print(sentence.startswith("Data"))    # True
print(sentence.endswith("everywhere"))  # True

# String formatting
name = "Bob"
score = 98.5
print(f"Student {name} scored {score:.1f}%")   # f-string
print("Student {} scored {}%".format(name, score))  # .format()

# ============================================================
# SECTION 3: Lists and List Operations
# ============================================================

print("\n--- Lists ---")

# A list is an ordered, changeable collection of items
# Lists can hold mixed data types
fruits = ["apple", "banana", "cherry", "mango"]
numbers = [10, 20, 30, 40, 50]
mixed = [1, "hello", 3.14, True]

print(fruits)
print(fruits[0])      # First item: 'apple'
print(fruits[-1])     # Last item: 'mango'
print(fruits[1:3])    # Slice: ['banana', 'cherry']

# Modifying lists
fruits.append("orange")         # Add to end
fruits.insert(1, "grape")       # Insert at position 1
fruits.remove("banana")         # Remove specific item
popped = fruits.pop()           # Remove and return last item
print("Popped:", popped)
print("Updated fruits:", fruits)

# List operations
nums = [3, 1, 4, 1, 5, 9, 2, 6]
print("Length:", len(nums))
print("Sum:", sum(nums))
print("Max:", max(nums))
print("Min:", min(nums))
print("Sorted:", sorted(nums))    # Returns new sorted list
nums.sort()                       # Sorts in-place
print("After sort:", nums)
nums.reverse()                    # Reverses in-place
print("Reversed:", nums)

# Check if item exists
print("Is 5 in nums?", 5 in nums)

# List comprehension (creating a list using a short expression)
squares = [x ** 2 for x in range(1, 6)]
print("Squares:", squares)  # [1, 4, 9, 16, 25]

even = [x for x in range(1, 11) if x % 2 == 0]
print("Even numbers:", even)  # [2, 4, 6, 8, 10]

# ============================================================
# SECTION 4: Tuples and Immutability
# ============================================================

print("\n--- Tuples ---")

# A tuple is like a list BUT it cannot be changed (immutable)
# Use parentheses ()
coordinates = (10.5, -3.2)
colors = ("red", "green", "blue")
single = (42,)  # Single-item tuple needs a trailing comma

print(coordinates)
print(coordinates[0])    # Access like a list
print(len(colors))

# You CANNOT change a tuple:
# colors[0] = "yellow"   <-- This will throw a TypeError!

# When to use tuples vs lists:
# - Tuples: fixed data that should not change (coordinates, RGB values, DB rows)
# - Lists: data that will change (shopping cart, list of names)

# Tuple unpacking (very useful!)
x, y = coordinates
print(f"x = {x}, y = {y}")

# Function returning multiple values (actually returns a tuple)
def get_stats(data):
    return min(data), max(data), sum(data) / len(data)

lo, hi, avg = get_stats([4, 7, 2, 9, 1])
print(f"Min: {lo}, Max: {hi}, Avg: {avg}")

# ============================================================
# SECTION 5: Sets and Set Operations
# ============================================================

print("\n--- Sets ---")

# A set is an UNORDERED collection of UNIQUE items
# Duplicates are automatically removed
# Use curly braces {}
fruits_set = {"apple", "banana", "cherry", "apple", "banana"}
print(fruits_set)  # Duplicates removed, order may vary

# Adding and removing
fruits_set.add("mango")
fruits_set.discard("cherry")  # No error if not found
print(fruits_set)

# Set operations (like math sets)
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

print("Union (all items):", a | b)           # {1,2,3,4,5,6,7,8}
print("Intersection (common):", a & b)       # {4, 5}
print("Difference (in a not b):", a - b)     # {1, 2, 3}
print("Symmetric diff:", a ^ b)              # {1,2,3,6,7,8}

# Very useful: removing duplicates from a list
names = ["Alice", "Bob", "Alice", "Charlie", "Bob"]
unique_names = list(set(names))
print("Unique names:", unique_names)

# ============================================================
# SECTION 6: Dictionaries and Key-Value Mapping
# ============================================================

print("\n--- Dictionaries ---")

# A dictionary stores data as key: value pairs
# Keys must be unique; values can be anything
student = {
    "name": "Alice",
    "age": 22,
    "grade": "A",
    "courses": ["Math", "CS", "Statistics"]
}

# Accessing values
print(student["name"])           # Alice
print(student.get("age"))        # 22
print(student.get("gpa", "N/A")) # 'N/A' (default if key missing)

# Modifying
student["age"] = 23              # Update existing
student["email"] = "alice@example.com"  # Add new key
del student["grade"]             # Delete a key

# Checking keys
print("name" in student)         # True
print("grade" in student)        # False (we deleted it)

# Iterating over a dictionary
print("\nAll student info:")
for key, value in student.items():
    print(f"  {key}: {value}")

print("\nAll keys:", list(student.keys()))
print("All values:", list(student.values()))

# Nested dictionary
employees = {
    "E001": {"name": "John", "role": "Engineer", "salary": 70000},
    "E002": {"name": "Sarah", "role": "Manager", "salary": 90000},
}
print("\nEmployee E001 name:", employees["E001"]["name"])
print("Employee E002 salary:", employees["E002"]["salary"])

# Dictionary comprehension
squares_dict = {x: x**2 for x in range(1, 6)}
print("\nSquares dict:", squares_dict)  # {1:1, 2:4, 3:9, 4:16, 5:25}

print("\n--- End of Data Structures ---")
