from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer, util


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

# Load the same model
model = SentenceTransformer("all-MiniLM-L6-v2")


query = "What should I do if I cannot attend my appointment?"

query_embedding = model.encode(
    query,
    convert_to_numpy=True,
    normalize_embeddings=True,
)


# Library-based semantic search
results = util.semantic_search(
    query_embedding,
    embeddings,
    top_k=5,
)[0]


print("\nQuery:")
print(query)

print("\nTop 5 results using SentenceTransformers:\n")

for rank, result in enumerate(results, start=1):
    index = result["corpus_id"]
    score = result["score"]

    print(f"{rank}. Similarity: {score:.4f}")
    print(f"   {sentences[index]}")
    print()