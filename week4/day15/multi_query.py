from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer, util

CORPUS_PATH = Path("data/corpus.txt")
EMBEDDINGS_PATH = Path("data/embeddings.npy")

sentences = [
    line.strip()
    for line in CORPUS_PATH.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

embeddings = np.load(EMBEDDINGS_PATH)

model = SentenceTransformer("all-MiniLM-L6-v2")

queries = [
    "How can a patient book an appointment?",
    "How do I change my appointment?",
    "How can I find an available doctor?",
    "How are patient records protected?",
]


for query in queries:
    print("\n" + "=" * 70)
    print("QUERY:")
    print(query)

    # -------------------------
    # NumPy search
    # -------------------------
    query_embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    similarities = embeddings @ query_embedding
    top_indices = np.argsort(similarities)[::-1][:5]

    print("\n--- NumPy Search ---")

    for rank, index in enumerate(top_indices, start=1):
        print(f"{rank}. Score: {similarities[index]:.4f}")
        print(f"   {sentences[index]}")

    # -------------------------
    # Library search
    # -------------------------
    results = util.semantic_search(
        query_embedding,
        embeddings,
        top_k=5,
    )[0]

    print("\n--- SentenceTransformers Search ---")

    for rank, result in enumerate(results, start=1):
        index = result["corpus_id"]
        score = result["score"]

        print(f"{rank}. Score: {score:.4f}")
        print(f"   {sentences[index]}")