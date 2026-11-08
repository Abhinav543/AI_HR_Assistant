
import sqlite3
from datetime import date, datetime, timedelta

from src.database.db_connection import get_connection


# ============================================================
# CONFIGURATION
# ============================================================

# Demo assumption: managers should review a request within
# two working days after submission.
APPROVAL_SLA_WORKING_DAYS = 2

# Demo alert window for upcoming comp-off expiry.
COMPOFF_EXPIRY_WARNING_DAYS = 30

# Demo alert window for upcoming project deadlines.
PROJECT_DEADLINE_WARNING_DAYS = 7


# ============================================================
# DATE HELPERS
# ============================================================

def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def get_holidays(connection):
    rows = connection.execute(
        "SELECT holiday_date FROM holidays"
    ).fetchall()

    return {
        parsed
        for row in rows
        if (parsed := parse_date(row["holiday_date"])) is not None
    }


def is_working_day(day, holidays):
    return day.weekday() < 5 and day not in holidays


def add_working_days(start_date, number_of_days, holidays):
    current = start_date
    added = 0

    while added < number_of_days:
        current += timedelta(days=1)

        if is_working_day(current, holidays):
            added += 1

    return current


def next_working_day(start_date, holidays):
    current = start_date + timedelta(days=1)

    while not is_working_day(current, holidays):
        current += timedelta(days=1)

    return current


# ============================================================
# TIMELINE TABLE
# ============================================================

def create_timeline_table():
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS timeline_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                event_date TEXT NOT NULL,
                end_date TEXT,
                employee_id TEXT,
                reference_id TEXT,
                status TEXT,
                priority TEXT,
                created_at TEXT
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


# ============================================================
# TIMELINE EVENT STORAGE
# ============================================================

