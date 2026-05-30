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

from tools.escalation_tool import analyze_triage_note  # Keeps the same tool import structure
from demo.sample_notes import DEMO_CASES

# ANSI colours for terminal output
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def safety_flag_colour(flag: str) -> str:
    # Coerces flag to string to protect against int/str type disparities
    if str(flag) == "1":
        return f"{RED}{BOLD}⚠  1 — CRITICAL SAFETY ESCALATION{RESET}"
    elif str(flag) == "0":
        return f"{GREEN}✓  0 — NORMAL OPERATIONS{RESET}"
    return f"{YELLOW}?  UNKNOWN{RESET}"


def run_case(case: dict) -> bool:
    """Run one asset log scenario. Returns True if expected safety flag matched."""
    print(f"\n{BOLD}{'─' * 60}{RESET}")
    print(f"{CYAN}{BOLD}SCENARIO: {case['label']}{RESET}")
    print(f"\n{BOLD}Log entry:{RESET}")
    print(f"  {case['note']}")
    print(f"\n{BOLD}Telemetry:{RESET}  Pressure {case['pressure']} PSI  |  Temp {case['temperature']}°C"
          f"  |  Vibration {case['vibration']} mm/s  |  Flow {case['flow']}%"
          f"  |  RPM {case.get('rpm', 'N/R')}")

    print(f"\n{YELLOW}Processing telemetry metrics...{RESET}")

    try:
        result = analyze_triage_note(
            note=case["note"],
            pressure=case["pressure"],
            temperature=case["temperature"],
            vibration=case["vibration"],
            flow=case["flow"]
        )
    except Exception as e:
        print(f"{RED}ERROR EXECUTING REASONING ENGINE: {e}{RESET}")
        return False

    print(f"\n{BOLD}── Agent Evaluation Output ───────────────────────────{RESET}")
    print(f"  Safety Flag      : {safety_flag_colour(result.get('safety_flag', '?'))}")
    print(f"  Severity Level   : {BOLD}Level {result.get('severity_level', 'N/A')}{RESET}")
    print(f"  Incident Category: {result.get('category', 'NONE')}")
    print(f"  Action Plan      : {result.get('recommended_action', 'N/A')}")
    print(f"  Engineering Logic: {result.get('log_entry', 'N/A')}")

    expected = str(case.get("expected_flag", "?"))
    actual   = str(result.get("safety_flag", "?"))
    matched  = expected == actual
    status   = f"{GREEN}✓ MATCH{RESET}" if matched else f"{RED}✗ MISMATCH (expected {expected}){RESET}"
    print(f"\n  Validation Check : {status}")

    return matched


def main():
    parser = argparse.ArgumentParser(description="Run offshore asset telemetry demo cases")
    parser.add_argument("--case", type=int, default=None,
                        help="Run only case number N (0-indexed)")
    args = parser.parse_args()

    cases = [DEMO_CASES[args.case]] if args.case is not None else DEMO_CASES

    print(f"\n{BOLD}Offshore Equipment Intelligence Agent — Anomaly & Safety Dashboard{RESET}")
    print(f"Running {len(cases)} operational case(s) against {os.getenv('WATSONX_MODEL_ID', 'model not set')}")

    results = [run_case(c) for c in cases]

    total   = len(results)
    correct = sum(results)
    print(f"\n{BOLD}{'─' * 60}{RESET}")
    print(f"Results Summary: {correct}/{total} asset cases matched expected safety flag")
    if correct == total:
        print(f"{GREEN}{BOLD}All operational checks passed ✓{RESET}")
    else:
        print(f"{YELLOW}Some edge cases need prompt refinement — review model's engineering logic output.{RESET}")


if __name__ == "__main__":
    main()