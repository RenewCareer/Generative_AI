"""
Run this script to generate all 20 Jupyter notebooks.
  python generate_notebooks.py
"""

import json, os, uuid

def uid():
    return str(uuid.uuid4())

def md(lines):
    if isinstance(lines, str):
        lines = lines.split("\n")
        lines = [l + "\n" for l in lines]
    return {"cell_type": "markdown", "id": uid(), "metadata": {}, "source": lines}

def code(lines):
    if isinstance(lines, str):
        lines = lines.split("\n")
        lines = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    return {"cell_type": "code", "execution_count": None, "id": uid(),
            "metadata": {}, "outputs": [], "source": lines}

def notebook(cells):
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10.0"}
        },
        "cells": cells
    }

def save(path, nb):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print(f"  Created: {path}")

BASE = os.path.dirname(os.path.abspath(__file__))

# ===========================================================
# NOTEBOOK 1 — Orientation & Environment Setup
# ===========================================================
save(f"{BASE}/01_Orientation/01_Orientation.ipynb", notebook([
    md("# Topic 1: Orientation & Environment Setup\n\nWelcome to **Python for GenAI & Data Science**! In this notebook you will:\n- Understand what Python is and why it is used\n- Run your first Python program\n- Check your environment is ready"),
    md("## 1. Your First Python Program\n\nThe `print()` function displays output on the screen."),
    code('print("Hello, World!")\nprint("Welcome to Python for Data Science & GenAI!")'),
    md("## 2. Python as a Calculator\n\nPython can do maths instantly — no extra setup needed."),
    code("print(5 + 3)    # Addition\nprint(10 - 4)   # Subtraction\nprint(6 * 7)    # Multiplication\nprint(15 / 4)   # Division\nprint(15 // 4)  # Floor division (whole number)\nprint(15 % 4)   # Modulus (remainder)\nprint(2 ** 10)  # Power"),
    md("## 3. Scripts vs Notebooks\n\n| | Script (.py) | Notebook (.ipynb) |\n|---|---|---|\n| Runs | Top to bottom all at once | One cell at a time |\n| Best for | Automation, production | Learning, exploration |\n| Output | Terminal only | Inline (text + charts) |"),
    md("## 4. Check Your Python Version"),
    code("import sys\nprint('Python version:', sys.version)\nprint('Major version:', sys.version_info.major)"),
    md("## 5. Check Installed Libraries\n\nRun the cell below to see which data science libraries are ready on your machine."),
    code('libraries = ["numpy", "pandas", "matplotlib", "seaborn", "sklearn"]\nfor lib in libraries:\n    try:\n        __import__(lib)\n        print(f"  {lib:15} -- INSTALLED ✓")\n    except ImportError:\n        print(f"  {lib:15} -- NOT FOUND  (pip install {lib})")'),
    md("## 6. Installing Libraries\n\nOpen your terminal (or Anaconda Prompt) and run:\n\n```bash\npip install numpy pandas matplotlib seaborn scikit-learn jupyter\n```\n\n> **Tip:** If you use Anaconda, replace `pip` with `conda`."),
    md("## ✅ Summary\n- Python is free, readable, and the #1 language for Data Science & GenAI.\n- Use `print()` to show output.\n- Jupyter notebooks let you mix code, output, and explanations.\n- Install libraries with `pip install <name>`."),
]))

# ===========================================================
# NOTEBOOK 2 — Python Fundamentals
# ===========================================================
save(f"{BASE}/02_Python_Fundamentals/02_Python_Fundamentals.ipynb", notebook([
    md("# Topic 2: Python Fundamentals\n\n**What you'll learn:** syntax rules, variables, data types, type casting, input/output, and comments."),
    md("## 1. Syntax and Indentation\n\nPython uses **indentation (spaces)** to define code blocks — not curly braces `{}`.\nStandard = **4 spaces** per level."),
    code('# Correct indentation\nif True:\n    print("Inside the if block")   # 4 spaces\n    print("Still inside")           # 4 spaces\nprint("Outside the if block")       # 0 spaces'),
    md("## 2. Variables and Data Types\n\nA **variable** stores a value. Python automatically detects the type."),
    code('name       = "Alice"     # str  → text\nage        = 25          # int  → whole number\nheight     = 5.7         # float → decimal\nis_student = True        # bool  → True or False\n\nprint(name, type(name))\nprint(age,  type(age))\nprint(height, type(height))\nprint(is_student, type(is_student))'),
    md("### The four basic data types\n\n| Type | Example | Use |\n|------|---------|-----|\n| `str` | `\"Alice\"` | Text |\n| `int` | `25` | Whole numbers |\n| `float` | `5.7` | Decimal numbers |\n| `bool` | `True` | Yes/No flags |"),
    md("## 3. Type Casting (Converting Between Types)"),
    code('# String → Integer\nage_str = "30"\nage_int = int(age_str)\nprint(age_int, type(age_int))\n\n# Integer → Float\nnum_float = float(7)\nprint(num_float)\n\n# Float → Integer (truncates — does NOT round)\nprint(int(9.99))   # → 9\n\n# Number → String (needed to concatenate with text)\nscore = 95\nprint("Your score is: " + str(score))'),
    md("## 4. Input and Output"),
    code('# OUTPUT — the print() function\nname = "Bob"\nage  = 28\n\nprint("Name:", name, "Age:", age)              # comma-separated\nprint(f"My name is {name} and I am {age}.")    # f-string (recommended)\n\n# Number formatting with f-strings\npi = 3.14159\nprint(f"Pi to 2 decimal places: {pi:.2f}")\nprint(f"Pi to 4 decimal places: {pi:.4f}")\n\n# INPUT — uncomment to try interactively\n# your_name = input("What is your name? ")\n# print(f"Hello, {your_name}!")'),
    md("## 5. Comments and Code Readability\n\nComments start with `#`. Python ignores them — they are for humans."),
    code('# Single-line comment\n\n"""\nMulti-line comment (also called a docstring).\nUse this to describe a function or explain a block.\n"""\n\n# Good comment: explains WHY\ntax_rate = 0.2  # Ghana PAYE rate for this income bracket\n\n# Bad comment: just restates the code (avoid)\nx = x + 1  # add 1 to x    ← unhelpful'),
    md("## ✅ Summary\n\n| Concept | Key Point |\n|---|---|\n| Indentation | 4 spaces per level — mandatory |\n| Variables | No type declaration needed |\n| Type casting | `int()`, `float()`, `str()` |\n| Output | `print()` or f-strings |\n| Comments | `#` for one line, `\"\"\"` for multi-line |"),
]))

# ===========================================================
# NOTEBOOK 3 — Data Structures
# ===========================================================
save(f"{BASE}/03_Data_Structures/03_Data_Structures.ipynb", notebook([
    md("# Topic 3: Python Data Structures\n\nPython's built-in data structures are the backbone of every data science pipeline.\n\n**Topics:** Numbers · Strings · Lists · Tuples · Sets · Dictionaries"),
    md("## 1. Numbers"),
    code('# int: whole numbers\napples = 10\nbig = 1_000_000   # underscore makes big numbers readable\n\n# float: decimals\nprice = 19.99\n\n# Useful functions\nprint(abs(-45))          # 45\nprint(round(3.14159, 2)) # 3.14\nprint(max(10, 20, 5))    # 20\nprint(min(10, 20, 5))    # 5'),
    md("## 2. Strings"),
    code('greeting = "Hello, World!"\n\n# Length and indexing\nprint(len(greeting))    # 13\nprint(greeting[0])      # H  (first character)\nprint(greeting[-1])     # !  (last character)\nprint(greeting[0:5])    # Hello (slice)\n\n# Common methods\ntext = "  python for data science  "\nprint(text.strip())            # remove whitespace\nprint(text.strip().title())    # Title Case\nprint(text.strip().upper())    # UPPERCASE\nprint(text.strip().replace("python", "PYTHON"))\n\n# f-string formatting\nname, score = "Alice", 98.5\nprint(f"Student {name} scored {score:.1f}%")'),
    md("## 3. Lists\n\nAn **ordered, changeable** collection. Use `[]`."),
    code('fruits = ["apple", "banana", "cherry", "mango"]\n\nprint(fruits[0])    # apple  (first)\nprint(fruits[-1])   # mango  (last)\nprint(fruits[1:3])  # [\'banana\', \'cherry\']\n\n# Modifying\nfruits.append("orange")     # add to end\nfruits.remove("banana")     # remove by value\nfruits.insert(0, "grape")   # insert at position 0\nprint(fruits)\n\n# Useful operations\nnums = [3, 1, 4, 1, 5, 9, 2]\nprint("sum:", sum(nums))\nprint("sorted:", sorted(nums))\nprint("5 in list?", 5 in nums)\n\n# List comprehension — create a list in one line\nsquares = [x**2 for x in range(1, 6)]\nprint("squares:", squares)'),
    md("## 4. Tuples\n\nAn **ordered, immutable** (unchangeable) collection. Use `()`."),
    code('coords = (10.5, -3.2)\ncolors = ("red", "green", "blue")\n\nprint(coords[0])   # 10.5\nprint(len(colors)) # 3\n\n# Tuple unpacking\nx, y = coords\nprint(f"x={x}, y={y}")\n\n# Use tuples for data that should NOT change\n# (GPS coordinates, RGB values, database row records)'),
    md("## 5. Sets\n\nAn **unordered** collection of **unique** items. Use `{}`."),
    code('fruits_set = {"apple", "banana", "cherry", "apple"}  # duplicate removed!\nprint(fruits_set)\n\na = {1, 2, 3, 4, 5}\nb = {4, 5, 6, 7, 8}\n\nprint("Union:       ", a | b)   # all items\nprint("Intersection:", a & b)   # common items\nprint("Difference:  ", a - b)   # in a but not b\n\n# Very useful: remove duplicates from a list\nnames = ["Alice", "Bob", "Alice", "Charlie", "Bob"]\nprint("Unique:", list(set(names)))'),
    md("## 6. Dictionaries\n\nStores **key: value** pairs. Use `{}` with colons."),
    code('student = {\n    "name": "Alice",\n    "age": 22,\n    "courses": ["Math", "CS", "Statistics"]\n}\n\nprint(student["name"])          # Alice\nprint(student.get("gpa", "N/A")) # default if key missing\n\nstudent["email"] = "alice@example.com"   # add new key\nstudent["age"] = 23                      # update\n\n# Loop over key-value pairs\nfor key, value in student.items():\n    print(f"  {key}: {value}")\n\n# Dictionary comprehension\nsquares = {x: x**2 for x in range(1, 6)}\nprint(squares)'),
    md("## ✅ Summary\n\n| Structure | Ordered | Changeable | Unique | Syntax |\n|-----------|---------|------------|--------|--------|\n| List | ✅ | ✅ | ❌ | `[...]` |\n| Tuple | ✅ | ❌ | ❌ | `(...)` |\n| Set | ❌ | ✅ | ✅ | `{...}` |\n| Dictionary | ✅ (3.7+) | ✅ | Keys only | `{k:v}` |"),
]))