def save_event(
    connection,
    event_id,
    event_type,
    title,
    description,
    event_date,
    end_date=None,
    employee_id=None,
    reference_id=None,
    status=None,
    priority="Normal"
):
    connection.execute(
        """
        INSERT OR REPLACE INTO timeline_events
        (
            event_id,
            event_type,
            title,
            description,
            event_date,
            end_date,
            employee_id,
            reference_id,
            status,
            priority,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            event_type,
            title,
            description,
            event_date.isoformat(),
            end_date.isoformat() if end_date else None,
            employee_id,
            reference_id,
            status,
            priority,
            datetime.now().isoformat(timespec="seconds")
        )
    )


# ============================================================
# REFRESH TIMELINE FROM HR DATABASE
# ============================================================

def sync_timeline():
    """
    Rebuild the timeline snapshot from the current HR records.

    The source of truth remains the original HR tables.
    timeline_events stores a refreshed, queryable timeline.
    """

    create_timeline_table()

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:
        holidays = get_holidays(connection)

        employees = {
            row["employee_id"]: row["name"]
            for row in connection.execute(
                "SELECT employee_id, name FROM employees"
            ).fetchall()
        }

        # Refresh generated events to avoid stale duplicates.
        connection.execute("DELETE FROM timeline_events")

        # ----------------------------------------------------
        # 1. LEAVE REQUEST EVENTS
        # ----------------------------------------------------

        leave_requests = connection.execute(
            """
            SELECT
                request_id,
                employee_id,
                leave_type,
                start_date,
                end_date,
                status,
                applied_date
            FROM leave_requests
            """
        ).fetchall()

        for request in leave_requests:

            start = parse_date(request["start_date"])
            end = parse_date(request["end_date"])
            applied = parse_date(request["applied_date"])

            if not start or not end or end < start:
                continue

            employee_name = employees.get(
                request["employee_id"],
                request["employee_id"]
            )

            request_id = request["request_id"]
            status = request["status"] or "Unknown"

            save_event(
                connection,
                f"LEAVE_{request_id}",
                "Leave",
                f"{employee_name} - {request['leave_type']} leave",
                f"Leave request {request_id}. Status: {status}.",
                start,
                end,
                request["employee_id"],
                request_id,
                status,
                "High" if status.lower() == "pending" else "Normal"
            )

            # Submission event
            if applied:
                save_event(
                    connection,
                    f"SUBMISSION_{request_id}",
                    "Request Submission",
                    f"Leave request submitted: {request_id}",
                    f"{employee_name} submitted a leave request.",
                    applied,
                    employee_id=request["employee_id"],
                    reference_id=request_id,
                    status=status
                )

            # Approval deadline only applies to pending requests.
            if status.lower() == "pending" and applied:

                approval_deadline = add_working_days(
                    applied,
                    APPROVAL_SLA_WORKING_DAYS,
                    holidays
                )

                save_event(
                    connection,
                    f"APPROVAL_{request_id}",
                    "Approval Deadline",
                    f"Approval due: {request_id}",
                    (
                        f"{employee_name}'s leave request "
                        f"{request_id} requires manager/HR review."
                    ),
                    approval_deadline,
                    employee_id=request["employee_id"],
                    reference_id=request_id,
                    status="Pending",
                    priority="High"
                )

            # Return-to-work event
            return_date = next_working_day(end, holidays)

            save_event(
                connection,
                f"RETURN_{request_id}",
                "Return to Work",
                f"{employee_name} expected to return",
                (
                    f"Expected return date following leave request "
                    f"{request_id}."
                ),
                return_date,
                employee_id=request["employee_id"],
                reference_id=request_id,
                status=status
            )

        # ----------------------------------------------------
        # 2. COMPOFF EVENTS
        # ----------------------------------------------------

        comp_off_records = connection.execute(
            """
            SELECT
                comp_off_id,
                employee_id,
                earned_date,
                expiry_date,
                days,
                status
            FROM comp_off
            """
        ).fetchall()

        today = date.today()

        for record in comp_off_records:

            expiry = parse_date(record["expiry_date"])
            earned = parse_date(record["earned_date"])

            employee_name = employees.get(
                record["employee_id"],
                record["employee_id"]
            )

            comp_id = record["comp_off_id"]
            status = record["status"] or "Unknown"

            if earned:
                save_event(
                    connection,
                    f"COMPOFF_EARNED_{comp_id}",
                    "Comp-off Earned",
                    f"{employee_name} earned comp-off",
                    f"{record['days']} comp-off day(s) earned.",
                    earned,
                    employee_id=record["employee_id"],
                    reference_id=comp_id,
                    status=status
                )

            if expiry:
                days_remaining = (expiry - today).days

                if status.lower() == "available":
                    priority = (
                        "High"
                        if days_remaining <= COMPOFF_EXPIRY_WARNING_DAYS
                        else "Normal"
                    )

                    event_status = (
                        "Expired"
                        if days_remaining < 0
                        else "Available"
                    )

                    save_event(
                        connection,
                        f"COMPOFF_EXPIRY_{comp_id}",
                        "Comp-off Expiry",
                        f"Comp-off expiry: {employee_name}",
                        (
                            f"{record['days']} day(s) of comp-off. "
                            f"Expiry date: {expiry}. "
                            f"Days remaining: {days_remaining}."
                        ),
                        expiry,
                        employee_id=record["employee_id"],
                        reference_id=comp_id,
                        status=event_status,
                        priority=priority
                    )

        # ----------------------------------------------------
        # 3. HOLIDAY EVENTS
        # ----------------------------------------------------

        holiday_records = connection.execute(
            """
            SELECT holiday_date, holiday_name
            FROM holidays
            """
        ).fetchall()

        for holiday in holiday_records:

            holiday_date = parse_date(holiday["holiday_date"])

            if not holiday_date:
                continue

            holiday_name = holiday["holiday_name"]

            save_event(
                connection,
                f"HOLIDAY_{holiday_date.isoformat()}",
                "Holiday",
                holiday_name,
                f"Company holiday: {holiday_name}.",
                holiday_date,
                status="Scheduled"
            )

        # ----------------------------------------------------
        # 4. PROJECT DEADLINE EVENTS
        # ----------------------------------------------------

        projects = connection.execute(
            """
            SELECT
                p.project_id,
                p.project_name,
                p.employee_id,
                p.deadline_date,
                p.priority,
                p.status,
                b.backup_employee_id
            FROM project_deadlines p
            LEFT JOIN backup_assignments b
                ON p.project_id = b.project_id
            """
        ).fetchall()

        for project in projects:

            deadline = parse_date(project["deadline_date"])

            if not deadline:
                continue

            employee_name = employees.get(
                project["employee_id"],
                project["employee_id"]
            )

            backup_id = project["backup_employee_id"]

            backup_name = employees.get(
                backup_id, "No backup assigned"
            ) if backup_id else "No backup assigned"

            description = (
                f"Primary owner: {employee_name}. "
                f"Backup: {backup_name}. "
                f"Priority: {project['priority']}. "
                f"Status: {project['status']}."
            )

            save_event(
                connection,
                f"PROJECT_{project['project_id']}",
                "Project Deadline",
                project["project_name"],
                description,
                deadline,
                employee_id=project["employee_id"],
                reference_id=project["project_id"],
                status=project["status"],
                priority=project["priority"] or "Normal"
            )

        connection.commit()

        return {
            "message": "Timeline refreshed successfully.",
            "events_created": connection.execute(
                "SELECT COUNT(*) FROM timeline_events"
            ).fetchone()[0]
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# RETRIEVE TIMELINE
# ============================================================

def get_timeline(start_date=None, end_date=None, event_type=None):

    create_timeline_table()

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:
        query = """
            SELECT *
            FROM timeline_events
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND COALESCE(end_date, event_date) >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND event_date <= ?"
            params.append(str(end_date))

        if event_type and event_type != "All":
            query += " AND event_type = ?"
            params.append(event_type)

        query += " ORDER BY event_date ASC"

        rows = connection.execute(query, params).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


# ============================================================
# TIMELINE ALERTS
# ============================================================

def get_timeline_alerts():

    today = date.today()
    events = get_timeline()

    alerts = []

    for event in events:

        event_date = parse_date(event["event_date"])

        if not event_date:
            continue

        days_remaining = (event_date - today).days

        event_type = event["event_type"]
        status = (event["status"] or "").lower()

        # Overdue manager approval
        if (
            event_type == "Approval Deadline"
            and status == "pending"
            and days_remaining < 0
        ):
            alerts.append({
                "alert_type": "Overdue Approval",
                "title": event["title"],
                "date": event["event_date"],
                "message": (
                    f"Approval deadline passed "
                    f"{abs(days_remaining)} day(s) ago."
                ),
                "priority": "High",
                "reference_id": event["reference_id"]
            })

        # Upcoming or expired comp-off
        elif event_type == "Comp-off Expiry":

            if status == "expired":
                alerts.append({
                    "alert_type": "Expired Comp-off",
                    "title": event["title"],
                    "date": event["event_date"],
                    "message": event["description"],
                    "priority": "High",
                    "reference_id": event["reference_id"]
                })

            elif (
                status == "available"
                and 0 <= days_remaining <= COMPOFF_EXPIRY_WARNING_DAYS
            ):
                alerts.append({
                    "alert_type": "Expiring Comp-off",
                    "title": event["title"],
                    "date": event["event_date"],
                    "message": event["description"],
                    "priority": "High",
                    "reference_id": event["reference_id"]
                })

        # Upcoming project deadline
        elif (
            event_type == "Project Deadline"
            and status.lower() != "completed"
            and 0 <= days_remaining <= PROJECT_DEADLINE_WARNING_DAYS
        ):
            alerts.append({
                "alert_type": "Upcoming Project Deadline",
                "title": event["title"],
                "date": event["event_date"],
                "message": event["description"],
                "priority": event["priority"],
                "reference_id": event["reference_id"]
            })

    return sorted(
        alerts,
        key=lambda item: (item["date"], item["priority"])
    )


# ============================================================
# FIND OVERLAPPING LEAVE REQUESTS
# ============================================================

def get_overlapping_leave_requests(start_date=None, end_date=None):

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:
        query = """
            SELECT
                a.request_id AS request_1,
                a.employee_id AS employee_1,
                a.start_date AS start_1,
                a.end_date AS end_1,
                a.status AS status_1,
                b.request_id AS request_2,
                b.employee_id AS employee_2,
                b.start_date AS start_2,
                b.end_date AS end_2,
                b.status AS status_2
            FROM leave_requests a
            JOIN leave_requests b
                ON a.request_id < b.request_id
                AND a.employee_id != b.employee_id
                AND a.start_date <= b.end_date
                AND a.end_date >= b.start_date
            WHERE LOWER(a.status) IN ('approved', 'pending')
              AND LOWER(b.status) IN ('approved', 'pending')
        """

        params = []

        if start_date:
            query += " AND a.end_date >= ? AND b.end_date >= ?"
            params.extend([str(start_date), str(start_date)])

        if end_date:
            query += " AND a.start_date <= ? AND b.start_date <= ?"
            params.extend([str(end_date), str(end_date)])

        query += " ORDER BY a.start_date"

        rows = connection.execute(query, params).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


# ============================================================
# TIMELINE SUMMARY
# ============================================================

def get_timeline_summary():

    events = get_timeline()
    alerts = get_timeline_alerts()

    summary = {}

    for event in events:
        event_type = event["event_type"]
        summary[event_type] = summary.get(event_type, 0) + 1

    return {
        "total_events": len(events),
        "alerts": len(alerts),
        "event_counts": summary
    }
