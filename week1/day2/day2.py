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

contexts = [
    "Explain what Python is in one simple sentence.",

    "What major event happened on December 31, 2030? Give me specific details.",

    "Who is Dr. Arvind Moonwalker? What are his major contributions to artificial intelligence?",

    "What is the history of artificial intelligence? Give me three important facts and provide a citation or source for each fact.",

    "What is the 2027 Nobel Prize in Artificial Intelligence awarded to Dr. Arvind Moonwalker for? Give the exact award citation, date, and research paper title.",

    "Give me the exact title, authors, DOI, and publication date of the 2024 research paper 'Quantum Attention Networks for Universal AGI' by Dr. Arvind Moonwalker.",
]

for context in contexts:

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": context,
            }
        ],
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

    print("\n" + "=" * 60)
    print("QUESTION:")
    print(context)

    print("\nANSWER:")
    print(answer)

    print("\nRAW JSON:")
    print(data)