import json

import psycopg
from sentence_transformers import SentenceTransformer


DB_URL = "postgresql://postgres:pgadmin@localhost:5432/genai"

model = SentenceTransformer("all-MiniLM-L6-v2")

with open("eval_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)


failures = {
    "fixed": [4, 8, 12, 17, 19],
    "recursive": [4],
    "structure-aware": [4]
}


def search(question, strategy, k=3):
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
        WHERE chunking_strategy = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (query_embedding, strategy, query_embedding, k)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


for strategy, question_ids in failures.items():

    print("\n" + "=" * 70)
    print(f"STRATEGY: {strategy}")
    print("=" * 70)

    for qid in question_ids:

        item = next(q for q in questions if q["id"] == qid)

        print(f"\nQ{qid}: {item['question']}")
        print(f"GOLD: {item['gold_text']}")

        rows = search(item["question"], strategy)

        print("\nTop 3 retrieved:")

        for rank, row in enumerate(rows, start=1):
            chunk_id, content, source, page, section, distance = row

            print(f"\n#{rank} | ID={chunk_id} | distance={distance:.4f}")
            print(f"Source: {source}")
            print(f"Page: {page}")
            print(f"Section: {section}")
            print(f"Content: {content}")