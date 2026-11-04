# Pilot audit: what country does an AI answer assume?

A pilot study of whether AI answers to everyday questions assume a US reader, and how that changes with the language and dialect of the prompt (US English, Indian English, Hindi/Marathi/Hinglish).

- `report/REPORT.md`: the write-up. Every number comes from `scripts/analyze.py`.
- `data/`: prompts, run-1 responses, coded results. See `data/README.md` for the context-leak caveat.
- `coding/`: codebook, first-pass codes, blind second-coder codes, adjudication.
- `scripts/`: `rerun_api.py` (clean API re-run, needs an API key), `rerun_cli.py` (replication through a Claude plan; account email is injected, so not clean), `analyze.py`, `check_leaks.py`, `second_coder.py`.

Reproduce the tables: `python scripts/analyze.py data/coded_run1.csv`.
Clean re-run: set `ANTHROPIC_API_KEY`, then `python scripts/rerun_api.py --limit 3`, then the full run.
Replication without an API key: `python scripts/rerun_cli.py --repeats 3 --turns 1`, then `python scripts/check_leaks.py data/rerun_cli_responses.jsonl`. This route adds the account email to every call, so leaked answers are excluded from the report's clean tables.

Status: pilot, not peer reviewed. One vendor, three models, one sample per cell.