# ===========================================================
# NOTEBOOK 4 — Control Flow
# ===========================================================
save(f"{BASE}/04_Control_Flow/04_Control_Flow.ipynb", notebook([
    md("# Topic 4: Control Flow & Logic Building\n\nControl flow lets you make decisions and repeat actions in your code.\n\n**Topics:** if/elif/else · Comparison & logical operators · for/while loops · break/continue/pass · Nested loops"),
    md("## 1. Conditional Statements"),
    code('grade = 85\n\nif grade >= 90:\n    print("Grade: A")\nelif grade >= 80:\n    print("Grade: B")\nelif grade >= 70:\n    print("Grade: C")\nelse:\n    print("Grade: F")\n\n# One-line (ternary) expression\nlabel = "pass" if grade >= 50 else "fail"\nprint(f"Result: {label}")'),
    md("## 2. Comparison and Logical Operators\n\n| Operator | Meaning |\n|---|---|\n| `==` | Equal to |\n| `!=` | Not equal |\n| `<` `>` `<=` `>=` | Less/Greater |\n| `and` | Both must be True |\n| `or` | At least one True |\n| `not` | Flips True↔False |"),
    code('salary = 55000\nexperience = 4\n\nif salary > 40000 and experience >= 2:\n    print("Eligible for promotion")\n\nage = 17\nhas_permission = True\nif age >= 18 or has_permission:\n    print("Access granted")'),
    md("## 3. For Loop\n\nIterates over any sequence (list, string, range)."),
    code('fruits = ["apple", "banana", "cherry"]\nfor fruit in fruits:\n    print(fruit)\n\n# range(start, stop, step)\nfor i in range(1, 11, 2):\n    print(i, end=" ")  # 1 3 5 7 9\nprint()  # newline\n\n# enumerate() gives index AND value\nfor idx, fruit in enumerate(fruits, start=1):\n    print(f"{idx}. {fruit}")\n\n# Loop over dictionary\nperson = {"name": "Alice", "age": 25, "city": "Accra"}\nfor key, value in person.items():\n    print(f"  {key}: {value}")'),
    md("## 4. While Loop\n\nRuns as long as the condition is `True`."),
    code('count = 0\nwhile count < 5:\n    print(f"Count: {count}")\n    count += 1  # ALWAYS update the variable — prevents infinite loop\n\nprint("Done!")'),
    md("## 5. Loop Control: break, continue, pass"),
    code('# break: stop the loop immediately\nfor i in range(10):\n    if i == 5:\n        print("Found 5! Stopping.")\n        break\n    print(i, end=" ")\n\nprint()\n\n# continue: skip this iteration, continue to next\nfor i in range(10):\n    if i % 2 == 0:\n        continue       # skip even numbers\n    print(i, end=" ")  # only prints odd numbers\n\nprint()\n\n# pass: do nothing (placeholder)\nfor i in range(3):\n    pass  # fill in later'),
    md("## 6. Nested Loops"),
    code('# Multiplication table 1–5\nfor i in range(1, 6):\n    for j in range(1, 6):\n        print(f"{i*j:3}", end="")\n    print()  # new line after each row'),
    md("## 7. Real-World Example: Analysing Scores"),
    code('scores = [85, 42, 91, 67, 55, 78, 39, 95, 60, 73]\n\npassed, failed = [], []\nfor score in scores:\n    if score >= 50:\n        passed.append(score)\n    else:\n        failed.append(score)\n\nprint(f"Passed : {len(passed)} — {passed}")\nprint(f"Failed : {len(failed)} — {failed}")\nprint(f"Average: {sum(scores)/len(scores):.1f}")'),
    md("## ✅ Summary\n\n| Construct | Use |\n|---|---|\n| `if/elif/else` | Make decisions |\n| `for` | Iterate a known number of times |\n| `while` | Repeat until a condition changes |\n| `break` | Exit loop early |\n| `continue` | Skip to next iteration |\n| `pass` | Placeholder — do nothing |"),
]))

# ===========================================================
# NOTEBOOK 5 — Functions
# ===========================================================
save(f"{BASE}/05_Functions/05_Functions.ipynb", notebook([
    md("# Topic 5: Functions & Modular Programming\n\nFunctions let you write code once and reuse it anywhere.\n\n**Topics:** Defining functions · Arguments · Default/keyword args · Lambda · Scope · Modules"),
    md("## 1. Defining and Calling Functions"),
    code('def greet():\n    print("Hello! Welcome to Python.")\n\ngreet()  # call it\ngreet()  # call it again — reusable!'),
    md("## 2. Arguments and Return Values"),
    code('def greet_person(name):\n    print(f"Hello, {name}!")\n\ngreet_person("Alice")\ngreet_person("Bob")\n\ndef add(a, b):\n    return a + b\n\nresult = add(5, 3)\nprint("5 + 3 =", result)\n\n# Multiple return values (returns a tuple)\ndef min_max(data):\n    return min(data), max(data)\n\nlo, hi = min_max([4, 2, 9, 1, 7])\nprint(f"Min: {lo}, Max: {hi}")'),
    md("## 3. Default and Keyword Arguments"),
    code('def introduce(name, language="Python"):\n    print(f"Hi, I\'m {name} and I code in {language}.")\n\nintroduce("Alice")               # uses default\nintroduce("Bob", "JavaScript")   # overrides default\n\n# Keyword arguments — order does not matter\ndef describe(name, age, city):\n    print(f"{name}, {age}, from {city}")\n\ndescribe(age=25, city="Accra", name="Alice")'),
    md("## 4. Lambda Functions (Anonymous Functions)\n\nA `lambda` is a short one-line function without a name."),
    code('square = lambda x: x ** 2\nprint(square(5))    # 25\n\nmultiply = lambda a, b: a * b\nprint(multiply(4, 7))  # 28\n\n# Lambdas with sorted(), map(), filter()\nstudents = [("Alice", 85), ("Bob", 72), ("Charlie", 91)]\nby_score = sorted(students, key=lambda s: s[1], reverse=True)\nprint("By score:", by_score)\n\nnums = [1, 2, 3, 4, 5]\ndoubled = list(map(lambda x: x*2, nums))\nevens   = list(filter(lambda x: x%2==0, nums))\nprint("Doubled:", doubled)\nprint("Evens:  ", evens)'),
    md("## 5. Scope (Local vs Global)"),
    code('message = "I am global"\n\ndef show():\n    local_var = "I am local"\n    print(message)   # can read global\n    print(local_var) # only visible inside\n\nshow()\n# print(local_var)  ← NameError if uncommented\n\n# Use global to MODIFY a global variable\ncounter = 0\ndef increment():\n    global counter\n    counter += 1\n\nincrement(); increment(); increment()\nprint("Counter:", counter)'),
    md("## 6. Importing Modules"),
    code('import math\nprint(math.sqrt(16))    # 4.0\nprint(math.pi)          # 3.14159...\nprint(math.factorial(5))  # 120\n\nimport random\nprint(random.randint(1, 10))   # random int\nprint(round(random.random(), 4))\n\nfrom math import sqrt, ceil\nprint(sqrt(25), ceil(4.2))\n\nimport math as m   # alias\nprint(m.pi)'),
    md("## 7. Reusable Functions — Real Example"),
    code('def calculate_bmi(weight_kg, height_m):\n    """Calculate BMI given weight in kg and height in metres."""\n    return round(weight_kg / (height_m ** 2), 1)\n\ndef classify_bmi(bmi):\n    if bmi < 18.5: return "Underweight"\n    elif bmi < 25: return "Normal weight"\n    elif bmi < 30: return "Overweight"\n    else:          return "Obese"\n\nbmi = calculate_bmi(70, 1.75)\nprint(f"BMI: {bmi} — {classify_bmi(bmi)}")'),
    md("## ✅ Summary\n\n| Concept | Syntax |\n|---|---|\n| Define function | `def name(args):` |\n| Return value | `return value` |\n| Default argument | `def f(x=10):` |\n| Lambda | `lambda x: x*2` |\n| Import module | `import math` |\n| Import specific | `from math import sqrt` |"),
]))

# ===========================================================
# NOTEBOOK 6 — Error Handling
# ===========================================================
save(f"{BASE}/06_Error_Handling/06_Error_Handling.ipynb", notebook([
    md("# Topic 6: Error Handling & Debugging\n\nRobust code handles errors gracefully instead of crashing.\n\n**Topics:** Common errors · try/except · Multiple exceptions · else/finally · raise · Debugging"),
    md("## 1. Common Python Errors\n\n| Error | Cause | Example |\n|---|---|---|\n| `SyntaxError` | Wrong syntax | `if x == 5` (missing `:`) |\n| `NameError` | Undefined variable | `print(y)` — y never defined |\n| `TypeError` | Wrong type | `\"hi\" + 5` |\n| `IndexError` | Index out of range | `lst[99]` |\n| `KeyError` | Missing dict key | `d[\"x\"]` |\n| `ZeroDivisionError` | Divide by zero | `10 / 0` |\n| `ValueError` | Wrong value | `int(\"abc\")` |"),
    md("## 2. try–except"),
    code('# Without error handling — this crashes:\n# result = 10 / 0\n\n# With try-except — handles gracefully:\ntry:\n    result = 10 / 0\nexcept ZeroDivisionError:\n    print("Cannot divide by zero!")\n\ntry:\n    num = int("abc")\nexcept ValueError:\n    print("\'abc\' is not a valid integer.")\n\nprint("Program continues normally.")'),
    md("## 3. Handling Multiple Exceptions"),
    code('def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        print("  Error: division by zero")\n    except TypeError:\n        print("  Error: inputs must be numbers")\n    return None\n\nprint(safe_divide(10, 2))   # 5.0\nprint(safe_divide(10, 0))   # Error\nprint(safe_divide(10, "x")) # Error\n\n# Catch multiple exceptions in one line\ndef to_int(value):\n    try:\n        return int(value)\n    except (ValueError, TypeError):\n        print(f"  Cannot convert {value!r} to int")\n        return 0\n\nprint(to_int("42"))\nprint(to_int("hello"))\nprint(to_int(None))'),
    md("## 4. else and finally"),
    code('def read_number(value):\n    try:\n        result = int(value)\n    except ValueError:\n        print(f"  \'{value}\' is not a number.")\n    else:\n        print(f"  Success: {result}")   # only if no exception\n    finally:\n        print("  (cleanup — always runs)")  # always runs\n\nread_number("25")\nprint()\nread_number("abc")'),
    md("## 5. Raising Custom Errors"),
    code('def get_age(age):\n    if not isinstance(age, int):\n        raise TypeError("Age must be an integer.")\n    if age < 0 or age > 150:\n        raise ValueError(f"Age {age} is not realistic.")\n    return age\n\ntry:\n    print(get_age(25))\n    print(get_age(-5))\nexcept ValueError as e:\n    print(f"ValueError: {e}")\n\ntry:\n    print(get_age("twenty"))\nexcept TypeError as e:\n    print(f"TypeError: {e}")'),
    md("## 6. Robust Code Example"),
    code('def calculate_average(scores):\n    """Calculate average, handling messy input gracefully."""\n    if not isinstance(scores, list):\n        raise TypeError("Input must be a list.")\n    if len(scores) == 0:\n        return None\n    clean = []\n    for i, s in enumerate(scores):\n        try:\n            clean.append(float(s))\n        except (ValueError, TypeError):\n            print(f"  Skipping invalid value at index {i}: {s!r}")\n    return sum(clean) / len(clean) if clean else None\n\nmessy = [85, 90, "N/A", 78, None, 95, "88", 72]\navg = calculate_average(messy)\nprint(f"Average: {avg:.2f}")'),
    md("## ✅ Summary\n\n```python\ntry:\n    # code that might fail\nexcept SpecificError:\n    # handle it\nexcept (Error1, Error2):\n    # handle either\nelse:\n    # runs only if no error\nfinally:\n    # ALWAYS runs\n```"),
]))

