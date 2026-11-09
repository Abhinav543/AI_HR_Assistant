"""AI-Powered HR Assistant — redesigned Streamlit presentation layer.

The existing business logic, database access, analytics and RAG modules are
intentionally kept in src/ and are called through their existing interfaces.
"""

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.leave_management.manager_actions import make_leave_decision
from src.leave_management.leave_request_service import submit_leave_request
from src.leave_management.leave_calculator import evaluate_leave_request
from src.analytics.project_risk_analysis import get_project_risks
from src.rag.rag_assistant import ask_hr_question, refresh_policy_index
from src.analytics.attendance_analysis import (
    get_employee_attendance_summary,
    get_department_attendance_summary,
    get_monthly_attendance_summary,
    get_attendance_by_month,
)
from src.analytics.leave_analysis import (
    get_leave_summary,
    get_leave_type_summary,
    get_department_leave_summary,
    get_employee_leave_summary,
    get_monthly_leave_summary,
    get_pending_leave_summary,
)
from src.leave_management.leave_database import (
    get_employee_details,
    get_employee_leave_requests,
    get_all_pending_requests,
    get_pending_request_details,
)
from src.analytics import (
    get_attendance_summary,
    get_workforce_summary,
    get_team_availability,
)
from src.analytics.timeline_manager import (
    sync_timeline,
    get_timeline,
    get_timeline_alerts,
    get_overlapping_leave_requests,
    get_timeline_summary,
)
from src.leave_management.comp_off_tracker import (
    get_comp_off_summary,
    get_comp_off_records,
    validate_comp_off_usage,
    use_comp_off,
    get_all_comp_off_records,
)


