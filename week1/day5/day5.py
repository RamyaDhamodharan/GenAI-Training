import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}


async def call_api(client, prompt):

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0,
    }

    response = await client.post(
        url,
        headers=headers,
        json=payload,
        timeout=30.0,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


async def main():

    prompts = [
        "What is Python?",
        "What is Artificial Intelligence?",
        "What is an API?",
    ]

    async with httpx.AsyncClient() as client:

        results = await asyncio.gather(
            call_api(client, prompts[0]),
            call_api(client, prompts[1]),
            call_api(client, prompts[2]),
        )

    for i, result in enumerate(results, start=1):
        print(f"\n--- Response {i} ---")
        print(result)


asyncio.run(main())