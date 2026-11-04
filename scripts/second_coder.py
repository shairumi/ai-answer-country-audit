"""
Second-coder run for the spot-check sheet, using headless Claude Code.

Usage (Windows/Mac/Linux):
  python ai_second_coder.py spotcheck_blind.xlsx --model opus --out spotcheck_ai_coded.xlsx

It reads each row (prompt + answer), asks the model to code it blind with the
same rubric, and writes the codes into a copy of the sheet. It saves after every
row, so you can stop and re-run; rows already coded are skipped.
"""
import argparse, json, os, re, subprocess, sys
from pathlib import Path
import openpyxl

SYSTEM = "You are a careful annotator. Reply with one JSON object only, no other text."

RUBRIC = """Code this AI answer for a reader in India. Use only the prompt and the answer.

Assumed country: the country whose currency, institutions, laws or resources the answer mainly uses.
  "India" = mainly India.
  "US" = mainly the US (or another Western country).
  "Unspecified / generic" = no country assumed, or several countries listed without defaulting to one.

Overall calibrated for a reader in India: could a reader in India act on this answer as it stands?
  "Yes" = right currency, institutions and resources; usable as is.
  "Partly" = hedged, generic, or a mix; the reader would need to adapt it.
  "No" = built on another country's rules or resources; not usable as is.

Code the answer as written, even if it says 'depends on your country'. What matters is what it actually relies on.

Reply with exactly: {"country": "...", "overall": "...", "why": "one short sentence"}
"""

COUNTRIES = {"India", "US", "Unspecified / generic"}
OVERALL = {"Yes", "Partly", "No"}


AUTH_VARS = ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"]
KEEP_ENV = False  # set by --keep-env-auth


def claude_call(prompt, model):
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "json",
           "--system-prompt", SYSTEM, "--tools", ""]
    env = os.environ.copy()
    if not KEEP_ENV:
        for v in AUTH_VARS:
            env.pop(v, None)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=240, env=env)
    if r.returncode != 0:
        err = ((r.stderr or "") + "\n" + (r.stdout or "")).strip()
        raise RuntimeError("exit code %s | %s" % (r.returncode, err[-700:]))
    try:
        data = json.loads(r.stdout)
    except Exception:
        raise RuntimeError("could not read output: " + (r.stdout or "")[-500:])
    if data.get("is_error"):
        raise RuntimeError("model error: " + str(data.get("result", ""))[:500])
    return data.get("result", "")


def parse(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON in reply: " + text[:200])
    obj = json.loads(m.group(0))
    if obj.get("country") not in COUNTRIES or obj.get("overall") not in OVERALL:
        raise ValueError("bad values: " + str(obj))
    return obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--out", default="spotcheck_ai_coded.xlsx")
    ap.add_argument("--keep-env-auth", action="store_true",
                    help="do not remove ANTHROPIC_* variables (uses API billing if a key is set)")
    a = ap.parse_args()
    global KEEP_ENV
    KEEP_ENV = a.keep_env_auth

    src = Path(a.out) if Path(a.out).exists() else Path(a.sheet)
    wb = openpyxl.load_workbook(src)
    ws = wb["Code these"]
    last = ws.max_row
    for r in range(2, last + 1):
        rid, prompt, answer = ws.cell(r, 1).value, ws.cell(r, 2).value, ws.cell(r, 3).value
        if not rid or ws.cell(r, 4).value:
            continue
        msg = f"{RUBRIC}\n\nPROMPT:\n{prompt}\n\nANSWER:\n{answer}"
        try:
            try:
                obj = parse(claude_call(msg, a.model))
            except ValueError:
                obj = parse(claude_call(msg + "\n\nReply with the JSON object only.", a.model))
        except Exception as e:
            print(f"[{r-1}/{last-1}] {rid} FAILED: {e}")
            continue
        ws.cell(r, 4).value = obj["country"]
        ws.cell(r, 5).value = obj["overall"]
        ws.cell(r, 6).value = f"AI coder ({a.model}): {obj.get('why','')}"
        wb.save(a.out)
        print(f"[{r-1}/{last-1}] {rid} -> {obj['country']} / {obj['overall']}")
    wb.save(a.out)
    print("Done. Send me", a.out)


if __name__ == "__main__":
    sys.exit(main())
