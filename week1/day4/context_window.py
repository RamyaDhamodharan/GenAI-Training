import os
import httpx
from dotenv import load_dotenv

# Load .env
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

# Create a very large prompt
large_text = "This is a test sentence. " * 100000

prompt = f"""
Read the following text and summarize it in one sentence:

{large_text}
"""

payload = {
    "model": "openai/gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": prompt,
        }
    ],
}

response = httpx.post(
    url,
    headers=headers,
    json=payload,
    timeout=60.0,
)

data = response.json()

print("Status code:", response.status_code)

if response.is_success:

    print("Answer:")
    print(data["choices"][0]["message"]["content"])

else:

    print("API Error:")
    print(data)