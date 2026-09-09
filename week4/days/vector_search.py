import psycopg
from sentence_transformers import SentenceTransformer


DB_URL = "postgresql://postgres:pgadmin@localhost:5432/genai"

model = SentenceTransformer("all-MiniLM-L6-v2")


def search(query, top_k=5):
    # Convert query into embedding
    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    conn = psycopg.connect(DB_URL)
    cur = conn.cursor()

    # PostgreSQL pgvector cosine-distance search
    cur.execute(
        """
        SELECT
            id,
            content,
            source,
            page,
            section,
            embedding <=> %s::vector AS distance
        FROM document_chunks
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (
            query_embedding,
            query_embedding,
            top_k,
        ),
    )

    results = cur.fetchall()

    cur.close()
    conn.close()

    return results


query = "What should I do if I cannot attend my appointment?"

results = search(query, top_k=5)

print(f"\nQuery: {query}\n")
print("Top 5 results:\n")

for rank, row in enumerate(results, start=1):

    chunk_id, content, source, page, section, distance = row

    print(f"Rank: {rank}")
    print(f"ID: {chunk_id}")
    print(f"Source: {source}")
    print(f"Page: {page}")
    print(f"Section: {section}")
    print(f"Cosine distance: {distance:.4f}")
    print(f"Content: {content}")
    print("-" * 80)