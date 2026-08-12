"""Minimal scripted-model tool-calling agent loop.

run_agent(model, tools, task, max_turns=8) -> {"answer", "turns", "timeout"}

model: callable(messages) -> str. `messages` is the FULL transcript, a list
of {"role": ..., "content": ...} dicts, beginning
[{"role": "user", "content": task}]. After every model call, its reply is
appended as {"role": "assistant", "content": reply}; every observation is
appended as {"role": "tool", "content": obs}.

The reply must be a JSON object:
    {"final": <answer>}               -> stop, return the answer.
    {"tool": <name>, "args": {...}}   -> invoke a tool ("args" defaults
                                         to {} when omitted).

tools: {name: {"fn": callable, "required": [param, ...]}}; invocation is
fn(**args). Observation strings (EXACT):
    reply is not valid JSON                    -> "error: invalid JSON"
    JSON but not an object with "final"/"tool" -> "error: invalid action"
    unknown tool name                          -> "error: unknown tool <name>"
    a required param missing from args         -> "error: missing required argument <param>"
                                                  (first missing, in the tool's declared order)
    fn raises Exception e                      -> "error: <e>"
    success                                    -> str(<return value>)

Every model call is one turn. A "final" reply on turn n returns
{"answer": <answer>, "turns": n, "timeout": False}. If no "final" arrives
within max_turns turns, return {"answer": None, "turns": max_turns,
"timeout": True}.
"""


def run_agent(model, tools, task, max_turns=8):
    raise NotImplementedError
