
from src.database.db_connection import get_connection
from src.leave_management.leave_calculator import evaluate_leave_request

from datetime import date, datetime


def submit_leave_request(
    employee_id,
    leave_type,
    start_date,
    end_date,
    reason
):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # 1. Check whether employee exists
        cursor.execute(
            "SELECT employee_id FROM employees WHERE employee_id = ?",
            (employee_id,)
        )

        employee = cursor.fetchone()

        if employee is None:
            return "Employee not found."

        # 2. Validate leave type
        if leave_type not in ["Annual", "Sick"]:
            return "Invalid leave type."

        # 3. Validate dates
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

        if start < date.today():
            return "Leave start date cannot be in the past."

        if end < start:
            return "End date cannot be before start date."

        # 4. Validate reason
        if not reason or not reason.strip():
            return "Please provide a leave reason."

        # 5. Generate unique request ID
        cursor.execute(
            """
            SELECT MAX(CAST(SUBSTR(request_id, 3) AS INTEGER))
            FROM leave_requests
            WHERE request_id LIKE 'LR%'
            """
        )

        result = cursor.fetchone()[0]
        next_number = (result or 0) + 1
        request_id = f"LR{next_number:03d}"

        # 6. Insert leave request as Pending
        cursor.execute(
            """
            INSERT INTO leave_requests
            (
                request_id,
                employee_id,
                leave_type,
                start_date,
                end_date,
                reason,
                status,
                applied_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                employee_id,
                leave_type,
                start_date,
                end_date,
                reason.strip(),
                "Pending",
                date.today().isoformat()
            )
        )

        # 7. Evaluate leave eligibility.
        # Exclude this newly inserted request from overlap detection.
        assessment = evaluate_leave_request(
            employee_id,
            leave_type,
            start_date,
            end_date,
            date.today().isoformat(),
            exclude_request_id=request_id
        )

        # 8. Save request
        connection.commit()

        # 9. Return result
        return {
            "message": f"Leave request {request_id} submitted successfully.",
            "request_id": request_id,
            "status": "Pending",
            "assessment": assessment
        }

    except ValueError:
        connection.rollback()
        return "Invalid date format. Please use YYYY-MM-DD."

    except Exception as error:
        connection.rollback()
        return f"Error submitting request: {error}"

    finally:
        connection.close()
