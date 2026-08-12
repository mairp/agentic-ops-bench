"""Length-normalized TF-IDF chunk scorer."""
import math


def score(query_tokens, chunks):
    """One score per chunk: the sum over the UNIQUE query terms of
    tf(term, chunk) * idf(term), DIVIDED by len(chunk) so long chunks do not
    win on raw volume (empty chunk -> 0.0). idf(term) = ln(N / df) with
    N = len(chunks) and df = number of chunks containing the term; terms
    with df == 0 contribute 0."""
    N = len(chunks)
    out = []
    for ch in chunks:
        s = 0.0
        for term in set(query_tokens):
            df = sum(1 for c in chunks if term in c)
            if df:
                s += ch.count(term) * math.log(N / df)
        out.append(s)
    return out
