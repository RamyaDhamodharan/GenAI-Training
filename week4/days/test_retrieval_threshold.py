import psycopg
from sentence_transformers import SentenceTransformer

DATABASE_URL = "postgresql://postgres:pgadmin@localhost:5432/genai"

model = SentenceTransformer("all-MiniLM-L6-v2")

questions = [
    "What is the clinic's parking fee?",
    "What time does the clinic cafeteria open?",
    "Which insurance companies are accepted?",
    "What is the doctor's salary?",
    "Does the clinic provide ambulance transportation?",
]

conn = psycopg.connect(DATABASE_URL)
cur = conn.cursor()

for question in questions:

    query_embedding = model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    cur.execute(
        """
        SELECT
            source,
            page,
            section,
            embedding <=> %s::vector AS distance
        FROM document_chunks
        ORDER BY embedding <=> %s::vector
        LIMIT 3;
        """,
        (
            query_embedding,
            query_embedding
        )
    )

    rows = cur.fetchall()

    print("\n" + "=" * 70)
    print("QUESTION:", question)

    for rank, row in enumerate(rows, start=1):
        print(
            f"{rank}. distance={row[3]:.4f} | "
            f"{row[0]} | page={row[1]} | section={row[2]}"
        )

cur.close()
conn.close()