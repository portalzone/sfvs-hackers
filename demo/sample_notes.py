"""
sample_notes.py

Demo cases drawn from the synthetic triage dataset (1000 cases).
7 cases covering all major clinical categories.
"""

DEMO_CASES = [
    # ── HIGH RISK (should flag YES) ──────────────────────────────────────────

    {
        "label": "Stroke — CTAS 1 expected",
        "expected_flag": "YES",
        "note": "Pt c/o sudden onset facial drooping L side, slurred speech x1hr ago. Wife states arm weakness noted at home. No hx of CVA. Last known well 1hr ago.",
        "hr": 105, "sbp": 160, "dbp": 108,
        "rr": 22, "o2": 96.0, "temp": 36.5,
    },

    {
        "label": "Cardiac — CTAS 1 expected",
        "expected_flag": "YES",
        "note": "Tearing chest pain radiating to back, onset sudden earlier today. Hx of Marfan syndrome. BP asymmetry noted. Pale, diaphoretic.",
        "hr": 96, "sbp": 180, "dbp": 101,
        "rr": 24, "o2": 92.0, "temp": 36.5,
    },

    {
        "label": "Sepsis — CTAS 2 expected",
        "expected_flag": "YES",
        "note": "Nursing home resident, 47F, brought in unresponsive. Staff report fever x2d, not eating. Foley catheter in situ. Temp 40.1.",
        "hr": 110, "sbp": 84, "dbp": 64,
        "rr": 27, "o2": 89.0, "temp": 39.3,
    },

    {
        "label": "Respiratory — CTAS 2 expected",
        "expected_flag": "YES",
        "note": "47F, known severe asthma, not responding to nebs at home. Too breathless to complete sentences. O2 sat 88%. Onset 2hr ago.",
        "hr": 120, "sbp": 131, "dbp": 84,
        "rr": 33, "o2": 87.0, "temp": 37.3,
    },

    {
        "label": "Paediatric — CTAS 2 expected",
        "expected_flag": "YES",
        "note": "6yo F, sudden onset stridor and drooling. Appears toxic, sitting forward. Hx of no vaccinations. Onset 1.5hr ago.",
        "hr": 134, "sbp": 87, "dbp": 62,
        "rr": 26, "o2": 96.0, "temp": 38.3,
    },

    # ── ROUTINE (should flag NO) ──────────────────────────────────────────────

    {
        "label": "Minor — CTAS 5 expected",
        "expected_flag": "NO",
        "note": "Ear pain L side x2d, afebrile. No hearing loss reported. No vertigo. Hx of recurrent otitis media as child.",
        "hr": 69, "sbp": 112, "dbp": 69,
        "rr": 17, "o2": 97.0, "temp": 36.7,
    },

    {
        "label": "Fracture — CTAS 3 expected",
        "expected_flag": "NO",
        "note": "Pt c/o heel pain after jump from height. Unable to wt bear bilaterally. Bilateral calcaneal tenderness. MOI 30min ago.",
        "hr": 89, "sbp": 130, "dbp": 71,
        "rr": 14, "o2": 100.0, "temp": 36.5,
    },
]