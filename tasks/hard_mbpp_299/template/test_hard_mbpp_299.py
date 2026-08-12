from solution import max_aggregate


def test_hidden():
    assert max_aggregate(*[[('Juan Whelan', 90), ('Sabah Colley', 88), ('Peter Nichols', 7), ('Juan Whelan', 122), ('Sabah Colley', 84)]]) == ('Juan Whelan', 212)
    assert max_aggregate(*[[('Juan Whelan', 50), ('Sabah Colley', 48), ('Peter Nichols', 37), ('Juan Whelan', 22), ('Sabah Colley', 14)]]) == ('Juan Whelan', 72)
    assert max_aggregate(*[[('Juan Whelan', 10), ('Sabah Colley', 20), ('Peter Nichols', 30), ('Juan Whelan', 40), ('Sabah Colley', 50)]]) == ('Sabah Colley', 70)
    assert max_aggregate(*[[('Alice', 80), ('Bob', 90), ('Charlie', 70), ('Alice', 60), ('Bob', 50), ('Charlie', 40)]]) == ('Alice', 140)
    assert max_aggregate(*[[('Alice', -50)]]) == ('Alice', -50)
    assert max_aggregate(*[[('Alice', 80), ('Bob', -90), ('Charlie', 70), ('Alice', -60), ('Bob', 50), ('Charlie', 40)]]) == ('Charlie', 110)
    assert max_aggregate(*[[('Alice', 80), ('Bob', 90), ('Charlie', 70), ('Alice', 80), ('Bob', 70), ('Charlie', 70)]]) == ('Alice', 160)
    assert max_aggregate(*[[('Alice', 50), ('Bob', 60), ('Charlie', 70), ('David', 80), ('Alice', 90), ('Bob', 100), ('Charlie', 110), ('David', 120), ('Alice', 130), ('Bob', 140), ('Charlie', 150), ('David', 160)]]) == ('David', 360)
    assert max_aggregate(*[[('Alice', 80), ('Bob', -90), ('Charlie', 70), ('Alice', -60), ('Bob', 50)]]) == ('Charlie', 70)
    assert max_aggregate(*[[('Alice', 80), ('Bob', -90), ('Charlie', 70), ('Alice', -60), ('Bobb', 50), ('Charlie', 40)]]) == ('Charlie', 110)
    assert max_aggregate(*[[('Alice', -50), ('Alice', -50)]]) == ('Alice', -100)
    assert max_aggregate(*[[('Alice', 80), ('Bob', -90), ('Charlie', 70), ('Bob', 50)]]) == ('Alice', 80)
    assert max_aggregate(*[[('Alice', 80), ('Bob', -90), ('Charlie', 70), ('Alice', -60), ('Bob', 50), ('Charlie', 40), ('Bob', -90)]]) == ('Charlie', 110)
    assert max_aggregate(*[[('Alice', 80), ('Bob', -90), ('Charlie', 70), ('Alice', -60), ('Bobb', 50)]]) == ('Charlie', 70)
    assert max_aggregate(*[[('Alice', 80), ('Bob', -90), ('Charlie', 70), ('Bob', 50), ('Charlie', 70), ('Charlie', 70)]]) == ('Charlie', 210)
