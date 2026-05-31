# Offshore Equipment Escalation Agent
### IBM × MUN watsonx Hackathon — May 29–31, 2026

An AI-powered safety decision support agent for offshore oil and gas operations in Newfoundland and Labrador. Built on IBM watsonx Orchestrate and watsonx.ai, the agent analyzes equipment log entries and live telemetry to flag safety risks, assign severity levels, and recommend immediate actions.

---

## Team

**SFVS-Hackers**

| Name | Email | Role |
|---|---|---|
| Victor Muojeke | vcmuojeke@mun.ca | Backend, prompt engineering, infrastructure |
| Sadia Afrin | safrin21@mun.ca | Data, analysis, knowledge base |
| Fatema AL-asbahi | falasbahi@mun.ca | UI/UX, frontend |
| Samuel Collins | samuelec@mun.ca | UI development, integration |

**IBM Environment Access:** vcmuojeke@mun.ca · safrin21@mun.ca

---

## Problem

Offshore platforms in Newfoundland and Labrador — including Hibernia, Terra Nova, White Rose, and Hebron — operate in some of the harshest conditions in the world. Equipment failures in these environments can escalate from anomaly to catastrophe in minutes.

Key challenges:
- Operators process dozens of sensor feeds and handover logs simultaneously during shift changes
- Critical signals (pressure spikes, thermal anomalies, vibration thresholds) can be buried in routine text logs
- Manual triage of equipment state relies on operator experience and is prone to alert fatigue
- Delayed escalation of mechanical faults has been a contributing factor in major offshore incidents globally

---

## Solution

A natural language equipment monitoring agent that lets operators describe an anomaly in plain English — with or without inline telemetry — and receive an immediate, structured safety assessment:

- **SAFETY_FLAG** — escalate (1) or routine (0)
- **SEVERITY_LEVEL** — 1 (critical shutdown risk) through 5 (normal operations)
- **CATEGORY** — incident type (blowout risk, gas leak, hydraulic failure, etc.)
- **RECOMMENDED_ACTION** — one clear sentence for the operator
- **REASONING** — plain English explanation of the assessment

The agent is deployed on IBM watsonx Orchestrate and accessible as a chat interface. A local Streamlit dashboard provides a two-panel view: live telemetry diagnostics chat on the right, and an active incident tracker with analytics on the left.

---

## Architecture

```
Operator Input (natural language + inline metrics)
        │
        ▼
┌─────────────────────┐
│   Streamlit UI      │  app/chat_app.py
│   (Two-panel)       │  • Chat panel (right)
│                     │  • Incident tracker + analytics (left)
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Telemetry Extractor│  extract_telemetry()
│  (regex NLP)        │  • Pressure, Temp, Vibration, Flow, Voltage, RPM
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Input Parser       │  tools/input_parser.py
│                     │  • Sanitizes text, strips units, validates ranges
│                     │  • Raises ValueError for invalid inputs
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Escalation Tool    │  tools/escalation_tool.py
│                     │  • Formats prompt with log + telemetry
│                     │  • Calls watsonx.ai via IBM SDK
│                     │  • Parses structured response
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  IBM watsonx.ai     │  meta-llama/llama-3-3-70b-instruct
│                     │  • temperature=0.0 (deterministic)
│                     │  • Grounded by Offshore Equipment Safety Examples
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Structured Output  │  safety_flag · severity_level · category
│                     │  recommended_action · reasoning
└─────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  watsonx Orchestrate Agent              │
│  • NL chat interface                    │
│  • Grounded on offshore_equipment_1000  │
│  • Deployable via Teams, Slack, Web     │
└─────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | meta-llama/llama-3-3-70b-instruct via IBM watsonx.ai |
| Agent platform | IBM watsonx Orchestrate |
| UI | Streamlit + Plotly |
| Backend | Python 3.13 |
| Knowledge base | offshore_equipment_1000.csv (1000 synthetic log entries) |
| Fonts / theme | IBM Plex Sans, IBM Plex Mono — dark theme |

---

## Dataset

`data/offshore_equipment_1000.csv` — 1000 synthetic offshore equipment log entries

| Column | Description |
|---|---|
| `log_id` | Unique entry ID |
| `platform` | Terra Nova, White Rose, Hibernia, Hebron |
| `shift` | Day / Night |
| `component` | Equipment system involved |
| `category` | Incident type (8 categories) |
| `severity_level` | 1 (critical) – 5 (normal) |
| `safety_flag` | 1 = escalate, 0 = routine |
| `pressure_psi` | Pressure reading in PSI |
| `temp_c` | Temperature in °C |
| `vibration_mms` | Vibration in mm/s |
| `flow_rate_pct` | Flow rate percentage |
| `voltage_v` | Voltage (V) |
| `rpm` | Rotational speed |
| `log_entry` | Free-text log description |

**Categories:** blowout_risk · gas_leak · pressure_anomaly · overheating · electrical_fault · hydraulic_failure · structural_fatigue · routine_maintenance · normal_ops

**Distribution:** Balanced across severity levels and categories.

---

## Severity Scale

| Level | Label | Meaning |
|---|---|---|
| 1 | Critical | Immediate shutdown risk — threshold breached |
| 2 | Urgent | Approaching critical — intervention needed soon |
| 3 | Elevated | Abnormal but stable — increased monitoring required |
| 4 | Scheduled | Minor deviation — plan maintenance |
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
# Edit .env with your watsonx credentials

# Run the Streamlit app
streamlit run app/chat_app.py
```

