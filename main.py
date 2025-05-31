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
    def __init__(self,student_id, student_name, email, course, year, status):
        self.student_id = student_id
        self.student_name = student_name
        self.email = email
        self.course = course
        self.year = year
        self.status = status

    @staticmethod
    def validate_email(email):
        """Validate if the email is in the correct format."""
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None

    # def format(self):
    #     print(f"Student ID: {self.student_id}")
    #     print(f"Student Name: {self.student_name}")
    #     print(f"Email: {self.email}")
    #     print(f"Courses Enrolled: {', '.join(self.course_list)}")
    #     print(f"Year of Study: {self.year}")
    #     print(f"Full-time/Part-time: {'Full-time' if self.status else 'Part-time'}")



# students = [ ]

# #sample student dict for testing
students = [
    {
        "Student ID":10001,
        "Student Name": "Alice Boo",
        "Email": "alice.boo@poly.edu",
        "Courses": ["IT101"],
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
    },
    {
        "Student ID": 10002,
        "Student Name": "Karina",
        "Email": "alice.green@poly.edu",
        "Courses": ["IT101", "SF100", "CS242", "IT200"],
        "Year": 1,
        "Full-Time": True
    },
    {
        "Student ID": 10003,
        "Student Name": "Winter",
        "Email": "bob.white@poly.edu",
        "Courses": ["IT202", "SF205", "CS500"],
        "Year": 3,
        "Full-Time": False
    }
]

admin = {"admin01": "admin01", "admin02": "admin02"}

