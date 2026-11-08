# Import Sentence Transformer

from sentence_transformers import SentenceTransformer

# Load our HR policy chunks

file_path = "documents/hr_policies/leave_policy_v1.txt"

with open(file_path, "r", encoding="utf-8") as file:
    policy_text = file.read()

# Divide text into chunks

chunk_size = 500

chunks = []

for i in range(0, len(policy_text), chunk_size):
    chunk = policy_text[i:i + chunk_size]
    chunks.append(chunk)

# Load embedding model

print("Loading Embedding Model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

# Convert chunks into embeddings

embeddings = model.encode(chunks)

# Display results

print("\n========== EMBEDDING RESULTS ==========")

print("Total Chunks:", len(chunks))

print("Embedding Shape:", embeddings.shape)

print("\nFirst Chunk:")
print(chunks[0])

print("\nFirst Chunk Embedding:")
print(embeddings[0])

print("\nEmbedding Dimensions:", len(embeddings[0]))