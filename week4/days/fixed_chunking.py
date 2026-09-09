from pathlib import Path

DOCUMENTS_DIR = Path("data/documents")
OUTPUT_FILE = Path("data/fixed_chunks.txt")

CHUNK_SIZE = 300


def fixed_chunk(text, chunk_size):
    chunks = []

    for start in range(0, len(text), chunk_size):
        chunk = text[start:start + chunk_size]
        chunks.append(chunk)

    return chunks


all_chunks = []

for file_path in DOCUMENTS_DIR.glob("*.txt"):
    if file_path.name == "clinic_patient_handbook_ocr.txt":
        source = "clinic_patient_handbook_scanned.pdf"
    else:
        source = file_path.name

    text = file_path.read_text(encoding="utf-8")

    chunks = fixed_chunk(text, CHUNK_SIZE)

    for index, chunk in enumerate(chunks):
        all_chunks.append(
            f"--- CHUNK {len(all_chunks) + 1} ---\n"
            f"Source: {source}\n"
            f"Chunk index: {index}\n\n"
            f"{chunk}\n"
        )

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE.write_text("\n".join(all_chunks), encoding="utf-8")

print(f"Total chunks: {len(all_chunks)}")
print(f"Saved to: {OUTPUT_FILE}")