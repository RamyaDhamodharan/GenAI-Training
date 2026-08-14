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

prompt = "Explain what Python is in simple sentence."


# Run the same prompt 10 times
for i in range(10):

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0,
        "max_tokens": 100,
    }

    response = httpx.post(
        url,
        headers=headers,
        json=payload,
        timeout=30.0,
    )

    response.raise_for_status()

    data = response.json()

    answer = data["choices"][0]["message"]["content"]

    print(f"\n--- Run {i + 1} ---")
    print(answer)
    print("Finish reason:", data["choices"][0]["finish_reason"])