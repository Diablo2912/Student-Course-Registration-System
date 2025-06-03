import numpy as np
import pandas as pd
import logging
import re
import colorama
from colorama import Fore, Back, Style
from tabulate import tabulate
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

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

    #email validator
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


# Empty student list to start from scratch
# students = [ ]

# Sample student list for testing and demonstration
# Comment away if not needed
students = [
    {
        "Student ID": 10001,
        "Student Name": "Alice Boo",
        "Email": "alice.boo@poly.edu",
        "Courses": ["IT101"],
        "Year": 1,
        "Status": True
    },
    {
        "Student ID": 10045,
        "Student Name": "Johan Power",
        "Email": "johan.pow@poly.edu",
        "Courses": ["IT111", "SF102"],
        "Year": 2,
        "Status": True
    },
    {
        "Student ID": 10002,
        "Student Name": "Karina",
        "Email": "karina@poly.edu",
        "Courses": ["IT101", "SF100", "CS242", "IT200"],
        "Year": 1,
        "Status": True
    },
    {
        "Student ID": 10003,
        "Student Name": "Winter",
        "Email": "winter@poly.edu",
        "Courses": ["IT202", "SF205", "CS500"],
        "Year": 3,
        "Status": False
    },
    {
        "Student ID": 10005,
        "Student Name": "Cristiano Ronaldo",
        "Email": "crstiano@gmail.com",
        "Courses": ["IT100", "SF209", "CS505"],
        "Year": 3,
        "Status": False
    },
    {
        "Student ID": 10088,
        "Student Name": "Yuna",
        "Email": "yuna@gmail.com",
        "Courses": ["SF500"],
        "Year": 3,
        "Status": True
    },
]

#admin accounts
admin = {"admin01": "admin01",
         "admin02": "admin02"}

#user accounts
user = {"user01": "user01",
        "user02": "user02"}

#login function
def login():
    global admin_logged_in, user_logged_in
    max_attempts = 2

    # Infinite username checking loop
    while True:
        try:
            # Ensure username isn't empty
            username = input(Fore.CYAN + "Enter Username (Type 'E' to quit): " + Style.RESET_ALL)

            if username == 'E':
                print(Fore.YELLOW + "Exiting login process." + Style.RESET_ALL)
                return  # Exit the login function

            while not username:  # Check if the username is empty
                print(Fore.RED + "Invalid Username. Please try again" + Style.RESET_ALL)
                username = input(Fore.CYAN + "Enter Username (Type 'E' to quit): " + Style.RESET_ALL)

            # Check if username exists in either admin or user dictionaries
            if username not in admin and username not in user:
                print(Fore.RED + "User does not exist. Please check your username and try again." + Style.RESET_ALL)
                continue  # Keep asking for the username if it doesn't exist

            # If username is valid, proceed to password input
            password_attempts = 0
            while password_attempts < max_attempts:
                password = input(Fore.CYAN + "Enter Password: " + Style.RESET_ALL)

                if username in admin and admin[username] == password:
                    admin_logged_in = True
                    print(Fore.GREEN + f"{username} has logged in successfully as an Admin! \n" + Style.RESET_ALL)
                    admin_menu()
                    return  # Exit after successful login

                elif username in user and user[username] == password:
                    user_logged_in = True
                    print(Fore.GREEN + f"{username} has logged in successfully as a User! \n" + Style.RESET_ALL)
                    user_menu()
                    return  # Exit after successful login

                else:
                    print(Fore.RED + "Invalid Password. Please try again." + Style.RESET_ALL)
                    password_attempts += 1

            print(Fore.RED + "Too many failed password attempts." + Style.RESET_ALL)
            return  # Exit after failed password attempts

        except ValueError:
            print(Fore.RED + "Invalid Input" + Style.RESET_ALL)
            continue  # Continue asking for the username if there's an invalid input

    # If the user exceeds the attempt limit for username
    print(Fore.RED + "Too many failed login attempts.\n" + Style.RESET_ALL)


#logout feature
def admin_logout():
    admin_logged_in = False
    print(Fore.GREEN + "You have successfully logged out! \n")
    login()

def user_logout():
    user_logged_in = False
    print(Fore.GREEN + "You have successfully logged out! \n")
    login()

#Admin menu when user is logged in as an admin
def admin_menu():
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
            "8: Generate Student Distribution by Year chart \n"
            "9: Login  \n"
            "10: Logout \n"
            "0: Exit the program "
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
            generate_distribution_chart()
        elif choice == "9":
            login()
        elif choice == "10":
            admin_logout()
        elif choice == "0":
            print("Exiting the programme...")
            logging.info(f"Admin has exited the programme")
            break
        else:
            print(Fore.RED + "Invalid Option, Please enter an input from 0-10 \n" + Style.RESET_ALL)
            logging.warning(f"Invalid menu option entered")

