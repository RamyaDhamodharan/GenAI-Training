from pathlib import Path
import re

import psycopg
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter


DB_URL = "postgresql://postgres:pgadmin@localhost:5432/genai"

DOCUMENTS_DIR = Path("data/documents")

model = SentenceTransformer("all-MiniLM-L6-v2")


# ------------------------------------------------------------
# Chunking settings
# ------------------------------------------------------------

CHUNK_SIZE = 300
CHUNK_OVERLAP = 50


recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


# ------------------------------------------------------------
# Helper: detect section
# ------------------------------------------------------------

def get_section(text):
    match = re.search(r"(?m)^\d+\.\s+.+$", text)

    if match:
        return match.group(0).strip()

    return None


# ------------------------------------------------------------
# Fixed chunking
# ------------------------------------------------------------

def fixed_chunks(text):
    chunks = []

    for i in range(0, len(text), CHUNK_SIZE):
        chunk = text[i:i + CHUNK_SIZE].strip()

        if chunk:
            chunks.append(chunk)

    return chunks


# ------------------------------------------------------------
# Structure-aware chunking
# ------------------------------------------------------------

def structure_aware_chunks(text):
    lines = text.splitlines()

    sections = []

    current_section = None
    current_content = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Ignore document title
        if line.startswith("CLINIC "):
            continue

        # Ignore OCR page markers
        if line.startswith("--- PAGE"):
            continue

        # Detect section heading
        if re.match(r"^\d+\.\s+", line):

            if current_content:
                sections.append(
                    (
                        current_section,
                        "\n".join(current_content)
                    )
                )

            current_section = line
            current_content = [line]

        else:
            current_content.append(line)

    if current_content:
        sections.append(
            (
                current_section,
                "\n".join(current_content)
            )
        )

    return sections


# ------------------------------------------------------------
# Read documents
# ------------------------------------------------------------

documents = []

for file_path in DOCUMENTS_DIR.glob("*.txt"):

    text = file_path.read_text(
        encoding="utf-8"
    )

    # OCR text belongs to the scanned PDF
    if file_path.name == "clinic_patient_handbook_ocr.txt":

        source = "clinic_patient_handbook_scanned.pdf"

        # Split OCR document into pages
        page_parts = re.split(
            r"--- PAGE \d+ ---",
            text
        )

        pages = []

        for page_number, page_text in enumerate(
            page_parts[1:],
            start=1
        ):
            pages.append(
                (
                    page_number,
                    page_text.strip()
                )
            )

    else:

        source = file_path.name

        pages = [
            (
                None,
                text
            )
        ]

    documents.append(
        (
            source,
            pages
        )
    )


# ------------------------------------------------------------
# Connect to PostgreSQL
# ------------------------------------------------------------

conn = psycopg.connect(DB_URL)
cur = conn.cursor()


# ------------------------------------------------------------
# Make sure strategy column exists
# ------------------------------------------------------------

cur.execute(
    """
    ALTER TABLE document_chunks
    ADD COLUMN IF NOT EXISTS chunking_strategy TEXT;
    """
)


# ------------------------------------------------------------
# Remove previous chunks
# ------------------------------------------------------------

cur.execute(
    "DELETE FROM document_chunks"
)


total_loaded = 0


# ------------------------------------------------------------
# Process every document
# ------------------------------------------------------------

for source, pages in documents:

    for page_number, text in pages:

        # ====================================================
        # 1. FIXED CHUNKING
        # ====================================================

        fixed = fixed_chunks(text)

        for content in fixed:

            embedding = model.encode(
                content,
                normalize_embeddings=True
            ).tolist()

            section = get_section(content)

            cur.execute(
                """
                INSERT INTO document_chunks
                (
                    content,
                    source,
                    page,
                    section,
                    embedding,
                    chunking_strategy
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    content,
                    source,
                    page_number,
                    section,
                    embedding,
                    "fixed",
                ),
            )

            total_loaded += 1


        # ====================================================
        # 2. RECURSIVE CHUNKING
        # ====================================================

        recursive = recursive_splitter.split_text(text)

        for content in recursive:

            embedding = model.encode(
                content,
                normalize_embeddings=True
            ).tolist()

            section = get_section(content)

            cur.execute(
                """
                INSERT INTO document_chunks
                (
                    content,
                    source,
                    page,
                    section,
                    embedding,
                    chunking_strategy
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    content,
                    source,
                    page_number,
                    section,
                    embedding,
                    "recursive",
                ),
            )

            total_loaded += 1


        # ====================================================
        # 3. STRUCTURE-AWARE CHUNKING
        # ====================================================

        structure = structure_aware_chunks(text)

        for section, content in structure:

            embedding = model.encode(
                content,
                normalize_embeddings=True
            ).tolist()

            cur.execute(
                """
                INSERT INTO document_chunks
                (
                    content,
                    source,
                    page,
                    section,
                    embedding,
                    chunking_strategy
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    content,
                    source,
                    page_number,
                    section,
                    embedding,
                    "structure-aware",
                ),
            )

            total_loaded += 1


# ------------------------------------------------------------
# Commit
# ------------------------------------------------------------

conn.commit()


# ------------------------------------------------------------
# Verification
# ------------------------------------------------------------

print("\nTotal chunks loaded:", total_loaded)

cur.execute(
    """
    SELECT
        chunking_strategy,
        COUNT(*)
    FROM document_chunks
    GROUP BY chunking_strategy
    ORDER BY chunking_strategy;
    """
)

print("\nChunks by strategy:")

for strategy, count in cur.fetchall():

    print(
        f"{strategy}: {count}"
    )


cur.close()
conn.close()