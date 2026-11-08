import streamlit as st
import pandas as pd
from datetime import date, timedelta

from src.leave_management.manager_actions import make_leave_decision
from src.leave_management.leave_request_service import submit_leave_request
from src.leave_management.leave_calculator import evaluate_leave_request
from src.analytics.project_risk_analysis import get_project_risks

from src.rag.rag_assistant import (
    ask_hr_question,
    refresh_policy_index
)

from src.analytics.attendance_analysis import (
    get_employee_attendance_summary,
    get_department_attendance_summary,
    get_monthly_attendance_summary,
    get_attendance_by_month
)
from src.analytics.leave_analysis import (
    get_leave_summary,
    get_leave_type_summary,
    get_department_leave_summary,
    get_employee_leave_summary,
    get_monthly_leave_summary,
    get_pending_leave_summary
)
from src.leave_management.leave_database import (
    get_employee_details,
    get_employee_leave_requests,
    get_all_pending_requests,
    get_pending_request_details
)

from src.analytics import (
    get_attendance_summary,
    get_workforce_summary,
    get_team_availability
)


from src.analytics.timeline_manager import (
    sync_timeline,
    get_timeline,
    get_timeline_alerts,
    get_overlapping_leave_requests,
    get_timeline_summary
)

from src.leave_management.comp_off_tracker import (
    get_comp_off_summary,
    get_comp_off_records,
    validate_comp_off_usage,
    use_comp_off,
    get_all_comp_off_records
)



# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI HR Assistant",
    page_icon="ðŸ¤–",
    layout="wide"
)

st.title("ðŸ¤– AI-Powered HR Assistant")
st.caption("Leave Management | Attendance | Workforce Planning")

st.divider()


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("Navigation")

role = st.sidebar.selectbox(
    "Select User Role",
    ["Employee", "Manager / HR"]
)

# Refresh timeline events from the latest HR database records
timeline_sync_result = sync_timeline()


# ==========================================
# EMPLOYEE DASHBOARD
# ==========================================


if role == "Employee":

    st.header("Employee Dashboard")

    employee_id = st.sidebar.selectbox(
        "Select Employee",
        [f"EMP00{i}" for i in range(1, 10)] + ["EMP010"]
    )

    employee = get_employee_details(employee_id)

    if employee:

        st.subheader(f"Welcome, {employee[1]}")

        col1, col2, col3 = st.columns(3)

        col1.metric("Department", employee[2])
        col2.metric("Annual Leave Balance", employee[6])
        col3.metric("Sick Leave Balance", employee[7])

        st.divider()

        # ==========================================
        # LEAVE APPLICATION FORM
        # ==========================================

        st.subheader("Apply for Leave")

        with st.form("leave_application_form"):

            leave_type = st.selectbox(
                "Leave Type",
                ["Annual", "Sick"]
            )

            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")

            reason = st.text_area("Reason for Leave")

            submit = st.form_submit_button(
                "Submit Leave Request"
            )

            if submit:

                result = submit_leave_request(
                    employee_id,
                    leave_type,
                    start_date.isoformat(),
                    end_date.isoformat(),
                    reason
                )

                if isinstance(result, dict):

                    st.success(result["message"])

                    st.info(
                        "Request ID: " + result["request_id"]
                    )

                    st.subheader(
                        "AI Leave Eligibility Assessment"
                    )

                    st.write(result["assessment"])

                    st.warning(
                        "This is an advisory recommendation. "
                        "Final approval must come from your manager or HR."
                    )

                else:
                    st.error(result)

        st.divider()

        # ==========================================
        # SINGLE HR CHATBOT
        # ==========================================

        st.subheader("ðŸ¤– Ask HR Assistant")

st.write(
    "Ask questions about company leave policies, "
    "your leave balance and leave requests."
)

hr_question = st.text_input(
    "Enter your question",
    placeholder="Show my leave history"
)

