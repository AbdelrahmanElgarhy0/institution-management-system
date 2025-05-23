import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def TeacherDashboard(container, show_frame):
    # Define color scheme
    global frames
    bg_color = "#f0f8ff"  # Light blue background
    header_color = "#4682b4"  # Steel blue for headers
    button_color = "#6ca6cd"  # Sky blue for buttons
    text_color = "white"

    teacher_dashboard = tk.Frame(container, bg=bg_color)
    teacher_dashboard.grid(row=0, column=0, sticky="nsew")

    # Header Label
    tk.Label(
        teacher_dashboard, text="Teacher Dashboard", font=("Arial", 24, "bold"),
        bg=header_color, fg=text_color, pady=10
    ).pack(fill="x")

    # Notebook for Tabs
    notebook = ttk.Notebook(teacher_dashboard)
    notebook.pack(fill="both", expand=True, padx=20, pady=20)

    # Grades Management Tab
    grades_tab = tk.Frame(notebook, bg=bg_color)
    notebook.add(grades_tab, text="Grades Management")

    tk.Label(
        grades_tab, text="Grades Management", font=("Arial", 16, "bold"), bg=bg_color
    ).pack(pady=10)

    tk.Label(grades_tab, text="Student:", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    student_dropdown = ttk.Combobox(grades_tab, state="readonly", width=40)
    student_dropdown.pack(padx=20, pady=5)

    tk.Label(grades_tab, text="Course:", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    course_dropdown = ttk.Combobox(grades_tab, state="readonly", width=40)
    course_dropdown.pack(padx=20, pady=5)

    tk.Label(grades_tab, text="Grade:", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    grade_entry = tk.Entry(grades_tab, font=("Arial", 12), width=40)
    grade_entry.pack(padx=20, pady=5)

    tk.Button(
        grades_tab, text="Upload Grade", font=("Arial", 12), bg=button_color, fg=text_color,
        command=lambda: upload_grade(student_dropdown.get(), course_dropdown.get(), grade_entry.get())
    ).pack(pady=10)

    # Attendance Management Tab
    attendance_tab = tk.Frame(notebook, bg=bg_color)
    notebook.add(attendance_tab, text="Attendance Management")

    tk.Label(
        attendance_tab, text="Attendance Management", font=("Arial", 16, "bold"), bg=bg_color
    ).pack(pady=10)

    tk.Label(attendance_tab, text="Date (YYYY-MM-DD):", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    attendance_date_entry = tk.Entry(attendance_tab, font=("Arial", 12), width=40)
    attendance_date_entry.pack(padx=20, pady=5)

    tk.Label(attendance_tab, text="Attendance Status:", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    attendance_status_var = tk.StringVar()
    tk.Radiobutton(attendance_tab, text="Present", variable=attendance_status_var, value="Present", bg=bg_color).pack(anchor="w", padx=20)
    tk.Radiobutton(attendance_tab, text="Absent", variable=attendance_status_var, value="Absent", bg=bg_color).pack(anchor="w", padx=20)

    tk.Button(
        attendance_tab, text="Mark Attendance", font=("Arial", 12), bg=button_color, fg=text_color,
        command=lambda: mark_attendance(student_dropdown.get(), course_dropdown.get(), attendance_date_entry.get(), attendance_status_var.get())
    ).pack(pady=10)

    # Assignments Management Tab
    assignments_tab = tk.Frame(notebook, bg=bg_color)
    notebook.add(assignments_tab, text="Assignments Management")

    tk.Label(
        assignments_tab, text="Assignments Management", font=("Arial", 16, "bold"), bg=bg_color
    ).pack(pady=10)

    tk.Label(assignments_tab, text="Assignment Title:", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    assignment_title_entry = tk.Entry(assignments_tab, font=("Arial", 12), width=40)
    assignment_title_entry.pack(padx=20, pady=5)

    tk.Label(assignments_tab, text="Assignment Description:", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    assignment_description_entry = tk.Text(assignments_tab, font=("Arial", 12), height=5, width=40)
    assignment_description_entry.pack(padx=20, pady=5)

    tk.Label(assignments_tab, text="Due Date (YYYY-MM-DD):", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    due_date_entry = tk.Entry(assignments_tab, font=("Arial", 12), width=40)
    due_date_entry.pack(padx=20, pady=5)

    tk.Button(
        assignments_tab, text="Assign Assignment", font=("Arial", 12), bg=button_color, fg=text_color,
        command=lambda: assign_assignment(assignment_title_entry.get(), assignment_description_entry.get("1.0", tk.END).strip(), due_date_entry.get(), course_dropdown.get())
    ).pack(pady=10)

        # Quiz Management Tab
    quiz_tab = tk.Frame(notebook, bg=bg_color)
    notebook.add(quiz_tab, text="Quiz Management")

    # Quiz Creation Section
    tk.Label(quiz_tab, text="Quiz Title:", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    quiz_title_entry = tk.Entry(quiz_tab, font=("Arial", 12), width=40)
    quiz_title_entry.pack(padx=20, pady=5)

    tk.Label(quiz_tab, text="Course:", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    quiz_course_dropdown = ttk.Combobox(quiz_tab, state="readonly", width=40)
    quiz_course_dropdown.pack(padx=20, pady=5)

    tk.Label(quiz_tab, text="Deadline (YYYY-MM-DD):", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    quiz_deadline_entry = tk.Entry(quiz_tab, font=("Arial", 12), width=40)
    quiz_deadline_entry.pack(padx=20, pady=5)

    def create_quiz():
        title = quiz_title_entry.get()
        course = quiz_course_dropdown.get()
        deadline = quiz_deadline_entry.get()
        if not title or not course or not deadline:
            messagebox.showerror("Error", "All fields are required!")
            return
        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO quizzes (quiz_title, course_name, deadline) VALUES (?, ?, ?)",
                (title, course, deadline)
            )
            conn.commit()
            messagebox.showinfo("Success", "Quiz created successfully!")
            quiz_title_entry.delete(0, tk.END)
            quiz_deadline_entry.delete(0, tk.END)
            load_quiz_dropdowns()  # Refresh quiz dropdowns
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    tk.Button(quiz_tab, text="Create Quiz", font=("Arial", 12), bg=button_color, fg=text_color, command=create_quiz).pack(pady=10)

    # Quiz Question Management Section
    tk.Label(quiz_tab, text="Add Questions to a Quiz", font=("Arial", 14), bg=bg_color).pack(anchor="w", padx=20, pady=5)

    quiz_dropdown = ttk.Combobox(quiz_tab, state="readonly", width=40)
    quiz_dropdown.pack(padx=20, pady=5)

    tk.Label(quiz_tab, text="Question Text:", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    question_entry = tk.Entry(quiz_tab, font=("Arial", 12), width=40)
    question_entry.pack(padx=20, pady=5)

    tk.Label(quiz_tab, text="Option A:", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    option_a_entry = tk.Entry(quiz_tab, font=("Arial", 12), width=40)
    option_a_entry.pack(padx=20, pady=5)

    tk.Label(quiz_tab, text="Option B:", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    option_b_entry = tk.Entry(quiz_tab, font=("Arial", 12), width=40)
    option_b_entry.pack(padx=20, pady=5)

    tk.Label(quiz_tab, text="Option C:", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    option_c_entry = tk.Entry(quiz_tab, font=("Arial", 12), width=40)
    option_c_entry.pack(padx=20, pady=5)

    tk.Label(quiz_tab, text="Option D:", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    option_d_entry = tk.Entry(quiz_tab, font=("Arial", 12), width=40)
    option_d_entry.pack(padx=20, pady=5)

    tk.Label(quiz_tab, text="Correct Option (A/B/C/D):", font=("Arial", 12), bg=bg_color).pack(anchor="w", padx=20, pady=5)
    correct_option_entry = tk.Entry(quiz_tab, font=("Arial", 12), width=40)
    correct_option_entry.pack(padx=20, pady=5)

    def add_question():
        quiz = quiz_dropdown.get()
        question = question_entry.get()
        option_a = option_a_entry.get()
        option_b = option_b_entry.get()
        option_c = option_c_entry.get()
        option_d = option_d_entry.get()
        correct_option = correct_option_entry.get()
        if not quiz or not question or not option_a or not option_b or not option_c or not option_d or not correct_option:
            messagebox.showerror("Error", "All fields are required!")
            return
        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO quiz_questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option)
                   VALUES ((SELECT id FROM quizzes WHERE quiz_title = ?), ?, ?, ?, ?, ?, ?)""",
                (quiz, question, option_a, option_b, option_c, option_d, correct_option)
            )
            conn.commit()
            messagebox.showinfo("Success", "Question added successfully!")
            question_entry.delete(0, tk.END)
            option_a_entry.delete(0, tk.END)
            option_b_entry.delete(0, tk.END)
            option_c_entry.delete(0, tk.END)
            option_d_entry.delete(0, tk.END)
            correct_option_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    tk.Button(quiz_tab, text="Add Question", font=("Arial", 12), bg=button_color, fg=text_color, command=add_question).pack(pady=10)

    # Helper Function to Load Dropdowns
    def load_quiz_dropdowns():
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT course_name FROM courses")
        courses = cursor.fetchall()
        quiz_course_dropdown['values'] = [course[0] for course in courses]
        cursor.execute("SELECT quiz_title FROM quizzes")
        quizzes = cursor.fetchall()
        quiz_dropdown['values'] = [quiz[0] for quiz in quizzes]
        conn.close()

    load_quiz_dropdowns()


    # Functions
    def refresh_dropdowns():
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE role = 'Student'")
        students = cursor.fetchall()
        cursor.execute("SELECT course_name FROM courses")
        courses = cursor.fetchall()
        conn.close()

        student_dropdown['values'] = [student[0] for student in students]
        course_dropdown['values'] = [course[0] for course in courses]

    def upload_grade(student, course, grade):
        if not student or not course or not grade:
            messagebox.showerror("Error", "All fields are required for uploading a grade!")
            return
        try:
            grade = float(grade)
        except ValueError:
            messagebox.showerror("Error", "Grade must be a number!")
            return
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO grades (student_username, course_name, grade) VALUES (?, ?, ?)",
                (student, course, grade)
            )
            conn.commit()
            messagebox.showinfo("Success", f"Grade uploaded for {student} in {course}")
            
            # Notify StudentDashboard to refresh data
            if "StudentDashboard" in frames:
                frames["StudentDashboard"].load_student_data(student)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def mark_attendance(student, course, date, status):
        if not student or not course or not date or not status:
            messagebox.showerror("Error", "All fields are required for marking attendance!")
            return
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO attendance (student_username, course_name, date, attendance_status) VALUES (?, ?, ?, ?)",
                (student, course, date, status)
            )
            conn.commit()
            messagebox.showinfo("Success", f"Attendance marked for {student} in {course} on {date}")
            
            # Notify StudentDashboard to refresh data
            if "StudentDashboard" in frames:
                frames["StudentDashboard"].load_student_data(student)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def assign_assignment(title, description, due_date, course):
        if not title or not description or not due_date or not course:
            messagebox.showerror("Error", "All fields are required to assign an assignment!")
            return
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO assignments (assignment_title, assignment_description, due_date, course_name) VALUES (?, ?, ?, ?)",
                (title, description, due_date, course)
            )
            conn.commit()
            messagebox.showinfo("Success", "Assignment created successfully!")
            
            # Notify StudentDashboard to refresh data
            if "StudentDashboard" in frames:
                frames["StudentDashboard"].load_student_data(None)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()
            

    refresh_dropdowns()

    # Back to Main Menu Button
    tk.Button(
        teacher_dashboard, text="Back to Main Menu", font=("Arial", 12), bg=button_color, fg=text_color,
        command=lambda: show_frame("MainMenu")
    ).pack(pady=10)