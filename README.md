# Offshore Equipment Escalation Agent
### IBM × MUN watsonx Hackathon, May 29 to 31, 2026

An AI-powered safety decision support agent for offshore oil and gas operations in Newfoundland and Labrador. Built on IBM watsonx Orchestrate and watsonx.ai, the agent analyzes free-text equipment log entries and live telemetry data to flag safety risks, assign severity levels, and recommend immediate actions, in under 11 seconds.

**This app needs an IBM watsonx API key.** Set it in a `.env` file before running, see [Environment Variables](#environment-variables) below.

---

## Team

**SFVS-Hackers**, led by Victor Muojeke, team of four.

| Name | Email | Role |
|---|---|---|
| Victor Muojeke | vcmuojeke@mun.ca | Backend, prompt engineering, infrastructure |
| Sadia Afrin | safrin21@mun.ca | Data, analysis, knowledge base |
| Fatema AL-asbahi | falasbahi@mun.ca | UI/UX, frontend |
| Samuel Collins | samuelec@mun.ca | UI development, integration |

**IBM Environment Access:** vcmuojeke@mun.ca · safrin21@mun.ca

---

## Problem

Offshore platforms in Newfoundland and Labrador, including Hibernia, Terra Nova, White Rose, and Hebron, operate in some of the harshest conditions in the world. Equipment failures in these environments can escalate from anomaly to catastrophe in minutes.

Key challenges:
- Operators process dozens of sensor feeds and handover logs simultaneously during shift changes
- Critical signals (pressure spikes, thermal anomalies, vibration thresholds) can be buried in routine text logs
- Manual review of equipment logs relies on operator experience and is prone to alert fatigue
- Missed or late escalations can lead to costly shutdowns and safety incidents

---

## Solution

A natural language equipment monitoring agent that lets operators describe an anomaly in plain English, with or without inline telemetry, and receive an immediate, structured safety assessment:

- **SAFETY_FLAG**: escalate (1) or routine (0)
- **SEVERITY_LEVEL**: 1 (critical shutdown risk) through 5 (normal operations)
- **CATEGORY**: incident type (blowout risk, gas leak, hydraulic failure, etc.)
- **RECOMMENDED_ACTION**: one clear sentence for the operator
- **REASONING**: plain English explanation of the assessment

During the hackathon, the agent was deployed on IBM watsonx Orchestrate as a chat interface. A local Streamlit dashboard provides a two-panel view: live telemetry diagnostics chat on the right, and an active incident tracker with analytics on the left.

---

## Proven Results

Evaluated against 30 live cases from the offshore equipment dataset using the live watsonx.ai model:

| Metric | Result |
|---|---|
| Overall safety flag accuracy | **90.0%** |
| Severity level accuracy | 56.7%, model tends to over-escalate (conservative) |
| False positive rate | **0.0%**, never unnecessarily alarms on routine logs |
| False negative rate | 10.0%, 3 missed escalations (gas_leak, electrical_fault edge cases) |
| Average response time | **10.23 seconds** per log entry |
| Fastest response | 3.42 seconds |
| Categories at 100% accuracy | 8 out of 10 |

---

## Architecture

```
Operator Input (natural language + inline metrics)
        │
        ▼
┌─────────────────────┐
│   Streamlit UI      │  app/chat_app.py
│   (Two-panel)       │  • Chat panel, Asset Telemetry Diagnostics
│                     │  • Active Incident Tracker + Analytics
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Telemetry Extractor│  extract_telemetry()
│  (NLP regex)        │  • Pressure, Temperature, Vibration, Flow
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Input Parser       │  tools/input_parser.py
│                     │  • Sanitizes text, strips units, validates ranges
│                     │  • Raises descriptive errors for invalid inputs
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Escalation Tool    │  tools/escalation_tool.py
│                     │  • Formats prompt with log + telemetry
│                     │  • Calls watsonx.ai via IBM Python SDK
│                     │  • Parses structured response fields
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  IBM watsonx.ai     │  meta-llama/llama-3-3-70b-instruct
│                     │  • temperature=0.0 (deterministic output)
│                     │  • Grounded by 1000-case offshore knowledge base
└────────┬────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  IBM watsonx Orchestrate Agent          │
│  • ReAct reasoning (high-stakes mode)  │
│  • Knowledge: offshore_equipment_1000   │
│  • 3 safety guidelines configured      │
│  • Deployable via Teams, Slack, Web    │
└─────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | meta-llama/llama-3-3-70b-instruct via IBM watsonx.ai |
| Agent platform | IBM watsonx Orchestrate (ReAct mode) |
| Agent reasoning | ReAct: think, act, observe, refine |
| UI | Streamlit + Plotly |
| Backend | Python 3.13 |
| Knowledge base | offshore_equipment_1000.csv (1000 synthetic log entries) |
| Fonts / theme | IBM Plex Sans, IBM Plex Mono, dark theme |

---

## Dataset

`data/offshore_equipment_1000.csv`, 1000 synthetic offshore equipment log entries

| Column | Description |
|---|---|
| `log_id` | Unique entry ID |
| `platform` | Terra Nova, White Rose, Hibernia, Hebron |
| `shift` | Day / Night |
| `component` | Equipment system involved |
| `category` | Incident type (10 categories) |
| `severity_level` | 1 (critical) to 5 (normal) |
| `safety_flag` | 1 = escalate, 0 = routine |
| `pressure_psi` | Pressure reading in PSI |
| `temp_c` | Temperature in °C |
| `vibration_mms` | Vibration in mm/s |
| `flow_rate_pct` | Flow rate percentage |
| `voltage_v` | Voltage (V) |
| `rpm` | Rotational speed |
| `log_entry` | Free-text log description |

**Categories:** blowout_risk · gas_leak · pressure_anomaly · overheating · electrical_fault · hydraulic_failure · structural_fatigue · corrosion · routine_maintenance · normal_ops

---

## Severity Scale

| Level | Label | Meaning |
|---|---|---|
| 1 | Critical | Immediate shutdown risk, threshold breached |
| 2 | Urgent | Approaching critical, intervention needed soon |
| 3 | Elevated | Abnormal but stable, increased monitoring required |
| 4 | Scheduled | Minor deviation, plan maintenance |
| 5 | Normal | All parameters within operational range |

---

## Local Setup

**Requirements:** Python 3.11+, pip

```bash
git clone <repo-url>
cd sfvs-hackers

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and fill in your IBM watsonx credentials

# Run the Streamlit app
streamlit run app/chat_app.py
```

The app will open at `http://localhost:8501`

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your IBM watsonx credentials:

```
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_ENDPOINT_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=meta-llama/llama-3-3-70b-instruct
```

Credentials are available from your IBM Cloud account under **watsonx.ai → Manage → API key**.

---

## File Structure

```
sfvs-hackers/
├── app/
│   └── chat_app.py                   # Main Streamlit UI (two-panel dark dashboard)
├── analysis/
│   ├── impact_analysis.py            # Accuracy evaluation script (30 live cases)
│   ├── results.json                  # Full results from live model evaluation
│   └── summary.txt                   # Summary of evaluation results
├── data/
│   └── offshore_equipment_1000.csv   # 1000-case synthetic offshore dataset
├── demo/
│   ├── run_demo.py                   # CLI demo runner
│   └── sample_notes.py              # Sample log entries for testing
├── prompts/
│   └── triage_prompt.txt             # Prompt template (offshore domain)
├── tests/
│   ├── test_tool.py                  # Backend unit + integration tests
│   └── test_parser.py                # Input parser unit tests (25 cases)
├── tools/
│   ├── escalation_tool.py            # Core backend, calls watsonx.ai
│   └── input_parser.py               # Input sanitizer and validator
├── .env.example                      # Environment variable template
├── .gitignore
├── agent.yaml                        # watsonx Orchestrate ADK definition
└── requirements.txt
```

---

## Running Tests

```bash
# Input parser unit tests (no API needed)
python tests/test_parser.py

# Backend integration tests (requires .env with valid credentials)
python tests/test_tool.py

# Run accuracy evaluation against live model (30 cases, ~5 minutes)
python analysis/impact_analysis.py
```

---

## watsonx Orchestrate Agent (hackathon)

The agent was deployed on IBM watsonx Orchestrate under the **SFVS-Hackers** workspace during the hackathon.

**Agent name:** Offshore Equipment Agent
**Mode:** ReAct (high-stakes reasoning)

**Critical event prompt (example):**
```
High-pressure cementing unit, gas detection triggered. Pressure 172 PSI,
Temp 65C, Vibration 8.4 mms, Flow 49%
```

**Routine event prompt (example):**
```
Completed 500-hour service on drill string compensator. Checked fluid levels,
swapped filters, torqued fittings. Three loose nuts found and sorted.
No leaks, no unusual wear. Pressure 160 PSI, Temp 52C, Vibration 2.1 mms, Flow 88%
```

---

## Technical Notes

**Level 4 Scheduled business rule:** The LLM does not natively return Level 4 for routine maintenance. It classifies fully resolved service tasks as Level 5 (Normal). A post-processing rule in `tools/escalation_tool.py` enforces the constraint that any log classified as `routine_maintenance` receives a minimum severity of 4. This is a valid safety engineering rule: if maintenance was performed, it must be logged at Scheduled level minimum. Level 5 is reserved for pure passive monitoring with zero intervention.

**Severity accuracy vs flag accuracy:** The agent achieves 90% accuracy on the binary escalation flag (escalate vs routine). Severity level accuracy (56.7%) is lower because the model is conservative. It tends to assign Level 1 or 2 where Level 3 might be more precise. For a safety-critical tool, over-escalation is the preferred failure mode.

---

## Responsible AI

This agent is designed as a **decision support tool only**. It does not replace human judgment in safety-critical operations.

- All responses end with: *"Final operational decisions rest with the platform supervisor."*
- The agent is configured with three safety guidelines enforcing escalation behaviour and decision boundaries
- Temperature is set to 0.0, deterministic, reproducible output for auditability
- No personal information is stored or processed

---

*Built at the IBM × Memorial University watsonx Hackathon, May 29 to 31, 2026.*
*This is a decision support tool only. Final operational decisions rest with the platform supervisor.*
