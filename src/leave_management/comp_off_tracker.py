from src.database.db_connection import get_connection
from datetime import date


# ==========================================
# GET COMP-OFF SUMMARY
# ==========================================

def get_comp_off_summary(employee_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT days, status, expiry_date
        FROM comp_off
        WHERE employee_id = ?
        """,
        (employee_id,)
    )

    records = cursor.fetchall()
    connection.close()

    today = date.today()

    earned = 0
    available = 0
    used = 0
    expired = 0
    expiring_soon = 0

    for days, status, expiry_date in records:

        if days is None or days <= 0:
            continue

        earned += days

        try:
            expiry = date.fromisoformat(expiry_date)
        except (ValueError, TypeError):
            continue

        if status == "Used":

            used += days

        elif status == "Available" and expiry < today:

            expired += days

        elif status == "Available":

            available += days

            remaining_days = (expiry - today).days

            if 0 <= remaining_days <= 30:
                expiring_soon += days

    return {
        "earned": earned,
        "available": available,
        "used": used,
        "expired": expired,
        "expiring_soon": expiring_soon
    }


# ==========================================
# GET INDIVIDUAL COMP-OFF RECORDS
# ==========================================

def get_comp_off_records(employee_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            rowid,
            employee_id,
            days,
            status,
            expiry_date
        FROM comp_off
        WHERE employee_id = ?
        ORDER BY expiry_date
        """,
        (employee_id,)
    )

    records = cursor.fetchall()

    connection.close()

    return records


# ==========================================
# VALIDATE COMP-OFF USAGE
# ==========================================

def validate_comp_off_usage(employee_id, comp_off_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT days, status, expiry_date
        FROM comp_off
        WHERE rowid = ?
        AND employee_id = ?
        """,
        (comp_off_id, employee_id)
    )

    record = cursor.fetchone()

    connection.close()

    if not record:
        return False, "Comp-off record not found for this employee."

    days, status, expiry_date = record

    if days is None or days <= 0:
        return False, "Invalid comp-off balance."

    if status != "Available":
        return False, "This comp-off record has already been used or is unavailable."

    try:
        expiry = date.fromisoformat(expiry_date)
    except (ValueError, TypeError):
        return False, "Invalid comp-off expiry date."

    if expiry < date.today():
        return False, "This comp-off has expired and cannot be used."

    return True, "Comp-off is valid and available for use."


# ==========================================
# USE COMP-OFF
# ==========================================

def use_comp_off(employee_id, comp_off_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        today = date.today().isoformat()

        cursor.execute(
            """
            UPDATE comp_off
            SET status = 'Used'
            WHERE rowid = ?
            AND employee_id = ?
            AND status = 'Available'
            AND expiry_date >= ?
            AND days > 0
            """,
            (comp_off_id, employee_id, today)
        )

        if cursor.rowcount == 1:

            connection.commit()

            return True, "Comp-off successfully marked as Used."

        connection.rollback()

        # Identify why the update did not happen.
        cursor.execute(
            """
            SELECT status, expiry_date
            FROM comp_off
            WHERE rowid = ?
            AND employee_id = ?
            """,
            (comp_off_id, employee_id)
        )

        record = cursor.fetchone()

        if not record:
            return False, "Comp-off record not found for this employee."

        status, expiry_date = record

        if status != "Available":
            return False, "This comp-off has already been used or is unavailable."

        try:
            expiry = date.fromisoformat(expiry_date)
        except (ValueError, TypeError):
            return False, "Invalid comp-off expiry date."

        if expiry < date.today():
            return False, "This comp-off has expired and cannot be used."

        return False, "Unable to use this comp-off record."

    except Exception as error:

        connection.rollback()

        return False, f"Database error: {error}"

    finally:

        connection.close()


# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":

    employee_id = "EMP001"

    summary = get_comp_off_summary(employee_id)

    print("\n========== COMP-OFF SUMMARY ==========")

    print("Earned:", summary["earned"])
    print("Available:", summary["available"])
    print("Used:", summary["used"])
    print("Expired:", summary["expired"])
    print("Expiring Soon:", summary["expiring_soon"])

    print("\n========== COMP-OFF RECORDS ==========")

    records = get_comp_off_records(employee_id)

    for record in records:

        print(
            f"ID: {record[0]} | "
            f"Employee: {record[1]} | "
            f"Days: {record[2]} | "
            f"Status: {record[3]} | "
            f"Expiry: {record[4]}"
        )

def get_all_comp_off_records():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            comp_off_id,
            employee_id,
            earned_date,
            expiry_date,
            days,
            status
        FROM comp_off
        ORDER BY expiry_date
    """)

    records = cursor.fetchall()

    connection.close()

    return records