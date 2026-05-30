# NL Triage Escalation Agent — Claude Code Brief
## IBM × MUN watsonx Hackathon | May 29–31, 2026

---

## What has been built so far

### Working components
- `tools/escalation_tool.py` — calls watsonx.ai (llama-3-3-70b-instruct) via IBM SDK
- `prompts/triage_prompt.txt` — engineered prompt returning structured ESCALATION_FLAG, ACUITY_ESTIMATE, RISK_SIGNALS, RECOMMENDED_ACTION, REASONING
- `demo/sample_notes.py` — 7 real cases from the 1000-case synthetic dataset
- `demo/run_demo.py` — CLI demo runner with colour output, 7/7 passing
- `data/triage_synthetic_1000.csv` — 1000 synthetic triage cases, 10 categories, balanced 50/50
- `knowledge/triage_examples.md` — knowledge base uploaded to watsonx Orchestrate
- `agent.yaml` — ADK agent definition
- `tests/test_tool.py` — parser unit tests + live API test
- Deployed agent on watsonx Orchestrate with knowledge base attached

### Current scores against judging rubric (estimated)
| Category | Max | Current estimate | Gap |
|---|---|---|---|
| 1. Problem & Relevance | 10 | 7 | NL context stated but not evidenced with data |
| 2. Innovation | 10 | 7 | Works well but no quantified novelty |
| 3. Technical Execution | 10 | 8 | Solid but deprecation warnings, no input validation |
| 4. Video & Communication | 10 | 0 | NOT STARTED — no video, no slides |
| 5. Impact & Value | 10 | 6 | No quantified impact numbers |
| **Total** | **50** | **28** | **Need ~40+ to be competitive** |

---

## Team split

- **Teammate** — building the web UI (Flask/HTML frontend). Do NOT touch `demo/app.py` or any UI files.
- **This Claude Code session** — backend data quality, input parsing, impact analysis, and documentation.

---

## What Claude Code needs to build

### PRIORITY 1 — Input parser and data cleaner
Create `tools/input_parser.py` that sanitizes and validates all inputs before they reach
`analyze_triage_note()`. This is critical — the web UI teammate will call this parser before
passing data to the escalation tool.

The parser must handle:

**Triage note (text):**
- Strip leading/trailing whitespace
- Collapse multiple spaces and newlines into single space
- Remove any special characters that could break the prompt (e.g. curly braces `{}` which
  would corrupt the prompt template substitution)
- Enforce minimum length of 10 characters — raise `ValueError` with clear message if too short
- Enforce maximum length of 1000 characters — truncate with a warning if exceeded
- Detect and reject empty or whitespace-only input

**Vitals (numeric fields: hr, sbp, dbp, rr, o2, temp):**
- Accept strings OR numbers — cast strings to float/int safely
- Strip any units if accidentally included (e.g. "96%" → 96, "36.8C" → 36.8, "120bpm" → 120)
- Validate physiologically plausible ranges and raise `ValueError` with specific message if
  outside range:
  - HR: 20–300 bpm
  - SBP: 50–300 mmHg
  - DBP: 20–200 mmHg
  - RR: 4–80 breaths/min
  - O2: 50–100 %
  - Temp: 25.0–45.0 °C
- GCS: optional string, if provided strip whitespace, default to "Not recorded" if empty

**Return value:**
Return a `ParsedInput` dataclass with all cleaned fields plus a `warnings` list of non-fatal
issues (e.g. "O2 value 99.5 rounded to 99.5 — within range").

**Raise** `ValueError` with a human-readable message for any fatal validation failure so the
UI can display it directly to the nurse.

Example usage (what the UI teammate will call):
```python
from tools.input_parser import parse_triage_input
from tools.escalation_tool import analyze_triage_note

parsed = parse_triage_input(
    note="  72F, sudden facial drooping...  ",
    hr="105bpm", sbp="160", dbp=108, rr=22, o2="96%", temp="36.5C"
)
result = analyze_triage_note(**parsed.to_dict())
```

### PRIORITY 2 — Fix deprecation warning
In `tools/escalation_tool.py`, suppress the WatsonxAPIWarning cleanly so it does not
appear in the web UI output or terminal during demo.

Add at the top of `escalation_tool.py` after existing imports:
```python
import warnings
from ibm_watsonx_ai.wml_client_error import WatsonxAPIWarning
warnings.filterwarnings("ignore", category=WatsonxAPIWarning)
```

### PRIORITY 3 — Impact numbers script
Create `analysis/impact_analysis.py` that runs a sample of the 1000-case dataset through
the model and produces accuracy metrics for the pitch.

