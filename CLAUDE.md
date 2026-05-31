# Offshore Equipment Escalation Agent — Developer Brief
## IBM × MUN watsonx Hackathon | May 29–31, 2026

---

## Project pivot (as of May 30, 2026)

The project domain has changed from **NL medical triage** to **offshore equipment safety monitoring**.
The agent now analyzes equipment log entries and telemetry data (pressure, temperature, vibration,
flow rate) and flags safety escalations for offshore operations personnel.

The UI and tests have been updated. The backend tools (`escalation_tool.py`, `input_parser.py`,
and `prompts/triage_prompt.txt`) still use the old medical schema and **must be aligned** before
the app will work end-to-end.

---

## What has been built

### Working components
- `tools/escalation_tool.py` — calls watsonx.ai (llama-3-3-70b-instruct) via IBM SDK. Still uses
  old medical signature `(note, hr, sbp, dbp, rr, o2, temp, gcs)` — needs update (see gap below)
- `tools/input_parser.py` — validates and sanitizes inputs. Still uses old medical fields — needs update
- `prompts/triage_prompt.txt` — still uses medical triage prompt — needs rewrite for offshore domain
- `app/chat_app.py` — **UPDATED** two-panel Streamlit UI (IBM dark theme, IBM Plex fonts):
  - Left panel: Active Incident Tracker with stat cards (logs analyzed, safety flags, severity counts)
  - Right panel: Asset Telemetry Diagnostics chat, accepts free-text log entries with inline metrics
  - Extracts telemetry inline: pressure (PSI), temp (°C), vibration (mm/s), flow (%), voltage (V), RPM
  - Submissions sorted by priority: safety flag → severity level → timestamp
- `tests/test_parser.py` — **UPDATED** for offshore schema: `pressure`, `temperature`, `vibration`, `flow`
- `tests/test_tool.py` — still uses old medical test cases — needs update
- `demo/sample_notes.py` — still contains medical triage demo cases — needs update
- `data/triage_synthetic_1000.csv` — still the medical dataset — superseded by offshore domain
- `knowledge/triage_examples.md` — still medical knowledge base — needs update
- `agent.yaml` — ADK agent definition (update domain description)
- Deprecation warning fix: `WatsonxAPIWarning` suppressed with graceful fallback for older SDK versions
- `python-dotenv` import made optional — falls back silently if not installed

### Current scores against judging rubric (estimated)
| Category | Max | Current estimate | Gap |
|---|---|---|---|
| 1. Problem & Relevance | 10 | 7 | Domain context not yet evidenced with data |
| 2. Innovation | 10 | 7 | Works well but no quantified novelty |
| 3. Technical Execution | 10 | 6 | UI updated, but backend/UI schema mismatch blocks live calls |
| 4. Video & Communication | 10 | 0 | NOT STARTED — no video, no slides |
| 5. Impact & Value | 10 | 6 | No quantified impact numbers |
| **Total** | **50** | **26** | **Need ~40+ to be competitive** |

---

## Team split

- **Teammate (Samuel)** — owns `app/chat_app.py` UI. Running on Fedora / Python 3.14.
  Install fix: `sudo dnf install gcc-c++ python3-devel -y && pip install -r requirements.txt`
  OR: `python3 -m pip install ibm-watsonx-ai python-dotenv`
- **Backend developer** — backend alignment, prompt engineering, impact analysis, documentation.

**Do NOT touch** `demo/app.py` if it exists — that is the teammate's file.

---

## CRITICAL GAP — Backend / UI schema mismatch

The chat UI calls the backend with the **new offshore schema**:
```python
result = analyze_triage_note(
    note=user_text,
    pressure=telemetry["pressure_psi"],     # ← new
    temperature=telemetry["temp_c"],        # ← new
    vibration=telemetry["vibration_mms"],   # ← new
    flow=telemetry["flow_rate_pct"]         # ← new
)
```

But `escalation_tool.py` still has the **old medical signature**:
```python
def analyze_triage_note(note, hr, sbp, dbp, rr, o2, temp, gcs="Not recorded"):
```

This will throw `TypeError: got an unexpected keyword argument 'pressure'` on every live call.

Similarly, `tests/test_parser.py` now calls `parse_triage_input(note, pressure, temperature, vibration, flow)`
but `input_parser.py` still expects `(note, hr, sbp, dbp, rr, o2, temp, gcs)`.

---

## What still needs to be built

### PRIORITY 1 — Align `tools/input_parser.py` with offshore schema
Replace the medical `ParsedInput` dataclass and `parse_triage_input()` with offshore telemetry fields:

**Telemetry fields (`parse_triage_input` signature):**
- `note` (str) — free-text log entry, same cleaning rules as before (min 10, max 1000, no `{}`)
- `pressure` (int) — PSI, range 0–10000
- `temperature` (float) — °C, range -50.0–500.0
- `vibration` (float) — mm/s, range 0.0–100.0
- `flow` (int) — percentage, range 0–100

Strip units from strings: `"172psi"→172`, `"65.0C"→65.0`, `"8.4mms"→8.4`, `"49%"→49`

