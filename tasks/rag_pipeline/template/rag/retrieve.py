"""Top-k retrieval over chunked tokens."""
from rag.chunker import chunk
from rag.scorer import score


def top_k(query_tokens, doc_tokens, size, overlap, k):
    """Chunk the doc, score every chunk, return the indices of the k
    highest-scoring chunks; ties break toward the lower index."""
    chunks = chunk(doc_tokens, size, overlap)
    scores = score(query_tokens, chunks)
    order = sorted(range(len(chunks)), key=lambda i: (-scores[i], i))
    return order[:k]
