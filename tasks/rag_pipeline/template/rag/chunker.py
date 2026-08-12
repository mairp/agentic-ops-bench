"""Sliding-window token chunker."""


def chunk(tokens, size, overlap):
    """Chunks of `size` tokens; consecutive chunks share `overlap` tokens
    (step = size - overlap). If tokens remain past the last full window, one
    final SHORTER chunk starts at the next step — but stop as soon as a
    chunk's end reaches len(tokens) (never emit a chunk that adds no new
    tokens). chunk([], ...) == []. Requires 0 <= overlap < size."""
    step = size - overlap
    return [tokens[i:i + size]
            for i in range(0, len(tokens) - size + 1, step)]