# ===========================================================
# NOTEBOOK 7 — File Handling
# ===========================================================
save(f"{BASE}/07_File_Handling/07_File_Handling.ipynb", notebook([
    md("# Topic 7: File Handling & Data Input\n\n**Topics:** Text files · CSV files · JSON files · File paths · Intro to APIs"),
    md("## 1. Reading and Writing Text Files"),
    code('# Write a text file\nwith open("sample.txt", "w") as f:\n    f.write("Line 1: Hello\\n")\n    f.write("Line 2: Python file handling\\n")\n    f.write("Line 3: Easy and clean\\n")\nprint("File written.")\n\n# Read entire file\nwith open("sample.txt", "r") as f:\n    content = f.read()\nprint(content)\n\n# Read line by line\nwith open("sample.txt", "r") as f:\n    for line in f:\n        print(">", line.strip())\n\n# Append without overwriting\nwith open("sample.txt", "a") as f:\n    f.write("Line 4: Appended later\\n")'),
    md("## 2. Working with CSV Files\n\nCSV (Comma-Separated Values) is the most common format for datasets."),
    code('import csv\n\n# Write CSV\nstudents = [\n    ["Name", "Age", "Score"],\n    ["Alice", 22, 85],\n    ["Bob",   25, 92],\n    ["Charlie", 21, 78],\n]\nwith open("students.csv", "w", newline="") as f:\n    csv.writer(f).writerows(students)\nprint("students.csv created.")\n\n# Read with DictReader (each row is a dictionary)\nwith open("students.csv", "r") as f:\n    for row in csv.DictReader(f):\n        print(f"  {row[\'Name\']} scored {row[\'Score\']}") '),
    md("## 3. Working with JSON Files\n\nJSON is used heavily in APIs and web services."),
    code('import json\n\ndata = {\n    "company": "TechCorp",\n    "employees": [\n        {"id": 1, "name": "Alice", "salary": 70000},\n        {"id": 2, "name": "Bob",   "salary": 90000},\n    ]\n}\n\n# Write JSON\nwith open("employees.json", "w") as f:\n    json.dump(data, f, indent=4)\nprint("JSON saved.")\n\n# Read JSON\nwith open("employees.json", "r") as f:\n    loaded = json.load(f)\nfor emp in loaded["employees"]:\n    print(f"  {emp[\'name\']}: ${emp[\'salary\']:,}")'),
    md("## 4. File Paths and Directories"),
    code('import os\n\nprint("Current directory:", os.getcwd())\nprint("Files here:", os.listdir(".")[:8])\n\n# Check existence\nprint("sample.txt exists?", os.path.exists("sample.txt"))\n\n# Safe path joining (works on all OS)\npath = os.path.join("data", "report.csv")\nprint("Joined path:", path)\n\n# Create directory if missing\nos.makedirs("output", exist_ok=True)\nprint("output/ folder ready.")'),
    md("## 5. Introduction to APIs"),
    code('# An API lets your Python program talk to an online service.\n# Most APIs return JSON. You call them with the requests library.\n\ntry:\n    import requests\n    url = "https://official-joke-api.appspot.com/random_joke"\n    response = requests.get(url, timeout=5)\n    if response.status_code == 200:\n        joke = response.json()\n        print("Setup:    ", joke["setup"])\n        print("Punchline:", joke["punchline"])\nexcept ImportError:\n    print("Install requests: pip install requests")\nexcept Exception as e:\n    print(f"Could not reach API: {e}")'),
    md("## Cleanup"),
    code('import os\nfor f in ["sample.txt", "students.csv", "employees.json"]:\n    if os.path.exists(f): os.remove(f)\nif os.path.exists("output"): os.rmdir("output")\nprint("Cleanup done.")'),
    md("## ✅ Summary\n\n| Task | How |\n|---|---|\n| Write text | `open(file, 'w')` + `f.write()` |\n| Read text | `open(file, 'r')` + `f.read()` |\n| Write CSV | `csv.writer(f).writerows(data)` |\n| Read CSV | `csv.DictReader(f)` |\n| Write JSON | `json.dump(data, f, indent=4)` |\n| Read JSON | `json.load(f)` |\n| Call API | `requests.get(url).json()` |"),
]))

# ===========================================================
# NOTEBOOK 8 — NumPy
# ===========================================================
save(f"{BASE}/08_NumPy/08_NumPy.ipynb", notebook([
    md("# Topic 8: NumPy – Numerical Computing\n\nNumPy is the foundation of all numerical Python. It provides fast arrays and mathematical operations.\n\n```bash\npip install numpy\n```"),
    md("## 1. Arrays vs Lists"),
    code('import numpy as np\n\npy_list  = [1, 2, 3, 4, 5]\nnp_array = np.array([1, 2, 3, 4, 5])\n\n# The key difference: array operations work on ALL elements at once\nprint("List doubled :", [x*2 for x in py_list])  # needs a loop\nprint("Array doubled:", np_array * 2)              # direct!'),
    md("## 2. Creating Arrays"),
    code('import numpy as np\n\nprint(np.zeros(5))\nprint(np.ones(5))\nprint(np.arange(0, 10, 2))          # [0 2 4 6 8]\nprint(np.linspace(0, 1, 5))         # 5 evenly spaced values\nprint(np.random.rand(5).round(3))   # random floats\nprint(np.full(4, 7))                # [7 7 7 7]\n\narr = np.array([[1,2,3],[4,5,6],[7,8,9]])\nprint("\\n2D array (matrix):\\n", arr)\nprint("Shape:", arr.shape)'),
    md("## 3. Indexing and Slicing"),
    code('import numpy as np\n\narr = np.array([10, 20, 30, 40, 50, 60, 70])\n\nprint(arr[0])      # 10  (first)\nprint(arr[-1])     # 70  (last)\nprint(arr[1:4])    # [20 30 40]\nprint(arr[::-1])   # reversed\n\n# 2D indexing [row, column]\nm = np.array([[1,2,3],[4,5,6],[7,8,9]])\nprint(m[0, 1])   # 2 (row 0, col 1)\nprint(m[:, -1])  # [3 6 9] (last column)\n\n# Boolean indexing — filter by condition\ndata = np.array([5, 12, 8, 20, 3, 17])\nprint(data[data > 10])  # [12 20 17]'),
    md("## 4. Mathematical Operations"),
    code('import numpy as np\n\na = np.array([1, 2, 3, 4, 5])\nb = np.array([10, 20, 30, 40, 50])\n\nprint("a + b:", a + b)\nprint("a * b:", a * b)\nprint("sqrt(b):", np.sqrt(b))\n\nprint("\\nAggregate functions:")\nprint("Sum:     ", np.sum(a))\nprint("Mean:    ", np.mean(a))\nprint("Std Dev: ", np.std(a))\nprint("Cumsum:  ", np.cumsum(a))'),
    md("## 5. Broadcasting\n\nBroadcasting automatically stretches a smaller array to match a larger one."),
    code('import numpy as np\n\narr = np.array([1, 2, 3, 4, 5])\nprint("arr + 10:", arr + 10)  # 10 added to every element\nprint("arr ** 2:", arr ** 2)\n\n# 2D + 1D broadcasting\nmatrix = np.array([[1,2,3],[4,5,6],[7,8,9]])\nrow    = np.array([10, 20, 30])\nprint("\\nmatrix + row:\\n", matrix + row)\n\n# Normalise data (common preprocessing)\ndata = np.array([150, 200, 180, 220, 170])\nnorm = (data - data.mean()) / data.std()\nprint("\\nNormalised:", norm.round(3))'),
    md("## 6. Handling Missing Values (NaN)"),
    code('import numpy as np\n\ndata = np.array([10, 20, np.nan, 40, np.nan, 60])\nprint("Data:", data)\n\n# Regular mean fails with NaN:\nprint("np.mean    :", np.mean(data))     # nan\n\n# NaN-safe versions:\nprint("np.nanmean :", np.nanmean(data))  # correct\nprint("np.nansum  :", np.nansum(data))\nprint("NaN mask   :", np.isnan(data))\nprint("Count NaN  :", np.isnan(data).sum())\n\n# Fill NaN with mean\nmean = np.nanmean(data)\nfilled = np.where(np.isnan(data), mean, data)\nprint("Filled     :", filled)'),
    md("## ✅ Summary\n\n| Task | Code |\n|---|---|\n| Create array | `np.array([1,2,3])` |\n| Zeros/Ones | `np.zeros(5)`, `np.ones(5)` |\n| Range | `np.arange(0,10,2)` |\n| Math on all | `arr * 2`, `np.sqrt(arr)` |\n| Aggregate | `np.mean()`, `np.sum()`, `np.std()` |\n| Filter | `arr[arr > 5]` |\n| NaN-safe | `np.nanmean()`, `np.isnan()` |"),
]))

