import psycopg
from sentence_transformers import SentenceTransformer


DB_URL = "postgresql://postgres:pgadmin@localhost:5432/genai"

model = SentenceTransformer("all-MiniLM-L6-v2")


query = "What should I do if I cannot attend my appointment?"

query_embedding = model.encode(
    query,
    normalize_embeddings=True
).tolist()


conn = psycopg.connect(DB_URL)
cur = conn.cursor()


print("\n========== WITHOUT FILTER ==========\n")

cur.execute(
    """
    SELECT
        id,
        content,
        source,
        section,
        embedding <=> %s::vector AS distance
    FROM document_chunks
    ORDER BY embedding <=> %s::vector
    LIMIT 5;
    """,
    (
        query_embedding,
        query_embedding,
    ),
)

results = cur.fetchall()

for rank, row in enumerate(results, start=1):
    chunk_id, content, source, section, distance = row

    print(f"Rank: {rank}")
    print(f"Source: {source}")
    print(f"Section: {section}")
    print(f"Distance: {distance:.4f}")
    print(f"Content: {content}")
    print("-" * 80)


print("\n========== FILTER: SCANNED PDF ==========\n")

cur.execute(
    """
    SELECT
        id,
        content,
        source,
        section,
        embedding <=> %s::vector AS distance
    FROM document_chunks
    WHERE source = %s
    ORDER BY embedding <=> %s::vector
    LIMIT 5;
    """,
    (
        query_embedding,
        "clinic_patient_handbook_scanned.pdf",
        query_embedding,
    ),
)

results = cur.fetchall()

for rank, row in enumerate(results, start=1):
    chunk_id, content, source, section, distance = row

    print(f"Rank: {rank}")
    print(f"Source: {source}")
    print(f"Section: {section}")
    print(f"Distance: {distance:.4f}")
    print(f"Content: {content}")
    print("-" * 80)


cur.close()
conn.close()