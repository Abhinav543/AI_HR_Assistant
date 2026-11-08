
import pandas as pd


def get_workforce_summary():

    # Load employee data
    employees = pd.read_csv("data/employees.csv")

    # Count employees in each department
    department_counts = (
        employees.groupby("department")["employee_id"]
        .count()
        .to_dict()
    )

    # Total employees
    total_employees = len(employees)

    return {
        "total_employees": total_employees,
        "department_counts": department_counts
    }


# Test the function
if __name__ == "__main__":

    summary = get_workforce_summary()

    print("\n========== WORKFORCE SUMMARY ==========")

    print("Total Employees:", summary["total_employees"])

    print("\nEmployees by Department:")

    for department, count in summary["department_counts"].items():
        print(department, ":", count)
