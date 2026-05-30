"""
input_parser.py

Sanitizes and validates all inputs before they reach analyze_triage_note().
Raises ValueError with human-readable messages for fatal failures.
Non-fatal issues are collected in ParsedInput.warnings.
"""

import re
import warnings as _warnings_module
from dataclasses import dataclass, field


# ── Physiological validation ranges ──────────────────────────────────────────

_VITAL_RANGES = {
    "hr":   (20,   300,  int,   "HR",   "bpm"),
    "sbp":  (50,   300,  int,   "SBP",  "mmHg"),
    "dbp":  (20,   200,  int,   "DBP",  "mmHg"),
    "rr":   (4,    80,   int,   "RR",   "breaths/min"),
    "o2":   (50.0, 100.0, float, "O2",  "%"),
    "temp": (25.0, 45.0, float,  "Temp", "°C"),
}

# Units patterns to strip from numeric strings (order: longest first)
_UNIT_PATTERN = re.compile(
    r"(?i)(bpm|mmhg|breaths?/min|%|°?c|°?f|c|f)\s*$"
)


@dataclass
class ParsedInput:
    note: str
    hr: int
    sbp: int
    dbp: int
    rr: int
    o2: float
    temp: float
    gcs: str
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "note": self.note,
            "hr":   self.hr,
            "sbp":  self.sbp,
            "dbp":  self.dbp,
            "rr":   self.rr,
            "o2":   self.o2,
            "temp": self.temp,
            "gcs":  self.gcs,
        }


# ── Internal helpers ──────────────────────────────────────────────────────────

def _clean_note(raw: str, warnings: list) -> str:
    if not isinstance(raw, str):
        raise ValueError("Triage note must be a text string.")

    # Strip leading/trailing whitespace
    note = raw.strip()

    if not note:
        raise ValueError("Triage note cannot be empty.")

    # Remove curly braces that would corrupt the prompt template
    if "{" in note or "}" in note:
        note = note.replace("{", "").replace("}", "")
        warnings.append("Curly braces removed from triage note to prevent prompt corruption.")

    # Collapse multiple spaces/newlines into a single space
    note = re.sub(r"\s+", " ", note).strip()

    if len(note) < 10:
        raise ValueError(
            f"Triage note is too short ({len(note)} characters). "
            "Please provide at least 10 characters of clinical detail."
        )

    if len(note) > 1000:
        note = note[:1000]
        warnings.append(
            "Triage note exceeded 1000 characters and was truncated to 1000 characters."
        )

    return note


def _clean_vital(raw, name: str, warnings: list):
    """Strip units, cast to numeric type, and validate range for one vital."""
    lo, hi, cast, label, unit = _VITAL_RANGES[name]

    if raw is None or (isinstance(raw, str) and not raw.strip()):
        raise ValueError(f"{label} is required but was not provided.")

    # If already the right numeric type, work directly
    if isinstance(raw, (int, float)):
        value_str = str(raw)
    else:
        value_str = str(raw).strip()
        # Strip trailing unit text
        value_str = _UNIT_PATTERN.sub("", value_str).strip()

    try:
        value = float(value_str)
    except ValueError:
        raise ValueError(
            f"{label} value '{raw}' could not be parsed as a number. "
            f"Expected a numeric value in {unit}."
        )

    if value < lo or value > hi:
        raise ValueError(
            f"{label} value {value} is outside the physiologically plausible range "
            f"({lo}–{hi} {unit}). Please verify and re-enter."
        )

    return cast(value)


def _clean_gcs(raw) -> str:
    if raw is None:
        return "Not recorded"
    cleaned = str(raw).strip()
    return cleaned if cleaned else "Not recorded"


# ── Public API ────────────────────────────────────────────────────────────────

def parse_triage_input(
    note,
    hr,
    sbp,
    dbp,
    rr,
    o2,
    temp,
    gcs=None,
) -> ParsedInput:
    """
    Validate and clean all triage inputs.

    Raises ValueError with a human-readable message for any fatal failure.
    Non-fatal issues are stored in ParsedInput.warnings.

    Returns a ParsedInput whose .to_dict() is safe to pass directly to
    analyze_triage_note().
    """
    warns: list = []

    cleaned_note = _clean_note(note, warns)
    cleaned_hr   = _clean_vital(hr,   "hr",   warns)
    cleaned_sbp  = _clean_vital(sbp,  "sbp",  warns)
    cleaned_dbp  = _clean_vital(dbp,  "dbp",  warns)
    cleaned_rr   = _clean_vital(rr,   "rr",   warns)
    cleaned_o2   = _clean_vital(o2,   "o2",   warns)
    cleaned_temp = _clean_vital(temp, "temp", warns)
    cleaned_gcs  = _clean_gcs(gcs)

    # Sanity check: DBP should not exceed SBP
    if cleaned_dbp >= cleaned_sbp:
        raise ValueError(
            f"DBP ({cleaned_dbp} mmHg) must be less than SBP ({cleaned_sbp} mmHg). "
            "Please verify blood pressure values."
        )

    return ParsedInput(
        note=cleaned_note,
        hr=cleaned_hr,
        sbp=cleaned_sbp,
        dbp=cleaned_dbp,
        rr=cleaned_rr,
        o2=cleaned_o2,
        temp=cleaned_temp,
        gcs=cleaned_gcs,
        warnings=warns,
    )