if st.button("Ask HR Assistant"):

    if hr_question.strip():

        with st.spinner("HR Assistant is preparing your answer..."):

            try:

                result = ask_hr_question(
                    hr_question,
                    employee_id=employee_id
                )

                st.markdown("### Answer")
                st.write(result["answer"])

                if result.get("sources"):

                    st.markdown("### Sources")

                    for source in result["sources"]:

                        st.caption(
                            f"{source['document']} | "
                            f"{source['section']} | "
                            f"{source.get('version', 'N/A')}"
                        )

                if result.get("comparison"):

                    st.markdown("### Policy Comparison")

                    st.json(result["comparison"])

            except Exception as e:

                st.error(f"Unable to process your question: {e}")

    else:

        st.warning("Please enter a question.")

        st.divider()

        # ==========================================
        # EMPLOYEE LEAVE HISTORY
        # ==========================================

        st.subheader("My Leave Requests")

        requests = get_employee_leave_requests(employee_id)

        if requests:

            df = pd.DataFrame(
                requests,
                columns=[
                    "Request ID",
                    "Employee ID",
                    "Leave Type",
                    "Start Date",
                    "End Date",
                    "Reason",
                    "Status",
                    "Applied Date"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True
            )

        else:

            st.info("No leave requests found.")

        st.divider()




        # COMP-OFF BALANCE AND USAGE
        # ==========================================

        st.subheader("My Comp-Off Balance")

        comp_off = get_comp_off_summary(employee_id)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Earned", comp_off["earned"])
        c2.metric("Available", comp_off["available"])
        c3.metric("Used", comp_off["used"])
        c4.metric("Expiring Soon", comp_off["expiring_soon"])

        st.subheader("My Comp-Off Records")

        comp_records = get_comp_off_records(employee_id)

        if comp_records:

            comp_df = pd.DataFrame(
                comp_records,
                columns=[
                    "Record ID",
                    "Employee ID",
                    "Days",
                    "Status",
                    "Expiry Date"
                ]
            )

            st.dataframe(
                comp_df,
                use_container_width=True,
                hide_index=True
            )

            available_records = [
                record for record in comp_records
                if record[3] == "Available"
            ]

            if available_records:

                selected_record = st.selectbox(
                    "Select comp-off to use",
                    available_records,
                    format_func=lambda x: (
                        f"{x[0]} - {x[2]} days "
                        f"(Expires: {x[4]})"
                    )
                )

                if st.button("Use Selected Comp-Off"):

                    valid, message = validate_comp_off_usage(
                        employee_id,
                        selected_record[0]
                    )

                    if valid:

                        success, result_message = use_comp_off(
                            employee_id,
                            selected_record[0]
                        )

                        if success:
                            st.success(result_message)
                            st.rerun()
                        else:
                            st.error(result_message)

                    else:
                        st.warning(message)

            else:
                st.info("No available comp-off records to use.")

        else:
            st.info("No comp-off records found.")


# ==========================================
# MANAGER / HR DASHBOARD
# ==========================================

else:

    st.header("ðŸ¤– Manager / HR Dashboard")

    # ==========================================
    # HR POLICY MANAGEMENT
    # ==========================================

    st.header("HR Policy Management")

    st.write(
        "Refresh the policy knowledge base after adding "
        "or updating HR policy documents."
    )

    if st.button("ðŸ”„ Refresh HR Policy Knowledge Base"):

        with st.spinner("Re-indexing HR policy documents..."):

            success, message = refresh_policy_index()

        if success:
            st.success(message)
        else:
            st.error(message)

    st.divider()

    # ==========================================
    # ORGANIZATION-WIDE COMP-OFF MANAGEMENT
    # ==========================================

    st.header("Organization-wide Comp-Off Management")

    all_comp_off = get_all_comp_off_records()

    if all_comp_off:

        comp_columns = [
            "Comp-Off ID",
            "Employee ID",
            "Earned Date",
            "Expiry Date",
            "Days",
            "Status"
        ]

        comp_df = pd.DataFrame(
            all_comp_off,
            columns=comp_columns
        )

        total_available = comp_df.loc[
            comp_df["Status"] == "Available", "Days"
        ].sum()

        total_used = comp_df.loc[
            comp_df["Status"] == "Used", "Days"
        ].sum()

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Comp-Off Records", len(comp_df))
        col2.metric("Available Comp-Off Days", total_available)
        col3.metric("Used Comp-Off Days", total_used)

        st.dataframe(
            comp_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No comp-off records available.")

    st.divider()

    # ==========================================
    # TIMELINE AND DEADLINE MANAGEMENT
    # ==========================================

    st.header("Timeline & Deadline Management")

    timeline_summary = get_timeline_summary()

    summary_col1, summary_col2 = st.columns(2)

    summary_col1.metric(
        "Total Timeline Events",
        timeline_summary["total_events"]
    )

    summary_col2.metric(
        "Active Alerts",
        timeline_summary["alerts"]
    )

    # Timeline alerts
    st.subheader("Important Alerts")

    alerts = get_timeline_alerts()

    if alerts:
        for alert in alerts:
            alert_message = (
                f"**{alert['alert_type']}**: {alert['title']}\n\n"
                f"{alert['message']}\n\n"
                f"Date: {alert['date']}"
            )

            if alert["priority"] == "High":
                st.error(alert_message)
            else:
                st.warning(alert_message)
    else:
        st.success("No active timeline alerts.")

    # Timeline filters
    st.subheader("HR Timeline")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        timeline_start = st.date_input(
            "From Date",
            value=date.today(),
            key="timeline_start_date"
        )

    with filter_col2:
        timeline_end = st.date_input(
            "To Date",
            value=date.today() + timedelta(days=30),
            key="timeline_end_date"
        )

    with filter_col3:
        timeline_type = st.selectbox(
            "Event Type",
            [
                "All",
                "Leave",
                "Request Submission",
                "Approval Deadline",
                "Return to Work",
                "Comp-off Earned",
                "Comp-off Expiry",
                "Holiday",
                "Project Deadline"
            ],
            key="timeline_event_type"
        )

    if timeline_end < timeline_start:
        st.error("End date cannot be before start date.")
    else:
        timeline_records = get_timeline(
            timeline_start,
            timeline_end,
            timeline_type
        )

        if timeline_records:
            timeline_df = pd.DataFrame(timeline_records)

            display_columns = [
                "event_type",
                "title",
                "description",
                "event_date",
                "end_date",
                "employee_id",
                "reference_id",
                "status",
                "priority"
            ]

            st.dataframe(
                timeline_df[display_columns],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(
                "No timeline events found for the selected filters."
            )

    # Overlapping leave requests across different employees
    st.subheader("Overlapping Team Leave")

    overlaps = get_overlapping_leave_requests(
        timeline_start,
        timeline_end
    )

    if overlaps:
        st.warning(
            f"{len(overlaps)} overlapping leave combinations detected."
        )

        st.dataframe(
            pd.DataFrame(overlaps),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No overlapping team leave requests detected.")

    st.divider()


    pending_requests = get_all_pending_requests()

    st.metric(
        "Pending Leave Requests",
        len(pending_requests)
    )

    # ==========================================
    # PENDING REQUEST TABLE
    # ==========================================

    if pending_requests:

        df = pd.DataFrame(
            pending_requests,
            columns=[
                "Request ID",
                "Employee ID",
                "Leave Type",
                "Start Date",
                "End Date",
                "Reason",
                "Status",
                "Applied Date"
            ]
        )

        st.subheader("Pending Leave Requests")

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.success("No pending leave requests.")

    st.divider()

    # ==========================================
    # MANAGER APPROVAL SECTION
    # ==========================================

    st.subheader("Review Leave Requests")

    if pending_requests:

        request_ids = [
            request[0] for request in pending_requests
        ]

        with st.form("manager_decision_form"):

            selected_request = st.selectbox(
                "Select Leave Request",
                request_ids
            )

            decision = st.selectbox(
                "Manager Decision",
                ["Approved", "Rejected"]
            )

            comments = st.text_area(
                "Manager Comments",
                placeholder="Enter your decision remarks..."
            )

            submit_decision = st.form_submit_button(
                "Submit Decision"
            )

            if submit_decision:

                result = make_leave_decision(
                    selected_request,
                    "MGR001",
                    decision,
                    comments
                )

                if result.startswith("Request"):

                    st.success(result)
                    st.rerun()

                else:

                    st.error(result)

    else:

        st.info("There are no requests available for review.")

    st.divider()

    # ==========================================
    # DETAILED LEAVE REQUEST REVIEW
    # ==========================================

    st.subheader("Detailed Leave Request Review")

    detailed_requests = get_pending_request_details()

    if detailed_requests:

        for request in detailed_requests:

            (
                request_id,
                employee_id,
                employee_name,
                department,
                leave_type,
                start_date,
                end_date,
                reason,
                status,
                applied_date
            ) = request

            with st.expander(
                f"{request_id} - {employee_name}"
            ):

                st.write("**Employee ID:**", employee_id)
                st.write("**Employee Name:**", employee_name)
                st.write("**Department:**", department)
                st.write("**Leave Type:**", leave_type)
                st.write("**Start Date:**", start_date)
                st.write("**End Date:**", end_date)
                st.write("**Reason:**", reason)
                st.write("**Applied Date:**", applied_date)
                st.write("**Current Status:**", status)

                st.divider()

                st.write("**AI Eligibility Assessment**")

                assessment = evaluate_leave_request(
                    employee_id,
                    leave_type,
                    start_date,
                    end_date,
                    applied_date
                )

                st.info(assessment)

                st.caption(
                    "AI assessment is advisory only. "
                    "Manager / HR makes the final decision."
                )

    else:

        st.info(
            "No pending requests available for detailed review."
        )

    st.divider()

    # ==========================================
    # LEAVE ANALYTICS
    # ==========================================

    st.subheader("Leave Analytics")

    leave_summary = get_leave_summary()

    # Leave KPI cards
    leave_col1, leave_col2, leave_col3, leave_col4 = st.columns(4)

    leave_col1.metric(
        "Total Requests",
        leave_summary["total_requests"]
    )

    leave_col2.metric(
        "Approved",
        leave_summary["approved"]
    )

    leave_col3.metric(
        "Pending",
        leave_summary["pending"]
    )

    leave_col4.metric(
        "Rejected",
        leave_summary["rejected"]
    )

    st.caption(
        "These metrics summarize recorded leave requests. "
        "They describe request status, not employee performance."
    )

    # Leave type breakdown
    st.markdown("### Leave Type Breakdown")

    leave_type_data = get_leave_type_summary()

    if not leave_type_data.empty:

        st.bar_chart(
            leave_type_data.set_index("leave_type")
        )

        st.dataframe(
            leave_type_data,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No leave type data available.")

    # Department-wise leave analysis
    st.markdown("### Department-wise Leave Requests")

    department_leave_data = get_department_leave_summary()

    if not department_leave_data.empty:

        st.bar_chart(
            department_leave_data.set_index("department")
        )

        st.dataframe(
            department_leave_data,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No department-wise leave data available.")

    # Employee-wise leave analysis
    st.markdown("### Employee-wise Leave Requests")

    employee_leave_data = get_employee_leave_summary()

    if not employee_leave_data.empty:

        st.dataframe(
            employee_leave_data,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No employee leave data available.")

    # Monthly leave trend
    st.markdown("### Monthly Leave Request Trend")

    monthly_leave_data = get_monthly_leave_summary()

    if not monthly_leave_data.empty:

        st.line_chart(
            monthly_leave_data.set_index("month")[
                ["request_count"]
            ]
        )

        st.dataframe(
            monthly_leave_data,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No monthly leave data available.")

    # Pending requests by department
    st.markdown("### Pending Leave Requests by Department")

    pending_leave_data = get_pending_leave_summary()

    if not pending_leave_data.empty:

        st.bar_chart(
            pending_leave_data.set_index("department")[
                ["pending_requests"]
            ]
        )

        st.dataframe(
            pending_leave_data,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success("There are no pending leave requests.")

    st.divider()

    # ==========================================
    # ATTENDANCE ANALYTICS
    # ==========================================

    st.subheader("Attendance Analytics")

    attendance = get_attendance_summary()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Records", attendance["total_records"])
    c2.metric("Present", attendance["present"])
    c3.metric("Absent", attendance["absent"])
    c4.metric(
        "Attendance",
        f'{attendance["attendance_percentage"]}%'
    )

    st.caption(
        "Attendance percentage = (Present + Work From Home) / "
        "Total attendance records. It describes the available sample "
        "records and is not a disciplinary or performance measure."
    )

    # Attendance filters
    st.markdown("### Attendance Filters")

    employee_attendance = get_employee_attendance_summary()
    department_attendance = get_department_attendance_summary()
    monthly_attendance = get_monthly_attendance_summary()

    attendance_filter_col1, attendance_filter_col2, attendance_filter_col3 = st.columns(3)

    with attendance_filter_col1:
        employee_options = ["All"] + (
            sorted(employee_attendance["name"].dropna().unique().tolist())
            if not employee_attendance.empty else []
        )
        selected_employee = st.selectbox(
            "Employee",
            employee_options,
            key="attendance_employee_filter"
        )

    with attendance_filter_col2:
        department_options = ["All"] + (
            sorted(department_attendance["department"].dropna().unique().tolist())
            if not department_attendance.empty else []
        )
        selected_department = st.selectbox(
            "Department",
            department_options,
            key="attendance_department_filter"
        )

    with attendance_filter_col3:
        month_options = (
            sorted(monthly_attendance["month"].dropna().unique().tolist())
            if not monthly_attendance.empty else []
        )
        selected_month = st.selectbox(
            "Month",
            ["All"] + month_options,
            key="attendance_month_filter"
        )

    # Employee-level filtered attendance
    st.markdown("### Employee-wise Attendance")

    filtered_employee_attendance = employee_attendance.copy()

    if selected_employee != "All" and not filtered_employee_attendance.empty:
        filtered_employee_attendance = filtered_employee_attendance[
            filtered_employee_attendance["name"] == selected_employee
        ]

    if selected_department != "All" and not filtered_employee_attendance.empty:
        filtered_employee_attendance = filtered_employee_attendance[
            filtered_employee_attendance["department"] == selected_department
        ]

    if not filtered_employee_attendance.empty:
        st.dataframe(
            filtered_employee_attendance,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No employee attendance records match these filters.")

    # Department-level attendance
    st.markdown("### Department-wise Attendance")

    filtered_department_attendance = department_attendance.copy()

    if selected_department != "All" and not filtered_department_attendance.empty:
        filtered_department_attendance = filtered_department_attendance[
            filtered_department_attendance["department"] == selected_department
        ]

    if not filtered_department_attendance.empty:
        st.bar_chart(
            filtered_department_attendance.set_index("department")[
                ["attendance_percentage"]
            ]
        )
        st.dataframe(
            filtered_department_attendance,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No department attendance records match these filters.")

    # Monthly attendance
    st.markdown("### Monthly Attendance Trend")

    if not monthly_attendance.empty:
        if selected_month == "All":
            st.line_chart(
                monthly_attendance.set_index("month")[
                    ["attendance_percentage"]
                ]
            )
            st.dataframe(
                monthly_attendance,
                use_container_width=True,
                hide_index=True
            )
        else:
            selected_month_data = get_attendance_by_month(selected_month)

            if selected_employee != "All":
                selected_month_data = selected_month_data[
                    selected_month_data["name"] == selected_employee
                ]

            if selected_department != "All":
                selected_month_data = selected_month_data[
                    selected_month_data["department"] == selected_department
                ]

            if not selected_month_data.empty:
                month_present = (
                    selected_month_data["status"].str.lower() == "present"
                ).sum()
                month_absent = (
                    selected_month_data["status"].str.lower() == "absent"
                ).sum()
                month_wfh = (
                    selected_month_data["status"].str.lower() == "work from home"
                ).sum()
                month_total = len(selected_month_data)
                month_percentage = round(
                    (month_present + month_wfh) / month_total * 100, 2
                ) if month_total else 0

                month_col1, month_col2, month_col3, month_col4 = st.columns(4)
                month_col1.metric("Records", month_total)
                month_col2.metric("Present", int(month_present))
                month_col3.metric("Absent", int(month_absent))
                month_col4.metric("Attendance", f"{month_percentage}%")

                st.dataframe(
                    selected_month_data[
                        [
                            "employee_id",
                            "name",
                            "department",
                            "date",
                            "status"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No attendance records match the selected month and filters.")
    else:
        st.info("No monthly attendance data is available.")

    st.divider()

    # ==========================================
    # WORKFORCE DISTRIBUTION
    # ==========================================

    st.subheader("Workforce Distribution")

    workforce = get_workforce_summary()

    st.metric(
        "Total Employees",
        workforce["total_employees"]
    )

    department_df = pd.DataFrame(
        list(workforce["department_counts"].items()),
        columns=["Department", "Employees"]
    )

    st.bar_chart(
        department_df.set_index("Department")
    )

    st.divider()

    # ==========================================
    # TEAM AVAILABILITY
    # ==========================================

    st.subheader("Team Availability")

    availability = get_team_availability(
        "2026-11-09",
        "2026-11-11"
    )

    availability_df = pd.DataFrame(availability).T

    st.dataframe(
        availability_df,
        use_container_width=True
    )

    st.divider()

    # ==========================================
    # PROJECT DEADLINE & RISK MONITORING
    # ==========================================

    st.subheader("Project Deadline & Risk Monitoring")

    project_risks = get_project_risks()

    if project_risks:

        project_df = pd.DataFrame(project_risks)

        st.dataframe(
            project_df[
                [
                    "project_name",
                    "employee",
                    "deadline",
                    "priority",
                    "backup_employee",
                    "risk"
                ]
            ],
            use_container_width=True
        )

        risk_count = sum(
            1 for project in project_risks
            if project["risk"] == "Potential Leave Conflict"
        )

        st.metric(
            "Projects with Potential Leave Conflict",
            risk_count
        )

    else:

        st.info("No project records found.")


# ==========================================
# WORKFORCE PLANNING RECOMMENDATIONS
# ==========================================

st.header("Workforce Planning Recommendations")

st.caption(
    "Recommendations are based on scheduled leave, team availability, "
    "project deadlines and configured backup assignments. "
    "Managers make the final staffing decisions."
)

planning_col1, planning_col2 = st.columns(2)

with planning_col1:
    planning_start = st.date_input(
        "Planning Start Date",
        value=date.today(),
        key="planning_start"
    )

with planning_col2:
    planning_end = st.date_input(
        "Planning End Date",
        value=date.today() + timedelta(days=7),
        key="planning_end"
    )

if planning_end < planning_start:
    st.error("End date cannot be before start date.")

else:
    planning_data = get_team_availability(
        planning_start,
        planning_end
    )

    if planning_data:

        # Convert dictionary into a DataFrame
        planning_df = pd.DataFrame.from_dict(
            planning_data,
            orient="index"
        ).reset_index()

        planning_df.rename(
            columns={"index": "department"},
            inplace=True
        )

        if not planning_df.empty:

            st.subheader("Team Capacity Overview")

            required_columns = {
                "department",
                "total_employees",
                "employees_on_leave",
                "available_employees"
            }

            if required_columns.issubset(planning_df.columns):

                planning_df["coverage_percentage"] = (
                    planning_df["available_employees"]
                    / planning_df["total_employees"].replace(0, 1)
                ) * 100

                st.dataframe(
                    planning_df,
                    use_container_width=True,
                    hide_index=True
                )

                st.subheader("Staffing Recommendations")

                for _, team in planning_df.iterrows():

                    department = team["department"]
                    total = int(team["total_employees"])
                    on_leave = int(team["employees_on_leave"])
                    available = int(team["available_employees"])
                    coverage = team["coverage_percentage"]

                    st.markdown(f"### {department}")

                    if coverage < 50:
                        st.error(
                            f"Low coverage: {available} of {total} "
                            f"employees available ({coverage:.1f}%). "
                            "Manager review and backup planning required."
                        )

                    elif on_leave > 0:
                        st.warning(
                            f"{available} of {total} employees available "
                            f"({coverage:.1f}%). Review workload "
                            "distribution and backup assignments."
                        )

                    else:
                        st.success(
                            f"Full team availability: {available} "
                            "employees available."
                        )

            else:
                st.warning(
                    "Team availability data does not contain the "
                    "expected columns."
                )

        else:
            st.info("No workforce planning data for this period.")

    else:
        st.info("No team availability records found.")
