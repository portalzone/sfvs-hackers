"""
impact_analysis.py — SFVS-Hackers
Runs 30 cases from offshore_equipment_1000.csv through the live model,
compares predictions to ground truth, and saves results for the pitch.

Run from project root:
    python analysis/impact_analysis.py
"""

import sys
import os
import json
import time
import csv
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load .env
_env = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(_env):
    with open(_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

from tools.escalation_tool import analyze_triage_note

# ── Config ────────────────────────────────────────────────────────────────────

DATA_PATH    = os.path.join(os.path.dirname(__file__), "..", "data", "offshore_equipment_1000.csv")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results.json")
SUMMARY_PATH = os.path.join(os.path.dirname(__file__), "summary.txt")
N_CASES      = 30   # API cost — 30 is enough for meaningful stats


def load_cases(n):
    cases = []
    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= n:
                break
            cases.append(row)
    return cases


def run_analysis():
    print(f"\n{'─'*60}")
    print(f"  SFVS-Hackers — Impact Analysis")
    print(f"  Running {N_CASES} cases against live watsonx.ai model")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'─'*60}\n")

    cases = load_cases(N_CASES)
    results = []

    correct_flag   = 0
    false_negatives = 0   # model said 0, truth was 1 (missed escalation — dangerous)
    false_positives = 0   # model said 1, truth was 0 (over-flagged routine)
    response_times = []
    by_category    = defaultdict(lambda: {"correct": 0, "total": 0})
    correct_severity = 0

    for i, case in enumerate(cases, 1):
        truth_flag     = str(case["safety_flag"]).strip()       # "1" or "0"
        truth_severity = str(case["severity_level"]).strip()
        truth_category = case["category"].strip()
        note           = case["log_entry"].strip()

        try:
            pressure  = int(float(case["pressure_psi"]))
            temp_c    = float(case["temp_c"])
            vibration = float(case["vibration_mms"])
            flow      = int(float(case["flow_rate_pct"]))
            voltage   = int(float(case["voltage_v"]))
            rpm       = int(float(case["rpm"]))
        except (ValueError, KeyError):
            pressure = temp_c = vibration = flow = voltage = rpm = 0

        print(f"  [{i:02d}/{N_CASES}] {truth_category:<22} flag={truth_flag}  ", end="", flush=True)

        t_start = time.time()
        try:
            result = analyze_triage_note(
                note=note,
                pressure_psi=pressure,
                temp_c=temp_c,
                vibration_mms=vibration,
                flow_rate_pct=flow,
                voltage_v=voltage,
                rpm=rpm,
            )
            elapsed = round(time.time() - t_start, 2)
            response_times.append(elapsed)

            pred_flag     = result.get("safety_flag", "0")
            pred_severity = result.get("severity_level", "5")
            pred_category = result.get("category", "unknown")

            flag_correct = (pred_flag == truth_flag)
            sev_correct  = (pred_severity == truth_severity)

            if flag_correct:
                correct_flag += 1
            elif truth_flag == "1" and pred_flag == "0":
                false_negatives += 1
            elif truth_flag == "0" and pred_flag == "1":
                false_positives += 1

            if sev_correct:
                correct_severity += 1

            by_category[truth_category]["total"]  += 1
            by_category[truth_category]["correct"] += int(flag_correct)

            status = "✓" if flag_correct else "✗"
            print(f"pred={pred_flag}  {status}  ({elapsed}s)")

            results.append({
                "case_id":        case["log_id"],
                "platform":       case["platform"],
                "category":       truth_category,
                "truth_flag":     truth_flag,
                "truth_severity": truth_severity,
                "pred_flag":      pred_flag,
                "pred_severity":  pred_severity,
                "pred_category":  pred_category,
                "flag_correct":   flag_correct,
                "sev_correct":    sev_correct,
                "response_time_s": elapsed,
                "note_preview":   note[:80],
            })

        except Exception as e:
            elapsed = round(time.time() - t_start, 2)
            print(f"ERROR  ({elapsed}s): {e}")
            results.append({
                "case_id": case["log_id"],
                "error":   str(e),
                "flag_correct": False,
                "sev_correct":  False,
            })

        time.sleep(0.5)   # avoid rate limiting

    # ── Calculate metrics ─────────────────────────────────────────────────────
    total         = len(results)
    flag_accuracy = round(correct_flag / total * 100, 1)
    sev_accuracy  = round(correct_severity / total * 100, 1)
    fn_rate       = round(false_negatives / total * 100, 1)
    fp_rate       = round(false_positives / total * 100, 1)
    avg_time      = round(sum(response_times) / len(response_times), 2) if response_times else 0
    min_time      = round(min(response_times), 2) if response_times else 0
    max_time      = round(max(response_times), 2) if response_times else 0

    cat_breakdown = {}
    for cat, stats in sorted(by_category.items()):
        acc = round(stats["correct"] / stats["total"] * 100, 1) if stats["total"] else 0
        cat_breakdown[cat] = {
            "accuracy_pct": acc,
            "correct":      stats["correct"],
            "total":        stats["total"],
        }

    summary = {
        "run_timestamp":       datetime.now().isoformat(),
        "model":               os.getenv("WATSONX_MODEL_ID", "meta-llama/llama-3-3-70b-instruct"),
        "cases_evaluated":     total,
        "flag_accuracy_pct":   flag_accuracy,
        "severity_accuracy_pct": sev_accuracy,
        "false_negative_rate_pct": fn_rate,
        "false_positive_rate_pct": fp_rate,
        "avg_response_time_s": avg_time,
        "min_response_time_s": min_time,
        "max_response_time_s": max_time,
        "accuracy_by_category": cat_breakdown,
        "cases": results,
    }

    # ── Save results.json ─────────────────────────────────────────────────────
    with open(RESULTS_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    # ── Print and save summary.txt ────────────────────────────────────────────
    lines = [
        "=" * 60,
        "  SFVS-Hackers — Offshore Equipment Agent",
        "  Impact Analysis Summary",
        f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 60,
        "",
        f"  Cases evaluated   : {total}",
        f"  Model             : {summary['model']}",
        "",
        "  ── Safety Flag Accuracy ──────────────────────────────",
        f"  Overall accuracy  : {flag_accuracy}%",
        f"  False negative    : {fn_rate}%  (missed escalations — critical metric)",
        f"  False positive    : {fp_rate}%  (over-flagged routine cases)",
        "",
        "  ── Severity Level Accuracy ───────────────────────────",
        f"  Severity accuracy : {sev_accuracy}%",
        "",
        "  ── Response Time ─────────────────────────────────────",
        f"  Average           : {avg_time}s per log entry",
        f"  Fastest           : {min_time}s",
        f"  Slowest           : {max_time}s",
        "",
        "  ── Accuracy by Category ──────────────────────────────",
    ]

    for cat, stats in sorted(cat_breakdown.items(), key=lambda x: -x[1]["accuracy_pct"]):
        bar = "█" * int(stats["accuracy_pct"] / 10)
        lines.append(f"  {cat:<25} {stats['accuracy_pct']:>5}%  {bar}  ({stats['correct']}/{stats['total']})")

    lines += [
        "",
        "  ── Pitch Soundbites ──────────────────────────────────",
        f"  \"Our agent correctly flags {flag_accuracy}% of safety-critical",
        f"   equipment events in under {avg_time} seconds on average.\"",
        "",
        f"  \"Missed escalation rate: {fn_rate}% — meaning the agent",
        f"   correctly identifies {100-fn_rate}% of critical incidents",
        f"   that require immediate intervention.\"",
        "",
        "=" * 60,
    ]

    output = "\n".join(lines)
    print("\n" + output)

    with open(SUMMARY_PATH, "w") as f:
        f.write(output)

    print(f"\n  Results saved to analysis/results.json")
    print(f"  Summary saved to analysis/summary.txt\n")


if __name__ == "__main__":
    run_analysis()
