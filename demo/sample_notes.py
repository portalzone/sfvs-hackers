"""
sample_notes.py

Demo cases drawn from the synthetic offshore equipment dataset (1000 cases).
7 cases covering major operational and safety risk categories.
"""

DEMO_CASES = [
    # ── HIGH RISK (should flag 1) ──────────────────────────────────────────

    {
        "label": "Gas Leak — Severity Level 1 expected",
        "expected_flag": "1",
        "note": "High-pressure cementing unit — gas detection system triggered past 2 hours. Confirmed hydrocarbon leak at flange. Pressure 172 PSI. Shutdown valve closed. S. Newhook coordinating isolation.",
        "pressure": 172, "temperature": 65.0, "vibration": 8.4, "flow": 49,
    },

    {
        "label": "Electrical Anomaly — Severity Level 2 expected",
        "expected_flag": "1",
        "note": "Main generator bus voltage drop down to 180V. Severe phase imbalance causing starter coil overheat. Hot spot thermal imaging showing 94C on connection terminal. Risk of arc flash.",
        "pressure": 0, "temperature": 94.2, "vibration": 1.1, "flow": 0,
    },

    {
        "label": "Process Upset — Severity Level 2 expected",
        "expected_flag": "1",
        "note": "Hydraulic circuit — erratic pressure fluctuations between 253 and 340 PSI past 2 hours. Cavitation noise audible at pump inlet. Flow rate dropped to 37%.",
        "pressure": 253, "temperature": 68.4, "vibration": 15.2, "flow": 37,
    },

    {
        "label": "Structural Fatigue — Severity Level 3 expected",
        "expected_flag": "1",
        "note": "Abnormal vibration on Choke manifold — reading 49.7 mm/s vs baseline of 4 mm/s since 0600. Resonance suspected. RPM reduced from rated. Structural team reviewing.",
        "pressure": 348, "temperature": 54.5, "vibration": 49.7, "flow": 60,
    },

    {
        "label": "Corrosion — Severity Level 3 expected",
        "expected_flag": "1",
        "note": "Ballast pump connection thread showing corrosion and galling. Difficulty making up joint during stabbing. Pressure test not yet performed. Work stopped pending inspection.",
        "pressure": 300, "temperature": 74.8, "vibration": 10.7, "flow": 88,
    },

    # ── ROUTINE (should flag 0) ──────────────────────────────────────────────

    {
        "label": "Routine Maintenance — Severity Level 5 expected",
        "expected_flag": "0",
        "note": "Rotary table drive — scheduled 500hr service completed. Oil sample pulled, lube oil filters replaced. Drive spun un-loaded, parameters satisfactory, tool cleared back to operation.",
        "pressure": 336, "temperature": 63.9, "vibration": 5.9, "flow": 91,
    },

    {
        "label": "Normal Ops — Severity Level 5 expected",
        "expected_flag": "0",
        "note": "Shift handover check on Ballast pump — no issues to report. Flow rate 95%, all alarms clear. Previous shift completed without incident. C. Power handing over to R. Parsons.",
        "pressure": 333, "temperature": 59.5, "vibration": 1.4, "flow": 95,
    },
]