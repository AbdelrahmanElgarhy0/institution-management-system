import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import setup_database
from admindash import AdminDashboard, ITDashboard, SystemMonitoringPage
from studentdash import StudentDashboard  # Enhanced version
from teacherdash import TeacherDashboard
from userlinkedlist import UserLinkedList  # Import the linked list class
from departmenthead import DepartmentHeadApp

# Initialize the user linked list
user_list = UserLinkedList()

# Define color scheme
bg_color = "#f0f8ff"  # Light blue background
header_color = "#4682b4"  # Steel blue for headers
button_color = "#6ca6cd"  # Sky blue for buttons
text_color = "white"

# Main application setup
root = tk.Tk()
root.title("Smart Educational Institute Administration System")
root.geometry("800x600")

# Create a container for all frames
container = tk.Frame(root, bg=bg_color)
container.pack(fill="both", expand=True)
container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

# Dictionary to store frames
frames = {}

# Helper function to switch between frames
def show_frame(frame_name):
    """Raise the specified frame."""
    frame = frames.get(frame_name)
    if frame:
        frame.tkraise()
    else:
        print(f"Frame '{frame_name}' not found.")

# Initialize frames
frames["AdminDashboard"] = AdminDashboard(container, show_frame)
frames["ITDashboard"] = ITDashboard(container, show_frame, user_list)  # Pass user_list here
frames["SystemMonitoringPage"] = SystemMonitoringPage(container, show_frame)

# Ensure TeacherDashboard and StudentDashboard are initialized dynamically in login
frames["MainMenu"] = tk.Frame(container, bg=bg_color)
frames["MainMenu"].grid(row=0, column=0, sticky="nsew")

# Ensure proper frame grid configuration
for frame in frames.values():
    frame.grid(row=0, column=0, sticky="nsew")

# Define the role the user selects
selected_role = tk.StringVar(value="")  # Initialize selected_role with an empty value

# Main Menu
main_menu = frames["MainMenu"]
tk.Label(main_menu, text="Welcome to the Administration System", font=("Arial", 20, "bold"), bg=header_color, fg=text_color).pack(pady=20, fill="x")
tk.Button(main_menu, text="Admin", font=("Arial", 15), bg=button_color, fg=text_color, command=lambda: (selected_role.set("Admin"), show_frame("LoginPage"))).pack(pady=10)
tk.Button(main_menu, text="Student", font=("Arial", 15), bg=button_color, fg=text_color, command=lambda: (selected_role.set("Student"), show_frame("LoginPage"))).pack(pady=10)
tk.Button(main_menu, text="Teacher", font=("Arial", 15), bg=button_color, fg=text_color, command=lambda: (selected_role.set("Teacher"), show_frame("LoginPage"))).pack(pady=10)
tk.Button(main_menu, text="Department Head", font=("Arial", 15), bg=button_color, fg=text_color,
          command=lambda: (selected_role.set("DepartmentHead"), show_frame("LoginPage"))).pack(pady=10)
tk.Button(main_menu, text="Exit", font=("Arial", 12), bg=button_color, fg=text_color, command=root.quit).pack(pady=10)

# Login Page
login_page = tk.Frame(container, bg=bg_color)
login_page.grid(row=0, column=0, sticky="nsew")
frames["LoginPage"] = login_page

tk.Label(login_page, text="Login", font=("Arial", 20, "bold"), bg=header_color, fg=text_color).pack(pady=20, fill="x")
tk.Label(login_page, text="Username:", font=("Arial", 14), bg=bg_color).pack(pady=5)
username_entry = tk.Entry(login_page, font=("Arial", 14))
username_entry.pack(pady=5)
tk.Label(login_page, text="Password:", font=("Arial", 14), bg=bg_color).pack(pady=5)
password_entry = tk.Entry(login_page, font=("Arial", 14), show="*")
password_entry.pack(pady=5)

def validate_login():
    username = username_entry.get().strip()  # Get and clean username input
    password = password_entry.get().strip()  # Get and clean password input
    role = selected_role.get()  # Get the selected role (Admin, Teacher, Student, DepartmentHead)

    # Ensure all fields are filled
    if not username or not password or not role:
        tk.messagebox.showerror("Login Failed", "Please fill out all fields.")
        return

    try:
        # Connect to the database
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Query to validate the login credentials
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = ?", (username, password, role))
        user = cursor.fetchone()

        if user:  # If a user is found
            tk.messagebox.showinfo("Login Successful", f"Welcome, {role}")
            if role == "Admin":
                show_frame("AdminDashboard")
            elif role == "Teacher":
                if "TeacherDashboard" not in frames:
                    frames["TeacherDashboard"] = TeacherDashboard(container, show_frame)
                    frames["TeacherDashboard"].grid(row=0, column=0, sticky="nsew")
                show_frame("TeacherDashboard")
            elif role == "Student":
                # Define get_current_user function dynamically to return the current logged-in user
                def get_current_user():
                    return username

                # Dynamically initialize StudentDashboard if not already created
                if "StudentDashboard" not in frames:
                    frames["StudentDashboard"] = StudentDashboard(container, show_frame, get_current_user)
                    frames["StudentDashboard"].grid(row=0, column=0, sticky="nsew")
                
                # Show the StudentDashboard
                show_frame("StudentDashboard")
            elif role == "DepartmentHead":
                if "DepartmentHeadDashboard" not in frames:
                    # Initialize DepartmentHeadApp as a new frame
                    frames["DepartmentHeadDashboard"] = DepartmentHeadApp(container, show_frame)
                    frames["DepartmentHeadDashboard"].grid(row=0, column=0, sticky="nsew")
                show_frame("DepartmentHeadDashboard")
        else:  # If credentials are invalid
            tk.messagebox.showerror("Login Failed", "Invalid username, password, or role.")
    except sqlite3.Error as e:  # Catch database-related errors
        tk.messagebox.showerror("Database Error", f"An error occurred: {e}")
    finally:
        conn.close()  # Always close the database connection

tk.Button(login_page, text="Login", font=("Arial", 14), bg=button_color, fg=text_color, command=validate_login).pack(pady=10)
tk.Button(login_page, text="Back to Main Menu", font=("Arial", 12), bg=button_color, fg=text_color, command=lambda: show_frame("MainMenu")).pack(pady=10)

# Setup database
setup_database()

# Show the main menu initially
show_frame("MainMenu")

# Start the Tkinter loop
root.mainloop()