# ===========================================================
# NOTEBOOK 9 — Pandas
# ===========================================================
save(f"{BASE}/09_Pandas/09_Pandas.ipynb", notebook([
    md("# Topic 9: Pandas – Data Analysis\n\nPandas is the #1 library for data analysis in Python. Think of it as a powerful Excel in code.\n\n```bash\npip install pandas openpyxl\n```"),
    md("## 1. Series and DataFrames"),
    code('import pandas as pd\nimport numpy as np\n\n# Series — a single column\nages = pd.Series([25,30,22,28], index=["Alice","Bob","Charlie","Diana"])\nprint(ages)\nprint("Alice\'s age:", ages["Alice"])\n\n# DataFrame — a full table\ndata = {\n    "Name":   ["Alice","Bob","Charlie","Diana"],\n    "Age":    [25, 30, 22, 28],\n    "City":   ["Accra","Kumasi","Tamale","Accra"],\n    "Score":  [85.0, 92.0, 78.0, 95.0],\n}\ndf = pd.DataFrame(data)\nprint("\\n", df)\nprint("Shape:", df.shape)'),
    md("## 2. Exploring a Dataset"),
    code('import pandas as pd, numpy as np\nnp.random.seed(42)\nn = 50\ndf = pd.DataFrame({\n    "Name":  [f"S{i}" for i in range(n)],\n    "Age":   np.random.randint(18,30,n),\n    "Math":  np.random.randint(40,100,n).astype(float),\n    "English": np.random.randint(40,100,n).astype(float),\n    "City":  np.random.choice(["Accra","Kumasi","Tamale"],n),\n})\ndf.loc[[5,15], "Math"] = np.nan  # add some missing values\n\nprint(df.head())          # first 5 rows\nprint("\\n", df.tail(3))  # last 3 rows\ndf.info()\nprint("\\n", df.describe())\nprint("\\nMissing:", df.isnull().sum())'),
    md("## 3. Selecting and Filtering"),
    code('# Select column(s)\nprint(df["Name"].head())\nprint(df[["Name","Math"]].head())\n\n# By position (iloc) and label (loc)\nprint(df.iloc[0])           # first row\nprint(df.loc[0:2, ["Name","Math","City"]])  # rows 0-2, specific cols\n\n# Filter rows by condition\nhigh = df[df["Math"] > 80]\nprint(f"\\nStudents with Math>80: {len(high)}")\n\n# Multiple conditions\ntop = df[(df["Math"] > 70) & (df["English"] > 70)]\nprint(f"Math>70 AND English>70: {len(top)}")\n\n# isin()\naccra = df[df["City"].isin(["Accra","Kumasi"])]\nprint(f"From Accra or Kumasi: {len(accra)}")'),
    md("## 4. Sorting, Missing Values, and GroupBy"),
    code('# Sort\nprint(df.sort_values("Math", ascending=False).head(5)[["Name","Math"]])\n\n# Fill missing values\ndf["Math"] = df["Math"].fillna(df["Math"].median())\nprint("Missing after fill:", df["Math"].isnull().sum())\n\n# GroupBy\nprint("\\nMean Math by City:")\nprint(df.groupby("City")["Math"].mean().round(1))\n\nprint("\\nFull summary by City:")\nprint(df.groupby("City").agg(\n    Count=(\"Name\",\"count\"),\n    Avg_Math=(\"Math\",\"mean\"),\n    Avg_English=(\"English\",\"mean\")\n).round(1))'),
    md("## 5. Merging DataFrames"),
    code('import pandas as pd\n\nstudents = pd.DataFrame({\n    "id":   [1,2,3,4],\n    "name": ["Alice","Bob","Charlie","Diana"],\n    "city_id": [1,2,1,3]\n})\ncities = pd.DataFrame({\n    "city_id": [1,2,3],\n    "city":    ["Accra","Kumasi","Tamale"]\n})\n\n# Inner join — only matching rows\nmerged = pd.merge(students, cities, on="city_id")\nprint(merged)\n\n# Concatenate — stack vertically\npart1 = students.iloc[:2]\npart2 = students.iloc[2:]\nprint("\\nConcatenated:")\nprint(pd.concat([part1, part2], ignore_index=True))'),
    md("## ✅ Summary\n\n| Task | Code |\n|---|---|\n| Load CSV | `pd.read_csv('file.csv')` |\n| Explore | `.head()`, `.info()`, `.describe()` |\n| Select col | `df['col']` or `df[['a','b']]` |\n| Filter | `df[df['col'] > value]` |\n| Sort | `.sort_values('col')` |\n| Missing | `.isnull().sum()`, `.fillna()` |\n| GroupBy | `.groupby('col').agg(...)` |\n| Merge | `pd.merge(df1, df2, on='key')` |"),
]))

print("\nNotebooks 1–9 created. Continuing with 10–20...")

# ===========================================================
# NOTEBOOK 10 — Understanding Data
# ===========================================================
save(f"{BASE}/10_Understanding_Data/10_Understanding_Data.ipynb", notebook([
    md("# Topic 10: Understanding Data\n\n**Topics:** Types of data · Descriptive statistics · Central tendency · Dispersion · Skewness & Kurtosis"),
    md("## 1. Types of Data\n\n| Category | Type | Examples |\n|---|---|---|\n| **Numerical** | Continuous | Height, salary, temperature |\n| **Numerical** | Discrete | Goals scored, number of children |\n| **Categorical** | Nominal | City, gender, blood type |\n| **Categorical** | Ordinal | Education level, star ratings |"),
    code('import pandas as pd\nimport numpy as np\n\ndf = pd.DataFrame({\n    "Name":       ["Alice","Bob","Charlie"],\n    "Age":        [25, 30, 22],          # Discrete numeric\n    "Height":     [165.2, 178.5, 171.0], # Continuous numeric\n    "City":       ["Accra","Kumasi","Tamale"],  # Nominal\n    "Education":  ["BSc","MSc","BSc"],   # Ordinal\n    "Rating":     [3, 5, 2],            # Ordinal (scale)\n})\nprint(df)\nprint("\\nData types:")\nprint(df.dtypes)'),
    md("## 2. Descriptive Statistics"),
    code('import numpy as np, pandas as pd\nnp.random.seed(42)\ndf = pd.DataFrame({\n    "Score":  np.random.normal(70,15,100).clip(0,100).round(1),\n    "Salary": np.random.normal(60000,15000,100).clip(25000,120000).round(-2),\n})\nprint(df.describe().round(2))'),
    md("## 3. Measures of Central Tendency"),
    code('scores = df["Score"]\nprint(f"Mean   (average)    : {scores.mean():.2f}")\nprint(f"Median (middle)     : {scores.median():.2f}")\nprint(f"Mode   (most common): {scores.mode()[0]:.2f}")\nprint("""\nWhen to use:\n  Mean   → symmetric data, no outliers\n  Median → skewed data or outliers (e.g. income)\n  Mode   → categorical data\n""")'),
    md("## 4. Measures of Dispersion"),
    code('print(f"Range     : {scores.max()-scores.min():.2f}")\nprint(f"Std Dev   : {scores.std():.2f}")\nprint(f"Variance  : {scores.var():.2f}")\nprint(f"IQR       : {scores.quantile(0.75)-scores.quantile(0.25):.2f}")\nprint(f"Q1 (25%): {scores.quantile(0.25):.2f}")\nprint(f"Q2 (50%): {scores.quantile(0.50):.2f}")\nprint(f"Q3 (75%): {scores.quantile(0.75):.2f}")'),
    md("## 5. Skewness and Kurtosis\n\n- **Skewness = 0** → symmetric · **> 0** → right-skewed · **< 0** → left-skewed  \n- **Kurtosis > 0** → heavy tails (more outliers) · **< 0** → light tails"),
    code('import numpy as np, pandas as pd\nsymm  = pd.Series(np.random.normal(50, 10, 1000))\nright = pd.Series(np.random.exponential(10, 1000))\nleft  = pd.Series(100 - np.random.exponential(10, 1000))\n\nprint("Skewness:")\nprint(f"  Symmetric   : {symm.skew():.3f}")\nprint(f"  Right-skewed: {right.skew():.3f}")\nprint(f"  Left-skewed : {left.skew():.3f}")\n\nprint("\\nKurtosis:")\nprint(f"  Symmetric   : {symm.kurtosis():.3f}")'),
    md("## ✅ Summary\n\n| Metric | Measures | Function |\n|---|---|---|\n| Mean | Center (average) | `.mean()` |\n| Median | Center (robust) | `.median()` |\n| Std Dev | Spread | `.std()` |\n| IQR | Spread (robust) | `.quantile(0.75) - .quantile(0.25)` |\n| Skewness | Asymmetry | `.skew()` |\n| Kurtosis | Tail weight | `.kurtosis()` |"),
]))

# ===========================================================
# NOTEBOOK 11 — Data Cleaning
# ===========================================================
save(f"{BASE}/11_Data_Cleaning/11_Data_Cleaning.ipynb", notebook([
    md("# Topic 11: Data Cleaning\n\n> 'Garbage in, garbage out.' - Cleaning data is 70-80% of real data work.\n\n**Topics:** Detect missing values - Duplicates - Text formatting - Outliers - Normalisation - Encoding"),
    md("## 1. Build a Messy Dataset"),
    code('import pandas as pd, numpy as np\n\ndf = pd.DataFrame({\n    "Name":   ["Alice","bob","CHARLIE","diana","  Eve  ","Frank","Alice",None],\n    "Age":    [25, 30, -5, 28, 200, 35, 25, np.nan],\n    "Salary": [45000,72000,38000,np.nan,55000,90000,45000,61000],\n    "Score":  [85,92,78,95,88,91,85,200],\n    "City":   ["Accra","kumasi","Tamale","ACCRA","Accra","Kumasi","Accra",np.nan],\n})\nprint(df.to_string())\nprint("\\nMissing values:")\nprint(df.isnull().sum())'),
    md("## 2. Remove Duplicates"),
    code('print("Before:", len(df))\nprint("Duplicates:", df.duplicated().sum())\n\ndf = df.drop_duplicates().reset_index(drop=True)\nprint("After:", len(df))'),
    md("## 3. Fix Text Formatting"),
    code('df["Name"] = df["Name"].str.strip().str.title().fillna("Unknown")\ndf["City"] = df["City"].str.strip().str.title()\nprint(df[["Name","City"]])'),
    md("## 4. Outlier Detection"),
    code('print("Age outliers (outside 0–100):")\nprint(df[(df["Age"]<0)|(df["Age"]>100)][["Name","Age"]])\n\nprint("\\nScore outliers (outside 0–100):")\nprint(df[(df["Score"]<0)|(df["Score"]>100)][["Name","Score"]])\n\n# Clip to valid range\ndf["Age"]   = df["Age"].clip(0, 100)\ndf["Score"] = df["Score"].clip(0, 100)\nprint("\\nAfter clipping:")\nprint(df[["Name","Age","Score"]])'),
    md("## 5. Fill Missing Values"),
    code('df["Age"]    = df["Age"].fillna(df["Age"].median())\ndf["Salary"] = df["Salary"].fillna(df["Salary"].median())\ndf["City"]   = df["City"].fillna(df["City"].mode()[0])\nprint("Missing values after filling:")\nprint(df.isnull().sum())'),
    md("## 6. Data Normalisation"),
    code('def min_max(s): return (s - s.min()) / (s.max() - s.min())\ndef z_score(s): return (s - s.mean()) / s.std()\n\ndf["Salary_MinMax"] = min_max(df["Salary"]).round(3)\ndf["Salary_ZScore"] = z_score(df["Salary"]).round(3)\n\nprint(df[["Name","Salary","Salary_MinMax","Salary_ZScore"]].to_string(index=False))'),
    md("## ✅ Final Clean Dataset"),
    code('print("Final clean dataset:")\nprint(df[["Name","Age","Salary","City","Score"]].to_string(index=False))'),
]))

