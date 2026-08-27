import os
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

note = "Patient takes Paracetamol 500 mg twice daily."

prompt = Path(
    "prompts/task_v5.txt"
).read_text(encoding="utf-8")

prompt = prompt.replace("{note}", note)

data = {
    "model": "openai/gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
}

response = httpx.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers=headers,
    json=data,
    timeout=30.0
)

response.raise_for_status()

result = response.json()

print(result["choices"][0]["message"]["content"])