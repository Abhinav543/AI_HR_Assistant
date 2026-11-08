
from src.database.db_connection import get_connection
from datetime import date


def load_backup_data():

    connection = get_connection()
    cursor = connection.cursor()

    # Sample backup assignments
    assignments = [
        (
            "PRJ001", "EMP001", "EMP002",
            date.today().isoformat(),
            "Backup assigned for AI HR Assistant Development"
        ),
        (
            "PRJ002", "EMP003", "EMP009",
            date.today().isoformat(),
            "Backup assigned for Traffic Prediction Model"
        ),
        (
            "PRJ003", "EMP006", "EMP001",
            date.today().isoformat(),
            "Backup assigned for Data Analytics Dashboard"
        ),
        (
            "PRJ004", "EMP004", "EMP010",
            date.today().isoformat(),
            "Backup assigned for HR Policy Documentation"
        ),
        (
            "PRJ005", "EMP009", "EMP003",
            date.today().isoformat(),
            "Backup assigned for Network Optimization"
        )
    ]

    # Prevent duplicate assignments when rerunning
    for assignment in assignments:

        cursor.execute(
            """
            SELECT assignment_id
            FROM backup_assignments
            WHERE project_id = ?
            """,
            (assignment[0],)
        )

        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """
                UPDATE backup_assignments
                SET primary_employee_id = ?,
                    backup_employee_id = ?,
                    assignment_date = ?,
                    notes = ?
                WHERE project_id = ?
                """,
                (
                    assignment[1],
                    assignment[2],
                    assignment[3],
                    assignment[4],
                    assignment[0]
                )
            )

        else:
            cursor.execute(
                """
                INSERT INTO backup_assignments
                (
                    project_id,
                    primary_employee_id,
                    backup_employee_id,
                    assignment_date,
                    notes
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                assignment
            )

    connection.commit()
    connection.close()

    print("Backup assignments loaded successfully!")


if __name__ == "__main__":
    load_backup_data()
