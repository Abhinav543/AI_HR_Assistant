from datetime import datetime
import re
from pathlib import Path

# Folder containing HR policies
policy_folder = Path("documents/hr_policies")

# Find all policy version files
policy_files = sorted(
    policy_folder.glob("leave_policy_v*.txt")
)

policies = []

# Read each policy document
for file_path in policy_files:

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Extract policy version
    version_match = re.search(
        r"Policy Version:\s*([\d.]+)",
        content
    )

    # Extract effective date
    date_match = re.search(
        r"Effective Date:\s*(\d{2} \w+ \d{4})",
        content
    )

    if version_match and date_match:

        policies.append({
            "filename": file_path.name,
            "version": version_match.group(1),
            "effective_date": date_match.group(1),
            "content": content
        })

# Display policy information
print("\n========== POLICY VERSION DETAILS ==========")

for policy in policies:

    print("\nDocument:", policy["filename"])
    print("Version:", policy["version"])
    print("Effective Date:", policy["effective_date"])

# Identify latest version by effective date
policies.sort(
    key=lambda policy: datetime.strptime(
        policy["effective_date"], "%d %B %Y"
    ),
    reverse=True
)

if policies:
    latest_policy = policies[0]

    print("\n========== LATEST POLICY ==========")
    print("Document:", latest_policy["filename"])
    print("Version:", latest_policy["version"])
    print("Effective Date:", latest_policy["effective_date"])