import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# Load common .env from GenAI-Training/
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)


client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

MODEL = "qwen/qwen-2.5-7b-instruct"


def model_call(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content