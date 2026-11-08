from pathlib import Path
import re


def read_policy(filename):

    file_path = Path("documents/hr_policies") / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# Read both policy versions
policy_v1 = read_policy("leave_policy_v1.txt")
policy_v2 = read_policy("leave_policy_v2.txt")


# Extract annual leave days
annual_v1 = re.search(
    r"(\d+)\s+days of annual leave",
    policy_v1,
    re.IGNORECASE
)

annual_v2 = re.search(
    r"(\d+)\s+days of annual leave",
    policy_v2,
    re.IGNORECASE
)


# Extract sick leave days
sick_v1 = re.search(
    r"(\d+)\s+days of sick leave",
    policy_v1,
    re.IGNORECASE
)

sick_v2 = re.search(
    r"(\d+)\s+days of sick leave",
    policy_v2,
    re.IGNORECASE
)


# Extract annual leave notice period
notice_v1 = re.search(
    r"at least (\d+) calendar days",
    policy_v1,
    re.IGNORECASE
)

notice_v2 = re.search(
    r"at least (\d+) calendar days",
    policy_v2,
    re.IGNORECASE
)


# Display comparison
print("\n========== POLICY CHANGE REPORT ==========")

print("\nAnnual Leave:")
print("Version 1:", annual_v1.group(1), "days")
print("Version 2:", annual_v2.group(1), "days")

print("\nSick Leave:")
print("Version 1:", sick_v1.group(1), "days")
print("Version 2:", sick_v2.group(1), "days")

print("\nAnnual Leave Notice Period:")
print("Version 1:", notice_v1.group(1), "days")
print("Version 2:", notice_v2.group(1), "days")