import sqlite3

def setup_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    print("Setting up the database.")

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT DEFAULT 'Active'
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

    # Other table creation...

    # Insert default users
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role, status) VALUES ('admin', 'admin', 'Admin', 'Active')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role, status) VALUES ('student', 'student', 'Student', 'Active')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role, status) VALUES ('teacher', 'teacher', 'Teacher', 'Active')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role, status) VALUES ('dephead', 'dephead', 'DepartmentHead', 'Active')")
    print("Default users inserted successfully.")

    conn.commit()
    conn.close()

def update_assignments_table():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(assignments)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'assigned_to' not in columns:
        cursor.execute("ALTER TABLE assignments ADD COLUMN assigned_to TEXT DEFAULT NULL")
        print("Added 'assigned_to' column.")

    if 'due_date' not in columns:
        cursor.execute("ALTER TABLE assignments ADD COLUMN due_date TEXT NOT NULL DEFAULT '2025-01-01'")
        print("Added 'due_date' column.")

    conn.commit()
    conn.close()

def update_submissions_table():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(submissions)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'assignment_id' not in columns:
        print("Updating 'submissions' table to include 'assignment_id'.")
        cursor.execute("""
            CREATE TABLE temp_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER NOT NULL DEFAULT 0,
                student_username TEXT NOT NULL,
                file_path TEXT NOT NULL,
                FOREIGN KEY (assignment_id) REFERENCES assignments(id),
                FOREIGN KEY (student_username) REFERENCES users(username)
            )
        """)
        cursor.execute("""
            INSERT INTO temp_submissions (id, assignment_id, student_username, file_path)
            SELECT id, 0, student_username, file_path
            FROM submissions
        """)
        cursor.execute("DROP TABLE submissions")
        cursor.execute("ALTER TABLE temp_submissions RENAME TO submissions")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
    update_assignments_table()
    update_submissions_table()
