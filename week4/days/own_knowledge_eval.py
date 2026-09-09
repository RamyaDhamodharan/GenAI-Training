import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

with open("eval_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)


def generate_own_knowledge_answer(question):

    response = client.chat.completions.create(
        model="openai/gpt-4.1-mini",
        temperature=0,
        max_tokens=150,
        messages=[
            {
                "role": "system",
                "content": """
Answer the question using your general knowledge only.

Do NOT assume that you have access to the clinic documents.
If the question depends on a specific clinic's policy,
say that you cannot know the clinic-specific policy.
"""
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    return response.choices[0].message.content.strip()


results = []

for item in questions:

    answer = generate_own_knowledge_answer(
        item["question"]
    )

    print("\n" + "=" * 60)
    print(f"Q{item['id']:02d}: {item['question']}")
    print("OWN-KNOWLEDGE ANSWER:")
    print(answer)

    results.append({
        "id": item["id"],
        "question": item["question"],
        "own_knowledge_answer": answer
    })


with open(
    "own_knowledge_results.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        results,
        f,
        indent=2,
        ensure_ascii=False
    )

print("\nSaved: own_knowledge_results.json")