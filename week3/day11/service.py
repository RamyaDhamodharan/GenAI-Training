from openai import AsyncOpenAI

from config import settings


client = AsyncOpenAI(
    api_key=settings.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1"
)


cache = {}


async def ask_model(prompt: str) -> str:

    # 1. Check cache
    if prompt in cache:
        return cache[prompt]

    # 2. Call LLM if not cached
    response = await client.chat.completions.create(
        model=settings.model,
        temperature=settings.temperature,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        timeout=settings.request_timeout
    )

    answer = response.choices[0].message.content

    # 3. Store answer in cache
    cache[prompt] = answer

    return answer