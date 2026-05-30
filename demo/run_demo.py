"""
run_demo.py

Runs all synthetic demo cases through the escalation tool and prints
formatted output. Use this to:
  1. Verify your credentials work
  2. Iterate on prompt quality
  3. Generate output for the demo presentation

Usage:
    python demo/run_demo.py
    python demo/run_demo.py --case 0    # run only the first case
"""

import sys
import os
import argparse

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.escalation_tool import analyze_triage_note
from demo.sample_notes import DEMO_CASES

# ANSI colours for terminal output
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def flag_colour(flag: str) -> str:
    if flag == "YES":
        return f"{RED}{BOLD}⚠  YES — ESCALATE{RESET}"
    elif flag == "NO":
        return f"{GREEN}✓  NO — ROUTINE{RESET}"
    return f"{YELLOW}?  UNKNOWN{RESET}"


def run_case(case: dict) -> bool:
    """Run one case. Returns True if expected flag matched."""
    print(f"\n{BOLD}{'─' * 60}{RESET}")
    print(f"{CYAN}{BOLD}SCENARIO: {case['label']}{RESET}")
    print(f"\n{BOLD}Triage note:{RESET}")
    print(f"  {case['note']}")
    print(f"\n{BOLD}Vitals:{RESET}  HR {case['hr']}  BP {case['sbp']}/{case['dbp']}"
          f"  RR {case['rr']}  O2 {case['o2']}%  Temp {case['temp']}°C"
          f"  GCS {case.get('gcs', 'N/R')}")

    print(f"\n{YELLOW}Analyzing...{RESET}")

    try:
        result = analyze_triage_note(
            note=case["note"],
            hr=case["hr"],
            sbp=case["sbp"],
            dbp=case["dbp"],
            rr=case["rr"],
            o2=case["o2"],
            temp=case["temp"],
            gcs=case.get("gcs", "Not recorded"),
        )
    except Exception as e:
        print(f"{RED}ERROR: {e}{RESET}")
        return False

    print(f"\n{BOLD}── Agent Output ──────────────────────────────────────{RESET}")
    print(f"  Escalation flag  : {flag_colour(result.get('escalation_flag', '?'))}")
    print(f"  Acuity estimate  : {BOLD}{result.get('acuity_estimate', 'N/A')}{RESET}")
    print(f"  Risk signals     : {result.get('risk_signals', 'NONE')}")
    print(f"  Recommended action: {result.get('recommended_action', 'N/A')}")
    print(f"  Reasoning        : {result.get('reasoning', 'N/A')}")

    expected = case.get("expected_flag", "?")
    actual   = result.get("escalation_flag", "?")
    matched  = expected == actual
    status   = f"{GREEN}✓ MATCH{RESET}" if matched else f"{RED}✗ MISMATCH (expected {expected}){RESET}"
    print(f"\n  Validation       : {status}")

    return matched


def main():
    parser = argparse.ArgumentParser(description="Run triage agent demo cases")
    parser.add_argument("--case", type=int, default=None,
                        help="Run only case number N (0-indexed)")
    args = parser.parse_args()

    cases = [DEMO_CASES[args.case]] if args.case is not None else DEMO_CASES

    print(f"\n{BOLD}NL Triage Escalation Agent — IBM watsonx Hackathon 2026{RESET}")
    print(f"Running {len(cases)} demo case(s) against {os.getenv('WATSONX_MODEL_ID', 'model not set')}")

    results = [run_case(c) for c in cases]

    total   = len(results)
    correct = sum(results)
    print(f"\n{BOLD}{'─' * 60}{RESET}")
    print(f"Results: {correct}/{total} cases matched expected flag")
    if correct == total:
        print(f"{GREEN}{BOLD}All cases passed ✓{RESET}")
    else:
        print(f"{YELLOW}Some cases need prompt tuning — check raw_response for clues{RESET}")


if __name__ == "__main__":
    main()
