import ast
import numpy as np
import pandas as pd
import logging
import re
from colorama import Fore, Style, init
from tabulate import tabulate
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import os
from gtts import gTTS
from playsound import playsound
import hashlib

# Language for gTTS
language = "en"

# Logging
logging.basicConfig(filename='student_registration.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize colorama to auto-reset colors after each print statement
init(autoreset=True)

# Student Class
class Student:
    def __init__(self, student_id, student_name, email, course, year, status):
        self.student_id = student_id
        self.student_name = student_name
        self.email = email
        self.course = course
        self.year = year
        self.status = status

    # email validator
    @staticmethod
    def validate_email(email):
        """Validate if the email is in the correct format."""
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None


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

# Admin accounts
# Passwords are hashed using SHA-256
admin = {"admin01": "0876dfca6d6fedf99b2ab87b6e2fed4bd4051ede78a8a9135b500b2e94d99b88",  # pw: admin01
         "admin02": "243a5a4f4e3a27de86391f07cf058a7b0b73ce46069bf84df749306298560f4f"}  # pw: admin02

# User accounts
# Passwords are hashed using SHA-256
user = [
    {
        "Username": "user01",
        "Password": "aad415a73c4cef1ef94a5c00b2642b571a3e5494536328ad960db61889bd9368",  # pw: user01
        "Active": True  # User account is available
    },
    {
        "Username": "user02",
        "Password": "76431fac8a187241af8f3f37156deb94732f52fb45eb07ec4f462051bd82f183",  # pw: user02
        "Active": True
    },
    {
        "Username": "test",
        "Password": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",  # pw: test
        "Active": False  # User account is locked
    }
]


# Hash password using SHA-256
# Use SHA-256 instead of hash() due to session management
def hash_pw(password):
    # Use SHA-256 for consistent hashing
    return hashlib.sha256(password.encode()).hexdigest()

#Cleanup function that deletes .mp3 files after playback
def play_and_cleanup_audio(filename):
    try:
        playsound(filename)
    except Exception as e:
        logging.error(f"Audio playback failed: {e}")
    finally:
        try:
            if os.path.exists(filename):
                os.remove(filename)
                logging.info(f"Audio file deleted: {filename}")
        except Exception as e:
            logging.warning(f"Failed to delete audio file: {e}")

# Login function
def login():
    # Infinite username checking loop
    while True:
        try:
            username = input(Fore.CYAN + "Enter Username (Type 'E' to quit, 'Reset PW' to reset password): " )

            if username == 'E':
                print(Fore.YELLOW + "Exiting login process." )
                return  # Exit the login function


            elif username == "Reset PW":
                reset_password()
                return  # Exit after password reset

            while not username:  # Check if the username is empty
                print(Fore.RED + "Invalid Username. Please try again")
                username = input(Fore.CYAN + "Enter Username (Type 'E' to quit, 'Reset PW' to reset password): ")

            # Admin Login
            # Check if the username exists in admin
            if username in admin:
                # If found in admin, ask for the password
                password_attempts = 0
                max_attempts = 2

                while password_attempts < max_attempts:
                    password = input(
                        Fore.CYAN + "Enter Password (Enter 'Reset PW' to reset password): ")

                    if password == "Reset PW":
                        reset_password()
                        return  # Exit after password reset

                    hashed_pw_input = hash_pw(password)

                    if admin[username] == hashed_pw_input:
                        print(Fore.GREEN + f"{username} has logged in successfully as an Admin!\n")
                        # gTTS code - next 3 lines
                        tts = gTTS(text=f'Hello {username}', lang=language, slow=False)
                        tts.save(f'{username}.mp3')
                        play_and_cleanup_audio(f'{username}.mp3')
                        logging.info(f"{username} has logged in successfully as an Admin!")
                        admin_menu()
                        return  # Exit after successful login (exit from login function)


                    else:
                        print(Fore.RED + "Wrong Password. Please try again.")
                        password_attempts += 1

                # If the password attempts are exceeded
                print(Fore.RED + f"Too many failed password attempts for admin {username}.")
                logging.warning(f"Too many failed password attempts for admin: {username}")
                login()  # Exit after failed password attempts

            # User Login
            # Check if the username exists in the user list
            user_found = False
            locked_user = False
            for u in user:
                if u["Username"] == username:
                    user_found = True
                    if not u["Active"]:  # Check if the account is locked
                        locked_user = True
                        print(
                            Fore.RED + f"Account for '{username}' is locked. Please contact the admin.")
                    break  # Exit loop once the user is found (either locked or active)

            # If user is not found, inform the user
            if not user_found:
                print(Fore.RED + "User does not exist. Please check your username and try again.")
                continue


            # If the user is found but locked, prevent further login attempts
            elif locked_user:
                login()  # Exit if locked

            # If the user is found and active, ask for the password
            password_attempts = 0
            max_attempts = 2

            while password_attempts < max_attempts:
                password = input(Fore.CYAN + "Enter Password (Enter 'Reset PW' to reset password): ")
                if password == "Reset PW":
                    reset_password()
                    return  # Exit after password reset

                hashed_pw_input = hash_pw(password)

                # Check if the username and password match for a regular user
                for user_entry in user:
                    if user_entry["Username"] == username and user_entry["Active"]:
                        if user_entry["Password"] == hashed_pw_input:
                            print(Fore.GREEN + f"{username} has logged in successfully as a User!")
                            # gTTS code - next 3 lines
                            tts = gTTS(text=f'Hello {username}', lang=language, slow=False)
                            tts.save(f'{username}.mp3')
                            play_and_cleanup_audio(f'{username}.mp3')
                            logging.info(f"{username} has logged in successfully as a User!")
                            user_menu()
                            return  # Exit after successful login (exit from login function)

                # Incorrect password
                print(Fore.RED + "Wrong Password. Please try again." )
                password_attempts += 1

            # If the password attempts are exceeded
            print(
                Fore.RED + f"Too many failed password attempts for user: {username} \n{username} Account is locked. Please contact an admin" )
            for u in user:
                if u["Username"] == username:
                    u["Active"] = False
            logging.warning(f"Too many failed password attempts for user: {username}")
            login()  # Exit after failed password attempts

        except ValueError:
            print(Fore.RED + "Invalid Input" )
            continue


# Reset password function
def reset_password():
    while True:
        username = input(Fore.YELLOW + "Enter username to reset password for: ")

        if username in admin:
            print(Fore.RED + "Cannot reset admin password")
            continue

        for u in user:
            if u["Username"] == username:
                break
        break

    while True:
        password = input(Fore.YELLOW + "Enter new password: " )

        new_password = hash_pw(password)

        # Checks if old pw = new pw
        for u in user:
            if u["Password"] == new_password:
                # Error message in red
                print(Fore.RED + f"New password cannot be same as the old password")
                break
            else:
                u["Password"] = new_password  # update the user password
                print(Fore.GREEN + f"Password for {username} has been successfully reset. \n")
                logging.info(f'{username} has successfully reset their password')
                break

        login()


# Change user's "Active" status
def user_activation():
    username = input("Enter username to unlock account for: ")

    user_found = False
    for u in user:
        if u["Username"] == username:
            user_found = True
            # Check activation/deactivation based on user input
            activation_input = input("Activate [1] or Deactivate [2] account: ")

            # Ensure valid input
            if activation_input not in ["1", "2"]:
                print(Fore.RED + "Invalid option. Please enter 1 or 2.")
                return

            if activation_input == "1":  # Activate account
                if u["Active"]:
                    print(Fore.RED + f"User {username} is already active.")
                else:
                    u["Active"] = True
                    print(Fore.GREEN + f"User {username} has been activated.")
                    logging.warning(f"User {username} has been activated successfully")


            elif activation_input == "2":  # Deactivate account
                if not u["Active"]:
                    print(Fore.RED + f"User {username} is already deactivated.")
                else:
                    u["Active"] = False
                    print(Fore.GREEN + f"User {username} has been deactivated.")
                    logging.warning(f"User {username} has been deactivated successfully")
            break  # Exit the loop once the operation is performed

    if not user_found:
        print(Fore.RED + "User not found")


# Admin menu when admin is logged in
def admin_menu():
    while True:
        print(
            Fore.MAGENTA + "--- Student Course Registration System --- \n"  +
            Fore.BLUE + "--- Admin Menu --- \n"  + Style.RESET_ALL +
            "1: Display all student records \n"
            "2: Add a new student record \n"
            "3: Remove student by ID \n"
            "4: Enroll student for a new course \n"
            "5: Remove student from course \n"
            "6: Sort students by Year of Study \n"
            "7: Sort students by Num of Registered Course \n"
            "8: Search for a student by ID or Name \n"
            "9: Search Student ID by range \n"
            "10: Filter Students by Year of Study \n"
            "11: Import student data from CSV \n"
            "12: Export student data to CSV \n"
            "13: Generate Student Distribution by Year chart \n"
            "14: Manage Users \n"
            "15: Logout  \n"
            "0: Exit the program"
        )

        choice = input("Enter your choice: ")
        if choice == "1":
            display_all_students()
        elif choice == "2":
            add_student()
        elif choice == "3":
            remove_student_by_id()
        elif choice == "4":
            enroll_student()
        elif choice == "5":
            remove_course()
        elif choice == "6":
            sort_year()
        elif choice == "7":
            sort_course()
        elif choice == "8":
            search()
        elif choice == "9":
            student_range()
        elif choice == "10":
            filter_students()
        elif choice == "11":
            import_csv()
        elif choice == "12":
            export()
        elif choice == "13":
            generate_distribution_chart()
        elif choice == "14":
            manage_users_menu()
        elif choice == "15":
            print(Fore.GREEN + "You have successfully logged out! \n")
            login()
        elif choice == "0":
            print(Fore.RED + "Exiting the programme...")
            logging.info(f"Admin has exited the programme")
            exit()
        else:
            print(Fore.RED + "Invalid Option, Please enter an input from 0-15 \n")
            logging.warning(f"Invalid menu option entered")


# Menu to manage users
def manage_users_menu():
    print(
        Fore.MAGENTA + "--- Student Course Registration System --- \n"  +
        Fore.BLUE + "--- Manage Users --- \n" + Style.RESET_ALL +
        "1: Return to main menu \n"
        "2: Display all user records \n"
        "3: Add users \n"
        "4: Activate / Deactivate User \n"
        "0: Exit the program"
    )

    choice = input("Enter your choice: ")
    if choice == "1":
        admin_menu()
    elif choice == "2":
        display_all_users()
    elif choice == "3":
        add_users()
    elif choice == "4":
        user_activation()
    elif choice == "0":
        print(Fore.RED + "Exiting the programme...")
        logging.info(f"Admin has exited the programme")
        exit()
    else:
        print(Fore.RED + "Invalid Option, Please enter an input from 0-4 \n")
        logging.warning(f"Invalid menu option entered")


# User menu when user is logged in
def user_menu():
    while True:
        print(
            Fore.MAGENTA + "--- Student Course Registration System --- \n" +
            Fore.BLUE + "--- User Menu --- \n" + Style.RESET_ALL +
            "1: Display all student records \n"
            "2: Search for a student by ID or Name \n"
            "3: Reset Password  \n"
            "4: Logout  \n"
            "0: Exit the program "
        )

        choice = input("Enter your choice: ")
        if choice == "1":
            display_all_students()
        elif choice == "2":
            search()
        elif choice == "3":
            reset_password()
        elif choice == "4":
            print(Fore.GREEN + "You have successfully logged out! \n")
            login()
        elif choice == "0":
            print(Fore.RED + "Exiting the programme...")
            logging.info(f"User has exited the programme")
            exit()
        else:
            print(Fore.RED + "Invalid Option, Please enter an input from 0-4 \n")
            logging.warning(f"Invalid menu option entered")


# Function to display all users
def display_all_users():
    print(Fore.CYAN + "\nDisplay Of All User Records:" + Style.RESET_ALL)
    print(tabulate(user, headers="keys", tablefmt="fancy_grid"))


# Function to display all students and information
def display_all_students():
    if not students:
        print(Fore.RED + "No students found.")
        return

    # Convert Status:True to Full time and Status:False to Part-Time for display
    for student in students:
        student["Status"] = "Full-Time" if student["Status"] else "Part-Time"

    # Sort function to sort Student ID in descending order for display
    n = len(students)
    for i in range(n):
        for j in range(0, n - i - 1):
            if students[j]["Student ID"] > students[j + 1]["Student ID"]:  # < when descending
                students[j], students[j + 1] = students[j + 1], students[j]

    print(Fore.CYAN + "\nDisplay Of All Student Records: \n" + Style.RESET_ALL + tabulate(students, headers="keys",tablefmt="fancy_grid"))


# Function to add student
def add_student():
    # Student ID
    while True:
        try:
            student_id = (input("Enter Student ID: "))

            if len(student_id) != 5:
                print(Fore.RED + "Invalid Student ID input. Enter a 5 digit Student ID")
                continue

            student_id = int(student_id)

            for student in students:
                if student["Student ID"] == student_id:
                    # Error message in red
                    print(
                        Fore.RED + f"Student ID {student_id} already exists. Please enter a unique ID.")
                    logging.warning(f"Attempted to add student with an existing ID: {student_id}")
                    break  # when duplicate is found exit for loop


            else:
                break  # when no duplicate is found exit while loop


        except ValueError:
            print(Fore.RED + "Invalid Student ID input. Try again" )
            logging.error("Invalid Student ID input entered.")

    # Student Name
    while True:
        student_name = input("Enter Student Name: ").title()  # capitalise first character in every word

        if not student_name:
            print(Fore.RED + "Invalid student name entered. Please enter a valid name" )
            logging.error("Attempted to add student with an invalid name.")


        else:
            break

    # Student Email
    while True:
        try:
            email = input("Enter Student Email: ")

            if not Student.validate_email(email):
                print(Fore.RED + "Invalid email format. Please enter a valid email." )
                logging.warning(f"Invalid email format entered: {email}")
                continue  # if email not valid keep asking

            email_exists = any(student["Email"].lower() == email.lower() for student in students)
            if email_exists:
                print(Fore.RED + f"Email {email} already exists. Please enter a unique email.")
                logging.warning(f"Attempted to add student with an existing email: {email}")
                continue

            break  # if email valid break


        except ValueError:
            print(Fore.RED + "Invalid email format. Please enter a valid email.")
            logging.error("Invalid email format input entered.")

    # Student Course List
    while True:
        try:
            courses = input("Enter Course List (comma-separated): ").strip().upper().split(",")
            courses = [c.strip() for c in courses if c.strip()]  # remove extra spaces and ignore empty entries

            if not courses:
                print(Fore.RED + "Must enroll student into at least 1 course")
                continue

            if all(re.fullmatch(r'[A-Z]{2}\d{3}', c) for c in courses):
                break
            else:
                print(
                    Fore.RED + "Invalid input. Each course must have 2 letters followed by 3 digits (e.g., CS101). Try again.")
        except ValueError as ve:
            print(ve)

    # Student Year of Study
    while True:
        try:
            year = int(input("Enter Student Year of Study [1-3]: "))

            if year > 3 or year < 1:
                print(Fore.RED + "Invalid year of study. Enter a valid Year of Study")
                logging.warning(f"Invalid year entered: {year}.")
            else:
                break


        except ValueError:
            print(Fore.RED + "Invalid year of study. Enter a valid Year of Study")
            logging.error("Invalid year of study input.")

    # Student Status
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
                print(Fore.RED + "Invalid status input. Please enter 1 or 2.")
                logging.warning(f"Invalid status input entered: {status_input}.")
                continue


        except ValueError:
            print(Fore.RED + "Invalid status. Enter a valid Year of Study")
            logging.error("Invalid status input")

    # Add students into list
    students.append({
        "Student ID": student_id,
        "Student Name": student_name,
        "Email": email,
        "Courses": courses,
        "Year": year,
        "Status": status
    })

    logging.info(
        f"New student added: ID: {student_id}, Name: {student_name}, Email: {email}, Course: {courses}, Year: {year}, Status: {status}")
    print(Fore.GREEN + f"Student {student_name} added successfully. \n")


# Function to add users
def add_users():
    username = input("Enter new username: ")

    for u in user:
        if u["Username"] == username:
            print(Fore.RED + "User already exists.")
            return

    password = input("Enter password: ")
    hashed_pw = hash_pw(password)

    # All students create by admins are automatically active
    user.append({
        "Username": username,
        "Password": hashed_pw,
        "Active": True
    })

    print(Fore.GREEN + f"You have successfully added {username}")


# Function to remove students by ID
def remove_student_by_id():
    global students  # Use the global `students` list

    while True:
        try:
            # Ask the user to enter the student ID
            student_id = int(input("Enter the Student ID to remove: "))

            # Check if the student exists
            student_found = False
            for student in students:
                if student["Student ID"] == student_id:
                    student_found = True
                    break

            if student_found:
                # Remove the student with the given ID
                students = [student for student in students if student["Student ID"] != student_id]
                print(Fore.GREEN + f"Student with ID {student_id} has been removed. \n")
                logging.warning(f'{student_id} student details has been successfully removed')
                break
            else:
                print(Fore.RED + "Student ID not found. Please enter a valid student ID.")


        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a valid Student ID.")


# Function to enroll students
def enroll_student():
    while True:
        try:
            student_input = input("Enter student ID (Enter 'E' to exit): ")

            if student_input == 'E':
                print(Fore.GREEN + "Exiting the enrollment process...")
                break

            student_id = int(student_input)
            logging.info(f"User has started to enroll student {student_id} into courses")

            student = next((s for s in students if s["Student ID"] == student_id), None)

            if not student:
                logging.warning(f"Tried to enroll with an invalid student, ID: {student_id}")
                print(Fore.RED + "Student ID not found." )
                continue

            print(
                Fore.GREEN + f"Student {student['Student Name']}, ID: {student_id} has been chosen.")

            while True:
                courses_input = input("Enter course codes (comma-seperated) (Enter 'E' to exit): ")

                if not courses_input:
                    print(Fore.RED + "Invalid Course Code. Please enter a valid Course Code.")
                    continue

                if courses_input == "E":
                    print(Fore.GREEN + "Exiting the enrollment process...")
                    return

                courses = courses_input.strip().split(",")

                for course in courses:
                    course = course.upper()

                    if not re.match(r'^[A-Z]{2}\d{3}$', course):
                        print(
                            Fore.RED + f"Invalid course code: {course}. Each course must have 2 letters followed by 3 digits.")
                        continue

                    if course in student["Courses"]:
                        print(
                            Fore.RED + f"Student {student['Student Name']}, ID: {student_id} is already enrolled in {course}.")
                        continue

                    student["Courses"].append(course)
                    print(
                        Fore.GREEN + f"Student {student['Student Name']}, ID: {student_id} has been successfully enrolled in {course}.")
                    logging.info(f"Student {student['Student Name']}, ID: {student_id} enrolled in {course}")


        except ValueError:
            print(Fore.RED + "Invalid Student ID. Please enter a valid student ID.")


# Function to remove course for student by ID
def remove_course():
    while True:
        try:
            student_input = input("Enter student ID (Enter 'E' to exit): ")

            if student_input == 'E':
                print(Fore.GREEN + "Exiting the course removal process...")
                break

            student_id = int(student_input)
            logging.info(f"User has started to remove student {student_id} from courses")

            student = next((s for s in students if s["Student ID"] == student_id), None)

            if not student:
                logging.warning(f"Tried to remove course with an invalid student, ID: {student_id}")
                print(Fore.RED + "Student ID not found." )
                continue

            print(
                Fore.GREEN + f"Student {student['Student Name']}, ID: {student_id} has been chosen.")

            while True:
                courses_input = input("Enter course codes (comma-seperated) (Enter 'E' to exit): ")

                if not courses_input:
                    print(Fore.RED + "Invalid Course Code. Please enter a valid Course Code.")
                    continue

                if courses_input == "E":
                    print(Fore.GREEN + "Exiting the removal process...")
                    return

                courses = [course.strip().upper() for course in courses_input.strip().split(",")]

                for course in courses:
                    course = course.upper()

                    if not re.match(r'^[A-Z]{2}\d{3}$', course):
                        print(
                            Fore.RED + f"Invalid course code: {course}.Each course must have 2 letters followed by 3 digits." )
                        continue

                    if not course in student["Courses"]:
                        print(
                            Fore.RED + f"Student {student['Student Name']}, ID: {student_id}, is not enrolled into {course}.")
                        continue

                    student["Courses"].remove(course)
                    print(Fore.GREEN + f"Student {student['Student Name']}, ID: {student_id} has been successfully removed from {course}." )
                    logging.info(f"Student {student['Student Name']}, ID: {student_id} removed from {course}")


        except ValueError:
            print(Fore.RED + "Invalid Student ID. Please enter a valid student ID.")


# Bubble Sort - Ascending/Descending
# Sorted by year of study
def sort_year():
    sort_year_order = input(Fore.CYAN + "Sort Year of Study in Ascending or Descending order (A/D): ")

    if sort_year_order == "A":
        n = len(students)
        for i in range(n):
            for j in range(0, n - i - 1):
                if students[j]["Year"] > students[j + 1]["Year"]:  # > when ascending
                    students[j], students[j + 1] = students[j + 1], students[j]

        print("Sorted by Year Of Study in Ascending Order: \n" + tabulate(students, headers="keys",
                                                                          tablefmt="fancy_grid"))


    elif sort_year_order == "D":
        n = len(students)
        for i in range(n):
            for j in range(0, n - i - 1):
                if students[j]["Year"] < students[j + 1]["Year"]:  # < when descending
                    students[j], students[j + 1] = students[j + 1], students[j]

        print("Sorted by Year Of Study in Descending Order: \n" + tabulate(students, headers="keys",
                                                                           tablefmt="fancy_grid"))


    else:
        print(Fore.RED + "Invalid Sort Order!")


# Selection Sort - Ascending/Descending
# Sorted by num of registered courses
def sort_course():
    sort_course_order = input(
        Fore.CYAN + "Sort Num Of Course in Ascending or Descending order (A/D): ")

    n = len(students)

    if sort_course_order == "A":
        for i in range(n - 1):
            min_idx = i  # use min when it's ascending
            for j in range(i + 1, n):
                if len(students[j]['Courses']) < len(
                        students[min_idx]['Courses']):  # use len as comparing by no of | < if ascending
                    min_idx = j
            students[i], students[min_idx] = students[min_idx], students[i]
        print("Sorted by Num of Registered Courses in Ascending Order: \n" + tabulate(students, headers="keys",
                                                                                      tablefmt="fancy_grid"))


    elif sort_course_order == "D":
        for i in range(n - 1):
            max_idx = i  # use max when it's descending
            for j in range(i + 1, n):
                if len(students[j]['Courses']) > len(
                        students[max_idx]['Courses']):  # use len as comparing by no of | > if descending
                    max_idx = j
            students[i], students[max_idx] = students[max_idx], students[i]
        print("Sorted by Num of Registered Courses in Descending Order: \n" + tabulate(students, headers="keys",
                                                                                       tablefmt="fancy_grid"))


    else:
        print(Fore.RED + "Invalid Sort Order!")


# Search for student by id or name
def search():
    search_input = input("Enter Student ID or Student Name: ").strip()
    for student in students:
        if str(student["Student ID"]) == search_input or student["Student Name"].lower() == search_input.lower():
            print(Fore.CYAN + "\nSearched Student Details:\n" + tabulate([student], headers="keys",
                                                                                           tablefmt="fancy_grid"))
            break  # stop after first match
    else:
        logging.warning(f"Student with ID or name {search_input} not found.")
        print(Fore.RED + "Student not found.")


# Search for student ID in given range
def student_range():
    lower_limit = input("Enter lower limit for student ID: ")

    if not (lower_limit.isdigit() and len(lower_limit) == 5):
        print(Fore.RED + "Invalid lower limit. Enter a 5-digit Student ID.")
        return

    upper_limit = input("Enter upper limit for student ID: ")

    if not (upper_limit.isdigit() and len(upper_limit) == 5):
        print(Fore.RED + "Invalid upper limit. Enter a 5-digit Student ID." )
        return

    lower_limit = int(lower_limit)
    upper_limit = int(upper_limit)

    # Filter students
    filtered_students = [
        student for student in students
        if lower_limit <= student["Student ID"] <= upper_limit
    ]

    print(Fore.CYAN + f"\nStudents with ID from {lower_limit} to {upper_limit}:" +Style.RESET_ALL)

    if filtered_students:
        # Bubble sort ascending by Student ID
        n = len(filtered_students)
        for i in range(n):
            for j in range(0, n - i - 1):
                if filtered_students[j]["Student ID"] > filtered_students[j + 1]["Student ID"]:
                    filtered_students[j], filtered_students[j + 1] = filtered_students[j + 1], filtered_students[j]

        print(tabulate(filtered_students, headers="keys", tablefmt="fancy_grid"))
    else:
        print(Fore.YELLOW + "No student IDs found in the given range." )


# Filter students by year of study
def filter_students():
    try:
        filter_year_input = int(input("Enter year of students to filter: "))
    except ValueError:
        print(Fore.RED + "Invalid year. Please enter a number." )
        return

    filtered_students = [
        student for student in students
        if student["Year"] == filter_year_input
    ]

    print(Fore.CYAN + f"\nAll Year {filter_year_input} Students:")

    if filtered_students:
        print(tabulate(filtered_students, headers="keys", tablefmt="fancy_grid"))
    else:
        print(Fore.YELLOW + "No students found in the selected year.")


# import pandas - export to csv
def export():
    export_csv_filename = input(
        Fore.CYAN + "Enter the name of the file you wish to save as (with .csv extension): ")

    df = pd.DataFrame(students)

    df.to_csv(f'{export_csv_filename}.csv', index=False)

    print(Fore.GREEN + f"Data has been successfully exported to '{export_csv_filename}.csv'. \n")
    logging.info(f"Data has been successfully exported to '{export_csv_filename}.csv'")


# import pandas - import csv file
def import_csv():
    file_name = input(Fore.CYAN + "Enter the CSV file name (with .csv extension): ")

    if not file_name:
        print(Fore.RED + "File does not exist")
        return

    if not file_name.endswith('.csv'):
        print(Fore.RED + "The file must have a .csv extension. Please try again.")
        return

    if not os.path.exists(file_name):
        print(
            Fore.RED + f"The file {file_name} does not exist. Please check the file name and try again." )
        return

    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(file_name)

        # Validate if necessary columns exist in the CSV
        required_columns = ['Student ID', 'Student Name', 'Email', 'Courses', 'Year', 'Status']
        if not all(col in df.columns for col in required_columns):
            print(
                Fore.RED + f"CSV file must contain the following columns: {', '.join(required_columns)}")
            return

        # Convert 'Courses' from string to list
        df['Courses'] = df['Courses'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

        # Convert DataFrame to list of dictionaries
        new_students = df.to_dict(orient='records')

        # Add new students to the existing students list (without duplicates)
        global students
        for new_student in new_students:
            # Check if the student ID already exists
            if not any(student['Student ID'] == new_student['Student ID'] for student in students):
                students.append(new_student)
            else:
                print(Fore.RED + f"Student ID {new_student['Student ID']} already exists. Skipping.")

        print(Fore.GREEN + f"Student data from '{file_name}' has been successfully added to the current records.")
        logging.info(f"Student data from '{file_name}' has been successfully added.")


    except Exception as e:
        print(Fore.RED + f"Error reading the CSV file: {e}")
        logging.error(f"Error reading the CSV file: {e}")


# Generate Pie/Bar chart using matplotlib
def generate_distribution_chart():
    try:
        if not students:
            print(Fore.RED + "No student records found.")
            return

        chart_input = input(Fore.CYAN + "Generate a Pie Chart or a Bar Graph (P/B): ")

        chart_filename = input(Fore.CYAN + "Enter the name of the file you wish to save it as: ")

        # Count students in each year
        year_counts = {1: 0, 2: 0, 3: 0}
        for student in students:
            year = student.get("Year")
            if year in year_counts:
                year_counts[year] += 1

        if chart_input == "P":
            # Creating pie chart

            plt.pie(year_counts.values(), labels=["Year 1", "Year 2", "Year 3"], autopct='%1.1f%%', startangle=90)
            plt.title("Student Distribution by Year")

            # Show and save plot
            plt.savefig(chart_filename)
            plt.show()

            print(Fore.GREEN + f"Student distribution pie chart generated and saved as '{chart_filename}'.")
            logging.info(f"Student distribution pie chart generated and saved as '{chart_filename}'.")


        elif chart_input == "B":
            x = np.array(["Year 1", "Year 2", "Year 3"])
            y = np.array([year_counts[1], year_counts[2], year_counts[3]])

            fig, ax = plt.subplots()
            ax.bar(x, y, color='skyblue')
            ax.set_xlabel('Year of Study')
            ax.set_ylabel('Number of Students')
            ax.set_title('Student Distribution by Year')

            # Ensure y-axis has only whole numbers
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))

            plt.savefig(chart_filename)
            plt.show()

            print(Fore.GREEN + f"Student distribution bar chart generated and saved as '{chart_filename}'.")
            logging.info(f"Student distribution bar chart generated and saved as '{chart_filename}'.")

    except Exception as e:
        print(Fore.RED + f"Error generating department distribution chart: {e}")
        logging.error(f"Error generating department distribution chart: {e}")


if __name__ == "__main__":
    login()
