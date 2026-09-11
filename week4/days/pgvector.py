import psycopg

conn = psycopg.connect(
    "postgresql://postgres:pgadmin@localhost:5432/genai"
)

conn.autocommit = True

cur = conn.cursor()

cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

cur.execute(
    "SELECT extname FROM pg_extension WHERE extname = 'vector';"
)

print(cur.fetchall())

cur.close()
conn.close()

# to check whether the extension is installed, run the following command in psql: