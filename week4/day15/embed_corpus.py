from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


CORPUS_PATH = Path("data/corpus.txt")
OUTPUT_PATH = Path("data/embeddings.npy")

# Load corpus
sentences = [
    line.strip()
    for line in CORPUS_PATH.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

print(f"Number of sentences: {len(sentences)}")


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Convert sentences -> vectors
embeddings = model.encode(
    sentences,
    convert_to_numpy=True,
    normalize_embeddings=True,
)

print(f"Embedding shape: {embeddings.shape}")
print(f"First vector:\n{embeddings[0]}")
print(f"Vector dimension: {embeddings.shape[1]}")


# Save vectors
np.save(OUTPUT_PATH, embeddings)

print(f"Saved embeddings to: {OUTPUT_PATH}")