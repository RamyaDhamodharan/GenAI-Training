from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


CORPUS_PATH = Path("data/corpus.txt")
EMBEDDINGS_PATH = Path("data/embeddings.npy")


# Load corpus
sentences = [
    line.strip()
    for line in CORPUS_PATH.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

# Load stored embeddings
embeddings = np.load(EMBEDDINGS_PATH)

# Load the same embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


query = "What should I do if I cannot attend my appointment?"

# Convert query into a vector
query_embedding = model.encode(
    query,
    convert_to_numpy=True,
    normalize_embeddings=True,
)


# -----------------------------------------
# Manual cosine similarity using NumPy
# -----------------------------------------

similarities = embeddings @ query_embedding

# Highest similarity = closest meaning
top_k = 5

top_indices = np.argsort(similarities)[::-1][:top_k]


print("\nQuery:")
print(query)

print("\nTop 5 results:\n")

for rank, index in enumerate(top_indices, start=1):
    print(f"{rank}. Similarity: {similarities[index]:.4f}")
    print(f"   {sentences[index]}")
    print()