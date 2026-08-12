"""Continuous-batching KV-budget simulator for an LLM inference server.

simulate(requests, kv_budget) -> {"finished": {id: step}, "rejected": [ids]}

requests: dicts {"id": str, "arrive": int, "prompt": int, "gen": int}
(gen >= 1). A request's KV footprint is prompt + gen tokens, reserved IN
FULL at admission and freed at the end of the step it finishes on.

Steps are integers starting at 0. Each step, in this order:

  1. ADMISSION — strict FIFO by (arrive, id), never skip ahead: repeatedly
     consider the earliest waiting request with arrive <= step.
       - footprint > kv_budget entirely -> mark it rejected, continue with
         the next waiting request;
       - footprint fits in the free budget -> admit it, continue;
       - otherwise STOP admitting this step (head-of-line blocking, even if
         later, smaller requests would fit).
  2. DECODE — every active request generates exactly one token. A request
     finishes on the step it produces its gen-th token; record that step in
     "finished". Its footprint becomes free at the END of that step (usable
     from the next step on).

The simulation ends when every request is finished or rejected.
"""


def simulate(requests, kv_budget):
    raise NotImplementedError
