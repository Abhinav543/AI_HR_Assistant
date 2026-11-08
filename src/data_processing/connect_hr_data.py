import pandas as pd

# Load employee and leave request datasets
employees = pd.read_csv("data/employees.csv")
leave_requests = pd.read_csv("data/leave_requests.csv")

# Combine both datasets using employee_id
employee_leave_data = pd.merge(
    employees,
    leave_requests,
    on="employee_id",
    how="inner"
)

# Display employee names and their leave requests
print("\n========== EMPLOYEE LEAVE DETAILS ==========")

print(
    employee_leave_data[
        ["employee_id", "name", "department",
         "leave_type", "start_date", "end_date", "status"]
    ]
)

# Find Rahul Sharma's leave requests
print("\n========== RAHUL'S LEAVE REQUESTS ==========")

rahul_requests = employee_leave_data[
    employee_leave_data["employee_id"] == "EMP001"
]

print(rahul_requests)

# Count leave requests by status
print("\n========== LEAVE REQUEST SUMMARY ==========")

print(leave_requests["status"].value_counts())