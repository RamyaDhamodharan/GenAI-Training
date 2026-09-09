import psycopg
from sentence_transformers import SentenceTransformer


DB_URL = "postgresql://postgres:pgadmin@localhost:5432/genai"

model = SentenceTransformer("all-MiniLM-L6-v2")

query = "What should I do if I cannot attend my appointment?"

query_embedding = model.encode(
    query,
    normalize_embeddings=True
).tolist()


# ============================================================
# 1. RAW SQL
# ============================================================

print("\n========== RAW SQL ==========\n")

conn = psycopg.connect(DB_URL)
cur = conn.cursor()

sql = """
SELECT
    id,
    content,
    source,
    page,
    section,
    embedding <=> %s::vector AS distance
FROM document_chunks
ORDER BY embedding <=> %s::vector
LIMIT 5;
"""

print("SQL sent to PostgreSQL:")
print(sql)

cur.execute(
    sql,
    (
        query_embedding,
        query_embedding,
    ),
)

results = cur.fetchall()

for rank, row in enumerate(results, start=1):

    chunk_id, content, source, page, section, distance = row

    print(f"\nRank: {rank}")
    print(f"ID: {chunk_id}")
    print(f"Source: {source}")
    print(f"Page: {page}")
    print(f"Section: {section}")
    print(f"Distance: {distance:.4f}")
    print(f"Content: {content}")


cur.close()
conn.close()


# ============================================================
# 2. LANGCHAIN EQUIVALENT
# ============================================================

print("\n\n========== LANGCHAIN EQUIVALENT ==========\n")

print("""
LangChain conceptually performs the same operation:

vector_store.similarity_search(
    query,
    k=5
)

The important part is:

    query
      ↓
    embedding
      ↓
    vector store
      ↓
    cosine similarity
      ↓
    top 5 chunks
""")


# ============================================================
# 3. COMPARISON
# ============================================================

print("\n========== COMPARISON ==========\n")

print("RAW SQL:")
print("embedding <=> query_embedding")
print("ORDER BY distance")
print("LIMIT 5")

print("\nLANGCHAIN:")
print("similarity_search(query, k=5)")

print("\nConclusion:")
print(
    "Both approaches perform vector similarity search. "
    "Raw SQL gives direct control over PostgreSQL, while "
    "LangChain provides a higher-level abstraction."
)