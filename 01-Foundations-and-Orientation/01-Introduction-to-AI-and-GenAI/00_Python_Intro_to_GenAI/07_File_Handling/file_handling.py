# ============================================================
# TOPIC 7: File Handling & Data Input
# ============================================================

import os
import csv
import json

# ============================================================
# SECTION 1: Reading and Writing Text Files
# ============================================================

print("--- Text Files ---")

# WRITING a text file
# open(filename, mode)
# 'w' = write (creates new or overwrites existing)
# 'a' = append (adds to existing)
# 'r' = read (default)

with open("sample.txt", "w") as file:
    file.write("Hello, this is line 1.\n")
    file.write("This is line 2.\n")
    file.write("Python file handling is easy.\n")

print("File 'sample.txt' created and written.")

# READING a text file — read the whole file at once
with open("sample.txt", "r") as file:
    content = file.read()
    print("Full file content:")
    print(content)

# READING line by line (better for large files)
print("Reading line by line:")
with open("sample.txt", "r") as file:
    for line in file:
        print(" >", line.strip())  # strip() removes the trailing newline

# READING all lines into a list
with open("sample.txt", "r") as file:
    lines = file.readlines()
print(f"\nFile has {len(lines)} lines.")
print("First line:", lines[0].strip())

# APPENDING to a file (adding without overwriting)
with open("sample.txt", "a") as file:
    file.write("This line was appended later.\n")

print("\nAfter appending:")
with open("sample.txt", "r") as file:
    print(file.read())

# The 'with' keyword automatically closes the file — always use it!

# ============================================================
# SECTION 2: Working with CSV Files
# ============================================================

print("--- CSV Files ---")

# CSV = Comma-Separated Values — the most common format for datasets

# WRITING a CSV file
students = [
    ["Name", "Age", "Score", "City"],
    ["Alice", 22, 85, "Accra"],
    ["Bob", 25, 92, "Kumasi"],
    ["Charlie", 21, 78, "Tamale"],
    ["Diana", 23, 95, "Cape Coast"],
]

with open("students.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(students)  # Write all rows at once

print("students.csv created.")

# READING a CSV file
print("\nReading students.csv:")
with open("students.csv", "r") as file:
    reader = csv.reader(file)
    header = next(reader)  # Read the first row as header
    print("Columns:", header)
    for row in reader:
        print(" ", row)

# Using csv.DictReader: reads rows as dictionaries (column name as key)
print("\nUsing DictReader:")
with open("students.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(f"  {row['Name']} scored {row['Score']} and lives in {row['City']}")

# Writing with DictWriter
extra_students = [
    {"Name": "Eve", "Age": 24, "Score": 88, "City": "Takoradi"},
    {"Name": "Frank", "Age": 22, "Score": 74, "City": "Sunyani"},
]

with open("students.csv", "a", newline="") as file:
    fieldnames = ["Name", "Age", "Score", "City"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writerows(extra_students)

print("\nUpdated CSV with new students:")
with open("students.csv", "r") as file:
    print(file.read())

# ============================================================
# SECTION 3: Reading and Writing JSON Files
# ============================================================

print("--- JSON Files ---")

# JSON = JavaScript Object Notation
# Used heavily in APIs and web data
# Looks like Python dictionaries

# WRITING JSON
employee_data = {
    "company": "TechCorp",
    "employees": [
        {"id": 1, "name": "Alice", "role": "Engineer", "salary": 70000},
        {"id": 2, "name": "Bob", "role": "Manager", "salary": 90000},
        {"id": 3, "name": "Charlie", "role": "Analyst", "salary": 60000},
    ],
    "active": True,
    "founded": 2015,
}

with open("employees.json", "w") as file:
    json.dump(employee_data, file, indent=4)  # indent=4 makes it readable

print("employees.json created.")

# READING JSON
with open("employees.json", "r") as file:
    data = json.load(file)

print("\nCompany:", data["company"])
print("Founded:", data["founded"])
print("Employees:")
for emp in data["employees"]:
    print(f"  {emp['id']}. {emp['name']} — {emp['role']} (${emp['salary']:,})")

# Converting between JSON string and Python dict
json_string = '{"name": "Alice", "age": 22}'
python_dict = json.loads(json_string)      # JSON string → Python dict
print("\nParsed JSON string:", python_dict, type(python_dict))

back_to_json = json.dumps(python_dict, indent=2)  # Python dict → JSON string
print("Back to JSON string:\n", back_to_json)

# ============================================================
# SECTION 4: File Paths and Directories
# ============================================================

print("--- File Paths and Directories ---")

# Get current working directory
cwd = os.getcwd()
print("Current directory:", cwd)

# List files in the current directory
print("\nFiles in current directory:")
for item in os.listdir("."):
    print(" ", item)

# Check if a file or folder exists
print("\nDoes 'students.csv' exist?", os.path.exists("students.csv"))
print("Does 'missing.txt' exist?", os.path.exists("missing.txt"))

# Get file info
print("Is 'students.csv' a file?", os.path.isfile("students.csv"))
print("Is '.' a directory?", os.path.isdir("."))

# Join paths safely (works on all operating systems)
folder = "data"
filename = "report.csv"
full_path = os.path.join(folder, filename)
print("Joined path:", full_path)

# Create a directory if it doesn't exist
if not os.path.exists("output"):
    os.makedirs("output")
    print("Created 'output' folder.")
else:
    print("'output' folder already exists.")

# Get just the filename from a full path
path = "/home/user/projects/data/students.csv"
print("Filename:", os.path.basename(path))
print("Directory:", os.path.dirname(path))
print("Split:", os.path.splitext(os.path.basename(path)))  # name, extension

# ============================================================
# SECTION 5: Introduction to APIs (Basic Idea)
# ============================================================

print("\n--- Introduction to APIs ---")

# API = Application Programming Interface
# An API lets your Python program talk to another service over the internet.
# Common uses:
#   - Fetch weather data
#   - Get stock prices
#   - Use OpenAI / Gemini for GenAI
#   - Get data from a database on a server

# Most APIs return data in JSON format.
# You send a REQUEST and get back a RESPONSE.

# The 'requests' library is the standard way to call APIs in Python.
# Install it with: pip install requests

# Here is what a typical API call looks like (demonstration only):

try:
    import requests

    # Example: Fake API call (replace URL with a real API endpoint)
    # url = "https://api.example.com/data"
    # response = requests.get(url)
    # data = response.json()   <-- parse JSON response

    # Using a real public API that needs no key — joke API
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(url, timeout=5)

    if response.status_code == 200:
        joke = response.json()
        print("API call successful!")
        print(f"Setup: {joke['setup']}")
        print(f"Punchline: {joke['punchline']}")
    else:
        print(f"API error: status code {response.status_code}")

except ImportError:
    print("Note: 'requests' library not installed.")
    print("Install it with: pip install requests")
except Exception as e:
    print(f"Could not reach API (may be offline): {e}")

# Clean up demo files
for fname in ["sample.txt", "students.csv", "employees.json"]:
    if os.path.exists(fname):
        os.remove(fname)
if os.path.exists("output"):
    os.rmdir("output")

print("\n--- End of File Handling ---")
