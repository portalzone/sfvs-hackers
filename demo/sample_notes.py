"""
sample_notes.py

Synthetic triage notes for hackathon demonstration.
These are fictional patients — not based on real individuals.

Each entry is a dict with:
  - label: short name for the scenario
  - expected_flag: what we expect the model to return (for sanity checking)
  - note + vitals fields
"""

DEMO_CASES = [
    # ── HIGH RISK cases (should flag YES) ────────────────────────────────────

    {
        "label": "Stroke — CTAS 2 expected",
        "expected_flag": "YES",
        "note": (
            "72F brought in by husband. Sudden onset left facial drooping, "
            "slurred speech, right arm weakness. Husband says it started "
            "approximately 45 minutes ago. Patient confused and anxious. "
            "No known history of stroke. On ramipril for hypertension."
        ),
        "hr": 98, "sbp": 178, "dbp": 102, "rr": 18, "o2": 96.0,
        "temp": 36.8, "gcs": "E3V4M5",
    },

    {
        "label": "STEMI-like — CTAS 1/2 expected",
        "expected_flag": "YES",
        "note": (
            "58M, crushing chest pain radiating to jaw and left arm, onset 20 "
            "minutes ago. Profuse diaphoresis. Pale and clammy. Denies SOB but "
            "looks distressed. History of type 2 diabetes. Takes metformin."
        ),
        "hr": 112, "sbp": 88, "dbp": 56, "rr": 22, "o2": 94.0,
        "temp": 36.5, "gcs": "E4V5M6",
    },

    {
        "label": "Sepsis — CTAS 2 expected",
        "expected_flag": "YES",
        "note": (
            "81M from personal care home, brought by ambulance. Altered level "
            "of consciousness, not responding to verbal commands. Staff report "
            "he was well yesterday. Foul-smelling urine noted by staff. "
            "History of dementia and recurrent UTIs."
        ),
        "hr": 118, "sbp": 82, "dbp": 48, "rr": 26, "o2": 91.0,
        "temp": 38.9, "gcs": "E2V2M4",
    },

    {
        "label": "Pediatric respiratory distress — CTAS 2 expected",
        "expected_flag": "YES",
        "note": (
            "4M infant, brought by mother. Increased work of breathing for "
            "past 3 hours, nasal flaring, subcostal retractions. Poor feeding "
            "since yesterday. No fever. Born premature at 34 weeks."
        ),
        "hr": 168, "sbp": 78, "dbp": 42, "rr": 62, "o2": 89.0,
        "temp": 37.1, "gcs": "Not recorded",
    },

    # ── LOW RISK cases (should flag NO) ──────────────────────────────────────

    {
        "label": "Minor ankle sprain — CTAS 4/5 expected",
        "expected_flag": "NO",
        "note": (
            "23M, twisted right ankle playing hockey approximately 2 hours ago. "
            "Moderate swelling and bruising lateral aspect. Full weight bearing "
            "with limp. No numbness or tingling. No other complaints."
        ),
        "hr": 76, "sbp": 124, "dbp": 78, "rr": 14, "o2": 99.0,
        "temp": 36.6, "gcs": "E4V5M6",
    },

    {
        "label": "URI / sore throat — CTAS 4 expected",
        "expected_flag": "NO",
        "note": (
            "19F, sore throat and mild fever for 2 days. Bilateral tonsillar "
            "erythema on inspection. No stridor, no drooling, voice normal. "
            "Able to swallow, tolerating fluids. No rash. Up to date on vaccines."
        ),
        "hr": 82, "sbp": 118, "dbp": 72, "rr": 15, "o2": 98.0,
        "temp": 38.1, "gcs": "E4V5M6",
    },
]
