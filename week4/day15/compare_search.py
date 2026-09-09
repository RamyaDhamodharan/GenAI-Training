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

# Load embeddings
embeddings = np.load(EMBEDDINGS_PATH)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def semantic_search(query, top_k=5):
    query_embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    similarities = embeddings @ query_embedding
    top_indices = np.argsort(similarities)[::-1][:top_k]

    return [
        (index, similarities[index])
        for index in top_indices
    ]


def keyword_search(query, top_k=5):
    query_words = set(query.lower().split())

    results = []

    for index, sentence in enumerate(sentences):
        sentence_words = set(sentence.lower().split())

        # Count how many query words appear in the sentence
        matches = len(query_words & sentence_words)

        if matches > 0:
            results.append((index, matches))

    # Highest number of matching words first
    results.sort(key=lambda x: x[1], reverse=True)

    return results[:top_k]


queries = [
    # Semantic search should perform well
    "I won't be able to come for my scheduled visit. What should I do?",

    # Exact keyword/code search should perform well
    "What is ZQ-7391?",
]


for query in queries:

    print("\n" + "=" * 70)
    print("QUERY:")
    print(query)

    # -------------------------
    # Semantic Search
    # -------------------------
    print("\n--- Semantic Search ---")

    semantic_results = semantic_search(query)

    for rank, (index, score) in enumerate(semantic_results, start=1):
        print(f"{rank}. Score: {score:.4f}")
        print(f"   {sentences[index]}")

    # -------------------------
    # Keyword Search
    # -------------------------
    print("\n--- Keyword Search ---")

    keyword_results = keyword_search(query)

    if not keyword_results:
        print("No keyword matches found.")
    else:
        for rank, (index, matches) in enumerate(keyword_results, start=1):
            print(f"{rank}. Keyword matches: {matches}")
            print(f"   {sentences[index]}")