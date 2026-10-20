"""
test_tool.py

Quick sanity checks — run these before deploying to Orchestrate.
Doesn't require pytest; just run: python tests/test_tool.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.escalation_tool import analyze_triage_note, _parse_response  # Retains core tool naming structures


# ── Unit test: parser (no API needed) ────────────────────────────────────────

def test_parser_escalate():
    raw = """SAFETY_FLAG: 1
SEVERITY_LEVEL: Level 1
CATEGORY: gas_leak
RECOMMENDED_ACTION: Trigger emergency shutdown valve (ESD) and isolate high-pressure line.
LOG_ENTRY: High-pressure cementing unit — gas detection system triggered past 2 hours. 
Confirmed hydrocarbon leak at flange. Pressure 172 PSI. Shutdown valve closed."""
    
    result = _parse_response(raw)
    assert str(result["safety_flag"]) == "1", f"Expected 1, got {result['safety_flag']}"
    assert result["severity_level"] == "1"
    assert "gas_leak" in result["category"]
    print("✓ test_parser_escalate passed")


def test_parser_routine():
    raw = """SAFETY_FLAG: 0
SEVERITY_LEVEL: Level 5
CATEGORY: normal_ops
RECOMMENDED_ACTION: Continue normal baseline tracking; standard shift handover.
LOG_ENTRY: Shift handover check on Ballast pump — no issues to report. 
Flow rate 95%, all telemetry indicators stable within safe operating thresholds."""
    
    result = _parse_response(raw)
    assert str(result["safety_flag"]) == "0", f"Expected 0, got {result['safety_flag']}"
    assert result["severity_level"] == "5"
    print("✓ test_parser_routine passed")


# ── Integration test: live API call (requires .env) ───────────────────────────

def test_live_api():
    """Calls the real API with a single stable baseline case. Skips if no credentials."""
    if not os.getenv("WATSONX_API_KEY"):
        print("⚠  WATSONX_API_KEY not set — skipping live API test")
        return

    result = analyze_triage_note(
        note="Ballast pump running within baseline design conditions. Vibration is minimal, "
             "seal temperatures matching surrounding ambient deck values. Mechanical visual inspection normal.",
        pressure=110, temperature=22.0, vibration=0.5, flow=100
    )
    
    assert str(result["safety_flag"]) in ("1", "0"), \
        f"Unexpected safety flag value returned: {result['safety_flag']}"
    assert result["severity_level"] is not None
    print(f"✓ test_live_api passed — safety_flag={result['safety_flag']}, "
          f"severity={result['severity_level']}")


if __name__ == "__main__":
    print("Running system sanity checks...\n")
    test_parser_escalate()
    test_parser_routine()
    test_live_api()
    print("\nAll tests completed.")
