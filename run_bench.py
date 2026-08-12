#!/usr/bin/env python3
"""Agentic A/B: run the same coding tasks through N agent harnesses x M models.

Each (model, harness, task) cell gets a fresh copy of the task template in an
isolated working directory. The agent is told to make `pytest` green and iterate.
Nothing gives the agent an oracle: it never sees the grading command's output
except by running the tests itself, and it is told not to edit the test files.

Grading is two-axis:
  pass_fraction  tests passed / tests run  (partial credit: fixing 1 of 2 planted
                 bugs scores 0.5, which is where model x harness discrimination
                 lives once binary pass/fail saturates)
  judge_score    optional LLM-as-judge score in [0,1] for craft and robustness,
                 so a solution that passes but is hardcoded to the tests ranks
                 below a clean, general one

Everything environment-specific lives in models.json -- endpoints, credentials,
model names and the harness command lines. Copy models.example.json and edit.

  python3 run_bench.py                          # every model, every harness
  python3 run_bench.py --models local-a          # a subset
  python3 run_bench.py --harnesses harness-a     # one harness
  python3 report_bench.py results/bench.json     # render the scorecard
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.join(HERE, "tasks")
CONFIG = os.environ.get("BENCH_CONFIG", os.path.join(HERE, "models.json"))


def load_config():
    if not os.path.exists(CONFIG):
        raise SystemExit(
            f"missing {CONFIG}\n"
            "Copy models.example.json to models.json and fill in your endpoints "
            "and model names. Nothing in this repo hardcodes a provider."
        )
    return json.load(open(CONFIG))


def run(cmd, cwd, timeout, log_path, env=None):
    """Run one agent invocation. A timeout is a result, not a crash: the cell is
    recorded with whatever the agent left on disk."""
    with open(log_path, "w") as log:
        t0 = time.time()
        try:
            rc = subprocess.run(cmd, cwd=cwd, timeout=timeout, stdout=log,
                                stderr=subprocess.STDOUT, env=env).returncode
        except subprocess.TimeoutExpired:
            rc = -1
            log.write("\n[[TIMEOUT]]\n")
        except FileNotFoundError as e:
            rc = -2
            log.write(f"\n[[HARNESS BINARY NOT FOUND: {e}]]\n")
        return rc, time.time() - t0


def grade(cwd):
    """-> (all_green, tail_line, pass_fraction)."""
    import re
    try:
        p = subprocess.run(["python3", "-m", "pytest", "-q"], cwd=cwd,
                           capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return False, "grading timed out", 0.0
    out = p.stdout + p.stderr
    lines = out.strip().splitlines()
    counts = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|error)s?\b", out)}
    total = sum(counts.values())
    frac = round(counts.get("passed", 0) / total, 3) if total else 0.0
    return p.returncode == 0, (lines[-1] if lines else ""), frac


def solution_untouched(wd):
    """True if the agent never edited the stub it was asked to implement.

    This catches a real and otherwise silent failure mode: an agent that
    mistranscribes its absolute working-directory path writes a correct solution
    into a directory that is never graded, then truthfully reports success. Such
    a cell is INVALID, not a failure of the model's coding ability, and pooling
    it with genuine failures corrupts the comparison.
    """
    for droot, _, files in os.walk(wd):
        for f in files:
            if f.endswith(".py") and not f.startswith("test_"):
                try:
                    if "NotImplementedError" not in open(os.path.join(droot, f)).read():
                        return False
                except OSError:
                    return False
    return True


def task_meta(task):
    mp = os.path.join(TASKS_DIR, task, "meta.json")
    if os.path.exists(mp):
        m = json.load(open(mp))
        return m.get("tier", "hard"), m.get("category", "code_hard")
    return "base", "code"


JUDGE_RUBRIC = (
    "You are a strict senior code reviewer scoring an AI agent's solution to a "
    "programming task. Judge the SOLUTION against the SPEC for correctness, "
    "edge-case handling, and code quality. The automated test result is given as "
    "context but you are scoring craft and robustness, not just pass/fail: a "
    "solution that passes but is fragile, hardcoded to the tests, or unidiomatic "
    "should score lower than a clean, general one. Reply with ONLY an integer 1-10.")


def judge_quality(cfg, spec, source, passed):
    """Quality score in [0,1], or None when no judge is configured.

    Never raises -- a judge outage must not fail a benchmark cell.
    """
    j = cfg.get("judge") or {}
    base, model = j.get("base_url"), j.get("model")
    key = os.environ.get(j.get("api_key_env", ""), "")
    if not (base and model and key):
        return None
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": JUDGE_RUBRIC},
            {"role": "user", "content": f"SPEC:\n{spec}\n\nSOLUTION:\n{source}\n\n"
                                        f"Automated tests passed: {passed}\n\nScore (1-10):"},
        ],
        "max_tokens": j.get("max_tokens", 512),
    }).encode()
    req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.load(r)
        txt = ((d.get("choices", [{}])[0].get("message", {}) or {}).get("content") or "")
        import re
        m = re.search(r"\d+", txt)
        return round(int(m.group(0)) / 10.0, 3) if m else None
    except Exception:
        return None


def gpu_cooldown(cfg):
    """Between locally-served models: wait for VRAM to drop, then settle.

    Serving several 30B-class models from one consumer GPU means loading them one
    at a time. Back-to-back sustained loads are the single most stressful thing
    you can do to an external-GPU enclosure, so pause between them.
    """
    c = cfg.get("gpu_cooldown") or {}
    if not c.get("enabled"):
        return
    idle_mib, max_wait, settle = c.get("idle_mib", 2000), c.get("max_wait_s", 180), c.get("settle_s", 15)
    deadline = time.time() + max_wait
    while time.time() < deadline:
        try:
            out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used",
                                  "--format=csv,noheader,nounits"],
                                 capture_output=True, text=True, timeout=10).stdout
            if int(out.strip().splitlines()[0]) < idle_mib:
                break
        except Exception:
            break
        time.sleep(5)
    time.sleep(settle)


def build_invocation(harness, spec, prompt, wd, timeout):
    """Turn a harness config entry into (argv, env).

    Placeholders in `cmd` and `env`:
      {prompt}    the task instruction
      {cwd}       the isolated working directory
      {model}     this harness's name for the current model
      {timeout_s} / {timeout_ms}
    """
    model = spec["models"].get(harness["name"])
    subs = {"prompt": prompt, "cwd": wd, "model": model or "",
            "timeout_s": str(int(timeout)), "timeout_ms": str(int(timeout * 1000))}

    def fill(s):
        for k, v in subs.items():
            s = s.replace("{" + k + "}", v)
        return s

    argv = [fill(a) for a in harness["cmd"] if not ("{model}" in a and not model)]
    env = dict(os.environ)
    for k, v in (harness.get("env") or {}).items():
        env[k] = fill(v)
    for k, v in (spec.get("env") or {}).items():
        env[k] = fill(v)
    return argv, env


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", help="subset of model keys")
    ap.add_argument("--harnesses", nargs="*", help="subset of harness keys")
    ap.add_argument("--tasks", nargs="*", help="subset of task names")
    ap.add_argument("--timeout", type=int, default=900, help="per-cell seconds")
    ap.add_argument("--keep-workdirs", action="store_true",
                    help="keep each cell's working copy for inspection")
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    cfg = load_config()
    os.makedirs(args.out, exist_ok=True)

    models = list(cfg["models"])
    if args.models:
        models = [m for m in models if m in args.models]
    harnesses = list(cfg["harnesses"])
    if args.harnesses:
        harnesses = [h for h in harnesses if h in args.harnesses]
    tasks = sorted(os.listdir(TASKS_DIR))
    if args.tasks:
        tasks = [t for t in tasks if t in args.tasks]

    out_json = os.path.join(args.out, f"bench{args.tag}.json")
    rows = []
    for model in models:                       # models OUTER: a local model loads once
        spec = cfg["models"][model]
        print(f"\n### MODEL {model} ({spec.get('kind', 'unknown')}) ###")
        for task in tasks:
            prompt = open(os.path.join(TASKS_DIR, task, "prompt.txt")).read().strip()
            template = os.path.join(TASKS_DIR, task, "template")
            tier, category = task_meta(task)
            for hkey in harnesses:
                harness = dict(cfg["harnesses"][hkey], name=hkey)
                # Underscores are deliberately absent from the prefix: some models
                # mistranscribe an underscore-heavy absolute path (writing dashes),
                # then work in a directory that is never graded. See solution_untouched.
                wd = tempfile.mkdtemp(prefix=f"bench-{hkey}-{model}-{task}-".replace("_", "-"))
                shutil.copytree(template, wd, dirs_exist_ok=True)
                log_path = os.path.join(args.out, f"{model}.{task}.{hkey}{args.tag}.log")
                print(f"  [{hkey:12s}] {task:18s} ... ", end="", flush=True)

                argv, env = build_invocation(harness, spec, prompt, wd, args.timeout)
                rc, wall = run(argv, wd, args.timeout + 30, log_path, env=env)

                try:
                    passed, tail, frac = grade(wd)
                except Exception as e:
                    passed, tail, frac = False, f"grade-error: {e}", 0.0
                invalid = solution_untouched(wd)

                parts = []
                for droot, _, dfiles in os.walk(wd):
                    for f in sorted(dfiles):
                        if f.endswith(".py") and not f.startswith("test_"):
                            try:
                                parts.append(f"# {os.path.relpath(os.path.join(droot, f), wd)}\n"
                                             + open(os.path.join(droot, f)).read())
                            except OSError:
                                pass
                src = ("\n\n".join(parts))[:8000] or "(no source produced)"
                jscore = None if invalid else judge_quality(cfg, prompt, src, passed)

                rows.append({"model": model, "task": task, "harness": hkey,
                             "tier": tier, "category": category,
                             "passed": passed, "pass_fraction": frac,
                             "judge_score": jscore, "invalid": invalid,
                             "rc": rc, "wall_s": round(wall, 1),
                             "pytest": tail, "log": log_path,
                             "workdir": wd if args.keep_workdirs else None})

                verdict = ("INVALID" if invalid else "PASS" if passed
                           else f"PART {frac:.0%}" if frac > 0 else "FAIL")
                js = f" judge={jscore}" if jscore is not None else ""
                print(f"{verdict} ({wall:.0f}s){js} {tail}")
                if invalid:
                    print("        ^ stub untouched: agent never edited the graded copy; "
                          "cell excluded from scoring")
                if not args.keep_workdirs:
                    shutil.rmtree(wd, ignore_errors=True)
                # Checkpoint every cell: a mid-run crash must never lose completed work.
                json.dump({"rows": rows}, open(out_json, "w"), indent=2)
        if spec.get("kind") == "local" and model != models[-1]:
            print("  [cooldown] waiting for the GPU to idle before the next local model ...")
            gpu_cooldown(cfg)

    summary = {}
    for model in models:
        for h in harnesses:
            hr = [r for r in rows if r["model"] == model and r["harness"] == h and not r["invalid"]]
            inv = sum(1 for r in rows if r["model"] == model and r["harness"] == h and r["invalid"])
            summary[f"{model}/{h}"] = {"solved": sum(r["passed"] for r in hr),
                                       "total": len(hr), "invalid": inv,
                                       "wall_s": round(sum(r["wall_s"] for r in hr), 1)}
    json.dump({"summary": summary, "rows": rows}, open(out_json, "w"), indent=2)
    print("\n=== SUMMARY (solved/graded) ===")
    for k, v in summary.items():
        extra = f"  [{v['invalid']} invalid]" if v["invalid"] else ""
        print(f"  {k:34} {v['solved']}/{v['total']}{extra}")
    print(f"\nwrote {out_json}")


if __name__ == "__main__":
    main()
