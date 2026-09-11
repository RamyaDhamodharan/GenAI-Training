from pathlib import Path
import re

DOCUMENTS_DIR = Path("data/documents")
OUTPUT_FILE = Path("data/structure_aware_chunks.txt")


def structure_aware_chunk(text):
    lines = text.splitlines()

    chunks = []
    current_section = []
    current_heading = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Detect numbered section headings
        if re.match(r"^\d+\.\s+", line):
            if current_section:
                chunks.append(
                    (current_heading, "\n".join(current_section))
                )

            current_heading = line
            current_section = [line]

        elif line.startswith("CLINIC "):
            # Document title
            continue

        elif line.startswith("--- PAGE"):
            # Page marker is metadata, not content
            continue

        else:
            current_section.append(line)

    if current_section:
        chunks.append(
            (current_heading, "\n".join(current_section))
        )

    return chunks


all_chunks = []

for file_path in DOCUMENTS_DIR.glob("*.txt"):

    if file_path.name == "clinic_patient_handbook_ocr.txt":
        source = "clinic_patient_handbook_scanned.pdf"
    else:
        source = file_path.name

    text = file_path.read_text(encoding="utf-8")

    sections = structure_aware_chunk(text)

    for index, (section, chunk) in enumerate(sections):
        all_chunks.append(
            f"--- CHUNK {len(all_chunks) + 1} ---\n"
            f"Source: {source}\n"
            f"Section: {section}\n"
            f"Chunk index: {index}\n\n"
            f"{chunk}\n"
        )


OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE.write_text("\n".join(all_chunks), encoding="utf-8")

print(f"Total chunks: {len(all_chunks)}")
print(f"Saved to: {OUTPUT_FILE}")