import psycopg

DB_URL = "postgresql://postgres:pgadmin@localhost:5432/genai"

conn = psycopg.connect(DB_URL)
cur = conn.cursor()

cur.execute("""
    DELETE FROM document_chunks
    WHERE chunking_strategy IN ('fixed', 'recursive');
""")

deleted = cur.rowcount

conn.commit()

print(f"Deleted chunks: {deleted}")

cur.execute("""
    SELECT chunking_strategy, COUNT(*)
    FROM document_chunks
    GROUP BY chunking_strategy;
""")

print("\nRemaining chunks:")

for strategy, count in cur.fetchall():
    print(f"{strategy}: {count}")

cur.close()
conn.close()