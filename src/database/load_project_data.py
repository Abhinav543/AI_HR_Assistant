
from src.database.db_connection import get_connection


def load_project_data():

    connection = get_connection()
    cursor = connection.cursor()

    # Sample project deadlines
    projects = [
        ("PRJ001", "AI HR Assistant Development", "EMP001",
         "2026-11-20", "High", "In Progress"),

        ("PRJ002", "Traffic Prediction Model", "EMP003",
         "2026-11-15", "Medium", "In Progress"),

        ("PRJ003", "Data Analytics Dashboard", "EMP006",
         "2026-11-25", "High", "In Progress"),

        ("PRJ004", "HR Policy Documentation", "EMP004",
         "2026-11-18", "Low", "In Progress"),

        ("PRJ005", "Network Optimization", "EMP009",
         "2026-11-30", "High", "In Progress")
    ]

    cursor.executemany(
        """
        INSERT OR REPLACE INTO project_deadlines
        (project_id, project_name, employee_id,
         deadline_date, priority, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        projects
    )

    connection.commit()
    connection.close()

    print("Project deadline data loaded successfully!")


if __name__ == "__main__":
    load_project_data()
