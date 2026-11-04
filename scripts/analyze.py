"""Compute the pilot's headline tables from data/coded_run1.csv.

Usage: python scripts/analyze.py [data/coded_run1.csv]

Reads one row per (prompt, framing, model) answer with these columns:
  id, prompt_number, framing_code, model, leak_flag,
  country_first (author first pass), country_ai (blind AI coder), country_final,
  overall_first, overall_ai, overall_final
and prints, for each coding stage (first pass, AI coder, final):
  - assumed country by framing (counts)
  - 'Yes' (calibrated as is) by framing
and agreement between first pass and AI coder. Nothing is hard-coded; every number in the
report comes from running this file.
"""
import csv, sys
from collections import Counter, defaultdict

FR = ["US", "IN", "HM"]
FR_NAME = {"US": "US English", "IN": "Indian English", "HM": "Hindi/Marathi/Hinglish"}


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def country_table(rows, col):
    t = defaultdict(Counter)
    for r in rows:
        t[r["framing_code"]][r[col]] += 1
    return t


def yes_table(rows, col):
    t = defaultdict(Counter)
    for r in rows:
        v = r[col].strip().rstrip("?")
        t[r["framing_code"]][v] += 1
    return t


def show(rows, label, ccol, ocol):
    print(f"\n=== {label} (n={len(rows)}) ===")
    ct, ot = country_table(rows, ccol), yes_table(rows, ocol)
    for fr in FR:
        n = sum(ct[fr].values())
        c = ", ".join(f"{k}: {v}" for k, v in sorted(ct[fr].items()))
        o = ", ".join(f"{k}: {v}" for k, v in sorted(ot[fr].items()))
        print(f"{FR_NAME[fr]:<24} n={n:<3} country -> {c}")
        print(f"{'':<24}        overall -> {o}")


def agreement(rows, a, b):
    same = sum(1 for r in rows if r[a] == r[b])
    return same, len(rows)


def main(path):
    rows = load(path)
    show(rows, "First pass (author)", "country_first", "overall_first")
    show(rows, "Blind AI coder", "country_ai", "overall_ai")
    show(rows, "Final (after adjudication)", "country_final", "overall_final")
    clean = [r for r in rows if r["leak_flag"] != "1"]
    show(clean, "Final, leak-flagged rows removed", "country_final", "overall_final")
    s, n = agreement(rows, "country_first", "country_ai")
    print(f"\nFirst pass vs AI coder, country: {s}/{n} agree")
    s, n = agreement(rows, "overall_first", "overall_ai")
    print(f"First pass vs AI coder, overall: {s}/{n} agree")
    by_model = defaultdict(Counter)
    for r in rows:
        if r["framing_code"] == "IN":
            by_model[r["model"]][r["country_final"]] += 1
    print("\nIndian-English prompts, final country by model:")
    for m, c in by_model.items():
        print(f"  {m}: " + ", ".join(f"{k}: {v}" for k, v in sorted(c.items())))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/coded_run1.csv")
