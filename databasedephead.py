import sqlite3

def add_departments_table():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Create a table for departments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT NOT NULL UNIQUE,
            head_of_department TEXT NOT NULL,
            FOREIGN KEY (head_of_department) REFERENCES users(username)
        )
    """)
    print("Departments table created successfully.")

    conn.commit()
    conn.close()

def add_resources_table():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Create a table for resources
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_name TEXT NOT NULL UNIQUE,
            resource_type TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            availability TEXT DEFAULT 'Available'
        )
    """)
    print("Resources table created successfully.")

    conn.commit()
    conn.close()

def add_schedules_table():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Create a table for course schedules
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            faculty_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            time_slot TEXT NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(id),
            FOREIGN KEY (faculty_id) REFERENCES users(id),
            FOREIGN KEY (room_id) REFERENCES resources(id)
        )
    """)
    print("Schedules table created successfully.")

    conn.commit()
    conn.close()

def add_prerequisites_table():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Create a table for course prerequisites
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_prerequisites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            prerequisite_id INTEGER NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(id),
            FOREIGN KEY (prerequisite_id) REFERENCES courses(id)
        )
    """)
    print("Course prerequisites table created successfully.")

    conn.commit()
    conn.close()

def seed_sample_data():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Insert sample data for departments
    cursor.execute("INSERT OR IGNORE INTO departments (department_name, head_of_department) VALUES ('Computer Science', 'Dr Wael')")
    cursor.execute("INSERT OR IGNORE INTO departments (department_name, head_of_department) VALUES ('Bussiness', 'Dr Tamer')")

    # Insert sample data for resources
    cursor.execute("INSERT OR IGNORE INTO resources (resource_name, resource_type, capacity) VALUES ('Room 101', 'Lecture Hall', 50)")
    cursor.execute("INSERT OR IGNORE INTO resources (resource_name, resource_type, capacity) VALUES ('Lab 202', 'Lab', 30)")

    # Insert sample data for courses
    cursor.execute("INSERT OR IGNORE INTO courses (course_name) VALUES ('Data Structures')")
    cursor.execute("INSERT OR IGNORE INTO courses (course_name) VALUES ('AI')")

    # Insert sample prerequisites
    cursor.execute("INSERT OR IGNORE INTO course_prerequisites (course_id, prerequisite_id) VALUES (1, 2)")

    conn.commit()
    print("Sample data seeded successfully.")
    conn.close()

if __name__ == "__main__":
    # Call the functions to set up the database
    add_departments_table()
    add_resources_table()
    add_schedules_table()
    add_prerequisites_table()
    seed_sample_data()

# check faculty 
# check prequisties with course ID 
# erbot el reasource allocation with course scheduling 
