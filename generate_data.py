"""
generate_data.py
-----------------
Generates a CSV file (students.csv) containing marks of 40 students
in five subjects: Maths, Science, English, History, Computer.

Marks are random integers between 20 and 100.
A fixed random seed (42) is used so the output is reproducible every time.

Usage:
    python generate_data.py
"""

import pandas as pd
import numpy as np
import os

# ── Configuration ────────────────────────────────────────────────────
NUM_STUDENTS = 40          # Total number of students to generate
SEED = 42                  # Fixed seed for reproducibility
MARKS_LOW = 20             # Minimum possible mark
MARKS_HIGH = 100           # Maximum possible mark
OUTPUT_FILE = "students.csv"

# Subjects for which marks will be generated
SUBJECTS = ["Maths", "Science", "English", "History", "Computer"]

# A pool of realistic Indian first names (used to name the students)
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun",
    "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
    "Ananya", "Diya", "Myra", "Sara", "Aadhya",
    "Isha", "Kiara", "Riya", "Priya", "Neha",
    "Rohan", "Karan", "Amit", "Rahul", "Vijay",
    "Sneha", "Pooja", "Kavya", "Meera", "Tanvi",
    "Yash", "Dev", "Harsh", "Nisha", "Simran",
    "Raj", "Mohit", "Sakshi", "Shreya", "Tushar",
]


def generate_student_data() -> pd.DataFrame:
    """
    Create a DataFrame with student IDs, names, and random marks.

    Returns:
        pd.DataFrame: DataFrame with columns
                       [Student_ID, Name, Maths, Science, English, History, Computer]
    """
    # Set the random seed so results are the same every run
    np.random.seed(SEED)

    # Build the data dictionary
    data = {
        "Student_ID": [f"STU{str(i).zfill(3)}" for i in range(1, NUM_STUDENTS + 1)],
        "Name": FIRST_NAMES[:NUM_STUDENTS],
    }

    # Generate random marks for each subject
    for subject in SUBJECTS:
        data[subject] = np.random.randint(MARKS_LOW, MARKS_HIGH + 1, size=NUM_STUDENTS)

    return pd.DataFrame(data)


def main():
    """Generate the dataset and save it as a CSV file."""
    df = generate_student_data()

    # Save to CSV (without the default pandas index)
    df.to_csv(OUTPUT_FILE, index=False)

    # Print a confirmation message
    print(f"[OK] '{OUTPUT_FILE}' created successfully with {len(df)} students.")
    print(f"\nFirst 5 rows:\n{df.head()}")


if __name__ == "__main__":
    main()
