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
    "pressure_psi":  (0,    2000,  int,   "Pressure",  "PSI"),
    "temp_c":        (0.0,  400.0, float, "Temp",      "°C"),
    "vibration_mms": (0.0,  200.0, float, "Vibration", "mm/s"),
    "flow_rate_pct": (0.0,  100.0, float, "Flow Rate", "%"),
    "voltage_v":     (0.0,  1000.0,float, "Voltage",   "V"),
    "rpm":           (0,    10000, int,   "RPM",       "rpm"),
}

# Units to strip from numeric strings
_UNIT_PATTERN = re.compile(
    r"(?i)(psi|°?c|mm/s|mms|%|v\b|rpm)\s*$"
)


@dataclass
class ParsedInput:
    note:          str
    pressure_psi:  int
    temp_c:        float
    vibration_mms: float
    flow_rate_pct: float
    voltage_v:     float
    rpm:           int
    warnings:      list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "note":          self.note,
            "pressure_psi":  self.pressure_psi,
            "temp_c":        self.temp_c,
            "vibration_mms": self.vibration_mms,
            "flow_rate_pct": self.flow_rate_pct,
            "voltage_v":     self.voltage_v,
            "rpm":           self.rpm,
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
            f"{label} value '{raw}' could not be parsed as a number. "
            f"Expected a numeric value in {unit}."
        )

    if value < lo or value > hi:
        raise ValueError(
            f"{label} value {value} is outside the plausible range "
            f"({lo}–{hi} {unit}). Please verify and re-enter."
        )

    return cast(value)


# ── Public API ────────────────────────────────────────────────────────────────

def parse_triage_input(
    note,
    pressure_psi  = None,
    temp_c        = None,
    vibration_mms = None,
    flow_rate_pct = None,
    voltage_v     = None,
    rpm           = None,
    # Legacy triage param names accepted silently so old call sites don't break
    hr=None, sbp=None, dbp=None, rr=None, o2=None, temp=None, gcs=None,
) -> ParsedInput:
    """
    Validate and clean all equipment log inputs.

    Accepts offshore sensor kwargs (pressure_psi, temp_c, etc.) or the legacy
    triage kwargs (hr, sbp, etc.) — whichever are provided get mapped across.

    Raises ValueError with a human-readable message for fatal failures.
    Non-fatal issues are stored in ParsedInput.warnings.

    Returns a ParsedInput whose .to_dict() is safe to pass directly to
    analyze_triage_note().
    """
    warns: list = []

    # Map legacy triage fields to sensor fields if offshore fields not supplied
    if pressure_psi  is None and hr   is not None: pressure_psi  = hr
    if temp_c        is None and temp is not None: temp_c        = temp
    if vibration_mms is None and rr   is not None: vibration_mms = float(rr)
    if flow_rate_pct is None and dbp  is not None: flow_rate_pct = float(dbp)
    if voltage_v     is None and sbp  is not None: voltage_v     = float(sbp)

    cleaned_note     = _clean_note(note, warns)
    cleaned_pressure = _clean_sensor(pressure_psi,  "pressure_psi",  warns)
    cleaned_temp     = _clean_sensor(temp_c,         "temp_c",        warns)
    cleaned_vib      = _clean_sensor(vibration_mms,  "vibration_mms", warns)
    cleaned_flow     = _clean_sensor(flow_rate_pct,  "flow_rate_pct", warns)
    cleaned_voltage  = _clean_sensor(voltage_v,      "voltage_v",     warns)
    cleaned_rpm      = _clean_sensor(rpm,            "rpm",           warns)

    return ParsedInput(
        note=cleaned_note,
        pressure_psi=cleaned_pressure,
        temp_c=cleaned_temp,
        vibration_mms=cleaned_vib,
        flow_rate_pct=cleaned_flow,
        voltage_v=cleaned_voltage,
        rpm=cleaned_rpm,
        warnings=warns,
    )