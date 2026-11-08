
import pandas as pd
from datetime import datetime, timedelta
from src.database.db_connection import get_connection


def get_hr_data(query, params=()):
    connection = get_connection()
    try:
        return pd.read_sql_query(query, connection, params=params)
    finally:
        connection.close()


def calculate_working_days(start_date, end_date):
    holidays = get_hr_data("SELECT holiday_date FROM holidays")
    holiday_dates = set(
        pd.to_datetime(holidays["holiday_date"]).dt.date
    )

    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    if end < start:
        return 0

    working_days = 0
    current_date = start

    while current_date <= end:
        if current_date.weekday() < 5 and current_date not in holiday_dates:
            working_days += 1

        current_date += timedelta(days=1)

    return working_days


def get_leave_balance(employee_id, leave_type):
    employees = get_hr_data(
        "SELECT * FROM employees WHERE employee_id = ?",
        (employee_id,)
    )

    if employees.empty:
        return None

    leave_type = leave_type.lower()

    if leave_type == "annual":
        entitlement = float(employees.iloc[0]["annual_leave_balance"])
    elif leave_type == "sick":
        entitlement = float(employees.iloc[0]["sick_leave_balance"])
    else:
        return None

    requests = get_hr_data(
        """
        SELECT start_date, end_date, status
        FROM leave_requests
        WHERE employee_id = ? AND LOWER(leave_type) = ?
        AND LOWER(status) IN ('approved', 'pending')
        """,
        (employee_id, leave_type)
    )

    approved_days = 0
    pending_days = 0

    for _, request in requests.iterrows():
        days = calculate_working_days(
            request["start_date"],
            request["end_date"]
        )

        if request["status"].lower() == "approved":
            approved_days += days
        elif request["status"].lower() == "pending":
            pending_days += days

    return {
        "entitlement": entitlement,
        "approved_used": approved_days,
        "pending_days": pending_days,
        "remaining_balance": entitlement - approved_days
    }


def check_overlapping_leave(
    employee_id, start_date, end_date, exclude_request_id=None
):
    query = """
        SELECT request_id, start_date, end_date, status
        FROM leave_requests
        WHERE employee_id = ?
        AND LOWER(status) IN ('approved', 'pending')
        AND start_date <= ?
        AND end_date >= ?
    """

    params = [employee_id, end_date, start_date]

    if exclude_request_id:
        query += " AND request_id != ?"
        params.append(exclude_request_id)

    requests = get_hr_data(query, tuple(params))

    for _, request in requests.iterrows():
        print("\nOVERLAPPING LEAVE DETECTED!")
        print("Request ID:", request["request_id"])
        print("Dates:", request["start_date"], "to", request["end_date"])
        print("Status:", request["status"])

    return not requests.empty


def check_team_coverage(employee_id, start_date, end_date):
    employee = get_hr_data(
        "SELECT department FROM employees WHERE employee_id = ?",
        (employee_id,)
    )

    if employee.empty:
        print("Employee not found!")
        return False

    department = employee.iloc[0]["department"]

    team = get_hr_data(
        "SELECT employee_id FROM employees WHERE department = ?",
        (department,)
    )

    requests = get_hr_data(
        """
        SELECT employee_id, start_date, end_date
        FROM leave_requests
        WHERE LOWER(status) IN ('approved', 'pending')
        AND start_date <= ?
        AND end_date >= ?
        """,
        (end_date, start_date)
    )

    employees_on_leave = set()

    for _, request in requests.iterrows():
        if request["employee_id"] in team["employee_id"].values:
            employees_on_leave.add(request["employee_id"])

    employees_on_leave.add(employee_id)

    total_employees = len(team)
    available_employees = total_employees - len(employees_on_leave)

    coverage = (
        available_employees / total_employees * 100
        if total_employees else 0
    )

    print("\n========== TEAM COVERAGE ==========")
    print("Department:", department)
    print("Total Employees:", total_employees)
    print("Employees on Leave:", len(employees_on_leave))
    print("Available Employees:", available_employees)
    print("Team Coverage:", round(coverage, 2), "%")

    # Demo warning threshold; this is not a universal HR policy.
    if coverage < 50:
        print("Warning: LOW TEAM COVERAGE!")
        return False

    print("Team Coverage: Sufficient")
    return True