# -----------------------------------------------------------------------------
# PAGE CONFIG + VISUAL SYSTEM
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PeopleOS | AI HR Assistant",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#172B4D; --muted:#64748B; --blue:#315D9B; --blue-soft:#EAF1FB; --line:#E7ECF3; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:#F6F8FC; color:var(--ink); }
.block-container { padding-top:1.65rem; padding-bottom:3rem; max-width:1500px; }
h1,h2,h3,h4 { font-family:'Manrope',sans-serif !important; color:#172B4D; letter-spacing:-.025em; }
h1 { font-size:2rem !important; font-weight:800 !important; }
h2 { font-size:1.45rem !important; font-weight:750 !important; }
h3 { font-size:1.08rem !important; font-weight:700 !important; }
p, label, .stCaption { color:#52627A; }
[data-testid="stSidebar"] { background:#14263F; border-right:1px solid #203653; }
[data-testid="stSidebar"] * { color:#E8EFF9 !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#AFC0D8 !important; }
[data-testid="stSidebar"] .stSelectbox label { color:#DCE7F5 !important; }
[data-testid="stSidebar"] hr { border-color:#30445F; }
[data-testid="stMetric"] { background:#FFFFFF; border:1px solid var(--line); padding:17px 18px; border-radius:14px; box-shadow:0 2px 8px rgba(25,45,75,.035); }
[data-testid="stMetricLabel"] { color:#64748B !important; font-weight:600; }
[data-testid="stMetricValue"] { color:#172B4D !important; font-family:'Manrope',sans-serif; font-weight:800; }
div[data-testid="stForm"], div[data-testid="stExpander"], div[data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--line) !important; border-radius:14px !important; }
.stButton > button, .stFormSubmitButton > button { border-radius:10px; border:1px solid #315D9B; background:#315D9B; color:white; font-weight:650; padding:.55rem 1rem; }
.stButton > button:hover, .stFormSubmitButton > button:hover { background:#244B82; border-color:#244B82; color:white; }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
[data-testid="stAlert"] { border-radius:12px; }
section[data-testid="stSidebar"] .stRadio label { padding:.2rem 0; }
.hero { background:linear-gradient(115deg,#17365F 0%,#315D9B 58%,#537EB6 100%); padding:25px 28px; border-radius:18px; color:white; margin-bottom:22px; box-shadow:0 10px 26px rgba(36,76,128,.13); }
.hero h1 { color:white !important; margin:0 0 5px 0; }
.hero p { color:#DCE8F8 !important; margin:0; font-size:.95rem; }
.section-kicker { color:#6E85A4; text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; font-weight:800; margin-bottom:5px; }
.info-card { background:#fff; border:1px solid #E7ECF3; border-radius:14px; padding:16px 18px; min-height:100px; }
.info-card .label { color:#718096; font-size:.8rem; font-weight:600; }
.info-card .value { color:#172B4D; font:800 1.55rem 'Manrope',sans-serif; margin-top:5px; }
.info-card .hint { color:#718096; font-size:.76rem; margin-top:3px; }
.small-muted { color:#718096; font-size:.82rem; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# HELPERS — presentation only; calls existing project services.
# -----------------------------------------------------------------------------
def page_header(kicker: str, title: str, subtitle: str = ""):
    st.markdown(f'<div class="section-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def hero(title: str, subtitle: str, eyebrow: str = "PEOPLEOS · HR WORKSPACE"):
    st.markdown(
        f'<div class="hero"><div style="font-size:.72rem;font-weight:800;letter-spacing:.14em;opacity:.8">{eyebrow}</div>'
        f'<h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def metric_row(items):
    cols = st.columns(len(items))
    for col, (label, value, help_text) in zip(cols, items):
        col.metric(label, value, help=help_text)


def safe_dataframe(df, **kwargs):
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True, **kwargs)
    else:
        st.info("There is no data to display for this selection.")


def employee_options():
    path = Path("data/employees.csv")
    if path.exists():
        try:
            data = pd.read_csv(path)
            if "employee_id" in data.columns:
                return data["employee_id"].dropna().astype(str).tolist()
        except Exception:
            pass
    return [f"EMP{i:03d}" for i in range(1, 11)]


def display_leave_history(employee_id: str):
    requests = get_employee_leave_requests(employee_id)
    if requests:
        df = pd.DataFrame(requests, columns=[
            "Request ID", "Employee ID", "Leave Type", "Start Date", "End Date",
            "Reason", "Status", "Applied Date",
        ])
        safe_dataframe(df)
    else:
        st.info("You have not submitted any leave requests yet.")


def display_comp_off_employee(employee_id: str):
    comp = get_comp_off_summary(employee_id)
    metric_row([
        ("Earned days", comp.get("earned", 0), None),
        ("Available days", comp.get("available", 0), None),
        ("Used days", comp.get("used", 0), None),
        ("Expiring soon", comp.get("expiring_soon", 0), None),
    ])
    records = get_comp_off_records(employee_id)
    if not records:
        st.info("No comp-off records found.")
        return
    comp_df = pd.DataFrame(records, columns=["Record ID", "Employee ID", "Days", "Status", "Expiry Date"])
    safe_dataframe(comp_df)
    available = [r for r in records if r[3] == "Available"]
    if available:
        with st.form("use_comp_off_form"):
            selected = st.selectbox(
                "Select an available comp-off record",
                available,
                format_func=lambda x: f"{x[0]} · {x[2]} day(s) · expires {x[4]}",
            )
            submitted = st.form_submit_button("Use selected comp-off")
        if submitted:
            valid, message = validate_comp_off_usage(employee_id, selected[0])
            if valid:
                success, result_message = use_comp_off(employee_id, selected[0])
                (st.success if success else st.error)(result_message)
                if success:
                    st.rerun()
            else:
                st.warning(message)


def display_hr_chat(employee_id=None, key_prefix="hr"):
    st.markdown("Ask questions about HR policies, leave rules, your leave balance or request history.")
    suggested = [
        "How many annual leaves are allowed?",
        "What is the sick leave policy?",
        "Show my leave history",
        "What happens when a leave request is pending?",
    ]
    st.caption("Try: " + " · ".join(suggested[:3]))
    with st.form(f"{key_prefix}_chat_form"):
        question = st.text_input("Your question", placeholder="Ask the HR assistant…")
        ask = st.form_submit_button("Ask HR Assistant")
    if ask:
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Searching HR knowledge and preparing an answer…"):
                try:
                    result = ask_hr_question(question.strip(), employee_id=employee_id)
                    st.markdown("#### HR Assistant")
                    st.markdown(result.get("answer", "No answer was returned."))
                    sources = result.get("sources") or []
                    if sources:
                        with st.expander("Sources used"):
                            for source in sources:
                                st.caption(
                                    f"{source.get('document', 'Document')} · "
                                    f"{source.get('section', 'Section')} · "
                                    f"Version {source.get('version', 'N/A')}"
                                )
                    comparison = result.get("comparison")
                    if comparison:
                        with st.expander("Policy comparison"):
                            st.json(comparison)
                except Exception as exc:
                    st.error(f"The HR assistant could not complete this request: {exc}")


def leave_application_form(employee_id: str):
    with st.form(f"leave_application_{employee_id}"):
        left, right = st.columns(2)
        with left:
            leave_type = st.selectbox("Leave type", ["Annual", "Sick"])
            start_date = st.date_input("Start date", value=date.today() + timedelta(days=1))
        with right:
            end_date = st.date_input("End date", value=date.today() + timedelta(days=1))
            reason = st.text_input("Reason", placeholder="Briefly explain your leave request")
        submitted = st.form_submit_button("Submit leave request")
    if submitted:
        result = submit_leave_request(
            employee_id, leave_type, start_date.isoformat(), end_date.isoformat(), reason
        )
        if isinstance(result, dict):
            st.success(result.get("message", "Leave request submitted."))
            if result.get("request_id"):
                st.info(f"Request ID: {result['request_id']}")
            if result.get("assessment"):
                st.markdown("**Eligibility assessment**")
                st.info(result["assessment"])
            st.caption("The assessment is advisory. Your manager or HR makes the final decision.")
        else:
            st.error(str(result))


# -----------------------------------------------------------------------------
# DATA REFRESH — same existing timeline service as the original app.
# -----------------------------------------------------------------------------
try:
    sync_timeline()
except Exception as exc:
    st.warning(f"Timeline data could not be refreshed: {exc}")


# -----------------------------------------------------------------------------
# SIDEBAR + ROLE-BASED NAVIGATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<div style='font:800 1.2rem Manrope;color:white'>◈ PeopleOS</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:.75rem;color:#AFC0D8;margin:3px 0 18px'>AI-powered HR workspace</div>", unsafe_allow_html=True)
    st.divider()
    role = st.selectbox("Workspace", ["Employee", "HR / Admin"], index=0)
    if role == "Employee":
        employee_id = st.selectbox("Employee profile", employee_options())
        nav_items = ["Overview", "Leave & Comp-off", "My Attendance", "AI HR Assistant"]
    elif role == "Manager":
        employee_id = None
        nav_items = ["Overview", "Leave Approvals", "Team Attendance", "Workforce Planning", "AI HR Assistant"]
    else:
        employee_id = None
        nav_items = ["Overview", "Employee & Leave Analytics", "Attendance Analytics", "Leave Approvals", "Workforce Planning", "Timeline & Deadlines", "Comp-off Management", "Policy Management", "AI HR Assistant"]
    page = st.radio("NAVIGATION", nav_items, label_visibility="visible")
    st.divider()
    

def render_workforce_planning():
    left, right = st.columns(2)
    start = left.date_input("Planning start date", value=date.today(), key=f"planning_start_{role}")
    end = right.date_input("Planning end date", value=date.today() + timedelta(days=7), key=f"planning_end_{role}")
    if end < start:
        st.error("End date cannot be before start date.")
        return
    planning = get_team_availability(start, end)
    if not planning:
        st.info("No team availability data found for this period.")
        return
    df = pd.DataFrame.from_dict(planning, orient="index").reset_index().rename(columns={"index": "department"})
    expected = {"department", "total_employees", "employees_on_leave", "available_employees"}
    if not expected.issubset(df.columns):
        st.warning("Team availability data is missing expected fields.")
        safe_dataframe(df)
        return
    df["coverage_percentage"] = (df["available_employees"] / df["total_employees"].replace(0, 1)) * 100
    metric_row([
        ("Departments", len(df), None),
        ("Employees", int(df["total_employees"].sum()), None),
        ("Available", int(df["available_employees"].sum()), None),
        ("On leave", int(df["employees_on_leave"].sum()), None),
    ])
    fig = px.bar(df, x="department", y="coverage_percentage", color="coverage_percentage",
                 color_continuous_scale=["#D97757", "#E8B85B", "#3A9D79"], range_color=[0, 100],
                 labels={"department": "Department", "coverage_percentage": "Coverage (%)"})
    fig.add_hline(y=50, line_dash="dash", line_color="#D97757", annotation_text="50% review threshold")
    fig.update_layout(height=350, margin=dict(l=5, r=5, t=25, b=5), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Team capacity details")
    safe_dataframe(df)
    st.subheader("Staffing recommendations")
    for _, team in df.iterrows():
        coverage = float(team["coverage_percentage"])
        label = f"{team['department']} · {int(team['available_employees'])}/{int(team['total_employees'])} available · {coverage:.1f}% coverage"
        if coverage < 50:
            st.error(label + " — low coverage. Manager review and backup planning required.")
        elif int(team["employees_on_leave"]) > 0:
            st.warning(label + " — review workload distribution and backup assignments.")
        else:
            st.success(label + " — no leave-related capacity reduction detected.")



# -----------------------------------------------------------------------------
# EMPLOYEE WORKSPACE
# -----------------------------------------------------------------------------
if role == "Employee":
    employee = get_employee_details(employee_id)
    if not employee:
        st.error(f"Employee record {employee_id} was not found in the database.")
        st.stop()
    employee_name = employee[1]
    department = employee[2]

    if page == "Overview":
        hero(f"Welcome back, {employee_name.split()[0]}", "Your personal HR workspace — leave, attendance and policy support in one place.", "EMPLOYEE SELF-SERVICE")
        metric_row([
            ("Department", department, "Your current department"),
            ("Annual leave balance", employee[6], "Available annual leave balance"),
            ("Sick leave balance", employee[7], "Available sick leave balance"),
        ])
        st.subheader("Your recent leave requests")
        display_leave_history(employee_id)
        st.subheader("Comp-off snapshot")
        comp = get_comp_off_summary(employee_id)
        metric_row([
            ("Available", comp.get("available", 0), None),
            ("Earned", comp.get("earned", 0), None),
            ("Used", comp.get("used", 0), None),
        ])
        st.info("Use the navigation on the left to apply for leave, review attendance or ask the HR assistant.")

    elif page == "Leave & Comp-off":
        hero("Leave & comp-off", "Submit a request and keep track of your leave entitlements.", "EMPLOYEE SERVICES")
        tab1, tab2, tab3 = st.tabs(["Apply for leave", "My requests", "Comp-off"])
        with tab1:
            leave_application_form(employee_id)
        with tab2:
            display_leave_history(employee_id)
        with tab3:
            display_comp_off_employee(employee_id)

    elif page == "My Attendance":
        hero("My attendance", "Review your recorded attendance summary and monthly history.", "EMPLOYEE SERVICES")
        attendance_df = get_employee_attendance_summary()
        if not attendance_df.empty:
            mine = attendance_df[attendance_df["employee_id"].astype(str) == str(employee_id)]
            if not mine.empty:
                row = mine.iloc[0]
                metric_row([
                    ("Attendance rate", f"{row.get('attendance_percentage', 0)}%", None),
                    ("Present", int(row.get("present", 0)), None),
                    ("Absent", int(row.get("absent", 0)), None),
                    ("Work from home", int(row.get("work_from_home", 0)), None),
                ])
            else:
                st.info("No attendance records are available for your profile.")
            monthly = get_monthly_attendance_summary()
            if not monthly.empty:
                st.subheader("Organization monthly attendance trend")
                fig = px.line(monthly, x="month", y="attendance_percentage", markers=True,
                              labels={"month": "Month", "attendance_percentage": "Attendance (%)"})
                fig.update_layout(margin=dict(l=10, r=10, t=25, b=10), height=300)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No attendance records are available.")

    elif page == "AI HR Assistant":
        hero("Ask your HR assistant", "Get policy-grounded answers from the HR knowledge base.", "AI POLICY ASSISTANT")
        display_hr_chat(employee_id, "employee")


# -----------------------------------------------------------------------------
# HR / ADMIN WORKSPACE
# -----------------------------------------------------------------------------
elif role == "HR / Admin":
    if page == "Overview":
        hero("HR command centre", "Organization-wide people operations at a glance.", "HR ADMINISTRATION")
        workforce = get_workforce_summary()
        attendance = get_attendance_summary()
        leaves = get_leave_summary()
        pending = get_all_pending_requests()
        comp_records = get_all_comp_off_records()
        metric_row([
            ("Employees", workforce.get("total_employees", 0), "Current employee dataset"),
            ("Attendance", f'{attendance.get("attendance_percentage", 0)}%', "Present plus work from home"),
            ("Pending leave", len(pending), "Requests awaiting review"),
            ("Leave requests", leaves.get("total_requests", 0), "All recorded requests"),
        ])
        st.subheader("Workforce by department")
        department_df = pd.DataFrame(list(workforce.get("department_counts", {}).items()), columns=["Department", "Employees"])
        if not department_df.empty:
            fig = px.pie(department_df, names="Department", values="Employees", hole=.58)
            fig.update_layout(height=340, margin=dict(l=10, r=10, t=15, b=10), legend_title="Department")
            st.plotly_chart(fig, use_container_width=True)
        st.subheader("Priority alerts")
        try:
            alerts = get_timeline_alerts()
            if alerts:
                for alert in alerts[:8]:
                    msg = f"**{alert['title']}** — {alert['message']} · {alert['date']}"
                    (st.error if alert.get("priority") == "High" else st.warning)(msg)
            else:
                st.success("No active timeline alerts.")
        except Exception as exc:
            st.warning(f"Timeline alerts unavailable: {exc}")

    elif page == "Employee & Leave Analytics":
        hero("Employee & leave analytics", "Understand leave demand, request status and department trends.", "HR ANALYTICS")
        summary = get_leave_summary()
        metric_row([
            ("Total requests", summary["total_requests"], None),
            ("Approved", summary["approved"], None),
            ("Pending", summary["pending"], None),
            ("Rejected", summary["rejected"], None),
        ])
        leave_type = get_leave_type_summary()
        department_leave = get_department_leave_summary()
        monthly_leave = get_monthly_leave_summary()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Leave type")
            if not leave_type.empty:
                fig = px.pie(leave_type, names="leave_type", values="request_count", hole=.55)
                fig.update_layout(height=310, margin=dict(l=5, r=5, t=20, b=5))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No leave type data.")
        with c2:
            st.subheader("Requests by department")
            if not department_leave.empty:
                fig = px.bar(department_leave, x="department", y="request_count", color="department")
                fig.update_layout(showlegend=False, height=310, margin=dict(l=5, r=5, t=20, b=5))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No department leave data.")
        st.subheader("Monthly leave trend")
        if not monthly_leave.empty:
            fig = px.line(monthly_leave, x="month", y="request_count", markers=True)
            fig.update_layout(height=300, margin=dict(l=5, r=5, t=20, b=5), yaxis_title="Requests")
            st.plotly_chart(fig, use_container_width=True)
        st.subheader("Employee leave summary")
        safe_dataframe(get_employee_leave_summary())
        st.subheader("Pending requests by department")
        safe_dataframe(get_pending_leave_summary())

    elif page == "Attendance Analytics":
        hero("Attendance analytics", "Filter attendance records and compare employee and department patterns.", "HR ANALYTICS")
        attendance = get_attendance_summary()
        metric_row([
            ("Total records", attendance["total_records"], None),
            ("Present", attendance["present"], None),
            ("Absent", attendance["absent"], None),
            ("Attendance rate", f'{attendance["attendance_percentage"]}%', None),
        ])
        emp = get_employee_attendance_summary()
        dept = get_department_attendance_summary()
        monthly = get_monthly_attendance_summary()
        f1, f2, f3 = st.columns(3)
        employees = ["All"] + (sorted(emp["name"].dropna().unique().tolist()) if not emp.empty else [])
        departments = ["All"] + (sorted(dept["department"].dropna().unique().tolist()) if not dept.empty else [])
        months = ["All"] + (sorted(monthly["month"].dropna().unique().tolist()) if not monthly.empty else [])
        selected_name = f1.selectbox("Employee", employees)
        selected_dept = f2.selectbox("Department", departments)
        selected_month = f3.selectbox("Month", months)
        filtered = emp.copy()
        if selected_name != "All" and not filtered.empty:
            filtered = filtered[filtered["name"] == selected_name]
        if selected_dept != "All" and not filtered.empty:
            filtered = filtered[filtered["department"] == selected_dept]
        st.subheader("Employee attendance")
        safe_dataframe(filtered)
        st.subheader("Department attendance")
        dept_filtered = dept.copy()
        if selected_dept != "All" and not dept_filtered.empty:
            dept_filtered = dept_filtered[dept_filtered["department"] == selected_dept]
        if not dept_filtered.empty:
            fig = px.bar(dept_filtered, x="department", y="attendance_percentage", color="department")
            fig.update_layout(showlegend=False, height=320, yaxis_title="Attendance (%)")
            st.plotly_chart(fig, use_container_width=True)
        if selected_month == "All":
            if not monthly.empty:
                fig = px.line(monthly, x="month", y="attendance_percentage", markers=True)
                fig.update_layout(height=300, yaxis_title="Attendance (%)")
                st.plotly_chart(fig, use_container_width=True)
        else:
            month_df = get_attendance_by_month(selected_month)
            if selected_name != "All" and not month_df.empty:
                month_df = month_df[month_df["name"] == selected_name]
            if selected_dept != "All" and not month_df.empty:
                month_df = month_df[month_df["department"] == selected_dept]
            safe_dataframe(month_df)

    elif page == "Leave Approvals":
        hero("Leave approvals", "Manage pending requests and review the existing eligibility assessment.", "HR OPERATIONS")
        pending = get_all_pending_requests()
        if pending:
            df = pd.DataFrame(pending, columns=["Request ID", "Employee ID", "Leave Type", "Start Date", "End Date", "Reason", "Status", "Applied Date"])
            safe_dataframe(df)
            details = get_pending_request_details()
            for req in details:
                (rid, eid, name, dept, leave_type, start, end, reason, status, applied) = req
                with st.expander(f"{rid} · {name} · {dept}"):
                    st.write(f"**{leave_type}:** {start} to {end}")
                    st.write(f"**Reason:** {reason}")
                    st.info(evaluate_leave_request(eid, leave_type, start, end, applied))
            with st.form("hr_decision_form"):
                rid = st.selectbox("Request ID", [r[0] for r in pending])
                decision = st.radio("Decision", ["Approved", "Rejected"], horizontal=True)
                comments = st.text_area("Comments")
                submitted = st.form_submit_button("Save decision")
            if submitted:
                result = make_leave_decision(rid, "MGR001", decision, comments)
                if str(result).startswith("Request"):
                    st.success(result)
                    st.rerun()
                else:
                    st.error(result)
        else:
            st.success("No pending requests.")

    elif page == "Workforce Planning":
        hero("Workforce planning", "Check department capacity and identify leave-related coverage risks.", "HR OPERATIONS")
        render_workforce_planning()

    elif page == "Timeline & Deadlines":
        hero("Timeline & deadlines", "Monitor upcoming HR events, approvals, leave overlaps and project dates.", "HR OPERATIONS")
        summary = get_timeline_summary()
        metric_row([
            ("Timeline events", summary.get("total_events", 0), None),
            ("Active alerts", summary.get("alerts", 0), None),
        ])
        alerts = get_timeline_alerts()
        st.subheader("Important alerts")
        if alerts:
            for alert in alerts:
                message = f"**{alert['alert_type']} · {alert['title']}**\n\n{alert['message']}\n\nDate: {alert['date']}"
                (st.error if alert.get("priority") == "High" else st.warning)(message)
        else:
            st.success("No active timeline alerts.")
        st.subheader("Timeline filters")
        c1, c2, c3 = st.columns(3)
        start = c1.date_input("From", value=date.today(), key="timeline_from")
        end = c2.date_input("To", value=date.today() + timedelta(days=30), key="timeline_to")
        event_type = c3.selectbox("Event type", ["All", "Leave", "Request Submission", "Approval Deadline", "Return to Work", "Comp-off Earned", "Comp-off Expiry", "Holiday", "Project Deadline"])
        if end < start:
            st.error("End date cannot be before start date.")
        else:
            records = get_timeline(start, end, event_type)
            if records:
                timeline_df = pd.DataFrame(records)
                cols = [c for c in ["event_type", "title", "description", "event_date", "end_date", "employee_id", "reference_id", "status", "priority"] if c in timeline_df.columns]
                safe_dataframe(timeline_df[cols])
            else:
                st.info("No timeline events match these filters.")
            st.subheader("Overlapping team leave")
            overlaps = get_overlapping_leave_requests(start, end)
            if overlaps:
                st.warning(f"{len(overlaps)} overlapping leave combinations detected.")
                safe_dataframe(pd.DataFrame(overlaps))
            else:
                st.success("No overlapping team leave requests detected.")

    elif page == "Comp-off Management":
        hero("Comp-off management", "Review organization-wide compensatory leave records.", "HR OPERATIONS")
        records = get_all_comp_off_records()
        if records:
            df = pd.DataFrame(records, columns=["Comp-off ID", "Employee ID", "Earned date", "Expiry date", "Days", "Status"])
            available = df.loc[df["Status"] == "Available", "Days"].sum()
            used = df.loc[df["Status"] == "Used", "Days"].sum()
            metric_row([
                ("Records", len(df), None),
                ("Available days", available, None),
                ("Used days", used, None),
            ])
            safe_dataframe(df)
        else:
            st.info("No comp-off records found.")

    elif page == "Policy Management":
        hero("HR policy knowledge base", "Refresh the retrieval index after HR policy documents are added or updated.", "AI KNOWLEDGE MANAGEMENT")
        st.info("This action rebuilds the existing policy search index. It does not modify policy documents.")
        if st.button("Refresh policy knowledge base", type="primary"):
            with st.spinner("Re-indexing policy documents…"):
                try:
                    success, message = refresh_policy_index()
                    (st.success if success else st.error)(message)
                except Exception as exc:
                    st.error(f"Policy index refresh failed: {exc}")

    elif page == "AI HR Assistant":
        hero("HR knowledge assistant", "Ask policy questions and review the supporting document references.", "AI POLICY ASSISTANT")
        display_hr_chat(None, "hr_admin")



# Footer
st.divider()
st.caption("PeopleOS · AI-Powered Leave, Attendance & Workforce Planning Assistant | HR recommendations support human decisions and do not replace manager approval.")
