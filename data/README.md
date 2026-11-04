# Data

- `prompts.csv`: 30 prompts (10 questions x 3 framings). No prompt names a country.
- `responses_run1.csv`: run 1, three Claude models, first answer plus up to three "I live in India." follow-ups.
- `coded_run1.csv`: one row per answer with first-pass, blind-AI and final codes. `leak_flag` = 1 marks answers that referenced the researcher's own context (Cornell, Ithaca, New York, an email address). `final_source` says whether the final code was agreed, adjudicated, or is still pending.

## Context leak in run 1

Run 1 went through a tool that attached account context, so 8 answers referenced the researcher's own context. Those rows stay in the data and are flagged; the report shows results with and without them. The clean re-run (`scripts/rerun_api.py`) sends only the prompt through the API; `scripts/check_leaks.py` checks its output for the same terms.
