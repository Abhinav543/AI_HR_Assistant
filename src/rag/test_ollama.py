import requests

# Ollama API address
url = "http://localhost:11434/api/generate"

# Data sent to the AI model
data = {
    "model": "qwen2.5:0.5b",
    "prompt": "Explain annual leave in simple words.",
    "stream": False
}

# Send request to Ollama
response = requests.post(url, json=data)

# Extract AI response
result = response.json()

# Display answer
print("\n========== AI RESPONSE ==========")

print(result["response"])