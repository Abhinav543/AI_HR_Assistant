import pandas as pd

from src.database.db_connection import get_connection


def load_leave_data():
    """
    Load leave requests together with employee information
    from the SQLite database.
    """

    connection = get_connection()

    query = """
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
        LEFT JOIN employees e
            ON lr.employee_id = e.employee_id
    """

    df = pd.read_sql_query(query, connection)

    connection.close()

    if not df.empty:
        df["start_date"] = pd.to_datetime(
            df["start_date"], errors="coerce"
        )

        df["end_date"] = pd.to_datetime(
            df["end_date"], errors="coerce"
        )

        df["applied_date"] = pd.to_datetime(
            df["applied_date"], errors="coerce"
        )

        df["month"] = df["start_date"].dt.to_period("M").astype(str)

    return df


def get_leave_summary():

    df = load_leave_data()

    if df.empty:
        return {
            "total_requests": 0,
            "approved": 0,
            "pending": 0,
            "rejected": 0
        }

    status = df["status"].str.lower()

    return {
        "total_requests": len(df),
        "approved": int((status == "approved").sum()),
        "pending": int((status == "pending").sum()),
        "rejected": int(
            status.isin(["rejected", "declined"]).sum()
        )
    }


def get_leave_type_summary():

    df = load_leave_data()

    if df.empty:
        return pd.DataFrame(
            columns=["leave_type", "request_count"]
        )

    return (
        df.groupby("leave_type")
        .size()
        .reset_index(name="request_count")
    )


def get_department_leave_summary():

    df = load_leave_data()

    if df.empty:
        return pd.DataFrame(
            columns=["department", "request_count"]
        )

    return (
        df.groupby("department")
        .size()
        .reset_index(name="request_count")
        .sort_values("request_count", ascending=False)
    )


def get_employee_leave_summary():

    df = load_leave_data()

    if df.empty:
        return pd.DataFrame(
            columns=[
                "employee_id",
                "name",
                "department",
                "request_count"
            ]
        )

    return (
        df.groupby(
            ["employee_id", "name", "department"],
            dropna=False
        )
        .size()
        .reset_index(name="request_count")
        .sort_values("request_count", ascending=False)
    )


def get_monthly_leave_summary():

    df = load_leave_data()

    if df.empty:
        return pd.DataFrame(
            columns=["month", "request_count"]
        )

    return (
        df.groupby("month")
        .size()
        .reset_index(name="request_count")
        .sort_values("month")
    )


def get_pending_leave_summary():

    df = load_leave_data()

    if df.empty:
        return pd.DataFrame(
            columns=["department", "pending_requests"]
        )

    pending = df[
        df["status"].str.lower() == "pending"
    ]

    if pending.empty:
        return pd.DataFrame(
            columns=["department", "pending_requests"]
        )

    return (
        pending.groupby("department")
        .size()
        .reset_index(name="pending_requests")
        .sort_values("pending_requests", ascending=False)
    )


if __name__ == "__main__":

    print("\nLEAVE SUMMARY")
    print(get_leave_summary())

    print("\nLEAVE TYPE SUMMARY")
    print(get_leave_type_summary())

    print("\nDEPARTMENT-WISE LEAVE")
    print(get_department_leave_summary())

    print("\nEMPLOYEE-WISE LEAVE")
    print(get_employee_leave_summary())

    print("\nMONTHLY LEAVE")
    print(get_monthly_leave_summary())

    print("\nPENDING LEAVE BY DEPARTMENT")
    print(get_pending_leave_summary())