#User menu when user is logged in as a user
def user_menu():
    while True:
        print(
            Fore.MAGENTA + "--- Student Course Registration System --- \n" + Style.RESET_ALL +
            "1: Display all student records \n"
            "2: Search for a student by ID or Name \n"
            "3: Logout  \n"
            "0: Exit the program "
        )

        choice = input("Enter your choice: ")
        if choice == "1":
            display_all()
        elif choice == "2":
            search()
        elif choice == "3":
            user_logout()
        elif choice == "0":
            print("Exiting the programme...")
            logging.info(f"User has exited the programme")
            break
        else:
            print(Fore.RED + "Invalid Option, Please enter an input from 0-3 \n" + Style.RESET_ALL)
            logging.warning(f"Invalid menu option entered")

def display_all():
    if not students:
        print(Fore.RED + "No students found." + Style.RESET_ALL)
        return

    for student in students:
        student["Status"] = "Full-Time" if student["Status"] else "Part-Time"

    print(Fore.CYAN + "Display Of All Student Records: \n" + Style.RESET_ALL + tabulate(students, headers="keys", tablefmt="fancy_grid"))


def add_student():
    while True:
        try:
            student_id = (input("Enter Student ID: "))

            if len(student_id) != 5:
                print(Fore.RED + "Invalid Student ID input. Enter a 5 digit Student ID" + Style.RESET_ALL)
                continue

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
        try:
            courses = input("Enter Course List (comma-separated): ").strip().upper().split(",")
            courses = [c.strip() for c in courses if c.strip()]  # remove extra spaces and ignore empty entries

            if not courses:
                print(Fore.RED + "Must enroll student into at least 1 course" +Style.RESET_ALL)
                continue

            if (re.fullmatch(r'[A-Z]{2}\d{3}', c) for c in courses):
                break
            else:
                print("Invalid input. Each course must have 2 letters followed by 3 digits (e.g., CS101). Try again.")
        except ValueError as ve:
            print(ve)

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

    while True:
        try:
            status_input = input("Enter Student Status, Full-Time [1] / Part-time [2]: ")

            if status_input == "1":
                status = True
                break
            elif status_input == "2":
                status = False
                break
            else:
                print("Invalid status input. Please enter 1 or 2.")
                logging.warning(f"Invalid status input entered: {status_input}.")
                continue

        except ValueError:
            print(Fore.RED + "Invalid status. Enter a valid Year of Study" + Style.RESET_ALL)
            logging.error("Invalid status input")

    students.append({
        "Student ID": student_id,
        "Student Name": capitalised_name,
        "Email": email,
        "Courses": courses,
        "Year": year,
        "Status": status
    })

    logging.info(f"New student added: ID: {student_id}, Name: {capitalised_name}, Email: {email}, Course: {courses}, Year: {year}, Status: {status}")
    print(Fore.GREEN + f"Student {capitalised_name} added successfully. \n" + Style.RESET_ALL)

# Initial Enrollment code - use if new enroll_student() code malfunctions
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

#Function to enroll students
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
                logging.warning(f"Tried to enroll with an invalid student, ID: {student_id}")
                print(Fore.RED + "Student ID not found." + Style.RESET_ALL)
                continue

            print(Fore.GREEN + f"Student {student['Student Name']}, ID: {student_id} has been chosen." + Style.RESET_ALL)

            while True:
                courses_input = input("Enter course codes (comma-seperated) (Enter 'E' to exit): ")

                if not courses_input:
                    print(Fore.RED + "Invalid Course Code. Please enter a valid Course Code." + Style.RESET_ALL)
                    continue

                if courses_input == "E":
                    print(Fore.GREEN + "Exiting the enrollment process..." + Style.RESET_ALL)
                    return

                courses = courses_input.strip().split(",")

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
            if students[j]["Year"] < students[j + 1]["Year"]:
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
            print(Fore.CYAN + "\nSearched Student Details:\n" + Style.RESET_ALL + tabulate([student], headers="keys", tablefmt="fancy_grid"))
            break  # stop after first match
    else:
        logging.warning(f"Student with ID or name {search_input} not found.")
        print(Fore.RED + "Student not found." + Style.RESET_ALL)

#import pandas - export to csv
def export():
    df = pd.DataFrame(students)

    df.to_csv('students.csv', index=False)

    print(Fore.GREEN + "Data has been successfully exported to 'students.csv'. \n" + Style.RESET_ALL)
    logging.info(f"Data has been successfully exported to 'students.csv'")


def generate_distribution_chart():
    try:
        if not students:
            print(Fore.RED + "No student records found.")
            return

        # Count students in each year
        year_counts = {1: 0, 2: 0, 3: 0}
        for student in students:
            year = student.get("Year")
            if year in year_counts:
                year_counts[year] += 1

        x = np.array(["Year 1", "Year 2", "Year 3"])
        y = np.array([year_counts[1], year_counts[2], year_counts[3]])

        fig, ax = plt.subplots()
        ax.bar(x, y, color='skyblue')
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of Students')
        ax.set_title('Student Distribution by Year')

        # Ensure y-axis has only whole numbers
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        chart_filename = 'student_distribution_chart.png'
        plt.savefig(chart_filename)
        plt.show()

        print(Fore.GREEN + f"Student distribution chart generated and saved as {chart_filename}.")
        logging.info(f"Student distribution chart generated and saved as {chart_filename}.")

    except Exception as e:
        print(Fore.RED + f"Error generating department distribution chart: {e}")
        logging.error(f"Error generating department distribution chart: {e}")


if __name__ == "__main__":
    login()