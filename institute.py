import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3

# Database setup
def setup_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
# Database setup for assignments and submissions
def setup_assignment_tables():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Create courses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL UNIQUE
        )
    """)

    # Create grades table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_username TEXT NOT NULL,
            course_name TEXT NOT NULL,
            grade TEXT,
            FOREIGN KEY (student_username) REFERENCES users(username),
            FOREIGN KEY (course_name) REFERENCES courses(course_name)
        )
    """)

    # Insert default users
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin', 'Admin')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('student', 'student', 'Student')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('teacher', 'teacher', 'Teacher')")
    conn.commit()
    conn.close()

# Add Attendance Table to Database
def setup_attendance_table():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_username TEXT NOT NULL,
            course_name TEXT NOT NULL,
            date TEXT NOT NULL,
            attendance_status TEXT NOT NULL,
            FOREIGN KEY (student_username) REFERENCES users(username),
            FOREIGN KEY (course_name) REFERENCES courses(course_name)
        )
    """)
    conn.commit()
    conn.close()

setup_database()
setup_attendance_table()

# Function to validate login credentials
def login(user_type):
    username = username_entry.get()
    password = password_entry.get()
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = ?", (username, password, user_type))
    user = cursor.fetchone()
    conn.close()

    if user:
        messagebox.showinfo("Login Successful", f"Welcome, {user_type}")
        if user_type == "Admin":
            show_frame(admin_dashboard)
        elif user_type == "Student":
            load_student_dashboard(username)
            show_frame(student_dashboard)
        elif user_type == "Teacher":
            load_teacher_dashboard()
            show_frame(teacher_dashboard)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

# Function to add a course
def add_course():
    course_name = course_name_entry.get()
    if not course_name:
        messagebox.showerror("Error", "Course name cannot be empty!")
        return

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO courses (course_name) VALUES (?)", (course_name,))
        conn.commit()
        messagebox.showinfo("Success", f"Course '{course_name}' added successfully!")
        course_name_entry.delete(0, tk.END)
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Course already exists!")
    conn.close()

# Function to load the student dashboard
def load_student_dashboard(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT course_name, grade FROM grades WHERE student_username = ?", (username,))
    results = cursor.fetchall()
    conn.close()

    # Clear the Treeview
    for row in student_tree.get_children():
        student_tree.delete(row)

    # Populate the Treeview with student grades
    for course, grade in results:
        student_tree.insert("", "end", values=(course, grade))

    # Load attendance records
    load_attendance(username)

# Function to load the teacher dashboard
def load_teacher_dashboard():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE role = 'Student'")
    students = cursor.fetchall()
    cursor.execute("SELECT course_name FROM courses")
    courses = cursor.fetchall()
    conn.close()

    # Populate dropdowns with students and courses
    student_dropdown['values'] = [student[0] for student in students]
    course_dropdown_teacher['values'] = [course[0] for course in courses]

# Function for teacher to upload a grade
def upload_grade():
    student = student_dropdown.get()
    course = course_dropdown_teacher.get()
    grade = grade_entry.get()

    if not student or not course or not grade:
        messagebox.showerror("Error", "All fields are required!")
        return

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO grades (student_username, course_name, grade) VALUES (?, ?, ?)",
                   (student, course, grade))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Grade uploaded for {student} in {course}")

# Function to mark attendance
def mark_attendance():
    student = student_dropdown.get()
    course = course_dropdown_teacher.get()
    date = attendance_date_entry.get()
    status = attendance_status_var.get()

    if not student or not course or not date or not status:
        messagebox.showerror("Error", "All fields are required!")
        return

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO attendance (student_username, course_name, date, attendance_status) VALUES (?, ?, ?, ?)",
                       (student, course, date, status))
        conn.commit()
        messagebox.showinfo("Success", f"Attendance marked for {student} in {course}")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        conn.close()

# Function to load attendance in student dashboard
def load_attendance(student_username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT course_name, date, attendance_status FROM attendance WHERE student_username = ?", (student_username,))
    attendance_records = cursor.fetchall()
    conn.close()

    # Clear the Treeview
    for row in attendance_tree.get_children():
        attendance_tree.delete(row)

    # Populate the Treeview with attendance records
    for record in attendance_records:
        attendance_tree.insert("", "end", values=record)

# GUI Setup
root = tk.Tk()
root.title("Smart Educational Institute Administration System")
root.geometry("800x600")

container = tk.Frame(root)
container.pack(fill="both", expand=True)
container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

# Define frames
main_menu = tk.Frame(container)
login_page = tk.Frame(container)
admin_dashboard = tk.Frame(container)
student_dashboard = tk.Frame(container)
teacher_dashboard = tk.Frame(container)
add_course_page = tk.Frame(container)

# Add frames to container
for frame in (main_menu, login_page, admin_dashboard, student_dashboard, teacher_dashboard, add_course_page):
    frame.grid(row=0, column=0, sticky="nsew")

# Main Menu
tk.Label(main_menu, text="Welcome to the Administration System", font=("Arial", 20)).pack(pady=20)
tk.Button(main_menu, text="Admin", font=("Arial", 15), command=lambda: (show_frame(login_page), set_login_title("Admin"))).pack(pady=10)
tk.Button(main_menu, text="Student", font=("Arial", 15), command=lambda: (show_frame(login_page), set_login_title("Student"))).pack(pady=10)
tk.Button(main_menu, text="Teacher", font=("Arial", 15), command=lambda: (show_frame(login_page), set_login_title("Teacher"))).pack(pady=10)

# Login Page
login_title = tk.StringVar()
login_title.set("Login")

tk.Label(login_page, textvariable=login_title, font=("Arial", 20)).pack(pady=20)
tk.Label(login_page, text="Username:", font=("Arial", 14)).pack(pady=5)
username_entry = tk.Entry(login_page, font=("Arial", 14))
username_entry.pack(pady=5)
tk.Label(login_page, text="Password:", font=("Arial", 14)).pack(pady=5)
password_entry = tk.Entry(login_page, font=("Arial", 14), show="*")
password_entry.pack(pady=5)
tk.Button(login_page, text="Login", font=("Arial", 14), command=lambda: login(login_title.get())).pack(pady=10)
tk.Button(login_page, text="Back to Main Menu", font=("Arial", 12), command=lambda: show_frame(main_menu)).pack(pady=10)

# Admin Dashboard
tk.Label(admin_dashboard, text="Admin Dashboard", font=("Arial", 20)).pack(pady=20)
tk.Button(admin_dashboard, text="Add Course", font=("Arial", 15), command=lambda: show_frame(add_course_page)).pack(pady=10)
tk.Button(admin_dashboard, text="Back to Main Menu", font=("Arial", 12), command=lambda: show_frame(main_menu)).pack(pady=10)

# Add Course Page
tk.Label(add_course_page, text="Add New Course", font=("Arial", 20)).pack(pady=20)
tk.Label(add_course_page, text="Course Name:", font=("Arial", 14)).pack(pady=5)
course_name_entry = tk.Entry(add_course_page, font=("Arial", 14))
course_name_entry.pack(pady=5)
tk.Button(add_course_page, text="Add Course", font=("Arial", 14), command=add_course).pack(pady=10)
tk.Button(add_course_page, text="Back to Admin Dashboard", font=("Arial", 12), command=lambda: show_frame(admin_dashboard)).pack(pady=10)

# Student Dashboard
tk.Label(student_dashboard, text="Student Dashboard", font=("Arial", 20)).pack(pady=20)
student_tree = ttk.Treeview(student_dashboard, columns=("Course", "Grade"), show="headings")
student_tree.heading("Course", text="Course")
student_tree.heading("Grade", text="Grade")
student_tree.pack(fill="both", expand=True, padx=20, pady=20)

# Add Attendance Table to Student Dashboard
tk.Label(student_dashboard, text="Attendance Records:", font=("Arial", 14)).pack(pady=10)
attendance_tree = ttk.Treeview(student_dashboard, columns=("Course", "Date", "Status"), show="headings")
attendance_tree.heading("Course", text="Course")
attendance_tree.heading("Date", text="Date")
attendance_tree.heading("Status", text="Status")
attendance_tree.pack(fill="both", expand=True, padx=20, pady=10)

tk.Button(student_dashboard, text="Back to Main Menu", font=("Arial", 12), command=lambda: show_frame(main_menu)).pack(pady=10)

# Teacher Dashboard
tk.Label(teacher_dashboard, text="Teacher Dashboard", font=("Arial", 20)).pack(pady=20)
tk.Label(teacher_dashboard, text="Student:", font=("Arial", 14)).pack(pady=5)
student_dropdown = ttk.Combobox(teacher_dashboard, state="readonly")
student_dropdown.pack(pady=5)
tk.Label(teacher_dashboard, text="Course:", font=("Arial", 14)).pack(pady=5)
course_dropdown_teacher = ttk.Combobox(teacher_dashboard, state="readonly")
course_dropdown_teacher.pack(pady=5)
tk.Label(teacher_dashboard, text="Date (YYYY-MM-DD):", font=("Arial", 14)).pack(pady=5)
attendance_date_entry = tk.Entry(teacher_dashboard, font=("Arial", 14))
attendance_date_entry.pack(pady=5)
tk.Label(teacher_dashboard, text="Status:", font=("Arial", 14)).pack(pady=5)
attendance_status_var = tk.StringVar()
status_frame = tk.Frame(teacher_dashboard)
tk.Radiobutton(status_frame, text="Present", variable=attendance_status_var, value="Present").pack(side=tk.LEFT, padx=5)
tk.Radiobutton(status_frame, text="Absent", variable=attendance_status_var, value="Absent").pack(side=tk.LEFT, padx=5)
status_frame.pack(pady=5)
tk.Button(teacher_dashboard, text="Mark Attendance", font=("Arial", 14), command=mark_attendance).pack(pady=10)

tk.Label(teacher_dashboard, text="Grade Entry:", font=("Arial", 14)).pack(pady=5)
grade_entry = tk.Entry(teacher_dashboard, font=("Arial", 14))
grade_entry.pack(pady=5)
tk.Button(teacher_dashboard, text="Upload Grade", font=("Arial", 14), command=upload_grade).pack(pady=10)

tk.Button(teacher_dashboard, text="Back to Main Menu", font=("Arial", 12), command=lambda: show_frame(main_menu)).pack(pady=10)

# Helper Functions
def show_frame(frame):
    frame.tkraise()

def set_login_title(user_type):
    login_title.set(user_type)

# Start the Tkinter event loop
show_frame(main_menu)
root.mainloop()