- Load `data/triage_synthetic_1000.csv`
- Run the first 50 cases through `analyze_triage_note()` (not all 1000 — API cost)
- Compare returned `escalation_flag` against the CSV `escalation_flag` column (0=NO, 1=YES)
- Calculate and print:
  - Overall accuracy %
  - False negative rate % (missed escalations — the dangerous ones)
  - False positive rate % (over-triaged routine cases)
  - Accuracy by category
  - Average response time per case (seconds)
- Save full results to `analysis/results.json`
- Save a summary to `analysis/summary.txt` (plain text, for pasting into slides)

Run with: `python analysis/impact_analysis.py`

### PRIORITY 4 — Update escalation_tool.py to use the parser
Modify `tools/escalation_tool.py` so `analyze_triage_note()` calls `parse_triage_input()`
internally at the top of the function before building the prompt. This means the UI teammate
does NOT need to remember to call the parser separately — it is automatic.

If the parser raises `ValueError`, let it propagate up so the UI can catch and display it.

### PRIORITY 5 — NL context data file
Create `data/nl_context.md` with these facts to reference in the pitch:
- Eastern Health operates 4 acute care sites in NL
- NL has the highest rate of cardiovascular disease mortality in Canada (Stats Canada)
- Average ambulance response time in rural NL exceeds 30 minutes
- CTAS was developed in Canada and is used in all NL emergency departments
- The Triage Nurse role in NL EDs often operates without immediate physician support
  during surge periods

### PRIORITY 6 — README overhaul
Rewrite `README.md` to tell the story for judges:
- Problem: NL has emergency departments serving a population spread across 405,000 km²
- Rural nurses often triage without immediate physician backup
- Solution: AI-powered triage support agent on IBM watsonx
- Architecture: Input → Parser → watsonx.ai (llama-3-3-70b) → Structured output
- How to run locally
- How to access the live Orchestrate agent
- Dataset description (1000 cases, 10 categories, 50/50 balanced)
- Results summary (fill in after Priority 3 is done)

---

## File structure after all improvements

```
ibmhackers/
├── data/
│   ├── triage_synthetic_1000.csv
│   └── nl_context.md              ← NEW (Priority 5)
├── analysis/
│   ├── impact_analysis.py         ← NEW (Priority 3)
│   ├── results.json               ← NEW (generated)
│   └── summary.txt                ← NEW (generated)
├── demo/
│   ├── app.py                     ← TEAMMATE — do not touch
│   ├── run_demo.py
│   └── sample_notes.py
├── knowledge/
│   └── triage_examples.md
├── prompts/
│   └── triage_prompt.txt
├── tests/
│   ├── test_tool.py
│   └── test_parser.py             ← NEW (write tests for input_parser)
├── tools/
│   ├── escalation_tool.py         ← MODIFY (Priority 2 + Priority 4)
│   └── input_parser.py            ← NEW (Priority 1)
├── .env.example
├── .gitignore
├── agent.yaml
├── CLAUDE.md
├── README.md                      ← REWRITE (Priority 6)
└── requirements.txt               ← no changes needed
```

---

## Interface contract with the UI teammate

The UI teammate's `app.py` should call the tool like this:

```python
from tools.input_parser import parse_triage_input, ParsedInput
from tools.escalation_tool import analyze_triage_note

try:
    parsed = parse_triage_input(
        note=request.form["note"],
        hr=request.form["hr"],
        sbp=request.form["sbp"],
        dbp=request.form["dbp"],
        rr=request.form["rr"],
        o2=request.form["o2"],
        temp=request.form["temp"],
        gcs=request.form.get("gcs", "")
    )
    result = analyze_triage_note(**parsed.to_dict())
except ValueError as e:
    # display e to the nurse as a validation error
    result = {"error": str(e)}
```

The `analyze_triage_note()` function signature does NOT change — the parser just cleans
inputs before they arrive. Backward compatible.

---

## Environment
- Python 3.13, Anaconda base environment
- Mac (Apple Silicon)
- IBM watsonx.ai credentials in `.env`
- Model: `meta-llama/llama-3-3-70b-instruct`
- Endpoint: `https://us-south.ml.cloud.ibm.com`
- All 7 current demo cases passing

## Key constraint
Do not commit `.env` — it is gitignored. `.env.example` is the template.
Do not touch `demo/app.py` — that is the UI teammate's file.

## Judging deadline
May 31, 2026. Presentation includes a video demo.
Work through priorities in order. Start with Priority 1 (input parser) and do not move
to the next priority until the current one has passing tests.
