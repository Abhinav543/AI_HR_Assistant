# Import Python's file handling capability

file_path = "documents/hr_policies/leave_policy_v1.txt"

# Open and read the policy document

with open(file_path, "r", encoding="utf-8") as file:

    policy_text = file.read()

# Display the extracted text

print("========== HR POLICY DOCUMENT ==========")

print(policy_text)

print("\n========== DOCUMENT DETAILS ==========")

print("Total Characters:", len(policy_text))