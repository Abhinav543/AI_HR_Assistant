# Import required libraries

import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


# STEP 1: Read HR policy document

file_path = "documents/hr_policies/leave_policy_v1.txt"

with open(file_path, "r", encoding="utf-8") as file:
    policy_text = file.read()


# STEP 2: Divide document into chunks

chunk_size = 500

chunks = []

for i in range(0, len(policy_text), chunk_size):

    chunk = policy_text[i:i + chunk_size]

    chunks.append(chunk)


# STEP 3: Load embedding model

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")


# STEP 4: Convert chunks into embeddings

embeddings = model.encode(
    chunks,
    normalize_embeddings=True
)

# Convert embeddings into NumPy array

embeddings = np.array(embeddings, dtype="float32")


# STEP 5: Create FAISS index

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(embeddings)

print("\nFAISS index created successfully!")

print("Total vectors stored:", index.ntotal)


# STEP 6: Ask a question

query = "How many days of annual leave do employees receive?"


# STEP 7: Convert question into embedding

query_embedding = model.encode(
    [query],
    normalize_embeddings=True
)

query_embedding = np.array(
    query_embedding,
    dtype="float32"
)


# STEP 8: Search FAISS

distances, indices = index.search(query_embedding, k=2)


# STEP 9: Display relevant chunks

print("\n========== SEARCH RESULTS ==========")

print("Question:", query)

for i, idx in enumerate(indices[0]):

    print("\nResult:", i + 1)

    print("Similarity Score:", distances[0][i])

    print("Relevant Policy Text:")

    print(chunks[idx])