import pandas as pd

# Load all HR datasets

employees = pd.read_csv("data/employees.csv")
attendance = pd.read_csv("data/attendance.csv")
leave_requests = pd.read_csv("data/leave_requests.csv")
holidays = pd.read_csv("data/holidays.csv")
comp_off = pd.read_csv("data/comp_off.csv")


# Display dataset information

print("\n========== EMPLOYEE DATA ==========")
print(employees.head())

print("\n========== ATTENDANCE DATA ==========")
print(attendance.head())

print("\n========== LEAVE REQUEST DATA ==========")
print(leave_requests.head())

print("\n========== HOLIDAY DATA ==========")
print(holidays.head())

print("\n========== COMP-OFF DATA ==========")
print(comp_off.head())


# Display the number of records in each dataset

print("\n========== DATASET SUMMARY ==========")

print("Total Employees:", len(employees))
print("Attendance Records:", len(attendance))
print("Leave Requests:", len(leave_requests))
print("Total Holidays:", len(holidays))
print("Comp-Off Records:", len(comp_off))