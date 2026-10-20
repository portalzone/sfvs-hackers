"""
escalation_tool.py

Core tool for the offshore equipment safety agent.
Calls watsonx.ai Granite with the engineered prompt and returns
a structured safety analysis.

This file is both:
  1. A standalone callable function you can test directly
  2. The tool implementation registered with watsonx Orchestrate ADK
"""

import os
import re
import warnings
from pathlib import Path
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*a, **kw): pass
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
try:
    from ibm_watsonx_ai.wml_client_error import WatsonxAPIWarning
    warnings.filterwarnings("ignore", category=WatsonxAPIWarning)
except ImportError:
    warnings.filterwarnings("ignore", module="ibm_watsonx_ai")

load_dotenv()

# ── Credentials (loaded from .env) ────────────────────────────────────────────
_ENDPOINT_URL = os.getenv("WATSONX_ENDPOINT_URL", "https://us-south.ml.cloud.ibm.com")
_API_KEY      = os.getenv("WATSONX_API_KEY")
_PROJECT_ID   = os.getenv("WATSONX_PROJECT_ID")
_MODEL_ID     = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")

# ── Prompt template ───────────────────────────────────────────────────────────
_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "triage_prompt.txt"
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
            "temperature": 0.0,
            "repetition_penalty": 1.1,
        },
    )


def _parse_response(raw: str) -> dict:
    """
    Parse the structured Granite output into a Python dict.
    Robust to minor whitespace or capitalisation variation.
    """
    fields = {
        "safety_flag":        "0",
        "severity_level":     "5",
        "category":           "normal_ops",
        "recommended_action": "Continue baseline monitoring protocols.",
        "reasoning":          "",
        "raw_response":       raw.strip(),
    }

    patterns = {
        "safety_flag":        r"SAFETY_FLAG:\s*(.+)",
        "severity_level":     r"SEVERITY_LEVEL:\s*(.+)",
        "category":           r"CATEGORY:\s*(.+)",
        "recommended_action": r"RECOMMENDED_ACTION:\s*(.+)",
        "reasoning":          r"REASONING:\s*(.+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, raw, re.IGNORECASE)
        if match:
            fields[key] = match.group(1).strip()

    # Normalise safety_flag — accept 1/0, yes/no, true/false
    flag_raw = fields["safety_flag"].lower()
    fields["safety_flag"] = "1" if any(x in flag_raw for x in ("1", "yes", "true")) else "0"

    # Normalise severity_level — extract first digit found
    sev_match = re.search(r"\d", fields["severity_level"])
    fields["severity_level"] = sev_match.group() if sev_match else "5"

    # Normalise category — strip to lowercase slug
    fields["category"] = fields["category"].lower().replace(" ", "_").split(",")[0].strip()

    # Business rule: routine_maintenance always involves work performed → minimum Level 4.
    # Level 5 (Normal) is reserved for pure monitoring with zero intervention.
    if fields["category"] == "routine_maintenance" and fields["severity_level"] == "5":
        fields["severity_level"] = "4"

    return fields


def analyze_triage_note(
    note: str,
    pressure: int,
    temperature: float,
    vibration: float,
    flow: int,
) -> dict:
    """
    Analyze an equipment log entry for safety risk.

    Returns:
        dict with keys: safety_flag, severity_level, category,
                        recommended_action, reasoning, raw_response
    """
    if not _API_KEY or not _PROJECT_ID:
        raise EnvironmentError(
            "WATSONX_API_KEY and WATSONX_PROJECT_ID must be set in .env"
        )

    prompt = _PROMPT_TEMPLATE.format(
        note=note.strip(),
        pressure=pressure,
        temperature=temperature,
        vibration=vibration,
        flow=flow,
    )

    model = _get_model()
    response = model.generate_text(prompt=prompt)
    return _parse_response(response)


# ── Quick manual test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Blowout risk — should flag 1, severity 1
    test_note = (
        "WELL CONTROL EVENT — BOP stack showing 920 PSI surface pressure since 0600. "
        "Pit gain 22 barrels observed. Gas cut mud at surface. "
        "OIM and well control team mobilised."
    )
    result = analyze_triage_note(
        note=test_note,
        pressure=920, temperature=98.5, vibration=24.2, flow=12
    )
    print("\n── Safety Analysis ──────────────────────────────────")
    for k, v in result.items():
        if k != "raw_response":
            print(f"  {k.upper():25s}: {v}")
    print("─────────────────────────────────────────────────────\n")