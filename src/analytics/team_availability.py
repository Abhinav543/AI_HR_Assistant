
import pandas as pd


def get_team_availability(start_date, end_date):

    employees = pd.read_csv("data/employees.csv")
    leave_requests = pd.read_csv("data/leave_requests.csv")

    # Convert dates into datetime format
    leave_requests["start_date"] = pd.to_datetime(
        leave_requests["start_date"]
    )

    leave_requests["end_date"] = pd.to_datetime(
        leave_requests["end_date"]
    )

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    results = {}

    # Check availability department by department
    for department in employees["department"].unique():

        department_employees = employees[
            employees["department"] == department
        ]

        total_employees = len(department_employees)

        department_leave = leave_requests[
            (leave_requests["employee_id"].isin(
                department_employees["employee_id"]
            ))
            & (leave_requests["status"].isin(["Pending", "Approved"]))
            & (leave_requests["start_date"] <= end_date)
            & (leave_requests["end_date"] >= start_date)
        ]

        employees_on_leave = department_leave[
            "employee_id"
        ].nunique()

        available_employees = total_employees - employees_on_leave

        results[department] = {
            "total_employees": total_employees,
            "employees_on_leave": employees_on_leave,
            "available_employees": available_employees
        }

    return results


if __name__ == "__main__":

    availability = get_team_availability(
        "2026-11-09",
        "2026-11-11"
    )

    print("\n========== TEAM AVAILABILITY ==========")

    for department, details in availability.items():

        print("\nDepartment:", department)
        print("Total Employees:", details["total_employees"])
        print("On Leave:", details["employees_on_leave"])
        print("Available:", details["available_employees"])
