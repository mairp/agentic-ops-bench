# Agentic Ops Bench

A small, honest benchmark for the question I actually care about: **can models I run
myself, on one consumer GPU, do my day job as well as hosted frontier models can?**

**[Read the report (PDF)](benchmark-report.pdf)** — leaderboard, quality-vs-latency
trade-off, per-domain breakdown, and the harness comparison.

My day job is agentic operations work — AIOps alert correlation, NetDevOps config
compilation and drift planning, HPC scheduling, inference serving, RAG pipelines,
tool-calling loops. So those are the tasks. Not leetcode, not trivia.

It measures two things at once:

- **model** — the weights doing the reasoning
- **harness** — the agent scaffolding driving them (tool loop, context management,
  retry policy)

Both matter, and the second is usually invisible in published benchmarks. Here the
same model is run through two different agent CLIs over identical tasks, so the
harness contribution becomes measurable.

## What a run looks like

Each `(model, harness, task)` cell gets a **fresh copy** of the task template in an
isolated working directory. The agent is told to make `pytest` green and iterate.
It never gets an oracle — no test output is fed to it, and it is instructed not to
edit the test files. Then the cell is graded on two independent axes:

| axis | what it measures |
|---|---|
| `pass_fraction` | tests passed / tests run — **partial credit**, so fixing 1 of 2 planted bugs scores 0.5 |
| `judge_score` | optional LLM-as-judge score in [0,1] for correctness, edge cases and craft |

The judge exists because binary pass/fail saturates fast on capable models, and
because a solution that passes by hardcoding the test cases is not the same thing as
a solution that passes because it is correct. Wall-clock time is recorded per cell —
real time to a finished task, every tool call and retry included, not token
throughput.

## Task battery

15 tasks in three tiers (`tasks/<name>/{prompt.txt,meta.json,template/}`):

- **hard** — held-out EvalPlus HumanEval+/MBPP+ problems, a cross-module refactor,
  and a long-context needle retrieval
- **domain** — the operations work: `netauto_acl` (intent → Cisco-style extended ACL
  compiler), `netauto_drift` (config-drift planning), `aiops_correlate` (alert
  correlation), `hpc_backfill` (backfill scheduling), `infer_batcher` (KV-budget
  batching), `rag_pipeline` (retrieval pipeline debugging), `agent_toolloop`
  (tool-calling loop)
- each task ships a failing `pytest` suite that encodes the contract

The battery was curated with Fable 5. Task content is synthetic and vendor-neutral:
addresses are RFC1918 examples, and no task contains real infrastructure, topology,
or configuration from any organisation.

## Running it

```bash
cp models.example.json models.json     # edit: your endpoints, model names, harness CLIs
export JUDGE_API_KEY=...               # optional; without it you get pass/fail only

python3 run_bench.py                   # every model x every harness x 15 tasks
python3 run_bench.py --models local-moe --harnesses harness-a --tasks netauto_acl
python3 report_bench.py results/bench.json -o results/REPORT.md
```

Nothing in this repo hardcodes a provider, endpoint, or agent CLI. `models.json`
holds all of that and is gitignored. Harness command lines are templates —
`{prompt}`, `{cwd}`, `{model}`, `{timeout_s}`, `{timeout_ms}` are substituted per
cell — so any agent CLI that can be driven headlessly can be plugged in.

Single-GPU hosts that hot-swap local models should leave `gpu_cooldown` enabled:
back-to-back sustained loads are hard on an external-GPU enclosure, and the cooldown
waits for VRAM to drain between models.

## The invalid-cell guard

`run_bench.py` checks whether the agent ever edited the stub it was asked to
implement. If the stub is untouched, the cell is marked **invalid** and excluded from
every aggregate rather than scored as a failure.

This is not hypothetical. Some models mistranscribe a long absolute working-directory
path — writing dashes where the real path has underscores — then write a perfectly
good solution into a directory that is never graded, run their own invented test
against it, and truthfully report success. Scored naively, that looks like a model
that cannot code. It is a plumbing failure, and pooling it with genuine failures
corrupts the comparison. The temp-directory prefix avoids underscores for the same
reason.

If you build your own agent benchmark, add this check. It is fifteen lines and it
will eventually save you from publishing a wrong number.

## Caveats, stated plainly

- **15 tasks per model per harness.** Small. Treat differences of a few points as
  noise.
- **The judge is a language model**, with the biases that implies. It sees the final
  source and the pass/fail result, not the trajectory.
- **This is one operator's setup.** My quantizations, my serving config, my hardware,
  my prompts, one day's run.
- **Not an official benchmark** for any model, vendor, product or organisation, and
  not endorsed by any of them. Results are not comparable to published leaderboards
  and are not a general claim about any model's capability. It is an engineering log.

## License

Apache-2.0 — see [LICENSE](LICENSE). Task content is original or derived from the public
EvalPlus datasets.
