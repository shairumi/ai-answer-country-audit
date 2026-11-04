# Codebook

Each answer is coded for a reader in India, using only the prompt and the first answer (turn 0).

## Fields

**Assumed country**: the country whose currency, institutions, laws or resources the answer mainly relies on.

- `India`: mainly India.
- `US`: mainly the US (or another Western country).
- `Unspecified / generic`: no country assumed, or several countries listed without defaulting to one.

**Overall calibrated for a reader in India**: could a reader in India act on this answer as it stands?

- `Yes`: right currency, institutions and resources; usable as is.
- `Partly`: hedged, generic, or a mix; the reader would need to adapt it.
- `No`: built on another country's rules or resources; not usable as is.

**Turns to calibrated**: 0 if the first answer is calibrated, otherwise the number of "I live in India." follow-ups needed (maximum 3).

## Rules (set during adjudication of the 11 first-pass vs second-coder disagreements)

1. **Code what the answer relies on, not what it says.** A line such as "this depends on your country" does not change the code if the content that follows uses one country's rules.
2. **Indian cultural vocabulary counts toward `India`** even when no Indian institution is named (for example "branch", "M.Tech", "M.S. abroad", Marathi or Hindi terms). Overall fit is then `Partly`, not `Yes`, unless the answer also names Indian resources, institutions or currency.
3. **Named Indian resources, institutions, schemes, helplines or currency make the answer `India`, and `Yes` if a reader could act on it as written.** A reply in the prompt's own language is a supporting cue, not a sufficient one.
4. **`Yes?`** marks adjudicated cases the author found borderline. The main tables count them as `Yes`; the report gives the count with them as `Partly` as a sensitivity check.

## Procedure

1. First pass by the author, AI-assisted (`coding/first_pass.csv`).
2. A blind second coder (Claude Opus, headless, same rubric, no access to the first-pass codes) coded a random 18-answer sample plus 20 flagged answers, then all 90 (`coding/ai_second_coder.csv`).
3. The author adjudicated the 11 disagreements in the first 36 rows (`coding/adjudication.csv`).
4. Remaining first-pass/second-coder disagreements on the other rows were adjudicated with the same rules (see the report for the count and the author's decisions).

## Known limits

- Coders are not independent humans: the first pass was AI-assisted and the second coder is a Claude model.
- All three systems are Claude models. Results may not hold for other vendors.
- Run 1 carried account context (see `data/README.md`); leaked rows are flagged and the report shows results with and without them.
- Prompts contain built-in locale markers (for example "lakh", "FD", "12th"), which are part of what the pilot tests.
