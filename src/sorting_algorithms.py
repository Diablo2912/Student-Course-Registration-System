from main import students,tabulate
from colorama import Fore, Style, init

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

# def quick_sort():

# Merge Sort by Num of Registered Course and Student ID

# def merge_sort():