import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def StudentDashboard(container, show_frame, get_current_user):
    # Define color scheme
    bg_color = "#f0f8ff"
    header_color = "#4682b4"
    button_color = "#6ca6cd"
    text_color = "white"

    student_dashboard = tk.Frame(container, bg=bg_color)
    student_dashboard.grid(row=0, column=0, sticky="nsew")

    # Header Label
    tk.Label(
        student_dashboard, text="Student Dashboard", font=("Arial", 24, "bold"),
        bg=header_color, fg=text_color, pady=10
    ).pack(fill="x")

    # Notebook for Tabs
    notebook = ttk.Notebook(student_dashboard)
    notebook.pack(fill="both", expand=True, padx=20, pady=20)

    # Assignments Tab
    assignments_tab = tk.Frame(notebook, bg=bg_color)
    notebook.add(assignments_tab, text="Assignments")
    tk.Label(assignments_tab, text="Your Assignments", font=("Arial", 16, "bold"), bg=bg_color).pack(pady=10)
    assignments_list = ttk.Treeview(assignments_tab, columns=("Title", "Description", "Due Date"), show="headings", height=10)
    assignments_list.heading("Title", text="Title")
    assignments_list.heading("Description", text="Description")
    assignments_list.heading("Due Date", text="Due Date")
    assignments_list.pack(fill="both", expand=True, padx=10, pady=10)

    # Attendance Tab
    attendance_tab = tk.Frame(notebook, bg=bg_color)
    notebook.add(attendance_tab, text="Attendance")
    tk.Label(attendance_tab, text="Your Attendance", font=("Arial", 16, "bold"), bg=bg_color).pack(pady=10)
    attendance_list = ttk.Treeview(attendance_tab, columns=("Date", "Course", "Status"), show="headings", height=10)
    attendance_list.heading("Date", text="Date")
    attendance_list.heading("Course", text="Course")
    attendance_list.heading("Status", text="Status")
    attendance_list.pack(fill="both", expand=True, padx=10, pady=10)

    # Grades Tab
    grades_tab = tk.Frame(notebook, bg=bg_color)
    notebook.add(grades_tab, text="Grades")
    tk.Label(grades_tab, text="Your Grades", font=("Arial", 16, "bold"), bg=bg_color).pack(pady=10)
    grades_list = ttk.Treeview(grades_tab, columns=("Course", "Grade"), show="headings", height=10)
    grades_list.heading("Course", text="Course")
    grades_list.heading("Grade", text="Grade")
    grades_list.pack(fill="both", expand=True, padx=10, pady=10)

    # Quizzes Tab
    quizzes_tab = tk.Frame(notebook, bg=bg_color)
    notebook.add(quizzes_tab, text="Quizzes")

    tk.Label(
        quizzes_tab, text="Available Quizzes", font=("Arial", 16, "bold"), bg=bg_color
    ).pack(pady=10)

    quizzes_tree = ttk.Treeview(quizzes_tab, columns=("Quiz", "Course", "Deadline"), show="headings")
    quizzes_tree.heading("Quiz", text="Quiz")
    quizzes_tree.heading("Course", text="Course")
    quizzes_tree.heading("Deadline", text="Deadline")
    quizzes_tree.pack(fill="both", expand=True, padx=10, pady=10)

    tk.Button(
        quizzes_tab, text="Attempt Selected Quiz", font=("Arial", 12), bg=button_color, fg=text_color,
        command=lambda: attempt_quiz(quizzes_tree.item(quizzes_tree.focus(), "values"))
    ).pack(pady=10)

    def load_quizzes():
        """Load quizzes available for the student into the TreeView."""
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT q.quiz_title, q.course_name, q.deadline 
            FROM quizzes q
            JOIN courses c ON q.course_name = c.course_name
            WHERE q.deadline >= DATE('now')
        """)
        quizzes = cursor.fetchall()
        conn.close()

        # Clear existing quizzes
        for row in quizzes_tree.get_children():
            quizzes_tree.delete(row)

        # Insert quizzes into the TreeView
        for quiz in quizzes:
            quizzes_tree.insert("", "end", values=quiz)

    def attempt_quiz(selected_quiz):
        """Display the quiz window for the student to attempt the quiz."""
        if not selected_quiz:
            messagebox.showerror("Error", "Please select a quiz to attempt!")
            return

        quiz_title, course_name, _ = selected_quiz
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT qq.id, qq.question_text, qq.option_a, qq.option_b, qq.option_c, qq.option_d
            FROM quiz_questions qq
            JOIN quizzes q ON qq.quiz_id = q.id
            WHERE q.quiz_title = ?
        """, (quiz_title,))
        questions = cursor.fetchall()
        conn.close()

        # Create Quiz Data
        quiz_data = {
            "title": quiz_title,
            "course": course_name,
            "questions": questions,
            "answers": {}  # To store student answers
        }

        show_quiz_window(quiz_data)

    def show_quiz_window(quiz_data):
        """Display the quiz question-by-question for the student."""
        quiz_window = tk.Toplevel(bg=bg_color)
        quiz_window.title(f"Attempt Quiz: {quiz_data['title']}")
        current_question_index = [0]  # Mutable index for tracking questions

        def show_question(index):
            for widget in quiz_window.winfo_children():
                widget.destroy()

            if index >= len(quiz_data["questions"]):
                submit_quiz()
                return

            question = quiz_data["questions"][index]
            question_id, question_text, option_a, option_b, option_c, option_d = question

            tk.Label(
                quiz_window, text=f"Question {index + 1}: {question_text}", font=("Arial", 14), bg=bg_color
            ).pack(pady=10)

            answer_var = tk.StringVar(value=quiz_data["answers"].get(question_id, ""))

            for option, label in zip([option_a, option_b, option_c, option_d], ["A", "B", "C", "D"]):
                tk.Radiobutton(
                    quiz_window, text=f"{label}: {option}", variable=answer_var, value=label, bg=bg_color
                ).pack(anchor="w", padx=20, pady=5)

            def next_question():
                quiz_data["answers"][question_id] = answer_var.get()
                current_question_index[0] += 1
                show_question(current_question_index[0])

            tk.Button(
                quiz_window, text="Next", font=("Arial", 12), bg=button_color, fg=text_color, command=next_question
            ).pack(pady=10)

        def submit_quiz():
            score = 0
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()

            for question_id, answer in quiz_data["answers"].items():
                cursor.execute("""
                    SELECT correct_option FROM quiz_questions WHERE id = ?
                """, (question_id,))
                correct_option = cursor.fetchone()[0]
                if answer == correct_option:
                    score += 1

            cursor.execute("""
                INSERT INTO quiz_submissions (quiz_id, student_username, score, submission_date)
                VALUES (
                    (SELECT id FROM quizzes WHERE quiz_title = ?),
                    ?, ?, DATE('now')
                )
            """, (quiz_data["title"], get_current_user(), score))
            conn.commit()
            conn.close()

            messagebox.showinfo("Quiz Completed", f"You scored {score} out of {len(quiz_data['questions'])}")
            quiz_window.destroy()

        show_question(current_question_index[0])

    # Load quizzes when the student dashboard starts
    load_quizzes()

    # Functions for Assignments, Attendance, and Grades
    def load_assignments():
        current_user = get_current_user()
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT assignment_title, assignment_description, due_date
                FROM assignments
                WHERE course_name IN (
                    SELECT course_name
                    FROM grades
                    WHERE student_username = ?
                )
            """, (current_user,))
            rows = cursor.fetchall()
            for row in assignments_list.get_children():
                assignments_list.delete(row)
            for row in rows:
                assignments_list.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def load_attendance():
        current_user = get_current_user()
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT date, course_name, attendance_status
                FROM attendance
                WHERE student_username = ?
            """, (current_user,))
            rows = cursor.fetchall()
            for row in attendance_list.get_children():
                attendance_list.delete(row)
            for row in rows:
                attendance_list.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def load_grades():
        current_user = get_current_user()
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT course_name, grade
                FROM grades
                WHERE student_username = ?
            """, (current_user,))
            rows = cursor.fetchall()
            for row in grades_list.get_children():
                grades_list.delete(row)
            for row in rows:
                grades_list.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    # Add Refresh Buttons
    tk.Button(assignments_tab, text="Refresh Assignments", font=("Arial", 12), bg=button_color, fg=text_color, command=load_assignments).pack(pady=10)
    tk.Button(attendance_tab, text="Refresh Attendance", font=("Arial", 12), bg=button_color, fg=text_color, command=load_attendance).pack(pady=10)
    tk.Button(grades_tab, text="Refresh Grades", font=("Arial", 12), bg=button_color, fg=text_color, command=load_grades).pack(pady=10)

    # Back to Main Menu Button
    tk.Button(
        student_dashboard, text="Back to Main Menu", font=("Arial", 12), bg=button_color, fg=text_color,
        command=lambda: show_frame("MainMenu")
    ).pack(pady=10)

    return student_dashboard
