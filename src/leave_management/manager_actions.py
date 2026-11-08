
from src.database.db_connection import get_connection
from datetime import datetime


def make_leave_decision(request_id, manager_id, decision, comments):

    if decision not in ["Approved", "Rejected"]:
        return "Invalid decision. Choose Approved or Rejected."

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Check whether the request exists and is pending
        cursor.execute(
            """
            SELECT status
            FROM leave_requests
            WHERE request_id = ?
            """,
            (request_id,)
        )

        request = cursor.fetchone()

        if request is None:
            return "Leave request not found."

        if request[0] != "Pending":
            return "This request has already been processed."

        # Update leave request status
        cursor.execute(
            """
            UPDATE leave_requests
            SET status = ?
            WHERE request_id = ?
            """,
            (decision, request_id)
        )

        # Store manager decision history
        cursor.execute(
            """
            INSERT INTO leave_decisions
            (request_id, manager_id, decision, comments, decision_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                request_id,
                manager_id,
                decision,
                comments,
                datetime.now().isoformat(timespec="seconds")
            )
        )

        connection.commit()

        return f"Request {request_id} successfully {decision.lower()}."

    except Exception as error:
        connection.rollback()
        return f"Error: {error}"

    finally:
        connection.close()


if __name__ == "__main__":

    result = make_leave_decision(
        "LR001",
        "MGR001",
        "Approved",
        "Approved after manager review."
    )

    print(result)
