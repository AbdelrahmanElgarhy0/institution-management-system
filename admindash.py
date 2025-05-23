import os
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import time

# Track system start time for uptime calculation
start_time = time.time()

# Centralized styles for buttons
button_style = {"font": ("Arial", 14), "bg": "#6ca6cd", "fg": "white", "activebackground": "#4682b4", "activeforeground": "white"}

def execute_query(query, parameters=None):
    """Execute a database query and handle errors."""
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    finally:
        conn.close()

def AdminDashboard(container, show_frame):
    """Admin Dashboard View."""
    admin_dashboard = tk.Frame(container, bg="#f0f8ff")
    admin_dashboard.grid(row=0, column=0, sticky="nsew")

    tk.Label(admin_dashboard, text="Admin Dashboard", font=("Arial", 20, "bold"), bg="#4682b4", fg="white").pack(pady=20, fill="x")

    # Add Course Section
    tk.Label(admin_dashboard, text="Add New Course", font=("Arial", 14), bg="#f0f8ff").pack(pady=10)
    course_name_entry = tk.Entry(admin_dashboard, font=("Arial", 14))
    course_name_entry.pack(pady=5)

    def add_course():
        """Add a new course to the database."""
        course_name = course_name_entry.get().strip()
        if not course_name:
            messagebox.showerror("Error", "Course name cannot be empty!")
            return

        query = "INSERT INTO courses (course_name) VALUES (?)"
        try:
            execute_query(query, (course_name,))
            messagebox.showinfo("Success", f"Course '{course_name}' added successfully!")
            course_name_entry.delete(0, tk.END)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Course already exists!")

    tk.Button(admin_dashboard, text="Add Course", **button_style, command=add_course).pack(pady=10)

    # Navigation Buttons
    tk.Button(admin_dashboard, text="IT Staff", **button_style, command=lambda: show_frame("ITDashboard")).pack(pady=10)
    tk.Button(admin_dashboard, text="Back to Main Menu", **button_style, command=lambda: show_frame("MainMenu")).pack(pady=10)

    return admin_dashboard

def SystemMonitoringPage(container, show_frame):
    """System Monitoring Page."""
    system_monitoring = tk.Frame(container, bg="#f0f8ff")
    system_monitoring.grid(row=0, column=0, sticky="nsew")

    tk.Label(system_monitoring, text="System Monitoring", font=("Arial", 20, "bold"), bg="#4682b4", fg="white").pack(pady=20, fill="x")

    stats_label = tk.Label(system_monitoring, text="Loading system stats...", font=("Arial", 14), bg="#f0f8ff", wraplength=600, anchor="w")
    stats_label.pack(pady=10, fill="x", padx=20)

    def fetch_system_stats():
        """Fetch and display system stats."""
        try:
            if not os.path.exists("users.db"):
                stats_label.config(text="Error: Database file 'users.db' not found!")
                return

            db_size = os.path.getsize("users.db") / (1024 * 1024)  # Size in MB
            uptime = time.time() - start_time
            hours, rem = divmod(int(uptime), 3600)
            minutes, seconds = divmod(rem, 60)
            stats_label.config(text=f"Database Size: {db_size:.2f} MB\nSystem Uptime: {hours}h {minutes}m {seconds}s")
        except Exception as e:
            stats_label.config(text=f"Error fetching stats: {e}")

    tk.Button(system_monitoring, text="Refresh System Stats", **button_style, command=fetch_system_stats).pack(pady=10)
    tk.Button(system_monitoring, text="Back to IT Dashboard", **button_style, command=lambda: show_frame("ITDashboard")).pack(pady=10)

    fetch_system_stats()
    return system_monitoring

def ITDashboard(container, show_frame, user_list):
    """IT Dashboard View."""
    it_dashboard = tk.Frame(container, bg="#f0f8ff")
    it_dashboard.grid(row=0, column=0, sticky="nsew")

    tk.Label(it_dashboard, text="IT Staff Dashboard", font=("Arial", 20, "bold"), bg="#4682b4", fg="white").pack(pady=20, fill="x")

    # User Management Section
    tk.Label(it_dashboard, text="User Management", font=("Arial", 16), bg="#f0f8ff").pack(pady=10)

    user_tree = ttk.Treeview(it_dashboard, columns=("Username", "Role", "Status"), show="headings", height=10)
    user_tree.heading("Username", text="Username")
    user_tree.heading("Role", text="Role")
    user_tree.heading("Status", text="Status")
    user_tree.pack(pady=10)

    def fetch_users():
        """Fetch users from the database."""
        user_tree.delete(*user_tree.get_children())  # Clear the tree before inserting new rows
        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("SELECT username, role, status FROM users")
            for user in cursor.fetchall():
                user_tree.insert("", "end", values=user)
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def add_user():
        """Open a dialog to add a new user."""
        def save_user():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            role = role_entry.get().strip()

            if not username or not password or not role:
                messagebox.showerror("Error", "All fields are required!")
                return

            try:
                # Add user to the linked list
                user_list.add_user(username, password, role)

                # Add user to the database
                conn = sqlite3.connect("users.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, role, status) VALUES (?, ?, ?, 'Active')",
                    (username, password, role),
                )
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", f"User '{username}' added successfully!")
                fetch_users()  # Refresh the user list
                add_user_window.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "User already exists!")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}")

        add_user_window = tk.Toplevel(it_dashboard, bg="#f0f8ff")
        add_user_window.title("Add User")
        tk.Label(add_user_window, text="Username:", bg="#f0f8ff").grid(row=0, column=0, padx=10, pady=5)
        username_entry = tk.Entry(add_user_window)
        username_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Label(add_user_window, text="Password:", bg="#f0f8ff").grid(row=1, column=0, padx=10, pady=5)
        password_entry = tk.Entry(add_user_window, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=5)
        tk.Label(add_user_window, text="Role:", bg="#f0f8ff").grid(row=2, column=0, padx=10, pady=5)
        role_entry = tk.Entry(add_user_window)
        role_entry.grid(row=2, column=1, padx=10, pady=5)
        tk.Button(add_user_window, text="Save", **button_style, command=save_user).grid(row=3, column=0, columnspan=2, pady=10)

    tk.Button(it_dashboard, text="Add User", **button_style, command=add_user).pack(pady=5)
    tk.Button(it_dashboard, text="Refresh User List", **button_style, command=fetch_users).pack(pady=5)
    tk.Button(it_dashboard, text="View System Monitoring", **button_style, command=lambda: show_frame("SystemMonitoringPage")).pack(pady=10)
    tk.Button(it_dashboard, text="Back to Admin Dashboard", **button_style, command=lambda: show_frame("AdminDashboard")).pack(pady=20)

    fetch_users()
    return it_dashboard
