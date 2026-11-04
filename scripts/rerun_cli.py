"""Replication run through Claude Code's headless mode (`claude -p`), billed to your Claude plan. No API key.

HONEST LIMIT: this route injects the account email into every call (tested: `claude -p` always adds a
"userEmail" context block, whatever flags are set). So this is a REPLICATION of run 1 under the same
condition, not a clean run. Answers that mention the researcher's context are flagged by check_leaks.py
and excluded in the report's "without leaked rows" tables. A truly clean run needs scripts/rerun_api.py.

Each (prompt, model, repeat) gets a fresh session started from an empty temporary folder. With --turns > 1
the follow-up "I live in India." resumes the SAME session.

Usage (from the repo root):
    python scripts/rerun_cli.py --limit 2 --models haiku        # smoke test
    python scripts/rerun_cli.py --repeats 3 --turns 1           # 30 prompts x 3 models x 3 repeats, first answers only
Finished jobs are skipped, so you can stop and re-run (for example after a usage limit resets).
Output: data/rerun_cli_responses.jsonl (same fields as rerun_api.py, plus flags_used and context_note).
"""
import argparse, csv, json, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path

ALIASES = ["sonnet", "opus", "haiku"]
FOLLOWUP = "I live in India."
TIMEOUT_S = 240
CONTEXT_NOTE = "Claude Code headless: account email injected by the tool; not a clean run."


def load_prompts(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def done_keys(out):
    keys = set()
    if Path(out).exists():
        for line in open(out, encoding="utf-8"):
            if line.strip():
                d = json.loads(line)
                keys.add((d["prompt_id"], d["model_requested"], d["repeat"]))
    return keys


def call(prompt, model, workdir, session=None, tools_off=True):
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "json"]
    if tools_off:
        cmd += ["--tools", ""]
    if session:
        cmd += ["--resume", session]
    r = None
    for attempt in range(3):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=TIMEOUT_S, cwd=workdir, stdin=subprocess.DEVNULL)
            break
        except subprocess.TimeoutExpired:
            print(f"   call took over {TIMEOUT_S}s (attempt {attempt + 1} of 3); retrying", flush=True)
            time.sleep(5)
    if r is None:
        sys.exit("Stopping: three calls in a row timed out. Check your connection, then re-run the same command to resume.")
    msg = (r.stderr or "") + (r.stdout or "")
    low = msg.lower()
    is_error = False
    try:
        is_error = bool(json.loads(r.stdout).get("is_error"))
    except Exception:  # noqa: BLE001
        pass
    if r.returncode != 0 or is_error:
        if any(x in low for x in ("usage limit", "limit reached", "rate limit", "resets at", "you've hit")):
            sys.exit("Stopping: looks like a usage limit. Wait for it to reset, then re-run the same command.\nRaw output: " + msg[-400:])
        sys.exit(f"Stopping: claude exited with code {r.returncode}.\nRaw output: {msg[-800:]}")
    d = json.loads(r.stdout)
    return d["result"], d.get("session_id"), list((d.get("modelUsage") or {}).keys())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", default="data/prompts.csv")
    ap.add_argument("--out", default="data/rerun_cli_responses.jsonl")
    ap.add_argument("--models", default=",".join(ALIASES), help="comma-separated aliases, e.g. sonnet,opus,haiku")
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--turns", type=int, default=1, help="1 = first answer only; 4 = first answer + 3 follow-ups")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--tools-on", action="store_true", help="leave Claude Code's tools on (default: off)")
    a = ap.parse_args()

    prompts = load_prompts(a.prompts)
    models = [m.strip() for m in a.models.split(",") if m.strip()]
    jobs = [(p, m, k) for k in range(1, a.repeats + 1) for p in prompts for m in models]
    if a.limit:
        jobs = jobs[: a.limit]
    finished = done_keys(a.out)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    flags = {"tools_off": not a.tools_on, "turns": a.turns}

    for n, (p, model, k) in enumerate(jobs, start=1):
        if (p["prompt_id"], model, k) in finished:
            continue
        print(f"[{n}/{len(jobs)}] {p['prompt_id']} {model} repeat {k}", flush=True)
        with tempfile.TemporaryDirectory() as wd:
            text, session, resolved = call(p["text"], model, wd, None, not a.tools_on)
            turns = [text]
            for _ in range(a.turns - 1):
                text, session, _r = call(FOLLOWUP, model, wd, session, not a.tools_on)
                turns.append(text)
        rec = {"prompt_id": p["prompt_id"], "framing_code": p["framing_code"], "model_requested": model,
               "model_resolved": resolved, "repeat": k, "turns": turns, "flags_used": flags,
               "context_note": CONTEXT_NOTE,
               "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        with open(a.out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("Done:", a.out)


if __name__ == "__main__":
    main()
