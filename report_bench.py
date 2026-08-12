#!/usr/bin/env python3
"""Render a bench.json produced by run_bench.py as a markdown scorecard.

  python3 report_bench.py results/bench.json [-o results/REPORT.md]

Cells flagged `invalid` (the agent never edited the graded copy) are excluded
from every aggregate and reported separately, so a harness plumbing failure is
never silently counted as a model failure.
"""
import argparse
import collections
import json
import statistics


def mean(xs):
    return statistics.mean(xs) if xs else None


def fmt(x, pct=False, nd=2):
    if x is None:
        return "—"
    return f"{100*x:.0f}%" if pct else f"{x:.{nd}f}"


def agg(rows, **flt):
    sel = [r for r in rows if all(r.get(k) == v for k, v in flt.items()) and not r.get("invalid")]
    return (mean([r["pass_fraction"] for r in sel]),
            mean([r["judge_score"] for r in sel if r.get("judge_score") is not None]),
            mean([r["wall_s"] for r in sel]), len(sel))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path")
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args()

    data = json.load(open(args.json_path))
    rows = data["rows"]
    models = sorted({r["model"] for r in rows})
    harnesses = sorted({r["harness"] for r in rows})
    tiers = sorted({r["tier"] for r in rows})
    cats = sorted({r["category"] for r in rows})

    out = ["# Agentic benchmark — model × harness\n",
           "`pass` = mean per-test pass fraction (partial credit). "
           "`judge` = LLM-as-judge quality in [0,1]. "
           "`median` = wall-clock seconds to a finished task, tool calls included.\n"]

    invalid = [r for r in rows if r.get("invalid")]
    if invalid:
        out.append(f"> **{len(invalid)} cell(s) excluded as invalid** — the agent never edited the "
                   "graded working copy (usually a mistranscribed absolute path), so the run says "
                   "nothing about the model. Excluded from every table below.\n")
        for r in invalid:
            out.append(f"> - `{r['model']}` / `{r['harness']}` / `{r['task']}`")
        out.append("")

    out.append("## Leaderboard — pooled over harnesses\n")
    out.append("| model | pass | judge | median s | cells |")
    out.append("|---|---|---|---|---|")
    board = []
    for m in models:
        p, j, w, n = agg(rows, model=m)
        med = statistics.median([r["wall_s"] for r in rows
                                 if r["model"] == m and not r.get("invalid")] or [0])
        board.append((j if j is not None else -1, m, p, j, med, n))
    for _, m, p, j, med, n in sorted(board, reverse=True):
        out.append(f"| {m} | {fmt(p, pct=True)} | {fmt(j, nd=3)} | {med:.0f} | {n} |")

    out.append("\n## Per harness\n")
    out.append("| model | harness | pass | judge | mean s | cells |")
    out.append("|---|---|---|---|---|---|")
    for m in models:
        for h in harnesses:
            p, j, w, n = agg(rows, model=m, harness=h)
            # Key the empty row off the cell count, not the mean latency: a cell that
            # finishes in under a second has a falsy mean and is still a real result.
            if n:
                out.append(f"| {m} | {h} | {fmt(p, pct=True)} | {fmt(j, nd=3)} | "
                           f"{w:.0f} | {n} |")
            else:
                out.append(f"| {m} | {h} | — | — | — | 0 |")

    out.append("\n## By tier\n")
    out.append("| model | harness | " + " | ".join(f"{t} pass" for t in tiers) + " |")
    out.append("|---" * (2 + len(tiers)) + "|")
    for m in models:
        for h in harnesses:
            cells = [fmt(agg(rows, model=m, harness=h, tier=t)[0], pct=True) for t in tiers]
            out.append(f"| {m} | {h} | " + " | ".join(cells) + " |")

    out.append("\n## By capability dimension (pass rate, pooled over harnesses)\n")
    out.append("| model | " + " | ".join(cats) + " |")
    out.append("|---" * (1 + len(cats)) + "|")
    for m in models:
        cells = [fmt(agg(rows, model=m, category=c)[0], pct=True) for c in cats]
        out.append(f"| {m} | " + " | ".join(cells) + " |")

    out.append("\n## Per-task detail\n")
    out.append("| model | task | tier | " + " | ".join(harnesses) + " |")
    out.append("|---" * (3 + len(harnesses)) + "|")
    by = {(r["model"], r["task"], r["harness"]): r for r in rows}
    tasks = sorted({r["task"] for r in rows})
    for m in models:
        for t in tasks:
            marks = []
            tier = ""
            for h in harnesses:
                r = by.get((m, t, h))
                if not r:
                    marks.append("—")
                    continue
                tier = r["tier"]
                if r.get("invalid"):
                    marks.append("⊘ invalid")
                else:
                    sym = "✓" if r["passed"] else ("◐" if r["pass_fraction"] > 0 else "✗")
                    j = f"·{r['judge_score']:.2f}" if r.get("judge_score") is not None else ""
                    marks.append(f"{sym}{j} {r['wall_s']:.0f}s")
            out.append(f"| {m} | {t} | {tier} | " + " | ".join(marks) + " |")

    out.append("\n## Totals\n")
    for h in harnesses:
        sel = [r for r in rows if r["harness"] == h and not r.get("invalid")]
        out.append(f"- **{h}** — {sum(r['passed'] for r in sel)}/{len(sel)} solved, "
                   f"mean judge {fmt(mean([r['judge_score'] for r in sel if r.get('judge_score') is not None]), nd=3)}")

    text = "\n".join(out) + "\n"
    if args.out:
        open(args.out, "w").write(text)
        print(f"wrote {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