def menu():
    while True:
        print(
            Fore.MAGENTA + "--- Student Course Registration System --- \n" + Style.RESET_ALL +
            "1: Display all student records \n"
            "2: Add a new student record \n"
            "3: Enroll student for a new course \n"
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
            enroll_student()
        elif choice == "4":
            sort_year()
        elif choice == "5":
            sort_course()
        elif choice == "6":
            search()
        elif choice == "7":
            export()
        elif choice == "8":
            login()
        elif choice == "9":
            print("Exiting the programme...")
            logging.info(f"User has exited the programme")
            break
        else:
            print(Fore.RED + "Invalid Option, Please enter an input from 1-9 \n" + Style.RESET_ALL)
            logging.warning(f"Invalid menu option entered")

def display_all():
    if not students:
        print(Fore.RED + "No students found." + Style.RESET_ALL)
        return

    print("Display Of All Student Records: \n" + tabulate(students, headers="keys", tablefmt="fancy_grid"))


def add_student():
    while True:
        try:
            student_id = (input("Enter Student ID: "))

            if len(student_id) != 5:
                print(Fore.RED + "Invalid Student ID input. Enter a 5 digit Student ID" + Style.RESET_ALL)

            student_id = int(student_id)

            for student in students:
                if student["Student ID"] == student_id:
                    # Error message in red
                    print(Fore.RED + f"Student ID {student_id} already exists. Please enter a unique ID." + Style.RESET_ALL)
                    logging.warning(f"Attempted to add student with an existing ID: {student_id}")
                    break  # when duplicate is found exit for loop

            else:
                break  # when no duplicate is found exit while loop

        except ValueError:
            print(Fore.RED + "Invalid Student ID input. Try again" +Style.RESET_ALL)
            logging.error("Invalid Student ID input: non-numeric value entered.")

    while True:

        student_name = input("Enter Student Name: ")
        capitalised_name = student_name.title()

        if not student_name:
            print(Fore.RED + "Invalid student name entered. Please enter a valid name" + Style.RESET_ALL)
            logging.error("Attempted to add student with an invalid name.")

        else:
            break

    while True:
        try:
            email = input("Enter Student Email: ")

            if not Student.validate_email(email):
                print(Fore.RED + "Invalid email format. Please enter a valid email." + Style.RESET_ALL)
                logging.warning(f"Invalid email format entered: {email}")
                continue  # if email not valid keep asking

            email_exists = any(student["Email"].lower() == email.lower() for student in students)
            if email_exists:
                print(Fore.RED + f"Email {email} already exists. Please enter a unique email." + Style.RESET_ALL)
                logging.warning(f"Attempted to add student with an existing email: {email}")
                continue

            break  # if email valid break

        except ValueError:
            print(Fore.RED + "Invalid email format. Please enter a valid email." + Style.RESET_ALL)
            logging.error("Invalid email format input entered.")

    while True:
        courses = input("Enter Course List (comma-separated): ").strip().upper().split(",")
        courses = [c.strip() for c in courses]  # remove extra spaces

        if (re.fullmatch(r'[A-Z]{2}\d{3}', c) for c in courses):
            break
        else:
            print("Invalid input. Each course must have 2 letters followed by 3 digits. Try again.")

    while True:
        try:
            year = int(input("Enter Student Year of Study [1-3]: "))

            if year > 3 or year < 1:
                print(Fore.RED + "Invalid year of study. Enter a valid Year of Study" + Style.RESET_ALL)
                logging.warning(f"Invalid year entered: {year}.")
            else:
                break

        except ValueError:
            print(Fore.RED + "Invalid year of study. Enter a valid Year of Study" + Style.RESET_ALL)
            logging.error("Invalid year of study input.")

    status_input = input("Enter Student Status, Full-Time [1] / Part-time [2]: ")

    if status_input == "1":
        status = True
    elif status_input == "2":
        status = False
    else:
        print("Invalid status input. Please enter 1 or 2.")
        logging.warning(f"Invalid status input entered: {status_input}.")
        return

    students.append({
        "Student ID": student_id,
        "Student Name": capitalised_name,
        "Email": email,
        "Courses": courses,
        "Year": year,
        "Full-Time": status
    })

    logging.info(f"New student added: ID: {student_id}, Name: {capitalised_name}, Email: {email}, Course: {courses}, Year: {year}, Full-Time: {status}")
    print(Fore.GREEN + f"Student {capitalised_name} added successfully. \n" + Style.RESET_ALL)

#enroll students by selecting ID
# def enroll_student():
#     while True:
#         try:
#             student_input = input("Enter student ID (Enter 'E' to exit): ")
#
#             # Exit the process if user enters 'E'
#             if student_input == 'E':
#                 print(Fore.GREEN + "Exiting the enrollment process..." + Style.RESET_ALL)
#                 break
#
#             student_id = int(student_input)  # Convert to int if not 'E'
#             logging.info(f"User has started to enroll student {student_id} into course")
#
#             student = None
#             # Find the student in the list based on student ID
#             for s in students:
#                 if s["Student ID"] == student_id:
#                     student = s
#                     print(Fore.GREEN + f"Student {student['Student Name']}, ID: {student_id} has been chosen" + Style.RESET_ALL)
#                     break
#
#             if not student:
#                 logging.warning(f"Tried to enroll invalid student, ID: {student_id} into a course.")
#                 print(Fore.RED + "Student ID not found." + Style.RESET_ALL)
#                 continue  # Ask for student ID again
#
#             while True:
#                 course = input("Enter course code (Enter 'E' to exit): ")
#
#                 if course == "E":
#                     print(Fore.GREEN + "Exiting the enrollment process..." + Style.RESET_ALL)
#                     return
#
#                 if not re.match(r'^[A-Za-z]{2}\d{3}$', course):
#                     print(Fore.RED + "Invalid course code. Please enter a valid course code." + Style.RESET_ALL)
#                     continue
#
#                 # Check if the student is already enrolled in the course
#                 if course.upper() in student["Courses"]:
#                     print(Fore.RED + f"Student {student['Student Name']} ID: {student_id} is already enrolled in {course.upper()}." + Style.RESET_ALL)
#                     continue  # Ask for a new course if already enrolled
#
#                 student["Courses"].append(course.upper())
#                 print(Fore.GREEN + f"Student {student['Student Name']}, ID: {student_id} has been successfully enrolled in {course.upper()}.\n" + Style.RESET_ALL)
#                 logging.info(f"Student {student['Student Name']}, ID: {student_id} has been successfully enrolled in {course.upper()}")
#                 break  # Exit the course enrollment loop after successful enrollment
#
#             break
#
#         except ValueError:
#             print(Fore.RED + "Invalid Student ID, Enter a valid student ID" + Style.RESET_ALL)
def enroll_student():
    while True:
        try:
            student_input = input("Enter student ID (Enter 'E' to exit): ")

            if student_input.upper() == 'E':
                print(Fore.GREEN + "Exiting the enrollment process..." + Style.RESET_ALL)
                break

            student_id = int(student_input)
            logging.info(f"User has started to enroll student {student_id} into courses")

            student = next((s for s in students if s["Student ID"] == student_id), None)

            if not student:
                logging.warning(f"Tried to enroll invalid student, ID: {student_id}")
                print(Fore.RED + "Student ID not found." + Style.RESET_ALL)
                continue

            print(Fore.GREEN + f"Student {student['Student Name']}, ID: {student_id} has been chosen." + Style.RESET_ALL)

            while True:
                courses_input = input("Enter course codes separated by spaces (Enter 'E' to exit): ")

                if not courses_input:
                    print(Fore.RED + "Invalid Course Code. Please enter a valid Course Code." + Style.RESET_ALL)
                    continue

                if courses_input == "E":
                    print(Fore.GREEN + "Exiting the enrollment process..." + Style.RESET_ALL)
                    return

                courses = courses_input.strip().split()

                for course in courses:
                    course = course.upper()

                    if not re.match(r'^[A-Z]{2}\d{3}$', course):
                        print(Fore.RED + f"Invalid course code: {course}. Must be in format like 'CS101'." + Style.RESET_ALL)
                        continue

                    if course in student["Courses"]:
                        print(Fore.RED + f"Student {student['Student Name']}, ID: {student_id} is already enrolled in {course}." + Style.RESET_ALL)
                        continue

                    student["Courses"].append(course)
                    print(Fore.GREEN + f"Student {student['Student Name']}, ID: {student_id} has been successfully enrolled in {course}." + Style.RESET_ALL)
                    logging.info(f"Student {student['Student Name']}, ID: {student_id} enrolled in {course}")

        except ValueError:
            print(Fore.RED + "Invalid Student ID. Please enter a valid student ID." + Style.RESET_ALL)

#bubble sort - ascending
#sort by year of study
def sort_year():
    n = len(students)
    for i in range(n):
        for j in range(0, n - i - 1):
            if students[j]["Year"] > students[j + 1]["Year"]:
                students[j], students[j + 1] = students[j + 1], students[j]

    print("Sorted by Year Of Study in Ascending Order: \n" + tabulate(students, headers="keys", tablefmt="fancy_grid"))
#
#selection sort - descending
#sort by num of registered courses
def sort_course():
    n = len(students)
    for i in range(n - 1):
        max_idx = i #use max instead of min due to descending
        for j in range(i + 1, n):
            if len(students[j]['Courses']) > len(students[max_idx]['Courses']): #use len as comparing by no of
                max_idx = j
        students[i], students[max_idx] = students[max_idx], students[i]

    print("Sorted by Num of Registered Courses in Descending Order: \n" + tabulate(students, headers="keys", tablefmt="fancy_grid"))


#search by student id or student name
def search():
    search_input = input("Enter Student ID or Student Name: ").strip()
    for student in students:
        if str(student["Student ID"]) == search_input or student["Student Name"].lower() == search_input.lower():
            print("\nSearched Student Details:\n" + tabulate([student], headers="keys", tablefmt="fancy_grid"))
            break  # stop after first match
    else:
        logging.warning(f"Student with ID or name {search_input} not found.")
        print(Fore.RED + "Student not found." + Style.RESET_ALL)

#import pandas - export to csv
def export():
    if logged_in == True:
        df = pd.DataFrame(students)

        df.to_csv('students.csv', index=False)

        print("Data has been successfully exported to 'students.csv'. \n")
        logging.info(f"Data has been successfully exported to 'students.csv'")
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