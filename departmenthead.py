import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from networkx import DiGraph
import networkx as nx
import matplotlib.pyplot as plt
import sqlite3
import heapq

# Utility function to fetch data from the database
def fetch_data(query, params=()):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data

# Utility function to execute a query in the database
def execute_query(query, params=()):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

# Priority Queue for Resources
class ResourcePriorityQueue:
    def __init__(self):
        self.queue = []
        heapq.heapify(self.queue)

    def add_resource(self, resource_name, resource_type, capacity, availability):
        # Calculate priority (lower number = higher priority)
        priority = self.calculate_priority(resource_type, capacity, availability)
        heapq.heappush(self.queue, (priority, resource_name))

    def calculate_priority(self, resource_type, capacity, availability):
        # Example priority logic:
        # Higher capacity -> Higher priority (lower number)
        # Labs preferred for lab-based courses
        base_priority = 0
        if resource_type == "Lab":
            base_priority -= 10  # Labs are prioritized
        if availability == "Unavailable":
            base_priority += 100  # Penalize unavailable resources
        base_priority -= capacity  # Higher capacity = higher priority
        return base_priority

    def get_best_resource(self):
        if self.queue:
            return heapq.heappop(self.queue)
        return None

# Department Head Dashboard
class DepartmentHeadApp(tk.Frame):

    def __init__(self, parent, show_frame):
        super().__init__(parent)
        self.show_frame = show_frame
        self.grid(row=0, column=0, sticky="nsew")

        # Tab Control
        tab_control = ttk.Notebook(self)
        self.course_tab = ttk.Frame(tab_control)
        self.resource_tab = ttk.Frame(tab_control)
        self.prerequisite_tab = ttk.Frame(tab_control)

        tab_control.add(self.course_tab, text="Course Scheduling")
        tab_control.add(self.resource_tab, text="Resource Allocation")
        tab_control.add(self.prerequisite_tab, text="Prerequisite Management")
        tab_control.pack(expand=1, fill="both")

        self.resource_priority_queue = ResourcePriorityQueue()  # Initialize Priority Queue

        # Initialize tabs
        self.setup_course_tab()
        self.setup_resource_tab()
        self.setup_prerequisite_tab()

    # ------------------ Course Scheduling Tab ------------------
    def setup_course_tab(self):
        tk.Label(self.course_tab, text="Course Scheduling", font=("Arial", 16)).pack(pady=10)

        # Dropdowns and Entry for scheduling
        form_frame = tk.Frame(self.course_tab)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Course:").grid(row=0, column=0, padx=10, pady=5)
        courses = [row[1] for row in fetch_data("SELECT * FROM courses")]
        self.course_dropdown = ttk.Combobox(form_frame, values=courses)
        self.course_dropdown.grid(row=0, column=1)

        tk.Label(form_frame, text="Faculty:").grid(row=1, column=0, padx=10, pady=5)
        faculty_departments = [row[0] for row in fetch_data("SELECT DISTINCT department FROM users WHERE role='Teacher'")]
        self.faculty_dropdown = ttk.Combobox(form_frame, values=faculty_departments)
        self.faculty_dropdown.grid(row=1, column=1)

        tk.Label(form_frame, text="Time Slot:").grid(row=2, column=0, padx=10, pady=5)
        self.time_entry = tk.Entry(form_frame)
        self.time_entry.grid(row=2, column=1)

        tk.Button(form_frame, text="Add Schedule with Priority", command=self.add_schedule_with_priority).grid(row=3, columnspan=2, pady=10)

        # TreeView for displaying schedules
        self.schedule_tree = ttk.Treeview(self.course_tab, columns=("Course", "Faculty", "Room", "Time"), show="headings")
        self.schedule_tree.heading("Course", text="Course")
        self.schedule_tree.heading("Faculty", text="Faculty")
        self.schedule_tree.heading("Room", text="Room")
        self.schedule_tree.heading("Time", text="Time")
        self.schedule_tree.pack(pady=10, fill="both", expand=True)

        self.load_schedules()

    def add_schedule_with_priority(self):
        course = self.course_dropdown.get()
        department = self.faculty_dropdown.get()
        time_slot = self.time_entry.get()

        if not course or not department or not time_slot:
            messagebox.showerror("Error", "All fields except room are required!")
            return

        # Get the highest-priority available room
        best_resource = self.resource_priority_queue.get_best_resource()
        if not best_resource:
            messagebox.showerror("Error", "No available resources!")
            return
        _, best_room = best_resource

        query = """
            INSERT INTO schedules (course_id, faculty_id, room_id, time_slot)
            VALUES (
                (SELECT id FROM courses WHERE course_name = ?),
                (SELECT id FROM users WHERE role = 'Teacher' AND department = ? LIMIT 1),
                (SELECT id FROM resources WHERE resource_name = ?),
                ?
            )
        """
        success = execute_query(query, (course, department, best_room, time_slot))
        if success:
            messagebox.showinfo("Success", f"Schedule added with room: {best_room}")
            execute_query("UPDATE resources SET availability = 'Unavailable' WHERE resource_name = ?", (best_room,))
            self.load_schedules()
            self.load_resources()
        else:
            messagebox.showerror("Error", "Failed to add schedule.")

    def load_schedules(self):
        # Clear existing rows
        for row in self.schedule_tree.get_children():
            self.schedule_tree.delete(row)

        # Fetch schedules from the database
        query = """
            SELECT c.course_name, u.department, r.resource_name, s.time_slot
            FROM schedules s
            JOIN courses c ON s.course_id = c.id
            JOIN users u ON s.faculty_id = u.id
            JOIN resources r ON s.room_id = r.id
        """
        schedules = fetch_data(query)
        for schedule in schedules:
            self.schedule_tree.insert("", "end", values=schedule)

    # ------------------ Resource Allocation Tab ------------------
    def setup_resource_tab(self):
        tk.Label(self.resource_tab, text="Resource Allocation", font=("Arial", 16)).pack(pady=10)

        # Display available resources
        self.resource_tree = ttk.Treeview(self.resource_tab, columns=("Resource", "Type", "Capacity", "Availability"), show="headings")
        self.resource_tree.heading("Resource", text="Resource")
        self.resource_tree.heading("Type", text="Type")
        self.resource_tree.heading("Capacity", text="Capacity")
        self.resource_tree.heading("Availability", text="Availability")
        self.resource_tree.pack(pady=10, fill="both", expand=True)

        self.load_resources()

    def load_resources(self):
        # Fetch resources from the database
        query = "SELECT resource_name, resource_type, capacity, availability FROM resources"
        resources = fetch_data(query)
        for row in self.resource_tree.get_children():
            self.resource_tree.delete(row)
        for resource in resources:
            resource_name, resource_type, capacity, availability = resource
            self.resource_tree.insert("", "end", values=resource)
            self.resource_priority_queue.add_resource(resource_name, resource_type, int(capacity), availability)

    # ------------------ Prerequisite Management Tab ------------------
    def setup_prerequisite_tab(self):
        tk.Label(self.prerequisite_tab, text="Prerequisite Management", font=("Arial", 16)).pack(pady=10)

        self.prerequisite_tree = ttk.Treeview(self.prerequisite_tab, columns=("Course", "Prerequisite"), show="headings")
        self.prerequisite_tree.heading("Course", text="Course")
        self.prerequisite_tree.heading("Prerequisite", text="Prerequisite")
        self.prerequisite_tree.pack(pady=10, fill="both", expand=True)

        tk.Button(self.prerequisite_tab, text="Visualize Prerequisites", command=self.visualize_prerequisites).pack(pady=10)

        self.load_prerequisites()

    def load_prerequisites(self):
        query = """
            SELECT c1.course_name AS course, c2.course_name AS prerequisite
            FROM course_prerequisites cp
            JOIN courses c1 ON cp.course_id = c1.id
            JOIN courses c2 ON cp.prerequisite_id = c2.id
        """
        prerequisites = fetch_data(query)
        for row in self.prerequisite_tree.get_children():
            self.prerequisite_tree.delete(row)
        for prerequisite in prerequisites:
            self.prerequisite_tree.insert("", "end", values=(prerequisite[0], prerequisite[1]))

    def visualize_prerequisites(self):
        query = """
            SELECT c1.course_name AS course, c2.course_name AS prerequisite
            FROM course_prerequisites cp
            JOIN courses c1 ON cp.course_id = c1.id
            JOIN courses c2 ON cp.prerequisite_id = c2.id
        """
        data = fetch_data(query)

        if not data:
            messagebox.showinfo("Info", "No prerequisites found to visualize.")
            return

        G = DiGraph()
        for course, prerequisite in data:
            G.add_edge(prerequisite, course)

        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', arrowsize=20, font_size=10)
        plt.title("Prerequisite Course Graph", fontsize=14)
        plt.show()
