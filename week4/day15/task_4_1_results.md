# Task 4.1 — See the Vectors for Yourself

## 1. Corpus
- Domain: Clinic Appointment Management
- Number of sentences: 200

## 2. Embedding
- Model: all-MiniLM-L6-v2
- Library: Sentence Transformers
- Embedding shape: (200, 384)
- Vector dimension: 384
- Storage: data/embeddings.npy

## 3. Query 1
Query:
"What should I do if I cannot attend my appointment?"

### NumPy Results
1. ...
2. ...
3. ...
4. ...
5. ...

### Library Results
1. ...
2. ...
3. ...
4. ...
5. ...

Result: Same Top 5 ✅

## 4. Query 2
...

## 5. Query 3
...

## 6. Query 4
...

## 7. Query 5
...

## 8. Semantic vs Keyword Search

### Semantic Search Wins
Query:
"I won't be able to come for my scheduled visit. What should I do?"

Semantic result:
"Patients should contact the clinic when they cannot attend a booking."

Why:
The words are different, but the meaning is similar.

### Keyword Search Wins / Is Better
Example:
"What is ZQ-7391?"

Keyword/exact matching is useful for identifiers,
codes, IDs, error codes, etc.

## 9. Design Conclusion

Semantic search is useful for finding...
However, embeddings are not ideal for exact identifiers...
Therefore, a hybrid search approach can combine semantic
and keyword search.

## 10. Important Observation

For:
"How can a patient book an appointment?"

the expected relevant sentence ranked #4 instead of #1.

This shows that high cosine similarity does not always
guarantee the most relevant result.

## 11. Concepts Learned

- Embeddings
- Vector dimensions
- Normalization
- Cosine similarity
- Dot product
- Nearest neighbours
- Top-K retrieval
- Semantic search
- Keyword search
- Hybrid search