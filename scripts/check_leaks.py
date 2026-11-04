"""Flag answers that mention the researcher's own context (a sign of account-context leakage).

Usage: python scripts/check_leaks.py data/rerun_responses.jsonl
Prints every turn-0 answer that contains a watched term, so you can confirm the clean run has none.
"""
import json, re, sys

TERMS = ["cornell", "ithaca", "tompkins", "cayuga", "your email", "email suggests", ".edu", "new york"]  # "new york" alone is a weaker signal


def main(path):
    hits = 0
    total = 0
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        total += 1
        first = d["turns"][0].lower()
        found = [t for t in TERMS if re.search(re.escape(t), first)]
        if found:
            hits += 1
            print(f"LEAK? {d['prompt_id']} {d['model_requested']} repeat {d['repeat']}: {found}")
    print(f"{hits} of {total} first answers contain a watched term.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
