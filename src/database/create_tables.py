
from .db_connection import get_connection


def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    # 1. Employee information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            name TEXT,
            department TEXT,
            designation TEXT,
            manager_id TEXT,
            joining_date TEXT,
            annual_leave_balance INTEGER,
            sick_leave_balance INTEGER
        )
    """)

    # 2. Leave requests
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            request_id TEXT PRIMARY KEY,
            employee_id TEXT,
            leave_type TEXT,
            start_date TEXT,
            end_date TEXT,
            reason TEXT,
            status TEXT,
            applied_date TEXT
        )
    """)

    # 3. Attendance records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            date TEXT,
            status TEXT,
            check_in TEXT,
            check_out TEXT
        )
    """)

    # 4. Company holidays
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS holidays (
            holiday_date TEXT PRIMARY KEY,
            holiday_name TEXT
        )
    """)

    # 5. Comp-off records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comp_off (
            comp_off_id TEXT PRIMARY KEY,
            employee_id TEXT,
            earned_date TEXT,
            expiry_date TEXT,
            days REAL,
            status TEXT
        )
    """)

    # 6. Manager decisions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_decisions (
            decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT,
            manager_id TEXT,
            decision TEXT,
            comments TEXT,
            decision_date TEXT
        )
    """)

    # 7. Project deadlines
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_deadlines (
            project_id TEXT PRIMARY KEY,
            project_name TEXT,
            employee_id TEXT,
            deadline_date TEXT,
            priority TEXT,
            status TEXT
        )
    """)

    # 8. Backup employee assignments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backup_assignments (
            assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            primary_employee_id TEXT,
            backup_employee_id TEXT,
            assignment_date TEXT,
            notes TEXT
        )
    """)

    connection.commit()
    connection.close()

    print("All HR database tables created successfully!")


if __name__ == "__main__":
    create_tables()
