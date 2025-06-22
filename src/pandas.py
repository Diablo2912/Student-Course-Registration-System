import pandas as pd

from main import *
from colorama import Fore, Style, init

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