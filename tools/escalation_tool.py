"""
escalation_tool.py

Core tool for the triage escalation agent.
Calls watsonx.ai Granite with the engineered prompt and returns
a structured escalation analysis.

This file is both:
  1. A standalone callable function you can test directly
  2. The tool implementation registered with watsonx Orchestrate ADK
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

load_dotenv()

# ── Credentials (loaded from .env) ──────────────────────────────────────────
_ENDPOINT_URL = os.getenv("WATSONX_ENDPOINT_URL", "https://us-south.ml.cloud.ibm.com")
_API_KEY      = os.getenv("WATSONX_API_KEY")
_PROJECT_ID   = os.getenv("WATSONX_PROJECT_ID")
_MODEL_ID     = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")

# ── Load prompt template once at import time ─────────────────────────────────
_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "triage_prompt.txt"
_PROMPT_TEMPLATE = _PROMPT_PATH.read_text()


def _get_model() -> ModelInference:
    """Initialise and return the watsonx.ai model client."""
    credentials = Credentials(url=_ENDPOINT_URL, api_key=_API_KEY)
    client = APIClient(credentials=credentials, project_id=_PROJECT_ID)
    return ModelInference(
        model_id=_MODEL_ID,
        api_client=client,
        params={
            "max_new_tokens": 400,
            "temperature": 0.0,       # deterministic — critical for clinical tools
            "repetition_penalty": 1.1,
        },
    )


def _parse_response(raw: str) -> dict:
    """
    Parse the structured Granite output into a Python dict.
    Robust to minor whitespace or capitalisation variation.
    """
    fields = {
        "escalation_flag": None,
        "acuity_estimate": None,
        "risk_signals": None,
        "recommended_action": None,
        "reasoning": None,
        "raw_response": raw.strip(),
    }

    patterns = {
        "escalation_flag":   r"ESCALATION_FLAG:\s*(.+)",
        "acuity_estimate":   r"ACUITY_ESTIMATE:\s*(.+)",
        "risk_signals":      r"RISK_SIGNALS:\s*(.+)",
        "recommended_action":r"RECOMMENDED_ACTION:\s*(.+)",
        "reasoning":         r"REASONING:\s*(.+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, raw, re.IGNORECASE)
        if match:
            fields[key] = match.group(1).strip()

    # Normalise escalation flag to boolean-friendly string
    if fields["escalation_flag"]:
        fields["escalation_flag"] = (
            "YES" if "yes" in fields["escalation_flag"].lower() else "NO"
        )

    return fields


def analyze_triage_note(
    note: str,
    hr: int,
    sbp: int,
    dbp: int,
    rr: int,
    o2: float,
    temp: float,
    gcs: str = "Not recorded",
) -> dict:
    """
    Analyze a triage note and vitals for escalation risk.

    Args:
        note:  Free-text triage note written by the nurse
        hr:    Heart rate in bpm
        sbp:   Systolic blood pressure in mmHg
        dbp:   Diastolic blood pressure in mmHg
        rr:    Respiratory rate in breaths/min
        o2:    O2 saturation as percentage (e.g. 94.0)
        temp:  Temperature in Celsius
        gcs:   Glasgow Coma Scale string e.g. "E4V5M6" (optional)

    Returns:
        dict with keys: escalation_flag, acuity_estimate, risk_signals,
                        recommended_action, reasoning, raw_response
    """
    if not _API_KEY or not _PROJECT_ID:
        raise EnvironmentError(
            "WATSONX_API_KEY and WATSONX_PROJECT_ID must be set in .env"
        )

    prompt = _PROMPT_TEMPLATE.format(
        note=note.strip(),
        hr=hr,
        sbp=sbp,
        dbp=dbp,
        rr=rr,
        o2=o2,
        temp=temp,
        gcs=gcs,
    )

    model = _get_model()
    response = model.generate_text(prompt=prompt)
    return _parse_response(response)


# ── Quick manual test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Stroke-like presentation — should flag YES, CTAS 2
    test_note = (
        "72F brought in by husband. Sudden onset facial drooping left side, "
        "slurred speech, right arm weakness. Husband says symptoms started "
        "approximately 45 minutes ago. Patient confused and anxious."
    )
    result = analyze_triage_note(
        note=test_note, hr=98, sbp=178, dbp=102, rr=18, o2=96.0, temp=36.8
    )
    print("\n── Escalation Analysis ──────────────────────────────")
    for k, v in result.items():
        if k != "raw_response":
            print(f"  {k.upper():25s}: {v}")
    print("─────────────────────────────────────────────────────\n")
