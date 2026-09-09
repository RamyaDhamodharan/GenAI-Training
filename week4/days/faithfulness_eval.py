import json
import os

import psycopg
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer


load_dotenv()

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:pgadmin@localhost:5432/genai"
)

model = SentenceTransformer("all-MiniLM-L6-v2")

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


with open("eval_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)


def retrieve(question, k=5):

    query_embedding = model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    conn = psycopg.connect(DB_URL)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, content, source, page, section,
               embedding <=> %s::vector AS distance
        FROM document_chunks
        WHERE chunking_strategy = 'structure-aware'
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (query_embedding, query_embedding, k)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def generate_answer(question, rows):

    context_parts = []

    for rank, row in enumerate(rows, start=1):

        chunk_id, content, source, page, section, distance = row

        context_parts.append(
            f"""
SOURCE {rank}
Document: {source}
Page: {page}
Section: {section}

{content}
"""
        )

    context = "\n".join(context_parts)

    response = client.chat.completions.create(
        model="openai/gpt-4.1-mini",
        temperature=0,
        max_tokens=200,
        messages=[
            {
                "role": "system",
                "content": """
You are answering questions about a clinic appointment management system.

Use ONLY the provided context.

Do not add information from your own knowledge.

If the context does not contain enough information, say:
"I don't have enough information in the clinic documents to answer this question."
"""
            },
            {
                "role": "user",
                "content": f"""
Context:
{context}

Question:
{question}

Answer:
"""
            }
        ]
    )

    return response.choices[0].message.content.strip()


results = []

for item in questions:

    print("\n" + "=" * 70)
    print(f"Q{item['id']:02d}: {item['question']}")
    print("=" * 70)

    rows = retrieve(item["question"], k=5)

    print("\nRetrieved context:")

    for rank, row in enumerate(rows, start=1):

        chunk_id, content, source, page, section, distance = row

        print(
            f"\n#{rank} | ID={chunk_id} | "
            f"distance={distance:.4f}"
        )
        print(f"Source: {source}")
        print(f"Page: {page}")
        print(f"Section: {section}")
        print(f"Content: {content}")

    answer = generate_answer(
        item["question"],
        rows
    )

    print("\nGENERATED ANSWER:")
    print(answer)

    results.append({
        "id": item["id"],
        "question": item["question"],
        "answer": answer,
        "retrieved_chunks": [
            {
                "id": row[0],
                "content": row[1],
                "source": row[2],
                "page": row[3],
                "section": row[4],
                "distance": float(row[5])
            }
            for row in rows
        ]
    })


with open(
    "faithfulness_results.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        results,
        f,
        indent=2,
        ensure_ascii=False
    )


print("\n\nSaved: faithfulness_results.json")