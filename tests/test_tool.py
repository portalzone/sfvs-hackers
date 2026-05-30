"""
test_tool.py

Quick sanity checks — run these before deploying to Orchestrate.
Doesn't require pytest; just run: python tests/test_tool.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.escalation_tool import analyze_triage_note, _parse_response


# ── Unit test: parser (no API needed) ────────────────────────────────────────

def test_parser_yes():
    raw = """ESCALATION_FLAG: YES
ACUITY_ESTIMATE: CTAS 2
RISK_SIGNALS: facial drooping, slurred speech, arm weakness
RECOMMENDED_ACTION: Activate stroke protocol and notify physician immediately.
REASONING: Sudden-onset focal neurological deficits in an elderly patient are
consistent with acute ischemic stroke. The 45-minute window makes this a
potential thrombolysis candidate."""
    result = _parse_response(raw)
    assert result["escalation_flag"] == "YES", f"Expected YES, got {result['escalation_flag']}"
    assert "CTAS 2" in result["acuity_estimate"]
    assert "facial drooping" in result["risk_signals"]
    print("✓ test_parser_yes passed")


def test_parser_no():
    raw = """ESCALATION_FLAG: NO
ACUITY_ESTIMATE: CTAS 4
RISK_SIGNALS: NONE
RECOMMENDED_ACTION: Standard assessment and X-ray of right ankle.
REASONING: Isolated musculoskeletal injury with stable vitals and preserved
weight-bearing — no systemic concern."""
    result = _parse_response(raw)
    assert result["escalation_flag"] == "NO"
    assert "CTAS 4" in result["acuity_estimate"]
    print("✓ test_parser_no passed")


# ── Integration test: live API call (requires .env) ───────────────────────────

def test_live_api():
    """Calls the real API with a single low-risk case. Skips if no credentials."""
    if not os.getenv("WATSONX_API_KEY"):
        print("⚠  WATSONX_API_KEY not set — skipping live API test")
        return

    result = analyze_triage_note(
        note="25M, mild headache since this morning. No nausea, vision normal, "
             "neurological exam intact. Works night shifts. Slept 4 hours.",
        hr=72, sbp=122, dbp=76, rr=14, o2=99.0, temp=36.7
    )
    assert result["escalation_flag"] in ("YES", "NO"), \
        f"Unexpected flag value: {result['escalation_flag']}"
    assert result["acuity_estimate"] is not None
    print(f"✓ test_live_api passed — flag={result['escalation_flag']}, "
          f"acuity={result['acuity_estimate']}")


if __name__ == "__main__":
    print("Running tests...\n")
    test_parser_yes()
    test_parser_no()
    test_live_api()
    print("\nAll tests done.")
