
from src.database.db_connection import get_connection


def get_project_risks():

    connection = get_connection()

    try:

        query = """
            SELECT
                p.project_id,
                p.project_name,
                p.employee_id,
                e.name,
                p.deadline_date,
                p.priority,
                p.status,
                b.backup_employee_id,
                backup.name
            FROM project_deadlines p

            LEFT JOIN employees e
                ON p.employee_id = e.employee_id

            LEFT JOIN backup_assignments b
                ON p.project_id = b.project_id

            LEFT JOIN employees backup
                ON b.backup_employee_id = backup.employee_id
        """

        projects = connection.execute(query).fetchall()

        risks = []

        for project in projects:

            (
                project_id,
                project_name,
                employee_id,
                employee_name,
                deadline,
                priority,
                status,
                backup_id,
                backup_name
            ) = project

            # Check leave during the 7 days before the deadline,
            # including the deadline date itself.
            leave_query = """
                SELECT start_date, end_date
                FROM leave_requests
                WHERE employee_id = ?
                AND status IN ('Pending', 'Approved')
                AND start_date <= ?
                AND end_date >= date(?, '-7 days')
            """

            leaves = connection.execute(
                leave_query,
                (employee_id, deadline, deadline)
            ).fetchall()

            if leaves:
                risk_status = "Potential Leave Conflict"
            else:
                risk_status = "No Leave Conflict"

            # Prepare project risk information
            risks.append({
                "project_id": project_id,
                "project_name": project_name,
                "employee_id": employee_id,
                "employee": employee_name or "Unknown",
                "deadline": deadline,
                "priority": priority,
                "status": status,
                "backup_employee_id": backup_id,
                "backup_employee": backup_name or "Not Assigned",
                "risk": risk_status
            })

        return risks

    finally:
        connection.close()


if __name__ == "__main__":

    results = get_project_risks()

    print("\n========== PROJECT RISK ANALYSIS ==========")

    for project in results:

        print("\nProject:", project["project_name"])
        print("Responsible Employee:", project["employee"])
        print("Deadline:", project["deadline"])
        print("Priority:", project["priority"])
        print("Backup:", project["backup_employee"])
        print("Risk:", project["risk"])