The app will open at `http://localhost:8501`.

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
│   ├── app.py                        # Placeholder
│   └── chat_app.py                   # Main Streamlit UI (two-panel)
├── data/
│   └── offshore_equipment_1000.csv   # 1000-case synthetic dataset
├── demo/
│   ├── run_demo.py                   # CLI demo runner
│   └── sample_notes.py              # Sample log entries for testing
├── knowledge/
│   └── triage_examples.md            # Supplementary knowledge base
├── prompts/
│   └── triage_prompt.txt             # Prompt template (offshore domain)
├── tests/
│   ├── test_tool.py                  # Backend unit + integration tests
│   └── test_parser.py                # Input parser unit tests
├── tools/
│   ├── escalation_tool.py            # Core backend — calls watsonx.ai
│   └── input_parser.py               # Input sanitizer and validator
├── .env.example                      # Environment variable template
├── .gitignore
├── agent.yaml                        # watsonx Orchestrate ADK definition
├── CLAUDE.md                         # Developer context (Claude Code)
├── README.md
└── requirements.txt
```

---

## Running Tests

```bash
# Input parser unit tests (no API needed)
python tests/test_parser.py

# Backend tests (requires .env with valid credentials)
python tests/test_tool.py
```

---

## Accessing the Live Agent

The agent is deployed on IBM watsonx Orchestrate under the **SFVS-Hackers** workspace.

**Agent name:** Offshore Equipment Agent
**Access:** Log into watsonx Orchestrate → Agent chat → Offshore Equipment Agent

Try this example prompt:
```
Mud pump number two losing pressure since start of afternoon shift.
Now reading 200 PSI, well below operating range. Reservoir level low,
possible internal leak. Switched to pump one. Pressure 200 PSI,
Temp 58C, Vibration 6.2 mms, Flow 18%
```

---

## Hackathon Judging Criteria

| Category | Max | Notes |
|---|---|---|
| Problem & Relevance | 10 | Offshore safety in NL — real platforms, real risk |
| Innovation | 10 | NL triage via LLM grounded on 1000-case dataset |
| Technical Execution | 10 | Full pipeline: parser → watsonx.ai → structured output |
| Video & Communication | 10 | Live demo via Streamlit + Orchestrate |
| Impact & Value | 10 | Reduces alert fatigue, supports offshore operators |

---

*Built at the IBM × Memorial University watsonx Hackathon, May 29–31, 2026.*
*This is a decision support tool only. Final operational decisions rest with the platform supervisor.*
