#!/usr/bin/env python3
"""
Pilot orchestrator (v2).

Modes:

  1. ingest  - read a JSONL of v2 examples, verify each via SelfVerifier,
                write the verified set to the output JSONL. This is the
                mode the in-session pilot uses after I (the LLM) have
                generated a batch of raw examples.

  2. fetch   - print the grounding context for one (data_type, topic) so
                a human or LLM can write the example manually.

  3. report  - read a v2 JSONL, run the pruner, write the pruned set +
                a stats report. Mirrors scripts/data_pruner.py for the
                v2 catalog.

Usage:
    python run_pilot.py ingest --in raw.jsonl --out pilot_verified.jsonl
    python run_pilot.py fetch --data_type tool_use --topic "Inventorying actors by class"
    python run_pilot.py report --in pilot_verified.jsonl --out pilot_pruned.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows where the default is GBK.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from context_fetcher import ContextFetcher
from self_verifier import Verifier, VerificationReport


# --- mode: ingest ---

def cmd_ingest(args) -> int:
    fetcher = ContextFetcher()
    verifier = Verifier(fetcher)

    in_path = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n_in, n_verified, n_repaired, n_rejected = 0, 0, 0, 0
    fail_log: list[dict] = []
    with open(in_path, "r", encoding="utf-8") as fi, \
         open(out_path, "w", encoding="utf-8") as fo:
        for line in fi:
            line = line.strip()
            if not line:
                continue
            n_in += 1
            ex = json.loads(line)
            report = verifier.verify(ex)
            # Stage B (judgment): the in-session pilot is the judgment.
            # If mechanical_pass is True and there are no failed claims,
            # we auto-verify. Otherwise the example is rejected; the user
            # can re-submit with judgment="repaired" already set.
            if report.mechanical_pass and report.claims_failed == 0:
                verifier.attach_judgment(report, "verified", "auto-verified: mechanical pass, no failed claims")
                n_verified += 1
            else:
                verifier.attach_judgment(
                    report, "rejected",
                    f"mechanical_pass={report.mechanical_pass}, "
                    f"failed_claims={report.claims_failed}, "
                    f"failed_tools={report.tool_calls_issued - report.tool_calls_valid}"
                )
                n_rejected += 1
                fail_log.append({
                    "example_id": ex.get("id"),
                    "report": report.to_dict(),
                })
            ex["verified"] = (report.judgment == "verified")
            ex["verification"] = report.to_dict()
            fo.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"[INGEST] Ingested {n_in} examples")
    print(f"   verified: {n_verified}")
    print(f"   rejected: {n_rejected}")
    if fail_log:
        log_path = out_path.with_suffix(".failures.json")
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(fail_log, f, indent=2, ensure_ascii=False)
        print(f"   failure log: {log_path}")
    return 0


# --- mode: fetch ---

# Per-data-type default grounding recipe. Each recipe is a list of
# (method_name, kwargs) tuples that the fetcher can run.
DEFAULT_GROUNDING = {
    "concept_qa": [
        ("ai_project_context", {}),
        ("get_editor_context", {}),
    ],
    "tool_use": [
        ("get_editor_context", {}),
    ],
    "scene_understanding": [
        ("get_editor_context", {}),
        ("list_actors", {}),
    ],
    "console_diagnosis": [
        ("get_editor_context", {}),
    ],
}


def cmd_fetch(args) -> int:
    fetcher = ContextFetcher()
    recipe = DEFAULT_GROUNDING.get(args.data_type, [])
    grounding: dict = {"data_type": args.data_type, "topic": args.topic, "calls": []}
    for method_name, kwargs in recipe:
        method = getattr(fetcher, method_name, None)
        if method is None:
            continue
        t0 = time.time()
        try:
            result = method(**kwargs)
            ok = True
            err = ""
        except Exception as e:
            result = None
            ok = False
            err = f"{type(e).__name__}: {e}"
        grounding["calls"].append({
            "method": method_name,
            "kwargs": kwargs,
            "ok": ok,
            "error": err,
            "elapsed_s": round(time.time() - t0, 2),
            "result": result,
        })
    out = args.output or "-"
    text = json.dumps(grounding, ensure_ascii=False, indent=2)
    if out == "-":
        print(text)
    else:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Wrote grounding to {out}")
    return 0


# --- mode: report ---

def cmd_report(args) -> int:
    import data_pruner_v2 as pruner
    # Delegate to the pruner's main() with the right args.
    sys.argv = [
        sys.argv[0],
        "--input", args.input,
        "--output", args.output,
        "--min_quality", str(args.min_quality),
        "--dedup_threshold", str(args.dedup_threshold),
        "--min_tokens", str(args.min_tokens),
        "--per_type_min", str(args.per_type_min),
    ]
    pruner.main()
    return 0


# --- main ---

def main():
    parser = argparse.ArgumentParser(description="Pilot orchestrator (v2)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ingest = sub.add_parser("ingest", help="Verify a JSONL of v2 examples")
    p_ingest.add_argument("--in", dest="input", required=True)
    p_ingest.add_argument("--out", dest="output", required=True)

    p_fetch = sub.add_parser("fetch", help="Print grounding for one (data_type, topic)")
    p_fetch.add_argument("--data_type", required=True, choices=("concept_qa", "tool_use", "scene_understanding", "console_diagnosis"))
    p_fetch.add_argument("--topic", required=True)
    p_fetch.add_argument("--output", default="-")

    p_report = sub.add_parser("report", help="Prune a v2 JSONL")
    p_report.add_argument("--in", dest="input", required=True)
    p_report.add_argument("--out", dest="output", required=True)
    p_report.add_argument("--min_quality", type=float, default=3.0)
    p_report.add_argument("--dedup_threshold", type=float, default=0.7)
    p_report.add_argument("--min_tokens", type=int, default=100,
                          help="Minimum conversation length in tokens (default 100; lower to ~50 for v2 compact tool traces)")
    p_report.add_argument("--per_type_min", type=int, default=0,
                          help="If >0, ensure each data_type has at least N records in output (Fix 2)")

    args = parser.parse_args()
    if args.cmd == "ingest":
        return cmd_ingest(args)
    if args.cmd == "fetch":
        return cmd_fetch(args)
    if args.cmd == "report":
        return cmd_report(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
