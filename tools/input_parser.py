"""
input_parser.py

Sanitizes and validates all inputs before they reach analyze_triage_note().
Raises ValueError with human-readable messages for fatal failures.
Non-fatal issues are collected in ParsedInput.warnings.
"""

import re
from dataclasses import dataclass, field


# ── Sensor validation ranges ──────────────────────────────────────────────────

_SENSOR_RANGES = {
    "pressure":    (0,    10000, int,   "Pressure",   "PSI"),
    "temperature": (-50.0, 500.0, float, "Temperature", "°C"),
    "vibration":   (0.0,  100.0, float, "Vibration",  "mm/s"),
    "flow":        (0,    100,   int,   "Flow",       "%"),
}

# Units to strip from numeric strings
_UNIT_PATTERN = re.compile(
    r"(?i)(psi|°?c|mm/s|mms|%|v\b|rpm)\s*$"
)


@dataclass
class ParsedInput:
    note:        str
    pressure:    int
    temperature: float
    vibration:   float
    flow:        int
    warnings:    list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "note":        self.note,
            "pressure":    self.pressure,
            "temperature": self.temperature,
            "vibration":   self.vibration,
            "flow":        self.flow,
        }


# ── Internal helpers ──────────────────────────────────────────────────────────

def _clean_note(raw: str, warnings: list) -> str:
    if not isinstance(raw, str):
        raise ValueError("Log entry must be a text string.")

    note = raw.strip()

    if not note:
        raise ValueError("Log entry cannot be empty.")

    # Remove curly braces that would corrupt the prompt template
    if "{" in note or "}" in note:
        note = note.replace("{", "").replace("}", "")
        warnings.append("Curly braces removed from log entry to prevent prompt corruption.")

    # Collapse multiple spaces/newlines
    note = re.sub(r"\s+", " ", note).strip()

    if len(note) < 10:
        raise ValueError(
            f"Log entry is too short ({len(note)} characters). "
            "Please provide at least 10 characters of detail."
        )

    if len(note) > 1000:
        note = note[:1000]
        warnings.append("Log entry exceeded 1000 characters and was truncated.")

    return note


def _clean_sensor(raw, name: str, warnings: list):
    """Strip units, cast to correct type, and validate range for one sensor."""
    lo, hi, cast, label, unit = _SENSOR_RANGES[name]

    if raw is None or (isinstance(raw, str) and not raw.strip()):
        # Non-fatal — use midpoint default and warn
        default = cast((lo + hi) / 2)
        warnings.append(
            f"{label} was not provided — defaulting to {default} {unit}."
        )
        return default

    if isinstance(raw, (int, float)):
        value_str = str(raw)
    else:
        value_str = _UNIT_PATTERN.sub("", str(raw).strip()).strip()

    try:
        value = float(value_str)
    except ValueError:
        raise ValueError(
            f"{name} value '{raw}' could not be parsed as a number. "
            f"Expected a numeric value in {unit}."
        )

    if value < lo or value > hi:
        raise ValueError(
            f"{name} value {value} is outside the plausible range "
            f"({lo}–{hi} {unit}). Please verify and re-enter."
        )

    return cast(value)


# ── Public API ────────────────────────────────────────────────────────────────

def parse_triage_input(
    note,
    pressure    = None,
    temperature = None,
    vibration   = None,
    flow        = None,
) -> ParsedInput:
    """
    Validate and clean all equipment log inputs.

    Raises ValueError with a human-readable message for fatal failures.
    Non-fatal issues are stored in ParsedInput.warnings.

    Returns a ParsedInput whose .to_dict() is safe to pass directly to
    analyze_triage_note().
    """
    warns: list = []

    cleaned_note = _clean_note(note, warns)
    cleaned_pressure = _clean_sensor(pressure, "pressure", warns)
    cleaned_temp = _clean_sensor(temperature, "temperature", warns)
    cleaned_vib = _clean_sensor(vibration, "vibration", warns)
    cleaned_flow = _clean_sensor(flow, "flow", warns)

    return ParsedInput(
        note=cleaned_note,
        pressure=cleaned_pressure,
        temperature=cleaned_temp,
        vibration=cleaned_vib,
        flow=cleaned_flow,
        warnings=warns,
    )