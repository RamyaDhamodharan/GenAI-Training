import os
import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

MODEL = "google/gemma-4-26b-a4b-it:free"

messages = []

while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True
    }

    with httpx.stream(
        "POST",
        url,
        headers=headers,
        json=payload,
        timeout=120.0
    ) as response:

        response.raise_for_status()

        for line in response.iter_lines():
            print(line)