# ===========================================================
# NOTEBOOK 12 — EDA Workflow
# ===========================================================
save(f"{BASE}/12_EDA_Workflow/12_EDA_Workflow.ipynb", notebook([
    md("# Topic 12: EDA Workflow (Exploratory Data Analysis)\n\nEDA = asking the right questions and letting the data answer.\n\n**Steps:** Overview → Univariate → Bivariate → Multivariate → Insights"),
    md("## 0. Build Dataset"),
    code('import numpy as np, pandas as pd\nnp.random.seed(0)\nn = 200\ndf = pd.DataFrame({\n    "Age":        np.random.randint(22,60,n),\n    "Gender":     np.random.choice(["Male","Female"],n,p=[0.55,0.45]),\n    "Education":  np.random.choice(["BSc","MSc","PhD","HND"],n,p=[0.45,0.30,0.10,0.15]),\n    "Department": np.random.choice(["Engineering","Sales","HR","Finance"],n),\n    "Experience": np.random.randint(0,30,n),\n    "Salary":     np.random.normal(60000,18000,n).clip(20000,130000).round(-2),\n    "Performance":np.random.choice([1,2,3,4,5],n,p=[0.05,0.10,0.30,0.35,0.20]),\n})\ndf["Salary"] = df["Salary"].fillna(df["Salary"].median())\nprint(df.shape)\ndf.head()'),
    md("## 1. Dataset Overview"),
    code('df.info()\nprint(df.describe().round(1))\nprint("\\nMissing:", df.isnull().sum())'),
    md("## 2. Univariate Analysis — one variable at a time"),
    code('for col in ["Age","Salary","Experience"]:\n    s = df[col]\n    print(f"\\n{col}: mean={s.mean():.1f}, median={s.median():.1f}, std={s.std():.1f}, skew={s.skew():.2f}")\n\nfor col in ["Gender","Education","Department"]:\n    print(f"\\n{col}:\\n{df[col].value_counts()}")'),
    md("## 3. Bivariate Analysis — two variables"),
    code('print("Salary by Gender:")\nprint(df.groupby("Gender")["Salary"].agg(["mean","median","count"]).round(0))\n\nprint("\\nSalary by Department:")\nprint(df.groupby("Department")["Salary"].mean().sort_values(ascending=False).round(0))\n\nprint("\\nCorrelation matrix:")\nprint(df[["Age","Experience","Salary","Performance"]].corr().round(3))'),
    md("## 4. Multivariate Analysis"),
    code('print("Salary by Gender AND Department:")\npivot = df.pivot_table(values="Salary", index="Department", columns="Gender", aggfunc="mean")\nprint(pivot.round(0))\n\nprint("\\nPerformance by Department:")\nprint(df.groupby("Department")["Performance"].mean().round(2).sort_values(ascending=False))'),
    md("## 5. Key Insights"),
    code('print("=== KEY INSIGHTS ===")\nprint(f"Mean salary  : ${df[\'Salary\'].mean():,.0f}")\nprint(f"Median salary: ${df[\'Salary\'].median():,.0f}")\nprint(f"Salary skew  : {df[\'Salary\'].skew():.2f} (right-skewed = a few high earners)")\n\ngap = df.groupby("Gender")["Salary"].mean()\nprint(f"\\nGender gap: Male ${gap.get(\'Male\',0):,.0f} vs Female ${gap.get(\'Female\',0):,.0f}")\n\ntop_dept = df.groupby("Department")["Salary"].mean().idxmax()\nprint(f"Top-paying dept: {top_dept}")\n\nprint(f"\\nExp ↔ Salary corr: {df[\'Experience\'].corr(df[\'Salary\']):.3f}")'),
]))

# ===========================================================
# NOTEBOOK 13 — Matplotlib
# ===========================================================
save(f"{BASE}/13_Matplotlib/13_Matplotlib.ipynb", notebook([
    md("# Topic 13: Matplotlib – Data Visualization\n\nMatplotlib is the core plotting library for Python.\n\n```bash\npip install matplotlib\n```\n\n> **Tip:** In Jupyter, add `%matplotlib inline` to show plots inline."),
    code("%matplotlib inline\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport pandas as pd\nnp.random.seed(42)\nprint('Libraries loaded.')"),
    md("## 1. Anatomy of a Plot\n\n```\nfig, ax = plt.subplots()  # fig = canvas, ax = the chart area\nax.plot(x, y)             # draw something\nax.set_title('My Plot')   # add title\nax.set_xlabel('X axis')   # label axes\nplt.show()                # display\n```"),
    md("## 2. Line Plot"),
    code('months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]\nsales_23 = [120,135,148,162,175,190,180,168,155,170,185,200]\nsales_24 = [130,142,160,172,188,202,195,180,170,185,200,220]\n\nfig, ax = plt.subplots(figsize=(10,4))\nax.plot(months, sales_23, marker="o", label="2023", linewidth=2)\nax.plot(months, sales_24, marker="s", label="2024", linewidth=2, linestyle="--")\nax.set_title("Monthly Sales 2023 vs 2024", fontsize=13, fontweight="bold")\nax.set_xlabel("Month"); ax.set_ylabel("Sales")\nax.legend(); ax.grid(True, alpha=0.3)\nplt.tight_layout(); plt.show()'),
    md("## 3. Bar Chart"),
    code('depts = ["Engineering","Sales","HR","Finance","Marketing"]\nsalary = [85000, 65000, 58000, 72000, 60000]\n\nfig, ax = plt.subplots(figsize=(8,4))\nbars = ax.bar(depts, salary, color=["#2196F3","#FF9800","#4CAF50","#9C27B0","#F44336"])\nfor b in bars:\n    ax.text(b.get_x()+b.get_width()/2, b.get_height()+500,\n            f"${b.get_height():,.0f}", ha="center", fontsize=8)\nax.set_title("Average Salary by Department")\nax.set_ylabel("Salary ($)"); ax.grid(axis="y", alpha=0.3)\nplt.tight_layout(); plt.show()'),
    md("## 4. Histogram"),
    code('scores = np.random.normal(70, 12, 500)\n\nfig, ax = plt.subplots(figsize=(8,4))\nax.hist(scores, bins=20, color="steelblue", edgecolor="white", alpha=0.8)\nax.axvline(scores.mean(),   color="red",  linestyle="--", label=f"Mean={scores.mean():.1f}")\nax.axvline(np.median(scores), color="navy", linestyle=":",  label=f"Median={np.median(scores):.1f}")\nax.set_title("Distribution of Student Scores")\nax.set_xlabel("Score"); ax.set_ylabel("Count"); ax.legend()\nplt.tight_layout(); plt.show()'),
    md("## 5. Scatter Plot"),
    code('exp = np.random.randint(0, 30, 150)\nsal = 30000 + exp*2000 + np.random.normal(0, 8000, 150)\n\nfig, ax = plt.subplots(figsize=(7,4))\nax.scatter(exp, sal, alpha=0.5, color="steelblue")\nz = np.polyfit(exp, sal, 1)\nax.plot(np.linspace(0,30), np.poly1d(z)(np.linspace(0,30)), "r--", label="Trend")\nax.set_title("Experience vs Salary")\nax.set_xlabel("Experience (years)"); ax.set_ylabel("Salary ($)")\nax.legend(); ax.grid(True, alpha=0.3)\nplt.tight_layout(); plt.show()'),
    md("## 6. Subplots — Multiple Charts in One Figure"),
    code('fig, axes = plt.subplots(2, 2, figsize=(11, 7))\nfig.suptitle("Employee Dashboard", fontsize=15, fontweight="bold")\n\nages = np.random.randint(22, 60, 200)\nsalaries = np.random.normal(60000, 15000, 200)\nperf = np.random.choice([1,2,3,4,5], 200)\ngender = np.random.choice(["Male","Female"], 200)\n\naxes[0,0].hist(ages, bins=15, color="skyblue", edgecolor="white")\naxes[0,0].set_title("Age Distribution")\n\naxes[0,1].hist(salaries, bins=20, color="salmon", edgecolor="white")\naxes[0,1].set_title("Salary Distribution")\n\ncounts = pd.Series(perf).value_counts().sort_index()\naxes[1,0].bar(counts.index, counts.values, color="mediumseagreen")\naxes[1,0].set_title("Performance Ratings")\n\ngc = pd.Series(gender).value_counts()\naxes[1,1].pie(gc, labels=gc.index, autopct="%1.0f%%", colors=["steelblue","lightcoral"])\naxes[1,1].set_title("Gender")\n\nplt.tight_layout(); plt.show()'),
    md("## ✅ Summary\n\n| Chart | Use | Function |\n|---|---|---|\n| Line | Trends over time | `ax.plot()` |\n| Bar | Compare categories | `ax.bar()` |\n| Histogram | Distribution | `ax.hist()` |\n| Scatter | Relationship | `ax.scatter()` |\n| Multiple | Dashboards | `plt.subplots(rows,cols)` |"),
]))

# ===========================================================
# NOTEBOOK 14 — Seaborn
# ===========================================================
save(f"{BASE}/14_Seaborn/14_Seaborn.ipynb", notebook([
    md("# Topic 14: Seaborn – Statistical Visualization\n\nSeaborn is built on Matplotlib and creates beautiful statistical charts with less code.\n\n```bash\npip install seaborn\n```"),
    code("%matplotlib inline\nimport numpy as np, pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nnp.random.seed(42)\nsns.set_theme(style='whitegrid', palette='muted')\n\nn = 300\ndf = pd.DataFrame({\n    'Gender':     np.random.choice(['Male','Female'], n),\n    'Department': np.random.choice(['Engineering','Sales','HR','Finance'], n),\n    'Education':  np.random.choice(['BSc','MSc','PhD'], n),\n    'Experience': np.random.randint(0, 30, n),\n    'Salary':     np.random.normal(65000,18000,n).clip(25000,130000).round(-2),\n    'Score':      np.random.normal(72, 12, n).clip(30,100).round(1),\n    'Performance':np.random.choice([1,2,3,4,5], n),\n})\ndf['Salary'] = (df['Salary'] + df['Experience']*1200).clip(25000,140000)\nprint('Dataset ready:', df.shape)"),
    md("## 1. Distribution Plots"),
    code('fig, axes = plt.subplots(1, 2, figsize=(12, 4))\nsns.histplot(df["Salary"], bins=25, kde=True, ax=axes[0], color="steelblue")\naxes[0].set_title("Salary Distribution")\n\nfor g, c in zip(["Male","Female"],["steelblue","coral"]):\n    sns.kdeplot(df[df["Gender"]==g]["Salary"], ax=axes[1], fill=True, label=g, alpha=0.4, color=c)\naxes[1].set_title("Salary by Gender"); axes[1].legend()\n\nplt.tight_layout(); plt.show()'),
    md("## 2. Box & Violin Plots\n\n- **Box plot:** shows median, Q1, Q3, whiskers, and outliers.\n- **Violin plot:** box plot + density curve — shows shape of distribution."),
    code('fig, axes = plt.subplots(1, 2, figsize=(12, 4))\nsns.boxplot(data=df, x="Department", y="Salary", ax=axes[0], palette="Set2")\naxes[0].set_title("Box Plot"); axes[0].tick_params(axis="x", rotation=15)\n\nsns.violinplot(data=df, x="Department", y="Salary", ax=axes[1], palette="Set3", inner="quartile")\naxes[1].set_title("Violin Plot"); axes[1].tick_params(axis="x", rotation=15)\n\nplt.tight_layout(); plt.show()'),
    md("## 3. Heatmaps\n\nCorrelation heatmaps show which variables are related."),
    code('fig, axes = plt.subplots(1, 2, figsize=(13, 4))\n\ncorr = df[["Experience","Salary","Score","Performance"]].corr()\nsns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=axes[0])\naxes[0].set_title("Correlation Heatmap")\n\npivot = df.pivot_table("Salary","Department","Education","mean")\nsns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd", ax=axes[1])\naxes[1].set_title("Mean Salary by Dept & Education")\n\nplt.tight_layout(); plt.show()'),
    md("## 4. Pair Plot\n\nPair plots show scatter plots for every pair of numeric variables."),
    code('sample = df[["Experience","Salary","Score","Gender"]].sample(100, random_state=1)\nsns.pairplot(sample, hue="Gender",\n             palette={"Male":"steelblue","Female":"coral"},\n             diag_kind="kde", plot_kws={"alpha":0.5,"s":20})\nplt.suptitle("Pair Plot", y=1.02); plt.show()'),
    md("## 5. Scatter & Regression Plots"),
    code('fig, axes = plt.subplots(1, 2, figsize=(12, 4))\n\nsns.scatterplot(data=df, x="Experience", y="Salary",\n                hue="Department", alpha=0.6, ax=axes[0])\naxes[0].set_title("Experience vs Salary by Department")\naxes[0].legend(fontsize=7)\n\nsns.regplot(data=df, x="Experience", y="Salary", ax=axes[1],\n            scatter_kws={"alpha":0.3}, line_kws={"color":"red","linewidth":2})\naxes[1].set_title("With Regression Line")\n\nplt.tight_layout(); plt.show()'),
    md("## ✅ Summary\n\n| Chart | Seaborn function |\n|---|---|\n| Histogram + density | `sns.histplot(kde=True)` |\n| Density only | `sns.kdeplot(fill=True)` |\n| Box plot | `sns.boxplot()` |\n| Violin plot | `sns.violinplot()` |\n| Heatmap | `sns.heatmap(annot=True)` |\n| Pair plot | `sns.pairplot(hue=...)` |\n| Scatter + trend | `sns.regplot()` |"),
]))

