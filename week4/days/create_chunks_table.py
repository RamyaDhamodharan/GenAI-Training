import psycopg

conn = psycopg.connect(
    "postgresql://postgres:pgadmin@localhost:5432/genai"
)
conn.autocommit = True

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    source TEXT NOT NULL,
    page INTEGER,
    section TEXT,
    embedding vector(384)
);
""")

print("Table created successfully.")

cur.close()
conn.close()