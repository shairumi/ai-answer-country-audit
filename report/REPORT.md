# What country does an AI answer assume? A pilot audit

Rumiza Shaikh · Draft v3 · November 2026 · Status: pilot, not peer reviewed

## Summary

I asked three Claude models the same ten everyday questions in three framings: US English, Indian English, and Hindi/Marathi/Hinglish. No prompt names a country. After coding, US-English prompts were answered with US assumptions in 29 of 30 answers and Hindi, Marathi and Hinglish prompts with India assumptions in 29 of 30. Indian-English prompts were answered with India assumptions in only 12 of 30 answers (7 went US, 11 stayed generic). One follow-up ("I live in India.") fixed every uncalibrated answer. The pilot is small and covers one vendor. A replication with three repeats per cell (run 2, 270 answers) found the same pattern: which Indian-English prompts went to India depended mostly on whether they contained a hard locale word such as "lakh" or "12th". Both runs went through a route that adds the account email to every call, and some answers used it, so neither is a clean run. The result is a hypothesis for a larger study: these models may read the language of a prompt as a location signal without reading Indian-English phrasing the same way.

## Design

- 10 prompts in health, money, government services and education, each in three framings (30 prompts; see `data/prompts.csv`).
- 3 models: Claude Sonnet 5.5, Opus 5.5 and Haiku 5.5, one answer per prompt and model: 90 first answers (`data/responses_run1.csv`).
- Each conversation continued with "I live in India." up to three times to record how many turns a calibrated answer needed.
- Each first answer coded for assumed country, currency and units, institutions, local resources, tone, reply language, turns to calibrated, and overall fit for a reader in India (`coding/CODEBOOK.md`).

## Coding and validation

1. First pass by the author, AI-assisted.
2. A blind second coder (Claude Opus, headless, same rubric, without the first-pass codes) coded all 90 answers.
3. The author adjudicated the first-pass vs second-coder disagreements in a 36-answer spot-check (11 disagreements) with written rules (`coding/CODEBOOK.md`).

Agreement before adjudication, all 90 answers: assumed country 85 of 90, overall fit 72 of 90. The author then adjudicated the eight remaining disagreements on the other 54 answers, so every disagreement between the first pass and the second coder has a final code.

## Results (final codes)

Assumed country in the first answer:

| Framing | India | US | Generic |
|---|---|---|---|
| US English (n=30) | 0 | 29 | 1 |
| Indian English (n=30) | 12 | 7 | 11 |
| Hindi/Marathi/Hinglish (n=30) | 29 | 0 | 1 |

Overall fit for a reader in India, first answer:

| Framing | Yes | Partly | No |
|---|---|---|---|
| US English (n=30) | 1 | 9 | 20 |
| Indian English (n=30) | 14 | 9 | 7 |
| Hindi/Marathi/Hinglish (n=30) | 29 | 1 | 0 |

The US-English row is a sanity check, not a finding: those prompts were written for US readers.

Indian-English prompts that contained hard locale words ("lakh", "FD", "12th") mostly went India. The prompts about a landlord's deposit and a diabetes test went US in all three models.

First-pass coding gave 9 of 30 India answers for Indian English. After adjudication it is 12 of 30, so my first pass under-counted India-specific answers: three answers moved to India after I re-read them against the written rules, where the answer pointed to Indian resources or used Indian cultural vocabulary.

## Robustness

