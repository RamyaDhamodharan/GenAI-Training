import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI


# Load the common .env from GenAI-Training/
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)


# Create OpenRouter client
client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


MODEL = "qwen/qwen-2.5-7b-instruct"


async def ask_question(context: str, question: str):

    # 1. Build prompt manually
    prompt = f"""
Answer only from the given context.

Context:
{context}

Question:
{question}
"""

    # 2. Call the model
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    # 3. Extract the answer manually
    answer = response.choices[0].message.content

    return answer