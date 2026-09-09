import os

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer


# ============================================================
# 1. LOAD CONFIGURATION
# ============================================================

load_dotenv(
    r"C:\Users\User\Desktop\GenAI-Training\.env"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:pgadmin@localhost:5432/genai"
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set in .env")


# ============================================================
# 2. INITIALIZE APPLICATION
# ============================================================

app = FastAPI(
    title="Clinic RAG API",
    description="RAG using FastAPI + PostgreSQL + pgvector + OpenRouter",
    version="1.0.0"
)


# ============================================================
# 3. INITIALIZE EMBEDDING MODEL
# ============================================================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# 4. INITIALIZE OPENROUTER
# ============================================================

llm_client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


# ============================================================
# 5. REQUEST MODEL
# ============================================================

class AskRequest(BaseModel):
    question: str


# ============================================================
# 6. CITATION MODEL
# ============================================================

class Citation(BaseModel):
    source: str
    page: int | None
    section: str | None


# ============================================================
# 7. RESPONSE MODEL
# ============================================================

class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]


# ============================================================
# 8. RETRIEVE CHUNKS FROM POSTGRESQL
# ============================================================

def retrieve_chunks(
    question: str,
    top_k: int = 5
):

    # Convert question into vector
    query_embedding = embedding_model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    conn = psycopg.connect(
        DATABASE_URL
    )

    cur = conn.cursor()

    # pgvector cosine-distance search
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
            top_k
        )
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


# ============================================================
# 9. RELEVANCE FILTER
# ============================================================

def get_relevant_chunks(rows):

    # Lower distance = more similar
    MAX_DISTANCE = 0.65

    relevant = []

    for row in rows:

        distance = row[5]

        if distance <= MAX_DISTANCE:
            relevant.append(row)

    return relevant


# ============================================================
# 10. BUILD CONTEXT FOR LLM
# ============================================================

def build_context(rows):

    context_parts = []

    for row in rows:

        chunk_id = row[0]
        content = row[1]
        source = row[2]
        page = row[3]
        section = row[4]
        distance = row[5]

        context_parts.append(
            f"""
SOURCE: {source}
PAGE: {page}
SECTION: {section}
CONTENT:
{content}
"""
        )

    return "\n---\n".join(context_parts)


# ============================================================
# 11. GENERATE ANSWER USING OPENROUTER
# ============================================================

def generate_answer(
    question: str,
    rows: list
):

    context = build_context(rows)

    system_prompt = """
You are a clinic appointment assistant.

Your job is to answer questions using ONLY the
provided clinic documents.

Rules:

1. Use only the provided context.
2. Do not use outside knowledge.
3. Do not invent facts.
4. If the context does not contain enough information,
   say exactly:

   I don't have enough information in the clinic
   documents to answer this question.

5. Keep the answer concise and clear.
"""

    user_prompt = f"""
Here is the retrieved clinic information:

{context}

User question:

{question}

Answer the question using only the retrieved information.
"""
    response = llm_client.chat.completions.create(
        model="openai/gpt-4.1-mini",
        temperature=0,
        max_tokens=500,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response.choices[0].message.content


# ============================================================
# 12. /ask ENDPOINT
# ============================================================

@app.post(
    "/ask",
    response_model=AskResponse
)
def ask(request: AskRequest):

    # --------------------------------------------------------
    # Step 1: Retrieve
    # --------------------------------------------------------

    retrieved_rows = retrieve_chunks(
        request.question,
        top_k=5
    )

    # --------------------------------------------------------
    # Step 2: Check relevance
    # --------------------------------------------------------

    relevant_rows = get_relevant_chunks(
        retrieved_rows
    )

    # --------------------------------------------------------
    # Step 3: Refuse if no relevant information
    # --------------------------------------------------------

    if not relevant_rows:

        return AskResponse(
            answer=(
                "I don't have enough information in the "
                "clinic documents to answer this question."
            ),
            citations=[]
        )

    # --------------------------------------------------------
    # Step 4: Generate answer
    # --------------------------------------------------------

    answer = generate_answer(
        request.question,
        relevant_rows
    )

    # --------------------------------------------------------
    # Step 5: Create citations
    # --------------------------------------------------------

    citations = []

    for row in relevant_rows:

        source = row[2]
        page = row[3]
        section = row[4]

        citations.append(
            Citation(
                source=source,
                page=page,
                section=section
            )
        )

    # --------------------------------------------------------
    # Step 6: Return response
    # --------------------------------------------------------

    return AskResponse(
        answer=answer,
        citations=citations
    )


# ============================================================
# 13. HEALTH CHECK
# ============================================================

@app.get("/")
def health_check():

    return {
        "status": "ok",
        "service": "Clinic RAG API"
    }