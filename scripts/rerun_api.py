"""Clean re-run of the pilot through the Anthropic API.

Why this exists: the first run went through a tool that attached account context
(email domain, location), and 7 answers referenced Cornell, Ithaca or New York.
This script sends ONLY the prompt text. No system prompt, no memory, no tools,
default sampling settings. It then sends the same follow-up ("I live in India.")
up to three times, keeping the conversation going, exactly as in run 1.

Setup:
    pip install anthropic
    export ANTHROPIC_API_KEY=...          # a Console API key, not a claude.ai login
Usage:
    python scripts/rerun_api.py --limit 3                 # smoke test (3 jobs)
    python scripts/rerun_api.py                           # full run: 30 prompts x 3 models x 1 repeat
    python scripts/rerun_api.py --repeats 3 --out data/rerun_responses_x3.jsonl

It writes one JSON line per (prompt, model, repeat) after every job, so you can
stop and re-run: finished jobs are skipped. Check the output for leaks with
    python scripts/check_leaks.py data/rerun_responses.jsonl
"""
import argparse, csv, json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path

MODELS = ["claude-sonnet-5-5", "claude-opus-5-5", "claude-haiku-5-5"]
FOLLOWUP = "I live in India."
N_FOLLOWUPS = 3
MAX_TOKENS = 2000


def load_prompts(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def done_keys(out):
    keys = set()
    if Path(out).exists():
        for line in open(out, encoding="utf-8"):
            line = line.strip()
            if line:
                d = json.loads(line)
                keys.add((d["prompt_id"], d["model_requested"], d["repeat"]))
    return keys


def ask(client, model, history):
    r = client.messages.create(model=model, max_tokens=MAX_TOKENS, messages=history)
    text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
    return text, {"model_returned": r.model, "stop_reason": r.stop_reason,
                  "input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens}


def ask_retry(client, model, history, tries=5):
    for i in range(tries):
        try:
            return ask(client, model, history)
        except Exception as e:  # noqa: BLE001
            code = getattr(e, "status_code", None)
            if code in (400, 401, 403, 404):
                sys.exit(f"\nStopping: {type(e).__name__}: {str(e)[:300]}\n"
                         "Check the model name and API key, then re-run (finished jobs are kept).")
            wait = 5 * (i + 1)
            print(f"   transient error ({type(e).__name__}: {str(e)[:100]}); retrying in {wait}s")
            time.sleep(wait)
    sys.exit("Stopping: no answer after retries. Re-run the same command to resume.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", default="data/prompts.csv")
    ap.add_argument("--out", default="data/rerun_responses.jsonl")
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0, help="run only the first N jobs (smoke test)")
    a = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set ANTHROPIC_API_KEY (a Console API key).")
    import anthropic
    client = anthropic.Anthropic()

    prompts = load_prompts(a.prompts)
    models = [m.strip() for m in a.models.split(",") if m.strip()]
    jobs = [(p, m, k) for k in range(1, a.repeats + 1) for p in prompts for m in models]
    if a.limit:
        jobs = jobs[: a.limit]
    finished = done_keys(a.out)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)

    for n, (p, model, k) in enumerate(jobs, start=1):
        if (p["prompt_id"], model, k) in finished:
            continue
        print(f"[{n}/{len(jobs)}] {p['prompt_id']} {model} repeat {k}")
        history = [{"role": "user", "content": p["text"]}]
        turns, meta = [], []
        for _ in range(N_FOLLOWUPS + 1):
            reply, m = ask_retry(client, model, history)
            turns.append(reply)
            meta.append(m)
            history += [{"role": "assistant", "content": reply}, {"role": "user", "content": FOLLOWUP}]
        rec = {"prompt_id": p["prompt_id"], "framing_code": p["framing_code"], "model_requested": model,
               "repeat": k, "turns": turns, "meta": meta,
               "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "sdk": "anthropic " + anthropic.__version__}
        with open(a.out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("Done:", a.out)


if __name__ == "__main__":
    main()
