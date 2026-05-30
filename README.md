# NL Triage Escalation Agent — IBM watsonx Hackathon 2026

Agentic triage support system built on watsonx Orchestrate + watsonx.ai (Granite).
Analyzes free-text nursing notes and vitals to flag deterioration risk and recommend escalation.

## Project structure

```
triage_agent/
├── README.md
├── .env.example           # Copy to .env and fill in your credentials
├── requirements.txt
├── agent.yaml             # watsonx Orchestrate ADK agent definition
├── tools/
│   └── escalation_tool.py # The core tool — calls watsonx.ai Granite
├── prompts/
│   └── triage_prompt.txt  # Prompt template (also paste this into Prompt Lab)
├── demo/
│   ├── sample_notes.py    # Synthetic triage notes for demo
│   └── run_demo.py        # Run all demo cases end-to-end
└── tests/
    └── test_tool.py       # Quick sanity checks before connecting to Orchestrate
```

## Setup

```bash
git clone <your-repo>
cd triage_agent
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # Then fill in WATSONX_API_KEY, PROJECT_ID, ENDPOINT_URL
```

## Run the demo

```bash
python demo/run_demo.py
```

## Deploy to Orchestrate (ADK)

```bash
pip install ibm-watsonx-orchestrate
wxo login
wxo agents deploy --file agent.yaml
```
# sfvs-hackers