def check_notice_period(leave_type, applied_date, start_date):
    applied = datetime.strptime(applied_date, "%Y-%m-%d").date()
    start = datetime.strptime(start_date, "%Y-%m-%d").date()

    if leave_type.lower() == "annual":
        required_notice = 5
    elif leave_type.lower() == "sick":
        required_notice = 0
    else:
        print("Invalid leave type!")
        return False

    notice_days = (start - applied).days

    print("\n========== NOTICE PERIOD CHECK ==========")
    print("Leave Type:", leave_type)
    print("Notice Days:", notice_days)
    print("Required Notice:", required_notice)

    if notice_days >= required_notice:
        print("Result: Notice period satisfied.")
        return True

    print("Result: Insufficient notice period.")
    print("Recommendation: Manager review required.")
    return False


def check_leave_balance(employee_id, leave_type, start_date, end_date):
    balance = get_leave_balance(employee_id, leave_type)

    if balance is None:
        print("Employee not found or invalid leave type!")
        return

    requested_days = calculate_working_days(start_date, end_date)

    print("\n========== LEAVE BALANCE ==========")
    print("Entitlement:", balance["entitlement"])
    print("Approved Leave Used:", balance["approved_used"])
    print("Pending Leave:", balance["pending_days"])
    print("Remaining Balance:", balance["remaining_balance"])
    print("New Request Days:", requested_days)

    if requested_days <= 0:
        print("Result: No working days requested.")
    elif requested_days <= balance["remaining_balance"]:
        print("Result: Sufficient leave balance.")
    else:
        print("Result: Insufficient leave balance.")


def evaluate_leave_request(
    employee_id,
    leave_type,
    start_date,
    end_date,
    applied_date,
    exclude_request_id=None
):
    print("\n====================================")
    print("       LEAVE REQUEST EVALUATION")
    print("====================================")

    employee = get_hr_data(
        "SELECT name FROM employees WHERE employee_id = ?",
        (employee_id,)
    )

    if employee.empty:
        return "NEEDS MANAGER REVIEW: Employee not found."

    print("Employee:", employee.iloc[0]["name"])

    if check_overlapping_leave(
        employee_id, start_date, end_date, exclude_request_id
    ):
        return "POTENTIAL CONFLICT: Overlapping leave request exists."

    requested_days = calculate_working_days(start_date, end_date)

    if requested_days <= 0:
        return "NEEDS MANAGER REVIEW: No working days requested."

    balance = get_leave_balance(employee_id, leave_type)

    if balance is None:
        return "NEEDS MANAGER REVIEW: Invalid leave type."

    balance_passed = requested_days <= balance["remaining_balance"]

    print("\n========== BALANCE CHECK ==========")
    print("Entitlement:", balance["entitlement"])
    print("Approved Used:", balance["approved_used"])
    print("Pending Days:", balance["pending_days"])
    print("Remaining Balance:", balance["remaining_balance"])
    print("Requested Days:", requested_days)
    print("Balance Check:", balance_passed)

    notice_passed = check_notice_period(
        leave_type, applied_date, start_date
    )

    coverage_passed = check_team_coverage(
        employee_id, start_date, end_date
    )

    if not balance_passed:
        recommendation = "NEEDS MANAGER REVIEW: Insufficient leave balance."
    elif not notice_passed:
        recommendation = "NEEDS MANAGER REVIEW: Insufficient notice period."
    elif not coverage_passed:
        recommendation = "NEEDS MANAGER REVIEW: Low team coverage."
    else:
        recommendation = "LIKELY ELIGIBLE: All automated checks passed."

    print("\nFINAL RECOMMENDATION:", recommendation)
    print("Final approval must be given by the manager or HR.")

    return recommendation
