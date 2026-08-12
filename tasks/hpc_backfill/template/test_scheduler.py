import pytest
from scheduler import schedule


def J(jid, submit, nodes, walltime):
    return {"id": jid, "submit": submit, "nodes": nodes, "walltime": walltime}


def test_backfill_fills_the_hole():
    # J2 (4 nodes) blocks at t=0 with a reservation at t=10; J3 (1 node,
    # 5t) finishes by then, so it backfills at t=0.
    out = schedule([J("J1", 0, 2, 10), J("J2", 0, 4, 10), J("J3", 0, 1, 5)], 4)
    assert out == {"J1": 0, "J2": 10, "J3": 0}


def test_no_backfill_when_it_would_delay_head():
    # Same but J3 runs 15t: it would overshoot the t=10 reservation.
    out = schedule([J("J1", 0, 2, 10), J("J2", 0, 4, 10), J("J3", 0, 1, 15)], 4)
    assert out == {"J1": 0, "J2": 10, "J3": 20}


def test_exact_fit_backfill_boundary():
    # t + walltime == t_r is allowed (finishes exactly at the reservation).
    out = schedule([J("J1", 0, 2, 10), J("J2", 0, 3, 5), J("J3", 0, 1, 10)], 3)
    assert out == {"J1": 0, "J2": 10, "J3": 0}


def test_one_over_the_boundary_waits():
    out = schedule([J("J1", 0, 2, 10), J("J2", 0, 3, 5), J("J3", 0, 1, 11)], 3)
    assert out == {"J1": 0, "J2": 10, "J3": 15}


def test_staggered_submits_head_not_delayed():
    out = schedule([J("J1", 0, 2, 10), J("J2", 1, 2, 10), J("J3", 2, 1, 3)], 2)
    assert out == {"J1": 0, "J2": 10, "J3": 20}


def test_oversized_job_rejected():
    with pytest.raises(ValueError):
        schedule([J("J1", 0, 5, 1)], 4)