- **Leaked rows removed (8 answers referenced Cornell, Ithaca, New York or the researcher's email):** Indian English India 12 of 27; US English 25 of 26; Hindi/Marathi/Hinglish 28 of 29. One of the eight, a Marathi deposit answer, is flagged because it gives a New York example and student legal aid, the same pattern as the other flagged rows.
- **Borderline "Yes?" rows:** three Hindi/Marathi/Hinglish answers are counted as Yes. Counting them as Partly gives 26 Yes and 4 Partly.
- **US-English overall fit:** adjudication gave one US-English answer (a fever question mentioning 911 and Tylenol) a Yes, which is hard to square with the rubric's reader-in-India standard; it does not affect any country count.
- **By model (Indian English, assumed country, n=10 each):** Sonnet India 3, US 2, generic 5; Opus India 6, US 2, generic 2; Haiku India 3, US 3, generic 4. Too small to compare models.

## Run 2: replication with three repeats

Run 2 repeated the design through the same route as run 1 (Claude Code headless, one fresh session per answer), with three repeats per prompt and model, first answers only: 270 answers (`data/rerun_cli_responses.jsonl`). The route injects the account email into every call, so run 2 is a replication under the same condition, not a clean run. All run-2 codes come from the blind AI coder (`scripts/second_coder.py`, same rubric); none has been adjudicated by a human.

Assumed country in the first answer, run 2 (blind AI coder, n=90 per framing):

| Framing | India | US | Generic |
|---|---|---|---|
| US English | 0 | 82 | 8 |
| Indian English | 30 | 25 | 35 |
| Hindi/Marathi/Hinglish | 84 | 1 | 5 |

**Leaks.** 21 answers mention Cornell, Ithaca or the account email (15 Opus, 4 Sonnet, 2 Haiku), for example "Your Cornell email suggests New York." All 21 assumed the US (18) or no country (3), none India, so the leak pulls answers away from India. Five more answers name New York without any other sign of leakage. With the 21 removed, Indian English is India 30, US 16, generic 34 (n=80); US English US 74, generic 8 (n=82); Hindi/Marathi/Hinglish India 84, generic 3 (n=87). Removing leaked answers also removes the ones the email pulled toward the US, so the clean India share (30 of 80) is probably biased upward; the all-answers figure (30 of 90) is biased downward by the same leak. The truth for a context-free run lies between them. The leak check looks for explicit mentions only, so a subtler influence of the email would not be caught.

**What decides Indian-English answers.** Across the nine answers per prompt (three models, three repeats):

| Indian-English prompt | Locale word | India | US | Generic |
|---|---|---|---|---|
| P3 flat savings | "12 lakh" | 9 | 0 | 0 |
| P9 engineering colleges | "12th" | 9 | 0 | 0 |
| P4 emergency savings | "FD" | 5 | 0 | 4 |
| P10 maths help | "class 5" | 4 | 0 | 5 |
| P5 bank SMS | "KYC" | 3 | 1 | 5 |
| P6 driving licence | none | 0 | 3 | 6 |
| P7 elder benefits | "scheme", "pension" | 0 | 3 | 6 |
| P1 child fever | "Kindly", °C | 0 | 0 | 9 |
| P2 diabetes test | none | 0 | 9 | 0 |
| P8 landlord deposit | none | 0 | 9 | 0 |

The pattern is by prompt, not by chance: prompts with a distinctive locale word went to India, and prompts written in Indian-English phrasing alone went to the US or stayed generic. This is the pilot's central pattern, now replicated, and it fits the hypothesis that these models treat explicit locale cues as a location signal but do not treat Indian-English phrasing the same way. Ten prompts cannot separate dialect from locale words; matched prompt pairs can.

**Models and stability.** Indian English assumed India in 13 of 30 Opus answers, 11 of 30 Sonnet and 6 of 30 Haiku. In 23 of 30 prompt-model cells all three repeats gave the same country (27 of 30 for US English and for Hindi/Marathi/Hinglish). Run 1 and run 2 agree on the assumed country in 76 of 90 Indian-English answers, 86 of 90 US-English and 87 of 90 Hindi/Marathi/Hinglish (same prompt and model, both coded by the AI coder). Run 1's Indian-English India count was 12 of 30 (40%) against 30 of 90 (33%) in run 2; with these sample sizes the difference is within what repeated sampling gives, and I did not test it.

## Limits

- One vendor, three models. Run 1 has one answer per cell; run 2 has three.
- Coders are not independent humans: the first pass was AI-assisted and the second coder is a Claude model.
- Run 1 went through a tool that attached account context. The clean re-run (`scripts/rerun_api.py`) sends only the prompt through the API.
- The prompts carry built-in locale markers, which is part of what is being tested but limits what the pilot can say about unmarked Indian English.
- Ten prompts cannot represent a domain; the Hindi/Marathi/Hinglish framing mixes three languages.

## Next steps

1. Run `scripts/rerun_api.py` with an API key for a run with no account context, and compare it with runs 1 and 2. This is the one change that removes the leak confound.
2. Separate language from locale words with matched prompt pairs, and add open-weight and other-vendor models.
3. Recruit human coders and readers in India for fit judgments.

## Files

`data/prompts.csv`, `data/responses_run1.csv`, `data/coded_run1.csv`, `data/rerun_cli_responses.jsonl`, `data/coded_run2.csv`, `coding/`, `scripts/analyze.py` and `scripts/analyze_run2.py` (every table above comes from these files), `scripts/rerun_api.py`, `scripts/rerun_cli.py`, `scripts/check_leaks.py`.
