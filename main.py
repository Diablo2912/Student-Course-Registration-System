import pandas as pd
import logging
import re
import colorama
from colorama import Fore, Back, Style
from tabulate import tabulate

#logging
logging.basicConfig(filename='student_registration.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Student():
    def __init__(self,student_id, student_name, email, course_list, year, status):
        self.student_id = student_id
        self.student_name = student_name
        self.email = email
        self.course_list = course_list
        self.year = year
        self.status = status

    # def format(self):
    #     print(f"Student ID: {self.student_id}")
    #     print(f"Student Name: {self.student_name}")
    #     print(f"Email: {self.email}")
    #     print(f"Courses Enrolled: {', '.join(self.course_list)}")
    #     print(f"Year of Study: {self.year}")
    #     print(f"Full-time/Part-time: {'Full-time' if self.status else 'Part-time'}")

    @staticmethod
    def validate_email(email):
        """Validate if the email is in the correct format."""
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None

# students = [
#     {
#
#     }
# ]

#sample student dict for testing
students = [
    {
        "Student ID":10001,
        "Student Name": "Alice Boo",
        "Email": "alice.boo@poly.edu",
        "Courses": ["IT101", "CS112"],
        "Year": 1,
        "Full-Time": True
    },
    {
        "Student ID": 10045,
        "Student Name": "Johan Power",
        "Email": "johan.pow@poly.edu",
        "Courses": ["IT111", "SF102"],
        "Year": 2,
        "Full-Time": True
    }
]

admin = {"admin01": "admin01", "admin02": "admin02"}

def menu():
    while True:
        print(
            Fore.MAGENTA + "--- Student Course Registration System --- \n" + Style.RESET_ALL +
            "1: Display all student records \n"
            "2: Add a new student record \n"
            "3: Enrol student for a new course \n"
            "4: Sort students by Year of Study \n"
            "5: Sort students by Num of Registered Course \n"
            "6: Search for a student by ID or Name \n"
            "7: Export student data to CSV \n"
            "8: Login  \n"
            "9: Exit the program "
        )

        choice = input("Enter your choice: ")
        if choice == "1":
            display_all()
        elif choice == "2":
            add_student()
        elif choice == "3":
            enrol_student()
        elif choice == "4":
            sort_year()
        elif choice == "5":
            sort_course()
        elif choice == "6":
            print("6")
        elif choice == "7":
            export()
        elif choice == "8":
            login()
        elif choice == "9":
            print("Exiting the programme")
            break
        else:
            print("Invalid Option, Try Again")

def display_all():
    if not students:
        print("No students found.")
        return

    print("Display Of All Student Records: \n" + tabulate(students, headers="keys", tablefmt="fancy_grid"))


def add_student():
    while True:
        try:
            student_id = int(input("Enter Student ID: "))  # This will not be affected by Fore.RED

            for student in students:
                if student["Student ID"] == student_id:
                    # Error message in red
                    print(Fore.RED + f"Student ID {student_id} already exists. Please enter a unique ID." + Style.RESET_ALL)
                    break  # for when duplicate is found exit for
            else:
                break  # when no duplicate is found exit while

        except ValueError:
            print("Invalid Student ID input. Try again")

    student_name = input("Enter Student Name: ")

    while True:
        try:
            email = input("Enter Student Email: ")

            if not Student.validate_email(email):
                print("Invalid email format. Please enter a valid email.")
                continue  # if email not valid keep asking

            email_exists = any(student["Email"].lower() == email.lower() for student in students)
            if email_exists:
                print(f"Email {email} already exists. Please enter a unique email.")
                continue

            break  # if email valid break

        except ValueError:
            print("Invalid email format. Please enter a valid email.")

    course = input("Enter Course List (comma-separated): ").split(",")

    while True:
        try:
            year = int(input("Enter Student Year of Study [1-3]: "))

            if year > 3 or year < 1:
                print("Invalid year of study. Enter valid Year of Study")

            else:
                break

        except ValueError:
            print(year)

    status_input = input("Enter Student Status, Full-Time [1] / Part-time [2]: ")

    if status_input == "1":
        status = True
    elif status_input == "2":
        status = False
    else:
        print("Invalid status input. Please enter 1 or 2.")
        return

    students.append({
        "Student ID": student_id,
        "Student Name": student_name,
        "Email": email,
        "Courses": course,
        "Year": year,
        "Full-Time": status
    })

    print(f"Student {student_name} added successfully. \n")


#
# def enrol_student():
#
# bubble sort - ascending
def sort_year():
    sorted_students = list(students.values())
    n = len(sorted_students)
    for i in range(n):
        for j in range(0, n - i - 1):
            if sorted_students[j]["Year"] > sorted_students[j + 1]["Year"]:
                sorted_students[j], sorted_students[j + 1] = sorted_students[j + 1], sorted_students[j]
#
# selection sort - descending
def sort_course():
    sorted_students = list(students.values())
    n = len(sorted_students)
    for i in range(n -1 ):
        min_idx = i
        for j in range(i+1, n):
            if sorted_students[j] < sorted_students[min_idx]:
                min_idx = j
        sorted_students[i], sorted_students[min_idx] = sorted_students[min_idx], sorted_students[i]

#
#search by student id or student name
# def search():
#
#import panda - export to csv
def export():
    if logged_in == True:
        df = pd.DataFrame(students)

        df.to_csv('students.csv', index=False)

        print("Data has been successfully exported to 'students.csv'. \n")
    else:
        print("You are not logged in \n")

logged_in = False

def login():
    global logged_in
    username = input("Enter Username: ")
    password = input("Enter Password: ")
    if username in admin and admin[username] == password:
        logged_in = True
        print(f"{username} has logged in successfully! \n")


if __name__ == "__main__":
    menu()