# ===========================================================
# NOTEBOOK 15 — ML Foundations
# ===========================================================
save(f"{BASE}/15_ML_Foundations/15_ML_Foundations.ipynb", notebook([
    md("# Topic 15: Machine Learning Foundations\n\n**Topics:** What is ML · Types of ML · ML vs AI vs GenAI · ML workflow"),
    md("## 1. What is Machine Learning?\n\n> Machine Learning = teaching computers to learn patterns from data, without explicitly programming every rule.\n\n| Approach | Formula |\n|---|---|\n| Traditional programming | Data + Rules → Answers |\n| Machine Learning | Data + Answers → Rules (learned!) |"),
    md("## 2. Types of Machine Learning\n\n### Supervised Learning\n- You provide **labeled** data (input + correct output)\n- **Regression:** predict a number (salary, price, temperature)\n- **Classification:** predict a category (spam/not spam, pass/fail)\n\n### Unsupervised Learning\n- **No labels** — the model finds patterns itself\n- **Clustering:** group similar items (K-Means)\n- **Dimensionality reduction** (PCA)\n\n### Reinforcement Learning\n- Agent learns by **trial and error** with rewards/penalties\n- Used in game AI, robotics, self-driving cars\n\n### Generative AI (Self-Supervised)\n- Model creates its own training signal from raw data\n- Foundation of GPT, Claude, Gemini, DALL-E"),
    md("## 3. ML vs AI vs GenAI\n\n```\nAI (anything that simulates intelligence)\n└── ML (learns from data)\n    └── Deep Learning (multi-layer neural networks)\n        └── GenAI (creates new content: text, images, code)\n```"),
    md("## 4. The ML Workflow\n\n1. **Define the problem** — What are you predicting?\n2. **Collect & clean data** — Handle missing values, outliers\n3. **Explore (EDA)** — Understand patterns\n4. **Prepare** — Train/test split, scale, encode\n5. **Train** — Fit a model to training data\n6. **Evaluate** — Test on held-out data\n7. **Improve** — Tune, try different models\n8. **Deploy** — Put model in production"),
    md("## 5. Hands-on Demo: Learning a Pattern from Data"),
    code('import numpy as np\n\nhours  = np.array([1,2,3,4,5,6,7,8,9,10])\nscores = np.array([45,52,58,65,70,76,82,85,91,96])\n\n# Fit a linear equation: score = slope * hours + intercept\nm = np.polyfit(hours, scores, 1)\nslope, intercept = m[0], m[1]\nprint(f"Learned equation: Score = {slope:.2f} x Hours + {intercept:.2f}")\n\n# Predict for new students\nfor h in [3.5, 7.5, 12]:\n    pred = slope * h + intercept\n    print(f"  {h} hours → predicted score: {pred:.1f}")\n\n# Evaluate: mean absolute error\npredicted = slope * hours + intercept\nmae = np.mean(np.abs(scores - predicted))\nprint(f"\\nMean Absolute Error: {mae:.2f} points")'),
    code('%matplotlib inline\nimport matplotlib.pyplot as plt\n\nfig, ax = plt.subplots(figsize=(7,4))\nax.scatter(hours, scores, color="steelblue", s=80, label="Actual data")\nx_line = np.linspace(1,10,100)\nax.plot(x_line, slope*x_line+intercept, "r-", linewidth=2, label="Learned line")\nax.set_xlabel("Hours Studied"); ax.set_ylabel("Score")\nax.set_title("Linear Regression — Learning a Pattern")\nax.legend(); ax.grid(True, alpha=0.3)\nplt.tight_layout(); plt.show()'),
    md("## ✅ Summary\n\n| Term | Definition |\n|---|---|\n| Machine Learning | Teaching machines using data |\n| Supervised | Labeled data → learns input→output |\n| Unsupervised | Unlabeled data → finds patterns |\n| Training | Fitting the model on known data |\n| Prediction | Using the model on new data |\n| Evaluation | Measuring how well the model performs |"),
]))

# ===========================================================
# NOTEBOOK 16 — Data Preparation
# ===========================================================
save(f"{BASE}/16_Data_Preparation/16_Data_Preparation.ipynb", notebook([
    md("# Topic 16: Data Preparation for Machine Learning\n\nBefore training any ML model, data must be properly prepared.\n\n**Topics:** Train-test split · Feature selection · Scaling · Encoding\n\n```bash\npip install scikit-learn\n```"),
    code('import numpy as np, pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.preprocessing import MinMaxScaler, StandardScaler, LabelEncoder\nnp.random.seed(42)\n\nn = 300\ndf = pd.DataFrame({\n    "Age":        np.random.randint(22,60,n),\n    "Experience": np.random.randint(0,30,n),\n    "Salary":     np.random.normal(60000,15000,n).clip(25000,120000).round(-2),\n    "Score":      np.random.normal(70,12,n).clip(30,100).round(1),\n    "Gender":     np.random.choice(["Male","Female"],n),\n    "Education":  np.random.choice(["BSc","MSc","PhD"],n),\n    "Promoted":   np.random.choice([0,1],n,p=[0.65,0.35]),\n})\ndf.loc[(df["Salary"]>75000)&(df["Experience"]>10),"Promoted"]=1\nprint(df.head()); print(df.shape)'),
    md("## 1. Train-Test Split\n\n> Split data so the model is **trained** on one part and **tested** on a completely unseen part."),
    code('X = df[["Age","Experience","Salary","Score"]]\ny = df["Promoted"]\n\nX_train, X_test, y_train, y_test = train_test_split(\n    X, y, test_size=0.20, random_state=42, stratify=y\n)\n\nprint(f"Training : {len(X_train)} rows")\nprint(f"Test     : {len(X_test)} rows")\nprint(f"\\nClass distribution in train:")\nprint(y_train.value_counts(normalize=True).round(3))'),
    md("## 2. Feature Scaling\n\nScaling ensures no single feature dominates just because its values are larger.\n\n| Method | Formula | Output |\n|---|---|---|\n| Min-Max | (x - min) / (max - min) | [0, 1] |\n| Z-score | (x - mean) / std | mean=0, std=1 |"),
    code('# IMPORTANT: fit on training data ONLY, then transform both\nscaler = StandardScaler()\nX_train_scaled = scaler.fit_transform(X_train)\nX_test_scaled  = scaler.transform(X_test)   # use same scaler!\n\nprint("Before scaling — Salary range:", X_train["Salary"].min(), "to", X_train["Salary"].max())\nprint("After scaling  — Salary range:", X_train_scaled[:,2].min().round(2),\n      "to", X_train_scaled[:,2].max().round(2))'),
    md("## 3. Encoding Categorical Variables\n\nML models need numbers — text categories must be converted.\n\n| Method | When to use |\n|---|---|\n| Label Encoding | Ordinal (BSc < MSc < PhD) |\n| One-Hot Encoding | Nominal (no order: city, gender) |"),
    code('# One-Hot Encoding (get_dummies)\ngender_ohe = pd.get_dummies(df["Gender"], prefix="Gender", drop_first=True)\nprint("One-Hot Encoded Gender:\\n", gender_ohe.head())\n\n# Label Encoding for Education (has natural order)\nedu_map = {"BSc": 0, "MSc": 1, "PhD": 2}\ndf["Education_Enc"] = df["Education"].map(edu_map)\nprint("\\nEducation encoded:\\n", df[["Education","Education_Enc"]].drop_duplicates())'),
    md("## 4. Full Preparation Pipeline"),
    code('from sklearn.preprocessing import StandardScaler\n\n# Encode\ndf["Gender_Enc"] = (df["Gender"] == "Male").astype(int)\ndept_dummies = pd.get_dummies(df.get("Department", pd.Series(["A"]*n)), prefix="Dept", drop_first=True)\n\nfeatures = ["Age","Experience","Salary","Score","Gender_Enc","Education_Enc"]\nX_all = df[features]\ny_all = df["Promoted"]\n\nX_tr, X_te, y_tr, y_te = train_test_split(X_all, y_all, test_size=0.2, random_state=42)\nsc = StandardScaler()\nX_tr[["Age","Experience","Salary","Score"]] = sc.fit_transform(X_tr[["Age","Experience","Salary","Score"]])\nX_te[["Age","Experience","Salary","Score"]] = sc.transform(X_te[["Age","Experience","Salary","Score"]])\n\nprint(f"Ready for ML!  Train: {X_tr.shape}  Test: {X_te.shape}")'),
    md("## ✅ Summary\n\n1. **Split first** — then fit the scaler on training data only\n2. **Scale numeric** features before algorithms that care about distance\n3. **Label-encode** ordinal categories (with natural order)\n4. **One-hot-encode** nominal categories (no natural order)\n5. Never let test data influence training preprocessing"),
]))

