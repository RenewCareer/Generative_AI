# ============================================================
# TOPIC 4: Control Flow & Logic Building
# ============================================================

# ============================================================
# SECTION 1: Conditional Statements (if, elif, else)
# ============================================================

print("--- Conditional Statements ---")

# The if statement runs a block ONLY if the condition is True
temperature = 35

if temperature > 30:
    print("It is hot outside.")

# if-else: one block runs if True, another if False
score = 72

if score >= 50:
    print("You passed!")
else:
    print("You failed.")

# if-elif-else: check multiple conditions in order
grade = 85

if grade >= 90:
    print("Grade: A")
elif grade >= 80:
    print("Grade: B")
elif grade >= 70:
    print("Grade: C")
elif grade >= 60:
    print("Grade: D")
else:
    print("Grade: F")

# Nested if (if inside an if)
age = 20
has_id = True

if age >= 18:
    if has_id:
        print("Entry allowed.")
    else:
        print("Please show your ID.")
else:
    print("You must be 18 or older.")

# One-line if (ternary expression)
x = 10
label = "positive" if x > 0 else "non-positive"
print(f"{x} is {label}")

# ============================================================
# SECTION 2: Comparison and Logical Operators
# ============================================================

print("\n--- Comparison Operators ---")

a = 10
b = 20

print(a == b)   # Equal to:            False
print(a != b)   # Not equal to:        True
print(a < b)    # Less than:           True
print(a > b)    # Greater than:        False
print(a <= 10)  # Less than or equal:  True
print(a >= 15)  # Greater or equal:    False

print("\n--- Logical Operators ---")

# and: True only if BOTH conditions are True
print(True and True)    # True
print(True and False)   # False

# or: True if AT LEAST ONE condition is True
print(True or False)    # True
print(False or False)   # False

# not: Flips True to False and vice versa
print(not True)         # False
print(not False)        # True

# Real-world example
salary = 50000
experience = 3

if salary > 40000 and experience >= 2:
    print("Eligible for promotion.")

age = 17
has_permission = True

if age >= 18 or has_permission:
    print("Can proceed.")

# ============================================================
# SECTION 3: Loops (for, while)
# ============================================================

print("\n--- For Loop ---")

# for loop: iterate over a sequence
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print("Fruit:", fruit)

# Looping with range()
# range(stop): 0 to stop-1
for i in range(5):
    print(i, end=" ")   # end=" " keeps output on same line
print()  # newline

# range(start, stop)
for i in range(1, 6):
    print(i, end=" ")
print()

# range(start, stop, step)
for i in range(0, 20, 5):
    print(i, end=" ")
print()

# Loop with index using enumerate()
students = ["Alice", "Bob", "Charlie"]
for index, student in enumerate(students):
    print(f"  {index + 1}. {student}")

# Loop over a dictionary
person = {"name": "Alice", "age": 25, "city": "Accra"}
for key, value in person.items():
    print(f"  {key}: {value}")

print("\n--- While Loop ---")

# while loop: runs as long as the condition is True
count = 0
while count < 5:
    print(f"Count: {count}")
    count += 1   # IMPORTANT: always update the variable to avoid infinite loop

# while loop for user input simulation
number = 10
guess = 0
attempts = 0

while guess != number:
    guess = 7  # Simulating a guess (in real use, this would be input())
    attempts += 1
    if guess == number:
        print(f"Correct! Found in {attempts} attempt(s).")
    elif guess < number:
        print(f"  Too low! (guess was {guess})")
    else:
        print(f"  Too high! (guess was {guess})")
    # Safety: break after 1 attempt in this demo
    break

# ============================================================
# SECTION 4: Loop Control (break, continue, pass)
# ============================================================

print("\n--- break ---")
# break: exit the loop immediately
for i in range(10):
    if i == 5:
        print("Found 5! Stopping.")
        break
    print(i, end=" ")
print()

print("\n--- continue ---")
# continue: skip the rest of this iteration and go to the next
for i in range(10):
    if i % 2 == 0:
        continue   # skip even numbers
    print(i, end=" ")  # only odd numbers printed
print()

print("\n--- pass ---")
# pass: do nothing — used as a placeholder
for i in range(3):
    pass   # we'll fill this in later
print("Loop with pass completed (no output inside)")

# pass is useful when you write the structure first:
def my_function():
    pass   # TODO: implement later

# ============================================================
# SECTION 5: Nested Loops
# ============================================================

print("\n--- Nested Loops ---")

# A loop inside a loop
# Outer loop runs each row, inner loop runs each column
for row in range(1, 4):
    for col in range(1, 4):
        print(f"({row},{col})", end="  ")
    print()  # new line after each row

# Multiplication table
print("\n--- Multiplication Table (1-5) ---")
for i in range(1, 6):
    for j in range(1, 6):
        print(f"{i * j:3}", end="")  # :3 means 3-character wide column
    print()

# ============================================================
# SECTION 6: Writing Clean Logic for Data Processing
# ============================================================

print("\n--- Clean Data Processing Logic ---")

# Example: Process a list of student scores
scores = [85, 42, 91, 67, 55, 78, 39, 95, 60, 73]

passed = []
failed = []

for score in scores:
    if score >= 50:
        passed.append(score)
    else:
        failed.append(score)

print(f"Total students : {len(scores)}")
print(f"Passed         : {len(passed)} — Scores: {passed}")
print(f"Failed         : {len(failed)} — Scores: {failed}")
print(f"Average score  : {sum(scores) / len(scores):.1f}")
print(f"Highest score  : {max(scores)}")
print(f"Lowest score   : {min(scores)}")

# Count how many got each grade
print("\n--- Grade Distribution ---")
grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}

for score in scores:
    if score >= 90:
        grade_counts["A"] += 1
    elif score >= 80:
        grade_counts["B"] += 1
    elif score >= 70:
        grade_counts["C"] += 1
    elif score >= 60:
        grade_counts["D"] += 1
    else:
        grade_counts["F"] += 1

for grade, count in grade_counts.items():
    print(f"  Grade {grade}: {count} student(s)")

print("\n--- End of Control Flow ---")
