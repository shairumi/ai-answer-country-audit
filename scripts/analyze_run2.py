"""Tables for run 2 (replication through Claude Code, 3 repeats, first answers only).

Usage: python scripts/analyze_run2.py [data/coded_run2.csv] [data/coded_run1.csv]

coded_run2.csv columns: id, prompt_id, framing_code, model, repeat, country_ai, overall_ai,
                        leak_strict, leak_broad
coded_run1.csv is the run-1 file (it has the blind AI codes in country_ai / overall_ai, keyed by
id like P1-US-1 where the last number is the model slot; the model name is in column `model`).

Run 2 has no human adjudication: every code is from the blind AI coder. The like-for-like
comparison with run 1 therefore uses run 1's AI-coder codes too.
"""
import csv, sys
from collections import Counter, defaultdict

FR = ["US", "IN", "HM"]
NAME = {"US": "US English", "IN": "Indian English", "HM": "Hindi/Marathi/Hinglish"}


def load(p):
    return list(csv.DictReader(open(p, newline="", encoding="utf-8")))


def tab(rows, label):
    print(f"\n=== {label} (n={len(rows)}) ===")
    for fr in FR:
        sub = [r for r in rows if r["framing_code"] == fr]
        c = Counter(r["country_ai"] for r in sub)
        o = Counter(r["overall_ai"] for r in sub)
        print(f"{NAME[fr]:<24} n={len(sub):<4} country: " + ", ".join(f"{k}: {v}" for k, v in sorted(c.items())))
        print(f"{'':<24}        overall: " + ", ".join(f"{k}: {v}" for k, v in sorted(o.items())))


def main(p2, p1):
    r2, r1 = load(p2), load(p1)
    tab(r2, "Run 2, all answers (blind AI coder)")
    tab([r for r in r2 if r["leak_strict"] != "1"], "Run 2, strict-leak answers removed")
    tab([r for r in r2 if r["leak_broad"] != "1"], "Run 2, broad-leak answers removed")
    print(f"\nStrict leaks: {sum(r['leak_strict']=='1' for r in r2)}; broad leaks: {sum(r['leak_broad']=='1' for r in r2)}")
    print("Strict leaks by model:", dict(Counter(r["model"] for r in r2 if r["leak_strict"] == "1")))
    print("Strict-leak answers by assumed country:", dict(Counter(r["country_ai"] for r in r2 if r["leak_strict"] == "1")))

    print("\nIndian-English prompts, India share by model (run 2, all answers / strict-clean):")
    for m in ("sonnet", "opus", "haiku"):
        a = [r for r in r2 if r["framing_code"] == "IN" and r["model"] == m]
        b = [r for r in a if r["leak_strict"] != "1"]
        print(f"  {m}: {sum(r['country_ai']=='India' for r in a)}/{len(a)}   clean {sum(r['country_ai']=='India' for r in b)}/{len(b)}")

    # consistency across the 3 repeats of the same (prompt, model)
    cells = defaultdict(list)
    for r in r2:
        cells[(r["prompt_id"], r["model"])].append(r["country_ai"])
    for fr in FR:
        cs = [v for (pid, m), v in cells.items() if pid.endswith("-" + fr)]
        same = sum(len(set(v)) == 1 for v in cs)
        print(f"Same country in all 3 repeats, {NAME[fr]}: {same}/{len(cs)} prompt-model cells")

    # run 1 (AI coder) vs run 2 per answer
    r1k = {}
    for r in r1:
        pid = r["id"].rsplit("-", 1)[0]
        r1k[(pid, r["model"])] = r["country_ai"]
    print("\nRun 1 (AI coder) vs run 2 repeats, same prompt and model, country match:")
    for fr in FR:
        tot = same = 0
        for r in r2:
            if r["framing_code"] == fr:
                tot += 1
                same += r["country_ai"] == r1k[(r["prompt_id"], r["model"])]
        print(f"  {NAME[fr]}: {same}/{tot}")
    print("Run 1 AI-coder India share, Indian English:", sum(1 for r in r1 if r["framing_code"] == "IN" and r["country_ai"] == "India"), "/ 30")


if __name__ == "__main__":
    main(*(sys.argv[1:3] if len(sys.argv) >= 3 else ["data/coded_run2.csv", "data/coded_run1.csv"]))