# ===========================================================
# NOTEBOOK 17 — First ML Models
# ===========================================================
save(f"{BASE}/17_First_ML_Models/17_First_ML_Models.ipynb", notebook([
    md("# Topic 17: First ML Models\n\nWe'll train 4 beginner models using scikit-learn.\n\n**Models:** Linear Regression · Logistic Regression · KNN · Decision Tree"),
    code('%matplotlib inline\nimport numpy as np, pandas as pd, matplotlib.pyplot as plt\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, r2_score\nimport numpy as np; np.random.seed(42)\n\n# Regression dataset\nexp = np.random.randint(0,30,200).reshape(-1,1)\nsal = 30000 + exp.ravel()*2500 + np.random.normal(0,6000,200)\n\n# Classification dataset\nn=200\nX_clf = pd.DataFrame({"Age":np.random.randint(22,55,n),"Experience":np.random.randint(0,25,n),\n                       "Salary":np.random.normal(60000,15000,n).clip(25000,120000),\n                       "Score":np.random.normal(72,12,n).clip(30,100)})\ny_clf = (X_clf["Salary"]>65000).astype(int)\n\nX_tr,X_te,y_tr,y_te = train_test_split(X_clf,y_clf,test_size=0.2,random_state=42)\nsc = StandardScaler()\nX_tr_s = sc.fit_transform(X_tr); X_te_s = sc.transform(X_te)\nprint("Datasets ready.")'),
    md("## 1. Linear Regression\n\n> Fits the best straight line through the data to predict a **continuous number**."),
    code('from sklearn.linear_model import LinearRegression\nfrom sklearn.metrics import r2_score, mean_absolute_error\nimport numpy as np\n\ne_tr, e_te, s_tr, s_te = train_test_split(exp, sal, test_size=0.2, random_state=42)\nmodel_lr = LinearRegression()\nmodel_lr.fit(e_tr, s_tr)\n\ny_pred = model_lr.predict(e_te)\nprint(f"Equation: Salary = {model_lr.coef_[0]:,.0f} x Experience + {model_lr.intercept_:,.0f}")\nprint(f"MAE: ${mean_absolute_error(s_te, y_pred):,.0f}")\nprint(f"R² : {r2_score(s_te, y_pred):.3f}")\n\nfor h in [2, 10, 20]:\n    print(f"  {h} years → ${model_lr.predict([[h]])[0]:,.0f}")'),
    md("## 2. Logistic Regression\n\n> Predicts a **probability** and classifies into 0 or 1."),
    code('from sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score, classification_report\n\nmodel_log = LogisticRegression(random_state=42)\nmodel_log.fit(X_tr_s, y_tr)\ny_pred_log = model_log.predict(X_te_s)\n\nprint(f"Accuracy: {accuracy_score(y_te, y_pred_log):.2%}")\nprint(classification_report(y_te, y_pred_log, target_names=["Class 0","Class 1"]))'),
    md("## 3. K-Nearest Neighbors (KNN)\n\n> Classifies based on the **k most similar** training examples."),
    code('from sklearn.neighbors import KNeighborsClassifier\n\nprint(f"Trying different k values:")\nfor k in [1, 3, 5, 7, 11, 15]:\n    knn = KNeighborsClassifier(n_neighbors=k)\n    knn.fit(X_tr_s, y_tr)\n    acc = accuracy_score(y_te, knn.predict(X_te_s))\n    print(f"  k={k:>2}: {acc:.2%}")'),
    md("## 4. Decision Tree\n\n> Makes predictions by asking a series of **yes/no questions**."),
    code('from sklearn.tree import DecisionTreeClassifier, export_text\n\nmodel_dt = DecisionTreeClassifier(max_depth=4, random_state=42)\nmodel_dt.fit(X_tr, y_tr)  # no scaling needed for trees\nprint(f"Accuracy: {accuracy_score(y_te, model_dt.predict(X_te)):.2%}")\nprint("\\nTree rules:")\nprint(export_text(model_dt, feature_names=list(X_clf.columns)))'),
    md("## 5. Model Comparison"),
    code('from sklearn.linear_model import LogisticRegression\nfrom sklearn.neighbors import KNeighborsClassifier\nfrom sklearn.tree import DecisionTreeClassifier\nfrom sklearn.metrics import accuracy_score\n\nresults = {\n    "Logistic Regression": accuracy_score(y_te, LogisticRegression(random_state=42).fit(X_tr_s,y_tr).predict(X_te_s)),\n    "KNN (k=5)":           accuracy_score(y_te, KNeighborsClassifier(5).fit(X_tr_s,y_tr).predict(X_te_s)),\n    "Decision Tree (d=4)": accuracy_score(y_te, DecisionTreeClassifier(max_depth=4,random_state=42).fit(X_tr,y_tr).predict(X_te)),\n}\nprint(f"{"Model":<25} {"Accuracy":>10}")\nprint("-"*38)\nfor name, acc in sorted(results.items(), key=lambda x:-x[1]):\n    print(f"{name:<25} {acc:>10.2%}  {"█"*int(acc*30)}")'),
    md("## ✅ Summary\n\n| Model | Type | Needs Scaling |\n|---|---|---|\n| Linear Regression | Regression | Yes |\n| Logistic Regression | Classification | Yes |\n| KNN | Classification | Yes |\n| Decision Tree | Classification | No |"),
]))

# ===========================================================
# NOTEBOOK 18 — Model Evaluation
# ===========================================================
save(f"{BASE}/18_Model_Evaluation/18_Model_Evaluation.ipynb", notebook([
    md("# Topic 18: Model Evaluation\n\n**Topics:** Accuracy · Precision · Recall · F1 · Confusion Matrix · Regression metrics · Overfitting vs Underfitting"),
    code('%matplotlib inline\nimport numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns\nfrom sklearn.model_selection import train_test_split, cross_val_score\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.tree import DecisionTreeClassifier\nfrom sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix\nnp.random.seed(42)\n\nX = pd.DataFrame({"A":np.random.randn(400),"B":np.random.randn(400),"C":np.random.randn(400),"D":np.random.randn(400)})\ny = (X["A"] + X["B"] > 0).astype(int)\nX_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)\nsc = StandardScaler()\nX_tr_s, X_te_s = sc.fit_transform(X_tr), sc.transform(X_te)\nmodel = LogisticRegression(random_state=42).fit(X_tr_s, y_tr)\ny_pred = model.predict(X_te_s)\nprint("Setup complete.")'),
    md("## 1. The Four Classification Metrics\n\n| Metric | Formula | Good when |\n|---|---|---|\n| **Accuracy** | Correct / Total | Classes are balanced |\n| **Precision** | TP / (TP+FP) | False positives are costly |\n| **Recall** | TP / (TP+FN) | False negatives are costly |\n| **F1-Score** | 2×P×R/(P+R) | Need balance of precision & recall |"),
    code('print(f"Accuracy  : {accuracy_score(y_te, y_pred):.2%}")\nprint(f"Precision : {precision_score(y_te, y_pred):.2%}")\nprint(f"Recall    : {recall_score(y_te, y_pred):.2%}")\nprint(f"F1-Score  : {f1_score(y_te, y_pred):.2%}")'),
    md("## 2. Confusion Matrix"),
    code('from sklearn.metrics import ConfusionMatrixDisplay\n\ncm = confusion_matrix(y_te, y_pred)\ntn, fp, fn, tp = cm.ravel()\nprint(f"True Negatives : {tn}")\nprint(f"False Positives: {fp}  (predicted Yes but actually No)")\nprint(f"False Negatives: {fn}  (predicted No  but actually Yes)")\nprint(f"True Positives : {tp}")\n\nfig, ax = plt.subplots(figsize=(5,4))\nsns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,\n            xticklabels=["Pred 0","Pred 1"], yticklabels=["Actual 0","Actual 1"])\nax.set_title("Confusion Matrix")\nplt.tight_layout(); plt.show()'),
    md("## 3. Regression Metrics\n\n| Metric | Measures |\n|---|---|\n| **MAE** | Average absolute prediction error (same unit as target) |\n| **RMSE** | Like MAE but penalises large errors more |\n| **R²** | Proportion of variance explained (1 = perfect) |"),
    code('from sklearn.linear_model import LinearRegression\nfrom sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score\n\nexp = np.random.randint(0,30,200).reshape(-1,1)\nsal = 28000 + exp.ravel()*2400 + np.random.normal(0,5000,200)\ne_tr,e_te,s_tr,s_te = train_test_split(exp,sal,test_size=0.2,random_state=42)\nreg = LinearRegression().fit(e_tr, s_tr)\npred = reg.predict(e_te)\n\nprint(f"MAE : ${mean_absolute_error(s_te,pred):,.0f}")\nprint(f"RMSE: ${mean_squared_error(s_te,pred)**0.5:,.0f}")\nprint(f"R²  : {r2_score(s_te,pred):.3f}")'),
    md("## 4. Overfitting vs Underfitting\n\n| | Underfitting | Good Fit | Overfitting |\n|---|---|---|---|\n| Train accuracy | Low | High | Very High |\n| Test accuracy | Low | High | Low |\n| Gap | Small | Small | Large |"),
    code('depths = range(1, 16)\ntrain_acc, test_acc = [], []\nfor d in depths:\n    dt = DecisionTreeClassifier(max_depth=d, random_state=42).fit(X_tr_s, y_tr)\n    train_acc.append(accuracy_score(y_tr, dt.predict(X_tr_s)))\n    test_acc.append(accuracy_score(y_te, dt.predict(X_te_s)))\n\nfig, ax = plt.subplots(figsize=(8,4))\nax.plot(depths, train_acc, "o-", label="Train", color="blue")\nax.plot(depths, test_acc,  "s-", label="Test",  color="red")\nax.axvline(3, linestyle="--", color="green", alpha=0.7, label="Sweet spot")\nax.set_title("Overfitting vs Underfitting")\nax.set_xlabel("Tree Depth"); ax.set_ylabel("Accuracy")\nax.legend(); ax.grid(True, alpha=0.3)\nplt.tight_layout(); plt.show()'),
    md("## 5. Cross-Validation\n\nMore reliable than a single train/test split — trains and tests **k** times."),
    code('from sklearn.model_selection import cross_val_score\n\nfor name, mdl in [("Logistic Regression", LogisticRegression(random_state=42)),\n                   ("Decision Tree d=3",  DecisionTreeClassifier(max_depth=3, random_state=42))]:\n    cv = cross_val_score(mdl, sc.fit_transform(X), y, cv=5, scoring="accuracy")\n    print(f"{name:<25} mean={cv.mean():.2%}  std={cv.std():.3f}")'),
    md("## ✅ Summary\n\n- Use **accuracy** only when classes are balanced.\n- Use **precision** when false positives are costly.\n- Use **recall** when false negatives are costly.\n- **F1** balances precision and recall.\n- Always check training **and** test performance — a big gap means overfitting.\n- Use **cross-validation** for a more reliable estimate."),
]))

