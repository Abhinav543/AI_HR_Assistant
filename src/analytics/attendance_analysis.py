
import pandas as pd
from src.database.db_connection import get_connection


# ============================================================
# LOAD ATTENDANCE DATA FROM SQLITE
# ============================================================

def load_attendance_data():
    connection = get_connection()

    try:
        query = """
            SELECT
                a.attendance_id,
                a.employee_id,
                e.name,
                e.department,
                a.date,
                a.status,
                a.check_in,
                a.check_out
            FROM attendance a
            LEFT JOIN employees e
                ON a.employee_id = e.employee_id
        """

        return pd.read_sql_query(query, connection)

    finally:
        connection.close()


# ============================================================
# COMMON ATTENDANCE CALCULATION
# ============================================================

def calculate_attendance_percentage(data):

    total_records = len(data)

    if total_records == 0:
        return 0

    attended = data["status"].str.lower().isin(
        ["present", "work from home"]
    ).sum()

    return round((attended / total_records) * 100, 2)


# ============================================================
# OVERALL ATTENDANCE SUMMARY
# ============================================================

def get_attendance_summary():

    attendance = load_attendance_data()

    total_records = len(attendance)

    present_count = (
        attendance["status"].str.lower() == "present"
    ).sum()

    absent_count = (
        attendance["status"].str.lower() == "absent"
    ).sum()

    wfh_count = (
        attendance["status"].str.lower() == "work from home"
    ).sum()

    attendance_percentage = calculate_attendance_percentage(
        attendance
    )

    return {
        "total_records": total_records,
        "present": int(present_count),
        "absent": int(absent_count),
        "work_from_home": int(wfh_count),
        "attendance_percentage": attendance_percentage
    }


# ============================================================
# EMPLOYEE-WISE ATTENDANCE
# ============================================================

def get_employee_attendance_summary():

    attendance = load_attendance_data()

    if attendance.empty:
        return pd.DataFrame()

    summary = attendance.groupby(
        ["employee_id", "name", "department"]
    ).agg(
        total_records=("status", "count"),
        present=("status", lambda x: (x.str.lower() == "present").sum()),
        absent=("status", lambda x: (x.str.lower() == "absent").sum()),
        work_from_home=(
            "status",
            lambda x: (x.str.lower() == "work from home").sum()
        )
    ).reset_index()

    summary["attendance_percentage"] = (
        (
            summary["present"] + summary["work_from_home"]
        ) / summary["total_records"] * 100
    ).round(2)

    return summary


# ============================================================
# DEPARTMENT-WISE ATTENDANCE
# ============================================================

def get_department_attendance_summary():

    attendance = load_attendance_data()

    if attendance.empty:
        return pd.DataFrame()

    summary = attendance.groupby("department").agg(
        total_records=("status", "count"),
        present=("status", lambda x: (x.str.lower() == "present").sum()),
        absent=("status", lambda x: (x.str.lower() == "absent").sum()),
        work_from_home=(
            "status",
            lambda x: (x.str.lower() == "work from home").sum()
        )
    ).reset_index()

    summary["attendance_percentage"] = (
        (
            summary["present"] + summary["work_from_home"]
        ) / summary["total_records"] * 100
    ).round(2)

    return summary


# ============================================================
# MONTHLY ATTENDANCE SUMMARY
# ============================================================

def get_monthly_attendance_summary():

    attendance = load_attendance_data()

    if attendance.empty:
        return pd.DataFrame()

    attendance["date"] = pd.to_datetime(
        attendance["date"],
        errors="coerce"
    )

    attendance = attendance.dropna(subset=["date"])

    attendance["month"] = attendance["date"].dt.strftime("%Y-%m")

    summary = attendance.groupby("month").agg(
        total_records=("status", "count"),
        present=("status", lambda x: (x.str.lower() == "present").sum()),
        absent=("status", lambda x: (x.str.lower() == "absent").sum()),
        work_from_home=(
            "status",
            lambda x: (x.str.lower() == "work from home").sum()
        )
    ).reset_index()

    summary["attendance_percentage"] = (
        (
            summary["present"] + summary["work_from_home"]
        ) / summary["total_records"] * 100
    ).round(2)

    return summary


# ============================================================
# FILTER ATTENDANCE BY MONTH
# ============================================================

def get_attendance_by_month(month):

    attendance = load_attendance_data()

    if attendance.empty:
        return attendance

    attendance["date"] = pd.to_datetime(
        attendance["date"],
        errors="coerce"
    )

    return attendance[
        attendance["date"].dt.strftime("%Y-%m") == month
    ].copy()


# ============================================================
# INDEPENDENT EXECUTION
# ============================================================

if __name__ == "__main__":

    print("\n========== OVERALL ATTENDANCE ==========")
    print(get_attendance_summary())

    print("\n========== EMPLOYEE ATTENDANCE ==========")
    print(get_employee_attendance_summary())

    print("\n========== DEPARTMENT ATTENDANCE ==========")
    print(get_department_attendance_summary())

    print("\n========== MONTHLY ATTENDANCE ==========")
    print(get_monthly_attendance_summary())
