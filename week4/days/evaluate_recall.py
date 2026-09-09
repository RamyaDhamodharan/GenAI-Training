import json

import psycopg
from sentence_transformers import SentenceTransformer


DB_URL = "postgresql://postgres:pgadmin@localhost:5432/genai"

model = SentenceTransformer("all-MiniLM-L6-v2")

with open("eval_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)


def search(question, strategy, k):
    query_embedding = model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    conn = psycopg.connect(DB_URL)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT content
        FROM document_chunks
        WHERE chunking_strategy = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (strategy, query_embedding, k)
    )

    results = cur.fetchall()

    cur.close()
    conn.close()

    return [row[0] for row in results]


strategies = [
    "fixed",
    "recursive",
    "structure-aware"
]


results = {}


for strategy in strategies:

    hits_at_3 = 0
    hits_at_5 = 0

    print(f"\n{'=' * 60}")
    print(f"Strategy: {strategy}")
    print(f"{'=' * 60}")

    for item in questions:

        question = item["question"]
        gold_text = item["gold_text"].lower()

        top3 = search(question, strategy, 3)
        top5 = search(question, strategy, 5)

        hit3 = any(
            gold_text in chunk.lower()
            for chunk in top3
        )

        hit5 = any(
            gold_text in chunk.lower()
            for chunk in top5
        )

        if hit3:
            hits_at_3 += 1

        if hit5:
            hits_at_5 += 1

        print(
            f"Q{item['id']:02d} | "
            f"Recall@3={'HIT' if hit3 else 'MISS'} | "
            f"Recall@5={'HIT' if hit5 else 'MISS'}"
        )

    recall3 = hits_at_3 / len(questions)
    recall5 = hits_at_5 / len(questions)

    results[strategy] = {
        "recall@3": recall3,
        "recall@5": recall5
    }


print("\n\nFINAL RESULTS")
print("=" * 60)

for strategy, scores in results.items():

    print(
        f"{strategy:20s} "
        f"Recall@3 = {scores['recall@3']:.2%} | "
        f"Recall@5 = {scores['recall@5']:.2%}"
    )