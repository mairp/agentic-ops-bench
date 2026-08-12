from batcher import simulate


def R(rid, arrive, prompt, gen):
    return {"id": rid, "arrive": arrive, "prompt": prompt, "gen": gen}


def test_admission_and_free_on_finish():
    # budget 10: R1 (3+2=5) and R2 (4+1=5) admitted at step 0; R3 (5+1=6)
    # blocked until R1's 5 free after step 1.
    out = simulate([R("R1", 0, 3, 2), R("R2", 0, 4, 1), R("R3", 0, 5, 1)], 10)
    assert out == {"finished": {"R1": 1, "R2": 0, "R3": 2}, "rejected": []}


def test_strict_fifo_no_skip_ahead():
    # R2 blocks the queue; R3 would fit but must NOT jump it.
    out = simulate([R("R1", 0, 6, 2), R("R2", 0, 4, 1), R("R3", 0, 1, 1)], 10)
    assert out == {"finished": {"R1": 1, "R2": 2, "R3": 2}, "rejected": []}


def test_oversized_request_rejected_not_blocking():
    out = simulate([R("R1", 0, 3, 2), R("R2", 0, 2, 1)], 4)
    assert out == {"finished": {"R2": 0}, "rejected": ["R1"]}


def test_late_arrival():
    out = simulate([R("R1", 3, 2, 2)], 10)
    assert out == {"finished": {"R1": 4}, "rejected": []}


def test_arrival_tie_broken_by_id():
    # Same arrival, only room for one: id order decides who goes first.
    out = simulate([R("b", 0, 4, 2), R("a", 0, 4, 2)], 6)
    assert out == {"finished": {"a": 1, "b": 3}, "rejected": []}
