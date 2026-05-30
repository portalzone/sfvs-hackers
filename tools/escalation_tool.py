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
_PROMPT_TEMPLATE = """\
You are a safety analysis assistant reviewing offshore drilling equipment logs \
from Newfoundland and Labrador platforms including Hibernia, Terra Nova, \
White Rose, SeaRose FPSO, and Hebron.

Given the log entry and sensor readings below, respond ONLY in this exact format \
with no preamble, explanation, or extra text:

SAFETY_FLAG: 1 or 0
SEVERITY_LEVEL: 1 (critical/life-safety), 2 (urgent/equipment risk), 3 (moderate/monitor), or 5 (routine)
CATEGORY: one of blowout_risk, gas_leak, pressure_anomaly, overheating, electrical_fault, hydraulic_failure, structural_fatigue, corrosion, routine_maintenance, or normal_ops
RECOMMENDED_ACTION: one sentence describing the appropriate offshore operations response
LOG_ENTRY: one to two sentences explaining which specific signals drove this assessment

Log entry: {note}
Sensors: Pressure {pressure_psi} PSI, Temp {temp_c}°C, Vibration {vibration_mms} mm/s, \
Flow {flow_rate_pct}%, Voltage {voltage_v}V, RPM {rpm}
"""


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
        "log_entry":          "",
        "raw_response":       raw.strip(),
    }

    patterns = {
        "safety_flag":        r"SAFETY_FLAG:\s*(.+)",
        "severity_level":     r"SEVERITY_LEVEL:\s*(.+)",
        "category":           r"CATEGORY:\s*(.+)",
        "recommended_action": r"RECOMMENDED_ACTION:\s*(.+)",
        "log_entry":          r"LOG_ENTRY:\s*(.+)",
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

    return fields


def analyze_triage_note(
    note: str,
    hr: int   = 300,
    sbp: int  = 415,
    dbp: int  = 85,
    rr: int   = 3,
    o2: float = 3.0,
    temp: float = 65.0,
    gcs: str  = "Not recorded",
    # Offshore sensor names (preferred when called from chat_app)
    pressure_psi:  int   = None,
    temp_c:        float = None,
    vibration_mms: float = None,
    flow_rate_pct: float = None,
    voltage_v:     float = None,
    rpm:           int   = None,
) -> dict:
    """
    Analyze an equipment log entry for safety risk.

    Accepts either offshore sensor kwargs (pressure_psi, temp_c, etc.)
    or the legacy triage kwargs (hr, sbp, dbp, rr, o2, temp) so both
    chat_app.py call styles work without error.

    Returns:
        dict with keys: safety_flag, severity_level, category,
                        recommended_action, log_entry, raw_response
    """
    if not _API_KEY or not _PROJECT_ID:
        raise EnvironmentError(
            "WATSONX_API_KEY and WATSONX_PROJECT_ID must be set in .env"
        )

    # Resolve sensor values — prefer explicit offshore kwargs, fall back to
    # legacy triage mappings so old call sites don't break
    pressure_psi  = pressure_psi  if pressure_psi  is not None else hr
    temp_c        = temp_c        if temp_c        is not None else temp
    vibration_mms = vibration_mms if vibration_mms is not None else float(rr)
    flow_rate_pct = flow_rate_pct if flow_rate_pct is not None else float(dbp)
    voltage_v     = voltage_v     if voltage_v     is not None else float(sbp)
    rpm           = rpm           if rpm           is not None else 1100

    prompt = _PROMPT_TEMPLATE.format(
        note=note.strip(),
        pressure_psi=pressure_psi,
        temp_c=temp_c,
        vibration_mms=vibration_mms,
        flow_rate_pct=flow_rate_pct,
        voltage_v=voltage_v,
        rpm=rpm,
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
        pressure_psi=920, temp_c=98.5, vibration_mms=24.2,
        flow_rate_pct=12.0, voltage_v=415.0, rpm=1850
    )
    print("\n── Safety Analysis ──────────────────────────────────")
    for k, v in result.items():
        if k != "raw_response":
            print(f"  {k.upper():25s}: {v}")
    print("─────────────────────────────────────────────────────\n")