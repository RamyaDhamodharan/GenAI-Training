# Task 4.5 - Retrieval Failures

## Measured Recall Results

| Chunking Strategy | Recall@3 | Recall@5 |
|---|---:|---:|
| Fixed | 75% | 85% |
| Recursive | 95% | 95% |
| Structure-aware | 95% | 100% |

Winner: structure-aware chunking, because it achieved the highest Recall@5 (100%).

## Three Retrieval Failure Causes

### 1. Fixed chunking - sentence boundary split

Fixed-size chunking split important sentences across chunk boundaries. Q12 and Q19 had important evidence whose beginning was cut off.

Cause: fixed-size chunking does not respect natural sentence boundaries.

### 2. Fixed chunking - fragmented evidence

Q17 showed that relevant appointment-search evidence was fragmented because the beginning of the sentence was cut by the fixed chunk boundary.

Cause: fixed-size chunking can separate important evidence across chunks.

### 3. Semantic similarity confusion

Q4 asked what staff should verify before confirming a booking. Closely related scheduling and rescheduling chunks ranked above the exact booking-policy evidence.

Structure-aware chunking retrieved the correct evidence within the top 5.

Cause: semantically similar concepts can compete with the exact answer during vector search.

## Additional Observation

Q8 was marked as a fixed Recall@3 miss because the exact gold sentence was not present verbatim. However, the retrieved chunk contained an equivalent statement.

This shows that exact-string evaluation can sometimes be stricter than semantic relevance.

## Conclusion

The main retrieval failure causes were:

1. Poor chunk boundaries.
2. Fragmented evidence.
3. Semantic similarity confusion.

Structure-aware chunking achieved 100% Recall@5 and was selected as the winning strategy.