`ParsedInput.to_dict()` must return `{"note", "pressure", "temperature", "vibration", "flow"}`
to match the new `analyze_triage_note()` signature.

The tests in `tests/test_parser.py` already reflect the new schema — use them to verify.

### PRIORITY 2 — Rewrite `prompts/triage_prompt.txt` for offshore domain
Replace the medical triage prompt with an offshore equipment safety prompt. Template variables:
`{note}`, `{pressure}`, `{temperature}`, `{vibration}`, `{flow}`

Expected output format (what `_parse_response` must parse):
```
SAFETY_FLAG: 1 or 0
SEVERITY_LEVEL: 1, 2, 3, 4, or 5
CATEGORY: one of: pressure_anomaly | thermal_event | vibration_fault | flow_disruption | electrical_fault | routine_maintenance
RECOMMENDED_ACTION: one sentence
REASONING: one to two sentences
```

Severity reference:
- Level 1: Immediate shutdown risk — critical threshold breach
- Level 2: Urgent intervention — approaching critical limits
- Level 3: Elevated monitoring — abnormal but stable
- Level 4: Scheduled maintenance — minor deviation
- Level 5: Normal operations — all parameters within range

### PRIORITY 3 — Align `tools/escalation_tool.py` with offshore schema
Update `analyze_triage_note()` signature:
```python
def analyze_triage_note(note: str, pressure: int, temperature: float,
                         vibration: float, flow: int) -> dict:
```
Update `_parse_response()` to extract: `safety_flag`, `severity_level`, `category`,
`recommended_action`, `reasoning` (matching the new prompt output format).

Normalize `safety_flag` to `"1"` or `"0"` (the UI checks `str(flag) == "1"`).

Update `_PROMPT_TEMPLATE.format(...)` call to use the new variable names.

### PRIORITY 4 — Update demo cases in `demo/sample_notes.py`
Replace the 7 medical cases with 7 offshore equipment cases covering:
- High pressure event (safety flag 1)
- Thermal anomaly (safety flag 1)
- Vibration fault (safety flag 1)
- Flow disruption (safety flag 1)
- Normal operations (safety flag 0)
- Routine maintenance (safety flag 0)
- Electrical deviation (safety flag 0 or 1)

Each case: `label`, `expected_flag`, `note`, `pressure`, `temperature`, `vibration`, `flow`

### PRIORITY 5 — Update `tests/test_tool.py`
Replace medical test cases with offshore cases to match the new `_parse_response` output keys.

### PRIORITY 6 — Impact analysis script
Create `analysis/impact_analysis.py` — run sample cases through the model, compare
`safety_flag` predictions, compute accuracy, false negative rate, average response time.
Save to `analysis/results.json` and `analysis/summary.txt`.

---

## Current interface contract (what the UI expects)

```python
# chat_app.py calls:
telemetry = extract_telemetry(user_text)   # extracts pressure, temp_c, vibration_mms, flow_rate_pct
result = analyze_triage_note(
    note=user_text,
    pressure=telemetry["pressure_psi"],
    temperature=telemetry["temp_c"],
    vibration=telemetry["vibration_mms"],
    flow=telemetry["flow_rate_pct"]
)

# format_reply() reads from result:
result.get("safety_flag")          # "1" or "0"
result.get("severity_level")       # "1"–"5"
result.get("category")             # e.g. "pressure_anomaly"
result.get("recommended_action")   # one sentence
result.get("log_entry")            # reasoning / log summary
```

---

## File structure (current)

```
ibmhackers/
├── app/
│   ├── app.py                     ← placeholder (teammate's original)
│   └── chat_app.py                ← UPDATED — two-panel offshore UI
├── data/
│   └── triage_synthetic_1000.csv  ← old medical dataset (superseded)
├── demo/
│   ├── run_demo.py
│   └── sample_notes.py            ← NEEDS UPDATE (still medical cases)
├── knowledge/
│   └── triage_examples.md         ← NEEDS UPDATE (still medical)
├── prompts/
│   └── triage_prompt.txt          ← NEEDS REWRITE (Priority 2)
├── tests/
│   ├── test_tool.py               ← NEEDS UPDATE (Priority 5)
│   └── test_parser.py             ← UPDATED — offshore schema, use to verify Priority 1
├── tools/
│   ├── escalation_tool.py         ← NEEDS UPDATE (Priority 3)
│   └── input_parser.py            ← NEEDS UPDATE (Priority 1)
├── .env.example
├── .gitignore
├── agent.yaml
├── CLAUDE.md
├── README.md
└── requirements.txt
```

---

## Environment

- **Your machine**: Python 3.13, Anaconda, Mac (Apple Silicon)
- **Teammate (Samuel)**: Python 3.14, Fedora Linux — install deps with gcc-c++ first
- IBM watsonx.ai credentials in `.env` (gitignored)
- Model: `meta-llama/llama-3-3-70b-instruct`
- Endpoint: `https://us-south.ml.cloud.ibm.com`
- Run app: `streamlit run app/chat_app.py` from project root

## Key constraints
- Do not commit `.env`
- Do not touch `demo/app.py`
- Work through priorities in order — do not move to the next until tests pass
- Judging deadline: **May 31, 2026**. Presentation includes a video demo.
