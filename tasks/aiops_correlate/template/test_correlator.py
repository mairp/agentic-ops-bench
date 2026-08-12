from correlator import correlate


def E(ts, dev, msg):
    return {"ts": ts, "device": dev, "msg": msg}


def test_dedup_anchored_window():
    out = correlate([E(0, "r1", "BGP-DOWN"), E(60, "r1", "BGP-DOWN"),
                     E(61, "r1", "BGP-DOWN")])
    assert out == [
        {"ts": 0, "device": "r1", "msg": "BGP-DOWN", "count": 2},
        {"ts": 61, "device": "r1", "msg": "BGP-DOWN", "count": 1},
    ]


def test_input_may_be_unsorted():
    evs = [E(61, "r1", "BGP-DOWN"), E(0, "r1", "BGP-DOWN"),
           E(60, "r1", "BGP-DOWN")]
    assert correlate(evs) == correlate(list(reversed(evs)))
    assert correlate(evs)[0]["count"] == 2


def test_flap_collapses_three_link_alerts():
    out = correlate([E(0, "r1", "LINK-DOWN"), E(100, "r1", "LINK-UP"),
                     E(200, "r1", "LINK-DOWN")])
    assert out == [{"ts": 0, "device": "r1", "msg": "LINK-FLAP", "count": 3}]


def test_two_link_alerts_survive():
    out = correlate([E(0, "r1", "LINK-DOWN"), E(100, "r1", "LINK-UP")])
    assert out == [
        {"ts": 0, "device": "r1", "msg": "LINK-DOWN", "count": 1},
        {"ts": 100, "device": "r1", "msg": "LINK-UP", "count": 1},
    ]


def test_widespread_adds_star_alert():
    out = correlate([E(0, "r1", "OSPF-ADJ-DOWN"), E(50, "r2", "OSPF-ADJ-DOWN"),
                     E(100, "r3", "OSPF-ADJ-DOWN")])
    assert {"ts": 0, "device": "*", "msg": "OSPF-ADJ-DOWN", "count": 3} in out
    assert len(out) == 4


def test_widespread_needs_three_devices():
    out = correlate([E(0, "r1", "OSPF-ADJ-DOWN"), E(50, "r2", "OSPF-ADJ-DOWN")])
    assert all(a["device"] != "*" for a in out)


def test_flap_alerts_do_not_go_widespread():
    evs = []
    for d in ("r1", "r2", "r3"):
        evs += [E(0, d, "LINK-DOWN"), E(30, d, "LINK-UP"), E(90, d, "LINK-DOWN")]
    out = correlate(evs)
    assert out == [{"ts": 0, "device": d, "msg": "LINK-FLAP", "count": 3}
                   for d in ("r1", "r2", "r3")]
