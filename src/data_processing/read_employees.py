import pandas as pd

# Read employee data
employees = pd.read_csv("data/employees.csv")

# Display all employees
print("\n--- ALL EMPLOYEES ---")
print(employees)

# Search for a particular employee
employee_id = "EMP001"

employee = employees[employees["employee_id"] == employee_id]

print("\n--- EMPLOYEE DETAILS ---")
print(employee)

# Display annual and sick leave balance
if not employee.empty:
    annual_leave = employee.iloc[0]["annual_leave_balance"]
    sick_leave = employee.iloc[0]["sick_leave_balance"]

    print("\n--- LEAVE BALANCE ---")
    print("Annual Leave:", annual_leave, "days")
    print("Sick Leave:", sick_leave, "days")

else:
    print("Employee not found!")

# Count employees in each department
print("\n--- DEPARTMENT-WISE EMPLOYEE COUNT ---")
print(employees["department"].value_counts())