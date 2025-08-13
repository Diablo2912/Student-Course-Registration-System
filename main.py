import ast
import hashlib
import json
import logging
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppresses INFO and WARNING logs for FaceID
import re
from collections import Counter, defaultdict
import heapq
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from colorama import Fore, Style, init
from gtts import gTTS
from matplotlib.ticker import MaxNLocator
from playsound import playsound
from tabulate import tabulate
from datetime import datetime
import google.generativeai as genai
from deepface import DeepFace
import cv2
import smtplib
from email.message import EmailMessage
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Language for gTTS
language = "en"

# Logging
logging.basicConfig(filename='student_registration.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialise colorama to auto-reset colors after each print statement
init(autoreset=True)

# Make folder to store faces ID if folder doesn't exist
UPLOAD_FOLDER = '/faces'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Predefined SMTP config
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USERNAME = 'cropzyssp@gmail.com'
MAIL_PASSWORD = 'wivz gtou ftjo dokp'
MAIL_USE_TLS = True

# Student Class
class Student:
    def __init__(self, student_id, student_name, email, course, year, status):
        self.student_id = student_id
        self.student_name = student_name
        self.email = email
        self.course = course
        self.year = year
        self.status = status
        self.history = CourseHistoryList()

    # email validator
    @staticmethod
    def validate_email(email):
        """Validate if the email is in the correct format."""
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None

    def add_courses(self, courses):
        for course in courses:
            course = course.strip().upper()
            if not re.match(r'^[A-Z]{2}\d{3}$', course):
                print(Fore.RED + f"Invalid course code format: {course}")
                continue
            if course in self.course:
                print(Fore.RED + f"Already enrolled in {course}")
            else:
                self.course.append(course)
                self.history.add_record(course, "enrolled")  # ✅ log to history
                print(Fore.GREEN + f"Enrolled in {course}")

    def remove_courses(self, courses):
        for course in courses:
            course = course.strip().upper()
            if not re.match(r'^[A-Z]{2}\d{3}$', course):
                print(Fore.RED + f"Invalid course code format: {course}")
                continue
            if course not in self.course:
                print(Fore.RED + f"Not enrolled in {course}")
            else:
                self.course.remove(course)
                self.history.add_record(course, "removed")  # ✅ log to history
                print(Fore.GREEN + f"Removed from {course}")

    def display_student_details(self):
        print(Fore.CYAN + f"\nStudent ID: {self.student_id}" + Style.RESET_ALL)
        print(Fore.CYAN + f"Student Name: {self.student_name}" + Style.RESET_ALL)
        print(Fore.CYAN + f"Email: {self.email}" + Style.RESET_ALL)
        print(Fore.CYAN + f"Year: {self.year}" + Style.RESET_ALL)
        print(Fore.CYAN + f"Status: {self.status}" + Style.RESET_ALL)
        print(Fore.CYAN + f"Enrolled Courses: {', '.join(self.course)}" + Style.RESET_ALL)

# StudentRequest Class

class StudentRequest:
    def __init__(self, student_id, request_type, priority, details, timestamp):
        self.student_id = student_id
        self.request_type = request_type
        self.priority = priority
        self.details = details
        self.timestamp = timestamp

    def __str__(self):
        return (
            f"Student ID: {self.student_id}\n"
            f"Request Type: {self.request_type}\n"
            f"Priority: {self.priority} ({self.priority})\n"
            f"Details: {self.details}\n"
            f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def __lt__(self, other):
        return self.priority < other.priority

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "request_type": self.request_type,
            "priority": self.priority,
            "details": self.details,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

# Initialize priority queue
request_queue = []

undo_stack = []

redo_stack = []

# Linked list node to store course action history
class CourseHistoryNode:
    def __init__(self, course_code, action, timestamp):
        self.course_code = course_code
        self.action = action  # "enrolled" or "removed"
        self.timestamp = timestamp
        self.next = None

# Linked list class to track registration history
class CourseHistoryList:
    def __init__(self):
        self.head = None

    def add_record(self, course_code, action):
        new_node = CourseHistoryNode(course_code, action, datetime.now())
        new_node.next = self.head
        self.head = new_node

    def display_history(self):
        if not self.head:
            print(Fore.YELLOW + "No course history available.")
            return
        print(Fore.CYAN + "Course Registration History:")
        current = self.head
        while current:
            print(f"{current.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {current.action.upper()} {current.course_code} \n")
            current = current.next

histories = defaultdict(CourseHistoryList)

class StudentBSTNode:
    def __init__(self, student):
        self.student = student
        self.left = None
        self.right = None

class StudentBST:
    def __init__(self):
        self.root = None

    def insert(self, student):
        def _insert(node, student):
            if not node:
                return StudentBSTNode(student)
            if student["Student ID"] < node.student["Student ID"]:
                node.left = _insert(node.left, student)
            else:
                node.right = _insert(node.right, student)
            return node
        self.root = _insert(self.root, student)

    def search(self, student_id):
        def _search(node, student_id):
            if not node:
                return None
            if student_id == node.student["Student ID"]:
                return node.student
            elif student_id < node.student["Student ID"]:
                return _search(node.left, student_id)
            else:
                return _search(node.right, student_id)
        return _search(self.root, student_id)

    def inorder_traversal(self):
        result = []
        def _inorder(node):
            if not node:
                return
            _inorder(node.left)
            result.append(node.student)
            _inorder(node.right)
        _inorder(self.root)
        return result

student_bst = StudentBST()

def rebuild_bst():
    global student_bst
    student_bst = StudentBST()
    for s in students:
        student_bst.insert(s)

# Empty student list
# students = [ ]


# Sample student list for testing and demonstration
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

# Loads the json file for persistent storage
def load_data():
    global students, user, request_queue
    if os.path.exists("data/students_data.json"):
        try:
            with open("data/students_data.json", "r") as f:
                students = json.load(f)
                print(Fore.GREEN + f"Successfully loaded {len(students)} student(s) from students_data.json.")
        except Exception as e:
            print(Fore.RED + f"Failed to load student data: {e}")
            logging.error(f"Error loading students data: {e}")
    else:
        print(Fore.RED + "Students data file not found. Failed to load data")

    if os.path.exists("data/user_data.json"):
        try:
            with open("data/user_data.json", "r") as f:
                user = json.load(f)
                print(Fore.GREEN + f"Successfully loaded {len(user)} user(s) from user_data.json.")
        except Exception as e:
            print(Fore.RED + f"Failed to load user data: {e}")
            logging.error(f"Error loading user data: {e}")
    else:
        print(Fore.RED + "User data file not found. Failed to load data")

    if os.path.exists("data/student_requests.json"):
        try:
            with open("data/student_requests.json", "r") as f:
                request_data = json.load(f)
                request_queue.clear()
                for item in request_data:
                    request = StudentRequest(
                        item["student_id"],
                        item["request_type"],
                        item["priority"],
                        item["details"],
                        datetime.fromisoformat(item["timestamp"])
                    )
                    request_queue.append(request)
                print(Fore.GREEN + f"Successfully loaded {len(request_queue)} request(s) from student_requests.json.\n")
        except Exception as e:
            print(Fore.RED + f"Failed to load student request data: {e}\n")
            logging.error(f"Error loading student request data: {e}")

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

def face_id_login_for_username(username):
    face_folder = "faces"
    if not os.path.exists(face_folder):
        print(Fore.RED + "faces folder not found.")
        return False

    face_path = os.path.join(face_folder, f"{username}.jpg")
    if not os.path.exists(face_path):
        print(Fore.RED + f"No registered face image found for '{username}'. Please register your face.")
        return False

    # Capture webcam image
    cam = cv2.VideoCapture(0)
    print("📸 Look into the camera. Press 'q' to capture your face.\n")

    while True:
        ret, frame = cam.read()
        cv2.imshow("faces ID Login", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

    temp_image_path = os.path.join(face_folder, f"{username}_temp.jpg")
    cv2.imwrite(temp_image_path, frame)

    try:
        result = DeepFace.verify(
            img1_path=face_path,
            img2_path=temp_image_path,
            model_name="Facenet",  # You can use: VGG-faces, Facenet, ArcFace, Dlib, SFace, etc.
            detector_backend="opencv",  # You can also use retinaface, mtcnn, mediapipe
            enforce_detection=False
        )
        os.remove(temp_image_path)

        if result["verified"]:
            print(Fore.GREEN + f"✅ face id successful for {username}!")
            return True
        else:
            print(Fore.RED + "❌ faces does not match.")
            return False

    except Exception as e:
        print(Fore.RED + f"faces verification failed: {str(e)}")
        return False

def register_face(username):
    face_folder = "faces"

    if not os.path.exists(face_folder):
        os.makedirs(face_folder)

    face_path = os.path.join(face_folder, f"{username}.jpg")

    # If face already exists, confirm overwrite
    if os.path.exists(face_path):
        confirm = input(Fore.YELLOW + f"A face is already registered for {username}. Overwrite? (Y/N): ").strip().upper()
        if confirm != "Y":
            print(Fore.CYAN + "Face registration cancelled.")
            return

    cam = cv2.VideoCapture(0)
    print(Fore.CYAN + f"\n📸 {username}, please look into the camera. Press 'q' to capture your face.")

    while True:
        ret, frame = cam.read()
        cv2.imshow("Register Face", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

    # Save face image
    cv2.imwrite(face_path, frame)
    print(Fore.GREEN + f"✅ Face image saved as '{face_path}'")

#email function
def send_email(subject, body, to_email, attachment_path=None):
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = MAIL_USERNAME
        msg['To'] = to_email
        msg.set_content(body)

        # Attach file if provided
        if attachment_path:
            with open(attachment_path, 'rb') as f:
                file_data = f.read()
                file_name = attachment_path.split('/')[-1]
            msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            if MAIL_USE_TLS:
                server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)

        print(Fore.GREEN + f"Email sent successfully to {to_email} \n")

    except Exception as e:
        print(Fore.RED + f"Failed to send email: {e}")
# Login function
def login():
    # Infinite username checking loop
    while True:
        try:
            username = input(Fore.CYAN + "Enter Username (Type 'E' to quit, 'Reset PW' to reset password): ")

            if username == 'E':
                print(Fore.YELLOW + "Exiting login process.")
                return

            elif username == "Reset PW":
                reset_password()
                return

            while not username:
                print(Fore.RED + "Invalid Username. Please try again")
                username = input(Fore.CYAN + "Enter Username (Type 'E' to quit, 'Reset PW' to reset password): ")

            # ---------- ADMIN LOGIN ----------
            if username in admin:
                print(Fore.YELLOW + f"Welcome {username} (Admin)")
                method = input("Login using [1] Password or [2] face ID: ").strip()

                if method == "2":
                    if face_id_login_for_username(username):
                        print(Fore.GREEN + f"{username} has logged in successfully using faces ID as an Admin!\n")
                        tts = gTTS(text=f'Hello {username}', lang=language, slow=False)
                        tts.save(f'{username}.mp3')
                        play_and_cleanup_audio(f'{username}.mp3')
                        logging.info(f"{username} logged in with faces ID (admin).")
                        main_menu(role="admin", current_user=username)
                        return
                    else:
                        print(Fore.RED + "faces ID login failed.")
                        return

                # Fallback to password login
                password_attempts = 0
                max_attempts = 2
                while password_attempts < max_attempts:
                    password = input(Fore.CYAN + "Enter Password (Enter 'Reset PW' to reset password): ")
                    if password == "Reset PW":
                        reset_password()
                        return

                    hashed_pw_input = hash_pw(password)

                    if admin[username] == hashed_pw_input:
                        print(Fore.GREEN + f"{username} has logged in successfully as an Admin!\n")
                        # tts = gTTS(text=f'Hello {username}', lang=language, slow=False)
                        # tts.save(f'{username}.mp3')
                        # play_and_cleanup_audio(f'{username}.mp3')
                        # logging.info(f"{username} has logged in successfully as an Admin!")
                        main_menu(role="admin", current_user=username)
                        return
                    else:
                        print(Fore.RED + "Wrong Password. Please try again.")
                        password_attempts += 1

                print(Fore.RED + f"Too many failed password attempts for admin {username}.")
                logging.warning(f"Too many failed password attempts for admin: {username}")
                login()

            # ---------- USER LOGIN ----------
            user_found = False
            locked_user = False
            for u in user:
                if u["Username"] == username:
                    user_found = True
                    if not u["Active"]:
                        locked_user = True
                        print(Fore.RED + f"Account for '{username}' is locked. Please contact the admin.")
                    break

            if not user_found:
                print(Fore.RED + "User does not exist. Please check your username and try again.")
                continue

            elif locked_user:
                login()

            print(Fore.YELLOW + f"Welcome {username} (User)")
            method = input("Login using [1] Password or [2] face ID: ").strip()

            if method == "2":
                if face_id_login_for_username(username):
                    print(Fore.GREEN + f"{username} has logged in successfully using faces ID as a User!")
                    tts = gTTS(text=f'Hello {username}', lang=language, slow=False)
                    tts.save(f'{username}.mp3')
                    play_and_cleanup_audio(f'{username}.mp3')
                    logging.info(f"{username} logged in with faces ID (user).")
                    main_menu(role="user", current_user=username)
                    return
                else:
                    print(Fore.RED + "faces ID login failed.")
                    return

            # Fallback to password login
            password_attempts = 0
            max_attempts = 2
            while password_attempts < max_attempts:
                password = input(Fore.CYAN + "Enter Password (Enter 'Reset PW' to reset password): ")
                if password == "Reset PW":
                    reset_password()
                    return

                hashed_pw_input = hash_pw(password)

                for user_entry in user:
                    if user_entry["Username"] == username and user_entry["Active"]:
                        if user_entry["Password"] == hashed_pw_input:
                            print(Fore.GREEN + f"{username} has logged in successfully as a User!")
                            tts = gTTS(text=f'Hello {username}', lang=language, slow=False)
                            tts.save(f'{username}.mp3')
                            play_and_cleanup_audio(f'{username}.mp3')
                            logging.info(f"{username} has logged in successfully as a User!")
                            main_menu(role="user", current_user=username)
                            return

                print(Fore.RED + "Wrong Password. Please try again.")
                password_attempts += 1

            print(
                Fore.RED + f"Too many failed password attempts for user: {username} \n{username} Account is locked. Please contact an admin")
            for u in user:
                if u["Username"] == username:
                    u["Active"] = False
            with open("../users_data.json", "w") as out_file:
                json.dump(user, out_file, indent=6)
            logging.warning(f"Too many failed password attempts for user: {username}")
            login()

        except ValueError:
            print(Fore.RED + "Invalid Input")
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
        password = input(Fore.YELLOW + "Enter new password: ")
        new_password = hash_pw(password)

        # Check if new password matches any existing password
        old_passwords = [u["Password"] for u in user]
        if new_password in old_passwords:
            print(Fore.RED + "New password cannot be same as the old password.")
            continue  # Ask again

        # Confirm password
        password_match = input("Re-Enter password: ")
        if password_match != password:
            print(Fore.RED + "Passwords do not match. Try again.")
            continue  # Ask again

        # Update password for current user
        for u in user:
            if u["Username"] == username:
                u["Password"] = new_password
                break

        print(Fore.GREEN + f"Password for {username} has been successfully reset.\n")
        logging.info(f'{username} has successfully reset their password')

        with open("../users_data.json", "w") as out_file:
            json.dump(user, out_file, indent=6)

        break  # Exit the while loop after success

    login()


# Admin menu when admin is logged in
def main_menu(role, current_user):

    # Define menu options by role
    admin_options = {
        "1": ("Dashboard", dashboard),
        "2": ("Display all student records", display_all_students),
        "3": ("Add a new student record", add_student),
        "4": ("Remove student by ID", remove_student_by_id),
        "5": ("Enroll student for a new course", enroll_student),
        "6": ("Remove student from course", remove_course),
        "7": ("Sort students by Year of Study - Bubble Sort", sort_year),
        "8": ("Quick Sort on Year of Study with Secondary Sort (on Name)", quick_sort),
        "9": ("Merge Sort by Num of Registered Course and Student ID", merge_sort_course_and_id),
        "10": ("Sort students by Num of Registered Course - Selection Sort", sort_course),
        "11": ("Search for a student by ID or Name", search),
        "12": ("Search Student ID by range", student_range),
        "13": ("View Student's Course Registration History", view_student_history),
        "14": ("Binary Search Tree", visualize_bst),
        "15": ("Filter Students by Year of Study", filter_students),
        "16": ("Import student data from CSV", import_csv),
        "17": ("Export student data to CSV", export),
        "18": ("Generate Student Distribution by Year chart", generate_distribution_chart),
        "19": ("Manage Users", manage_users_menu),
        "20": ("Manage Student Request", lambda: manage_request_menu(current_user)),
        "21": ("Chatbot", chatbot_loop),
        "22": ("Logout", login),
        "0": ("Exit the program", lambda: exit())
    }

    user_options = {
        "1": ("Display all student records", display_all_students),
        "2": ("Search for a student by ID or Name", search),
        "3": ("Add Student Request", add_student_request),
        "4": ("Chatbot", chatbot_loop),
        "5": ("Reset Password", reset_password),
        "6": ("Register Face ID", lambda: register_face(current_user)),
        "7": ("Logout", login),
        "0": ("Exit the program", lambda: exit())
    }


    options = admin_options  if role == "admin" else user_options

    while True:
        print(Fore.MAGENTA + "--- Student Course Registration System ---")
        print(Fore.BLUE + f"--- {role.capitalize()} Menu ---" + Style.RESET_ALL)

        for key, (desc, _) in options.items():
            print(f"{key}: {desc}")

        choice = input(Fore.CYAN + "Enter your choice: " + Style.RESET_ALL)

        if choice in options:
            print()  # spacing
            options[choice][1]()  # Call the corresponding function
        else:
            print(Fore.RED + "Invalid Option. Please enter a valid input.\n")
            logging.warning(f"Invalid menu option entered for {role}.")

# Menu to manage users
def manage_users_menu(current_user):
    print(
        Fore.MAGENTA + "--- Student Course Registration System --- \n"  +
        Fore.BLUE + "--- Manage Users --- \n" + Style.RESET_ALL +
        "1: Return to main menu \n"
        "2: Manage Student Request \n"
        "3: Display all user records \n"
        "5: Add users \n"
        "5: Activate / Deactivate User \n"
        "0: Exit the program"
    )

    choice = input(Fore.CYAN + "Enter your choice: " +Style.RESET_ALL)
    if choice == "1":
        main_menu(role="admin", current_user=current_user)
    elif choice == "2":
        manage_request_menu()
    elif choice == "3":
        display_all_users()
    elif choice == "4":
        add_users()
    elif choice == "5":
        user_activation()
    elif choice == "0":
        print(Fore.RED + "Exiting the programme...")
        logging.info(f"Admin has exited the programme")
        exit()
    else:
        print(Fore.RED + "Invalid Option, Please enter an input from 0-4 \n")
        logging.warning(f"Invalid menu option entered")

def manage_request_menu(current_user):
    print(
        Fore.MAGENTA + "--- Student Course Registration System --- \n"  +
        Fore.BLUE + "--- Manage Student Request --- \n" + Style.RESET_ALL +
        "1: Return to main menu \n"
        "2: Display All Student Request \n"
        "3: Add Student Request \n"
        "4: Process Next Student Requests \n"
        "5: Filter Request Priority \n"
        "6: Undo Last Request Action \n"
        "7: Redo Last Request Action \n"
        "0: Exit the program"
    )

    choice = input(Fore.CYAN + "Enter your choice: " +Style.RESET_ALL)
    if choice == "1":
        main_menu(role="admin", current_user=current_user)
    elif choice == "2":
        display_student_requests()
    elif choice == "3":
        add_student_request()
    elif choice == "4":
        process_student_request()
    elif choice == "5":
        filter_request_priority()
    elif choice == "6":
        undo_request()
    elif choice == "6":
        redo_request()
    elif choice == "0":
        print(Fore.RED + "Exiting the programme...")
        logging.info(f"Admin has exited the programme")
        exit()
    else:
        print(Fore.RED + "Invalid Option, Please enter an input from 0-4 \n")
        logging.warning(f"Invalid menu option entered")


# Dashboard
def dashboard():
    # Calculate Total Number of Students
    total_students = len(students)

    # Calculate Number of Full-Time and Part-Time Students
    full_time = 0
    for student in students:
        if student['Status'] == True:
            full_time += 1

    part_time = total_students - full_time

    #Most Common Course Enrolled
    all_courses = [course for student in students for course in student['Courses']]
    course_counts = Counter(all_courses)
    most_common_course = course_counts.most_common(1)
    most_common_course_name = most_common_course[0][0] if most_common_course else "No Courses"

    dashboard_data = [
        ["Total Number of Students", total_students],
        ["Number of Full-Time Students", full_time],
        ["Number of Part-Time Students", part_time],
        ["Most Common Course Enrolled", most_common_course_name],
        ["Total Number of Pending Requests", len(request_queue)]
    ]

    print(Fore.CYAN + "\nDashboard:" + Style.RESET_ALL)
    print(tabulate(dashboard_data, headers=["Category", "Value"], tablefmt="fancy_grid"))
    plot_students_per_course_to_file(students, filename="course_distribution.png")

    report_input = input("Would you like to generate a PDF report and send it via email? [Y/N]: ").upper()
    if report_input == 'Y':
        email_input = input('Please enter email: ')
        filename = "dashboard_report.pdf"
        generate_pdf_report(filename)
        send_email(
            subject="Student Dashboard Report",
            body="Please find the attached PDF report for student dashboard analytics.",
            to_email=email_input,
            attachment_path=filename
        )
    else:
        return

def plot_students_per_course_to_file(students, filename="course_distribution.png"):
    course_counts = defaultdict(int)
    for student in students:
        for course in student["Courses"]:
            course_counts[course] += 1

    sorted_courses = sorted(course_counts.items())
    courses = [course for course, _ in sorted_courses]
    counts = [count for _, count in sorted_courses]

    plt.figure(figsize=(10, 6))
    plt.bar(courses, counts)
    plt.xlabel('Courses')
    plt.ylabel('Number of Students')
    plt.title('Total Number of Students per Course')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.savefig(filename)   # Save as file for PDF use
    plt.show()              # <-- This line shows the graph window
    plt.close()

def generate_pdf_report(filename="dashboard_report.pdf"):
    total_students = len(students)
    full_time = sum(1 for student in students if student['Status'])
    part_time = total_students - full_time

    all_courses = [course for student in students for course in student['Courses']]
    course_counts = Counter(all_courses)
    most_common_course = course_counts.most_common(1)
    most_common_course_name = most_common_course[0][0] if most_common_course else "No Courses"

    dashboard_data = [
        ["Total Number of Students", total_students],
        ["Number of Full-Time Students", full_time],
        ["Number of Part-Time Students", part_time],
        ["Most Common Course Enrolled", most_common_course_name],
        ["Total Number of Pending Requests", len(request_queue)]
    ]

    # Prepare chart image file
    chart_filename = "course_distribution.png"
    plot_students_per_course_to_file(students, chart_filename)

    # PDF setup
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("Student Dashboard Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Generated on: {timestamp}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Table
    table = Table([["Category", "Value"]] + dashboard_data, colWidths=[250, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Add page break and chart image
    elements.append(PageBreak())
    elements.append(Paragraph("Course Distribution Chart", styles['Heading2']))
    elements.append(Spacer(1, 12))
    elements.append(Image(chart_filename, width=450, height=300))

    doc.build(elements)


def display_student_requests():
    if not request_queue:
        print(Fore.GREEN + "No pending requests.")
        print(f"Total Student Requests: 0 \n")
        return

    # Sort by priority and timestamp
    sorted_requests = sorted(request_queue)

    table = []
    for req in sorted_requests:
        table.append([
            req.student_id,
            req.request_type,
            req.priority,
            req.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            req.details
        ])
    print(f"Total Student Requests: {len(request_queue)}")

    high = sum(1 for req in request_queue if req.priority == 1)
    medium = sum(1 for req in request_queue if req.priority == 2)
    low = sum(1 for req in request_queue if req.priority == 3)

    print(f"Number Of High Priority Student Requests: {high}")
    print(f"Number Of Medium Priority Student Requests: {medium}")
    print(f"Number Of Low Priority Student Requests: {low}")
    headers = ["Student ID", "Request Type", "Priority", "Timestamp", "Details"]
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))
    plot_studentreq_priority()

    # Filtering logic
    filter_col = input(Fore.CYAN + 'Select a column to filter by: ').strip()

    if filter_col.lower() == 'request type':
        filter_value = input("Enter the Request Type to filter (e.g., Appeal, Drop Course): ").strip().lower()
        filtered = [req for req in sorted_requests if req.request_type.lower() == filter_value]

    elif filter_col.lower() == 'priority':
        try:
            level = int(input("Enter Priority Level to Filter [1 = High, 2 = Medium, 3 = Low]: "))
            if level not in [1, 2, 3]:
                raise ValueError
            filtered = [req for req in sorted_requests if req.priority == level]
        except ValueError:
            print(Fore.RED + "Invalid priority level.")
            return
    else:
        print(Fore.YELLOW + "Unknown filter option. Skipping filter.")
        return

    # Display filtered result
    if filtered:
        print(Fore.GREEN + f"\nFiltered Results ({len(filtered)} record(s)):")
        filtered_table = [
            [
                req.student_id,
                req.request_type,
                req.priority,
                req.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                req.details
            ] for req in filtered
        ]
        print(tabulate(filtered_table, headers=headers, tablefmt="fancy_grid"))
    else:
        print(Fore.RED + "No matching results found.")

def plot_studentreq_priority():
    if not request_queue:
        print(Fore.GREEN + "No data to plot. The request queue is empty.")
        return

    # Count priorities
    high = sum(1 for req in request_queue if req.priority == 1)
    medium = sum(1 for req in request_queue if req.priority == 2)
    low = sum(1 for req in request_queue if req.priority == 3)

    # Prepare data
    priorities = ['High', 'Medium', 'Low']
    counts = [high, medium, low]

    # Plotting
    plt.figure(figsize=(6, 4))
    plt.bar(priorities, counts)
    plt.title("Student Requests by Priority Level")
    plt.xlabel("Priority")
    plt.ylabel("Number of Requests")
    plt.tight_layout()
    plt.show()

def add_student_request():
    student_id = input("Enter Student ID: ").strip()

    # Validate Student ID (Sequential Search)
    exists = any(str(s["Student ID"]) == student_id for s in students)
    if not exists:
        print(Fore.RED + "Student not found.")
        return

    # Check for duplicate requests
    for req in request_queue:
        if req.student_id == student_id:
            confirm = input("A student request already exists. Add another request? [Y/N]: ").upper()
            if confirm != 'Y':
                print("Request cancelled.")
                return
            break

    # Collect request details
    request_type = input("Enter Request Type (e.g., Appeal, Drop Course): ")
    request_details = input("Enter Request Details: ")

    while True:
        try:
            priority_level = int(input("Enter Priority Level [1 = High, 2 = Medium, 3 = Low]: "))
            if priority_level not in [1, 2, 3]:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid priority (1, 2, or 3).")

    timestamp = datetime.now()

    # Create request and add to priority queue
    new_request = StudentRequest(student_id, request_type, priority_level, request_details, timestamp)
    heapq.heappush(request_queue, new_request)

    # Add to undo stack and clear redo stack
    undo_stack.append(('add', new_request))
    redo_stack.clear()

    print(Fore.GREEN + "Request successfully added.")

    # Save updated queue
    with open("data/student_requests.json", "w") as out_file:
        json.dump([req.to_dict() for req in request_queue], out_file, indent=6)

def process_student_request():
    if request_queue:
        next_request = heapq.heappop(request_queue)
        undo_stack.append(('process', next_request))
        redo_stack.clear()
        print(Fore.YELLOW + "Processing next request:")
        print(next_request)
    else:
        print(Fore.RED + "No requests to process.\n")

def undo_request():
    if not undo_stack:
        print(Fore.YELLOW + "Nothing to undo.")
        return

    action, request = undo_stack.pop()

    if action == 'add':
        try:
            request_queue.remove(request)
            print(Fore.GREEN + "Undo successful: Removed recently added request.")
            redo_stack.append(('add', request))
        except ValueError:
            print(Fore.RED + "Request not found in queue.")
    elif action == 'process':
        heapq.heappush(request_queue, request)
        print(Fore.GREEN + "Undo successful: Restored last processed request.")
        redo_stack.append(('process', request))


def redo_request():
    if not redo_stack:
        print(Fore.YELLOW + "Nothing to redo.")
        return

    action, request = redo_stack.pop()

    if action == 'add':
        heapq.heappush(request_queue, request)
        print(Fore.GREEN + "Redo successful: Re-added request.")
        undo_stack.append(('add', request))
    elif action == 'process':
        try:
            request_queue.remove(request)
            print(Fore.GREEN + "Redo successful: Re-processed request.")
            undo_stack.append(('process', request))
        except ValueError:
            print(Fore.RED + "Request not found for redo.")


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

        print("Sorted by Year Of Study in Descending Order: \n" + tabulate(students, headers="keys",tablefmt="fancy_grid"))

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
        print("Sorted by Num of Registered Courses in Ascending Order: \n" + tabulate(students, headers="keys",tablefmt="fancy_grid"))

    elif sort_course_order == "D":
        for i in range(n - 1):
            max_idx = i  # use max when it's descending
            for j in range(i + 1, n):
                if len(students[j]['Courses']) > len(
                        students[max_idx]['Courses']):  # use len as comparing by no of | > if descending
                    max_idx = j
            students[i], students[max_idx] = students[max_idx], students[i]
        print("Sorted by Num of Registered Courses in Descending Order: \n" + tabulate(students, headers="keys",tablefmt="fancy_grid"))


    else:
        print(Fore.RED + "Invalid Sort Order!")


# Quick Sort on Year of Study with Secondary Sort (on Name)
def quick_sort():
    def recursive_sort(left, right):
        if left >= right:
            return

        pivot_index = left
        pivot = students[pivot_index]
        i = left + 1
        j = right

        while i <= j:
            while i <= right and (students[i]["Year"], students[i]["Student Name"]) < (
            pivot["Year"], pivot["Student Name"]):
                i += 1
            while j > left and (students[j]["Year"], students[j]["Student Name"]) >= (
            pivot["Year"], pivot["Student Name"]):
                j -= 1
            if i < j:
                students[i], students[j] = students[j], students[i]

        if (students[j]["Year"], students[j]["Student Name"]) < (pivot["Year"], pivot["Student Name"]):
            students[left], students[j] = students[j], students[left]
            pivot_index = j

        recursive_sort(left, pivot_index - 1)
        recursive_sort(pivot_index + 1, right)

    recursive_sort(0, len(students) - 1)


    print(Fore.CYAN + "\nSorted by Year of Study with Secondary Sort on Name: " + Style.RESET_ALL)
    print(tabulate(students, headers="keys", tablefmt="fancy_grid"))

# Merge Sort by Num of Registered Course and Student ID
def merge_sort_course_and_id():
    try:
        # Get filter input
        filter_year = input(Fore.CYAN + "Enter Year of Study to filter and sort [1/2/3]: ")
        if filter_year not in ["1", "2", "3"]:
            print(Fore.RED + "Invalid year. Please enter 1, 2 or 3.")
            return
        filter_year = int(filter_year)

        # Filter students of selected year
        filtered = [s for s in students if s["Year"] == filter_year]

        if not filtered:
            print(Fore.YELLOW + f"No students found in Year {filter_year}.")
            return

        # Merge Sort implementation
        def merge_sort(lst):
            if len(lst) <= 1:
                return lst

            mid = len(lst) // 2
            left = merge_sort(lst[:mid])
            right = merge_sort(lst[mid:])
            return merge(left, right)

        def merge(left, right):
            result = []
            i = j = 0

            while i < len(left) and j < len(right):
                # Primary sort: Number of Courses
                # Secondary sort: Student ID
                if len(left[i]["Courses"]) < len(right[j]["Courses"]):
                    result.append(left[i])
                    i += 1
                elif len(left[i]["Courses"]) > len(right[j]["Courses"]):
                    result.append(right[j])
                    j += 1
                else:  # Same number of courses
                    if left[i]["Student ID"] < right[j]["Student ID"]:
                        result.append(left[i])
                        i += 1
                    else:
                        result.append(right[j])
                        j += 1

            result.extend(left[i:])
            result.extend(right[j:])
            return result

        # Sort the filtered list
        sorted_filtered = merge_sort(filtered)

        # Format status
        for s in sorted_filtered:
            s["Status"] = "Full-Time" if s["Status"] else "Part-Time"

        print(Fore.CYAN + f"\nStudents from Year {filter_year} sorted by Num of Courses and Student ID: " + Style.RESET_ALL)
        print(tabulate(sorted_filtered, headers="keys", tablefmt="fancy_grid"))

    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")


# Search for student by id or name
def search():
    search_input = input("Enter Student ID or Student Name: ").strip()
    for student in students:
        if str(student["Student ID"]) == search_input or student["Student Name"].lower() == search_input.lower():
            print(Fore.CYAN + "\nSearched Student Details:\n" + tabulate([student], headers="keys",tablefmt="fancy_grid" + Style.RESET_ALL))
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

def filter_request_priority():
    if not request_queue:
        print(Fore.YELLOW + "No requests to filter.")
        return

    try:
        filter_priority_input = int(input("Enter request priority level to filter [1 = High, 2 = Medium, 3 = Low]: "))
        if filter_priority_input not in [1, 2, 3]:
            print(Fore.RED + "Invalid priority level. Please enter 1, 2, or 3.")
            return
    except ValueError:
        print(Fore.RED + "Invalid level. Please enter a number.")
        return

    # Filter requests by priority
    filtered_requests = [req for req in request_queue if req.priority == filter_priority_input]

    priority_labels = {1: "High", 2: "Medium", 3: "Low"}
    print(Fore.CYAN + f"\nAll {priority_labels.get(filter_priority_input, 'Unknown')} Priority Requests:" + Style.RESET_ALL)

    if filtered_requests:
        headers = ["Student ID", "Request Type", "Priority", "Timestamp", "Details"]
        table = [
            [
                req.student_id,
                req.request_type,
                req.priority,
                req.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                req.details
            ]
            for req in filtered_requests
        ]
        print(tabulate(table, headers=headers, tablefmt="fancy_grid"))
    else:
        print(Fore.YELLOW + "No requests found in the selected priority level.")


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

    logging.info(f"New student added: ID: {student_id}, Name: {student_name}, Email: {email}, Course: {courses}, Year: {year}, Status: {status}")
    print(Fore.GREEN + f"Student {student_name} added successfully. \n")

    out_file = open("data/students_data.json", "w")

    json.dump(students, out_file, indent=6)

    out_file.close()

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

    out_file = open("data/students_data.json", "w")

    json.dump(students, out_file, indent=6)

    out_file.close()

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

            print(Fore.GREEN + f"Student {student['Student Name']}, ID: {student_id} has been chosen.")

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
                        print(Fore.RED + f"Invalid course code: {course}. Each course must have 2 letters followed by 3 digits.")
                        continue

                    if course in student["Courses"]:
                        print(Fore.RED + f"Student {student['Student Name']}, ID: {student_id} is already enrolled in {course}.")
                        continue

                    student["Courses"].append(course)
                    histories[student_id].add_record(course, "enrolled")
                    print(Fore.GREEN + f"Student {student['Student Name']}, ID: {student_id} has been successfully enrolled in {course}.")
                    logging.info(f"Student {student['Student Name']}, ID: {student_id} enrolled in {course}")
                    with open("data/students_data.json", "w") as out_file:
                        json.dump(students, out_file, indent=6)

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

            print(Fore.GREEN + f"Student {student['Student Name']}, ID: {student_id} has been chosen.")

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
                    histories[student_id].add_record(course, "enrolled")
                    print(Fore.GREEN + f"Student {student['Student Name']}, ID: {student_id} has been successfully removed from {course}." )
                    logging.info(f"Student {student['Student Name']}, ID: {student_id} removed from {course}")
                    with open("data/students_data.json", "w") as out_file:
                        json.dump(students, out_file, indent=6)

        except ValueError:
            print(Fore.RED + "Invalid Student ID. Please enter a valid student ID.")


def view_student_history():
    sid_str = input("Enter Student ID to view history: ").strip()
    if not sid_str.isdigit():
        print(Fore.RED + "Invalid Student ID")
        return
    sid = int(sid_str)

    # confirm student exists in the dict-based list
    exists = any(s["Student ID"] == sid for s in students)
    if not exists:
        print(Fore.RED + "Student not found")
        return

    # show the linked-list history (prints "No course history available." if empty)
    histories[sid].display_history()

# Function to display all users
def display_all_users():
    if not user:
        print(Fore.RED + "No students found.")
        return

    print(Fore.CYAN + "\nDisplay Of All User Records:" + Style.RESET_ALL)
    print(tabulate(user, headers="keys", tablefmt="fancy_grid"))


# Change user's "Active" status
def user_activation():
    username = input("Enter username to unlock account for: ")

    user_found = False
    for u in user:
        if u["Username"] == username:
            user_found = True
            activation_input = input("Activate [1] or Deactivate [2] account: ")

            if activation_input not in ["1", "2"]:
                print(Fore.RED + "Invalid option. Please enter 1 or 2.")
                return

            if activation_input == "1":
                if u["Active"]:
                    print(Fore.RED + f"User {username} is already active.")
                else:
                    u["Active"] = True
                    print(Fore.GREEN + f"User {username} has been activated.")
                    logging.warning(f"User {username} has been activated successfully")

            elif activation_input == "2":
                if not u["Active"]:
                    print(Fore.RED + f"User {username} is already deactivated.")
                else:
                    u["Active"] = False
                    print(Fore.GREEN + f"User {username} has been deactivated.")
                    logging.warning(f"User {username} has been deactivated successfully")

            # Save the updated user list
            with open("../users_data.json", "w") as out_file:
                json.dump(user, out_file, indent=6)
            break  # exit loop after update

    if not user_found:
        print(Fore.RED + "User not found")

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

    out_file = open("data/user_data.json", "w")

    json.dump(user, out_file, indent=6)

    out_file.close()


# Generate Pie & Bar chart using matplotlib
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


genai.configure(api_key="AIzaSyCAAPAaUHZj3frMPcaV54_v2PJ2jNyibuQ")
model = genai.GenerativeModel("gemini-1.5-flash")


def chatbot_response(message):
    message = message.lower().strip()

    keyword_mapping = {
        "student": "student", "students": "student", "record": "student", "details": "student",
        "course": "course", "courses": "course", "enroll": "course", "register": "course",
        "remove": "course", "drop": "course",
        "request": "request", "appeal": "request", "priority": "request", "form": "request",
        "search": "search", "find": "search", "sort": "search", "filter": "search",
        "user": "user", "login": "user", "sign": "user", "reset": "user",
        "password": "user", "account": "user"
    }

    if any(word in message for word in ["hello", "hi", "hey"]):
        return "Hey there! Welcome to the Student Course Advisor. How can I help you today?"
    elif "thank you" in message or "thanks" in message:
        return "You're welcome! Let me know if you need help with courses or student requests."
    elif "who are you" in message or "what is your name" in message:
        return "I'm your friendly course advisory assistant!"

    matched_categories = set()
    for keyword, category in keyword_mapping.items():
        if keyword in message:
            matched_categories.add(category)

    if matched_categories:
        response_lines = []
        for cat in matched_categories:
            if cat == "student":
                response_lines.append("You can view and manage student records using the student dashboard.")
            elif cat == "course":
                response_lines.append("To register or remove courses, go to the Course Registration menu.")
            elif cat == "request":
                response_lines.append("You can submit or process student requests in the Request Queue section.")
            elif cat == "search":
                response_lines.append("Use the search and sort options available in the student/course views.")
            elif cat == "user":
                response_lines.append("Account-related actions like login or password reset are in the User Settings.")
        return "\n".join(response_lines)

    return (Fore.YELLOW + "Sorry, I didn't understand that. I can help with course registration, student records, requests, or user accounts."+ Style.RESET_ALL)


def visualize_bst_text(node, level=0):
    if node is not None:
        # Traverse right child first (so it appears on top)
        visualize_bst_text(node.right, level + 1)

        # Print current node with indentation
        print("     " * level + f"{node.student['Student ID']} - {node.student['Student Name']}")

        # Traverse left child
        visualize_bst_text(node.left, level + 1)


def visualize_bst():
    if not student_bst.root:
        print(Fore.RED + "The BST is empty. Nothing to visualize.")
    else:
        print(Fore.CYAN + "\nBinary Search Tree (Student ID):\n" + Style.RESET_ALL)
        visualize_bst_text(student_bst.root)

# Loop to keep chatbot running
def chatbot_loop():
    while True:
        message = input(Fore.CYAN + 'Ask Student Course Advisor Anything [Type "exit" to quit]: ' + Style.RESET_ALL)
        if message.lower().strip() == "exit":
            print(Fore.GREEN + "Goodbye!" + Style.RESET_ALL)
            break

        response = chatbot_response(message)
        print(Fore.GREEN + response + Style.RESET_ALL)

if __name__ == "__main__":
    load_data()
    rebuild_bst()
    login()
