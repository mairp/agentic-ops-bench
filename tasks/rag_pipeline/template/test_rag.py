import math
import pytest
from rag.chunker import chunk
from rag.scorer import score
from rag.retrieve import top_k


def test_chunk_exact_windows():
    assert chunk(list("abcdefghij"), 4, 1) == \
        [list("abcd"), list("defg"), list("ghij")]


def test_chunk_includes_tail():
    assert chunk(list("abcdefghijk"), 4, 1) == \
        [list("abcd"), list("defg"), list("ghij"), list("jk")]


def test_chunk_empty():
    assert chunk([], 4, 1) == []


def test_score_is_length_normalized():
    chunks = [["gpu", "gpu", "off", "bus"],
              ["gpu", "gpu", "reset", "then", "gpu", "ok", "link", "up",
               "again", "cool"],
              ["cpu", "fine"]]
    s = score(["gpu"], chunks)
    idf = math.log(3 / 2)
    assert s[0] == pytest.approx(2 * idf / 4)
    assert s[1] == pytest.approx(3 * idf / 10)
    assert s[2] == 0.0
    assert s[0] > s[1]


def test_retrieve_finds_dense_tail():
    doc = list("abcdefghij") + ["gpu", "gpu"]
    assert top_k(["gpu"], doc, 4, 1, 2) == [3, 0]
