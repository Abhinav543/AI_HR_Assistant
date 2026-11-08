
from src.database.db_connection import get_connection


def verify_database():

    connection = get_connection()
    cursor = connection.cursor()

    tables = [
        "employees",
        "leave_requests",
        "attendance",
        "holidays",
        "comp_off",
        "leave_decisions"
    ]

    print("\n========== DATABASE VERIFICATION ==========")

    for table in tables:

        cursor.execute(f"SELECT COUNT(*) FROM {table}")

        count = cursor.fetchone()[0]

        print(f"{table}: {count} records")

    connection.close()


if __name__ == "__main__":
    verify_database()

from src.database.db_connection import get_connection

connection = get_connection()

connection.execute("""
    UPDATE leave_requests
    SET status = 'Pending'
    WHERE request_id IN ('LR003', 'LR005')
""")

connection.commit()
connection.close()

print("LR003 and LR005 restored to Pending!")