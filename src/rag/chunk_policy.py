# Step 1: Read the HR policy document

file_path = "documents/hr_policies/leave_policy_v1.txt"

with open(file_path, "r", encoding="utf-8") as file:
    policy_text = file.read()


# Step 2: Divide the document into chunks

chunk_size = 500

chunks = []

for i in range(0, len(policy_text), chunk_size):

    chunk = policy_text[i:i + chunk_size]

    chunks.append(chunk)


# Step 3: Display the chunks

print("========== POLICY CHUNKS ==========")

for index, chunk in enumerate(chunks):

    print(f"\nCHUNK {index + 1}")
    print(chunk)

    print("----------------------------------")


# Step 4: Display total chunks

print("\nTotal Chunks Created:", len(chunks))