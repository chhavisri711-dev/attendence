import json
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Get the folder where main.py is located
BASE_DIR = Path(__file__).resolve().parent

# Load API key from .env
load_dotenv(BASE_DIR / ".env")
api_key = os.getenv("GEMINI_API_KEY")

# Create Gemini client
client = genai.Client(api_key=api_key) if api_key else None


# Load attendance data
def load_attendance():
    file_path = BASE_DIR / "attendance.json"

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            students = json.load(file)

        if not isinstance(students, list) or not students:
            print("Error: No student records found in attendance.json.")
            return []

        return students

    except FileNotFoundError:
        print(f"Error: attendance.json not found at {file_path}")
        return []

    except json.JSONDecodeError as error:
        print("Error: Invalid JSON format.")
        print(error)
        return []


# Calculate attendance percentage
def calculate_attendance(student):
    total_days = student["total_days"]
    present_days = student["present_days"]

    if total_days <= 0:
        return 0

    return (present_days / total_days) * 100


# Display attendance report
def display_report(students):
    print("\n===== ATTENDANCE MANAGEMENT SYSTEM =====\n")
    report = []

    for student in students:
        percentage = calculate_attendance(student)
        status = "Eligible" if percentage >= 75 else "Below 75%"

        print(f"Name: {student['name']}")
        print(f"Roll No: {student['roll_no']}")
        print(f"Attendance: {percentage:.2f}%")
        print(f"Status: {status}")
        print("-" * 35)

        report.append(
            f"{student['name']} (Roll No: {student['roll_no']}): "
            f"{percentage:.2f}% attendance, "
            f"{student['present_days']} of "
            f"{student['total_days']} days present."
        )

    return "\n".join(report)


# Generate Gemini AI summary
def generate_ai_summary(report):
    print("\n===== GEMINI AI ATTENDANCE SUMMARY =====\n")

    if client is None:
        print("Gemini API key not found.")
        print("Please add GEMINI_API_KEY to your .env file.")
        return

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=(
                "You are an attendance management assistant. "
                "Analyze the following student attendance report. "
                "The minimum required attendance is 75%. "
                "Identify students below 75% and suggest ways "
                "to improve their attendance. Give a short summary.\n\n"
                + report
            ),
        )

        if response.text:
            print(response.text)
        else:
            print("Gemini returned an empty response.")

    except Exception as error:
        print("Could not generate Gemini summary.")
        print("Reason:", error)
        print("The attendance report was still calculated successfully.")


# Main program
def main():
    students = load_attendance()

    if not students:
        print("Please check your attendance.json file.")
        return

    report = display_report(students)
    generate_ai_summary(report)


if __name__ == "__main__":
    main()