
from src.database.db_connection import get_connection


# ==========================================
# 1. GET EMPLOYEE DETAILS
# ==========================================

def get_employee_details(employee_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM employees
        WHERE employee_id = ?
        """,
        (employee_id,)
    )

    employee = cursor.fetchone()
    connection.close()

    return employee


# ==========================================
# 2. GET EMPLOYEE LEAVE REQUESTS
# ==========================================

def get_employee_leave_requests(employee_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM leave_requests
        WHERE employee_id = ?
        ORDER BY rowid DESC
        """,
        (employee_id,)
    )

    requests = cursor.fetchall()
    connection.close()

    return requests


# ==========================================
# 3. GET ALL PENDING REQUESTS
# ==========================================

def get_all_pending_requests():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM leave_requests
        WHERE status = 'Pending'
        """
    )

    requests = cursor.fetchall()
    connection.close()

    return requests


# ==========================================
# 4. GET DETAILED PENDING REQUESTS
# ==========================================

def get_pending_request_details():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            lr.request_id,
            lr.employee_id,
            e.name,
            e.department,
            lr.leave_type,
            lr.start_date,
            lr.end_date,
            lr.reason,
            lr.status,
            lr.applied_date
        FROM leave_requests lr
        JOIN employees e
        ON lr.employee_id = e.employee_id
        WHERE lr.status = 'Pending'
        ORDER BY lr.applied_date
        """
    )

    requests = cursor.fetchall()
    connection.close()

    return requests


# ==========================================
# 5. TEST DATABASE FUNCTIONS
# ==========================================

if __name__ == "__main__":

    employee = get_employee_details("EMP001")

    print("\n========== EMPLOYEE DETAILS ==========")
    print(employee)

    requests = get_employee_leave_requests("EMP001")

    print("\n========== EMPLOYEE LEAVE REQUESTS ==========")

    for request in requests:
        print(request)

    pending = get_all_pending_requests()

    print("\n========== PENDING LEAVE REQUESTS ==========")
    print("Total pending requests:", len(pending))