# ===========================================================
# NOTEBOOK 19 — Python for GenAI
# ===========================================================
save(f"{BASE}/19_Python_for_GenAI/19_Python_for_GenAI.ipynb", notebook([
    md("# Topic 19: Python Skills for GenAI\n\n**Topics:** Large data · Embeddings · Text preprocessing · Tokenization · Bag of Words · TF-IDF · AI libraries"),
    md("## 1. Working with Large Datasets Efficiently"),
    code('# Generator: yields one item at a time — low memory\ndef data_generator(n):\n    for i in range(n):\n        yield {"id": i, "text": f"Document {i}", "label": i % 2}\n\ntotal, counts = 0, {0:0, 1:0}\nfor rec in data_generator(1_000_000):\n    counts[rec["label"]] += 1\n    total += 1\n\nprint(f"Processed {total:,} records")\nprint(f"Class distribution: {counts}")'),
    md("## 2. Understanding Embeddings\n\nAn **embedding** is a list of numbers (vector) that represents a word or sentence.\nSimilar meanings → similar vectors.\n\nFamous example: `king - man + woman ≈ queen`"),
    code('import numpy as np\n\nembeddings = {\n    "king":  np.array([0.82, 0.14, -0.31]),\n    "queen": np.array([0.79, 0.18, -0.28]),\n    "man":   np.array([0.65, 0.05, -0.40]),\n    "woman": np.array([0.62, 0.09, -0.37]),\n    "car":   np.array([0.02, -0.55, 0.80]),\n}\n\ndef cosine_sim(a, b):\n    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))\n\nprint("Similarity:")\nfor w1, w2 in [("king","queen"),("king","car"),("man","woman")]:\n    print(f"  {w1:6} ↔ {w2:6}: {cosine_sim(embeddings[w1],embeddings[w2]):.3f}")\n\n# king - man + woman = ?\nresult = embeddings["king"] - embeddings["man"] + embeddings["woman"]\nprint("\\nking - man + woman similarity to each word:")\nfor w, v in embeddings.items():\n    print(f"  {w}: {cosine_sim(result,v):.3f}")'),
    md("## 3. Text Preprocessing"),
    code('import re\n\ntexts = [\n    "The quick brown fox jumps over the lazy dog!",\n    "Machine Learning and AI are transforming the world.",\n    "Python is a GREAT language for Data Science & GenAI.",\n]\n\nSTOPWORDS = {"the","is","a","an","and","are","to","for","of","in","it","be","with","was"}\n\ndef preprocess(text):\n    text = text.lower()\n    text = re.sub(r"[^a-z0-9\\s]", "", text)\n    tokens = [w for w in text.split() if w not in STOPWORDS]\n    return tokens\n\nfor t in texts:\n    print(f"Original : {t}")\n    print(f"Processed: {preprocess(t)}")\n    print()'),
    md("## 4. Tokenization"),
    code('from collections import Counter\nimport re\n\ndef tokenize(text):\n    return re.sub(r"[^a-zA-Z0-9\\s]"," ",text).lower().split()\n\nall_docs = [\n    "I love machine learning",\n    "machine learning is fun",\n    "I love Python for machine learning",\n    "deep learning is part of machine learning",\n]\n\nall_tokens = [t for doc in all_docs for t in tokenize(doc)]\nvocab = sorted(set(all_tokens))\nword2id = {w:i for i,w in enumerate(vocab)}\n\nprint(f"Vocabulary ({len(vocab)} words): {vocab[:10]}...")\n\nsample = "machine learning is great"\nids = [word2id.get(w, -1) for w in sample.split()]\nprint(f"\\nText  : {sample}")\nprint(f"IDs   : {ids}")\n\nprint("\\nTop 10 words:")\nfor w, c in Counter(all_tokens).most_common(10):\n    print(f"  {w!r}: {c}")'),
    md("## 5. Bag of Words & TF-IDF"),
    code('from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer\nimport pandas as pd\n\ndocs = [\n    "I love machine learning",\n    "machine learning is fun",\n    "I love Python for machine learning",\n    "deep learning is part of machine learning",\n]\n\n# Bag of Words\ncv = CountVectorizer()\nbow = pd.DataFrame(cv.fit_transform(docs).toarray(), columns=cv.get_feature_names_out())\nprint("Bag of Words:")\nprint(bow)\n\n# TF-IDF\ntfidf = TfidfVectorizer()\ntf = pd.DataFrame(tfidf.fit_transform(docs).toarray().round(3),\n                   columns=tfidf.get_feature_names_out())\nprint("\\nTF-IDF:")\nprint(tf)'),
    md("## 6. GenAI API Structure (Reference)\n\nYou do **not** need to train your own model. Call a powerful model via API:\n\n```python\nimport anthropic\nclient = anthropic.Anthropic(api_key=\"your-api-key\")\n\nresponse = client.messages.create(\n    model=\"claude-opus-4-7\",\n    max_tokens=1024,\n    messages=[{\"role\": \"user\", \"content\": \"Explain embeddings in 2 sentences.\"}]\n)\nprint(response.content[0].text)\n```\n\nInstall with: `pip install anthropic`"),
    md("## ✅ Summary\n\n| Concept | Key Point |\n|---|---|\n| Generator | Processes data one item at a time — saves RAM |\n| Embedding | Dense vector representing meaning |\n| Cosine similarity | Measure closeness of embeddings |\n| Text preprocessing | Lowercase → remove punctuation → remove stopwords |\n| Tokenisation | Split text into tokens (word/subword/char) |\n| Bag of Words | Count of each word per document |\n| TF-IDF | Weighted counts — boosts rare, specific words |"),
]))

# ===========================================================
# NOTEBOOK 20 — Next Steps GenAI
# ===========================================================
save(f"{BASE}/20_Next_Steps_GenAI/20_Next_Steps_GenAI.ipynb", notebook([
    md("# Topic 20: Next Steps Toward GenAI\n\n**Topics:** Deep learning concepts · How a neuron works · Transformers · Python's role in LLMs · GenAI APIs · Your roadmap"),
    md("## 1. What is Deep Learning?\n\nDeep Learning = ML with **multi-layer neural networks**.\n\n```\nInput → [Layer 1] → [Layer 2] → ... → [Layer N] → Output\n```\n\n- Classic ML: you engineer features manually\n- Deep Learning: the network learns features automatically from raw data\n\n**Excels at:** images, text, audio, video"),
    md("## 2. How a Single Neuron Works\n\n```\nInputs (x₁, x₂, x₃)\n   × weights (w₁, w₂, w₃)\n   + bias (b)\n   → activation function\n   → output\n```\n\nExactly linear regression — but with an activation function and millions of neurons chained together."),
    code('import math\n\ndef sigmoid(z): return 1 / (1 + math.exp(-z))\ndef relu(z):    return max(0, z)\n\ndef neuron(inputs, weights, bias, activation="sigmoid"):\n    z = sum(w*x for w,x in zip(weights,inputs)) + bias\n    return sigmoid(z) if activation=="sigmoid" else relu(z)\n\ninputs  = [6.0, 0.85]   # [hours_studied, attendance_rate]\nweights = [0.4, 0.6]\nbias    = -0.5\n\nout = neuron(inputs, weights, bias)\nprint(f"Output: {out:.4f} → Prediction: {\'Pass\' if out >= 0.5 else \'Fail\'}")\n\nprint("\\nActivation functions:")\nfor z in [-3,-1,0,1,3]:\n    print(f"  z={z:3d}  sigmoid={sigmoid(z):.3f}  relu={relu(z):.1f}")'),
    md("## 3. Understanding Transformers\n\nTransformers (2017) power **all** modern GenAI: GPT, Claude, Gemini, BERT, LLaMA.\n\n**Key innovation: Self-Attention**\n> Each word looks at ALL other words to understand context.\n\n| Component | Purpose |\n|---|---|\n| Tokenisation | Text → tokens |\n| Embeddings | Tokens → vectors |\n| Positional encoding | Adds word position info |\n| Self-Attention | Each token attends to all others |\n| Feed-Forward layers | Further processing |\n| Stacking | 96+ layers deep in large models |"),
    code('# Conceptual self-attention demo\nsentence = "The cat sat on the mat"\nwords = sentence.split()\nfocus_word = "sat"\nprint(f\'Attention weights when processing "{focus_word}":\')\nimport numpy as np; np.random.seed(7)\nweights = np.array([0.05, 0.40, 0.15, 0.20, 0.05, 0.15])\nfor word, w in zip(words, weights):\n    bar = "█" * int(w*40)\n    print(f"  {word:8}: {w:.2f}  {bar}")'),
    md("## 4. Preview: PyTorch Neural Network"),
    code('try:\n    import torch, torch.nn as nn\n\n    class SimpleNN(nn.Module):\n        def __init__(self):\n            super().__init__()\n            self.fc1 = nn.Linear(4, 8)\n            self.relu = nn.ReLU()\n            self.fc2 = nn.Linear(8, 1)\n            self.sigmoid = nn.Sigmoid()\n        def forward(self, x):\n            return self.sigmoid(self.fc2(self.relu(self.fc1(x))))\n\n    model = SimpleNN()\n    print(model)\n    print(f"Parameters: {sum(p.numel() for p in model.parameters())}")\n\nexcept ImportError:\n    print("Install PyTorch: pip install torch")\n    print("Structure would look like:")\n    print("  fc1: Linear(4 → 8) + ReLU")\n    print("  fc2: Linear(8 → 1) + Sigmoid")'),
    md("## 5. GenAI APIs\n\nBuild real GenAI apps **today** — no training required:\n\n```python\n# Anthropic Claude\nimport anthropic\nclient = anthropic.Anthropic(api_key=\"YOUR_KEY\")\nresponse = client.messages.create(\n    model=\"claude-opus-4-7\",\n    max_tokens=1024,\n    messages=[{\"role\": \"user\", \"content\": \"Summarise this article: ...\"}]\n)\nprint(response.content[0].text)\n```\n\n**What you can build now:**\n- 📝 Document summariser\n- 🤖 Q&A bot over your own data\n- 🔍 Data extraction from unstructured text\n- 💬 Sentiment analysis tool\n- 🖼️ Image captioning (multimodal)"),
    md("## 6. Your Learning Roadmap\n\n```\n✅ COMPLETED — This course\n   Python Fundamentals → NumPy → Pandas → EDA\n   Visualisation → ML Foundations → First Models → Evaluation\n   Text Preprocessing → Embeddings\n\n📚 NEXT STEPS\n   1. Strengthen ML  — Random Forest, XGBoost, Kaggle competitions\n   2. Deep Learning  — PyTorch or TensorFlow (fast.ai is great)\n   3. NLP + Transformers — Hugging Face (free course available)\n   4. GenAI Apps     — LLM APIs, LangChain, RAG\n   5. Deploy         — FastAPI, Streamlit, Docker, Cloud\n\n🔗 Resources\n   fast.ai             → https://www.fast.ai/\n   Hugging Face        → https://huggingface.co/learn\n   Kaggle              → https://www.kaggle.com/learn\n   deeplearning.ai     → https://www.deeplearning.ai/\n```"),
    md("## ✅ Congratulations!\n\nYou have completed **Python for GenAI & Data Science**.\n\nYou now know:\n- Core Python (syntax, data structures, functions, OOP)\n- Data manipulation (NumPy, Pandas)\n- Exploratory Data Analysis\n- Data visualisation (Matplotlib, Seaborn)\n- Machine Learning foundations and first models\n- Model evaluation\n- Text processing and embeddings\n- How GenAI models work at a conceptual level\n\n> **The best next step: build something.** Pick a dataset from Kaggle, solve a problem with code, and keep going."),
]))

print("\n✅ All 20 Jupyter notebooks generated successfully!")
print("Open any .ipynb file in VS Code or Jupyter Notebook to get started.")
