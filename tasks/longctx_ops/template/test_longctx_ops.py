from ops import dispatch, OPS

def test_all_handlers_add_their_index():
    for name, fn in OPS.items():
        k = int(name.split("_")[1])
        assert dispatch(name, 100) == 100 + k, f"{name} is wrong"
