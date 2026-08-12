import json
from toolloop import run_agent


def scripted(replies, seen=None):
    it = iter(replies)

    def model(messages):
        if seen is not None:
            seen.append([dict(m) for m in messages])
        return next(it)
    return model


def _boom():
    raise RuntimeError("kaput")


TOOLS = {"add": {"fn": lambda a, b: a + b, "required": ["a", "b"]},
         "boom": {"fn": _boom, "required": []}}


def test_happy_path_tool_then_final():
    seen = []
    model = scripted([json.dumps({"tool": "add", "args": {"a": 2, "b": 3}}),
                      json.dumps({"final": "5"})], seen)
    res = run_agent(model, TOOLS, "add 2 and 3")
    assert res == {"answer": "5", "turns": 2, "timeout": False}
    assert seen[1][0] == {"role": "user", "content": "add 2 and 3"}
    assert seen[1][-1] == {"role": "tool", "content": "5"}


def test_invalid_json_then_recovery():
    model = scripted(["not json at all", json.dumps({"final": 42})])
    assert run_agent(model, TOOLS, "x") == \
        {"answer": 42, "turns": 2, "timeout": False}


def test_invalid_json_observation_text():
    seen = []
    model = scripted(["not json", json.dumps({"final": 1})], seen)
    run_agent(model, TOOLS, "x")
    assert seen[1][-1] == {"role": "tool", "content": "error: invalid JSON"}


def test_unknown_tool_and_missing_arg():
    seen = []
    model = scripted([json.dumps({"tool": "mul", "args": {}}),
                      json.dumps({"tool": "add", "args": {"a": 1}}),
                      json.dumps({"final": "done"})], seen)
    res = run_agent(model, TOOLS, "x")
    assert res["turns"] == 3
    assert seen[1][-1]["content"] == "error: unknown tool mul"
    assert seen[2][-1]["content"] == "error: missing required argument b"


def test_tool_exception_is_an_observation():
    seen = []
    model = scripted([json.dumps({"tool": "boom"}),
                      json.dumps({"final": "ok"})], seen)
    res = run_agent(model, TOOLS, "x")
    assert seen[1][-1]["content"] == "error: kaput"
    assert res["answer"] == "ok"


def test_invalid_action_shape():
    seen = []
    model = scripted([json.dumps([1, 2]), json.dumps({"final": None})], seen)
    res = run_agent(model, TOOLS, "x")
    assert seen[1][-1]["content"] == "error: invalid action"
    assert res == {"answer": None, "turns": 2, "timeout": False}


def test_timeout():
    model = scripted([json.dumps({"tool": "add",
                                  "args": {"a": 1, "b": 1}})] * 3)
    assert run_agent(model, TOOLS, "x", max_turns=3) == \
        {"answer": None, "turns": 3, "timeout": True}
