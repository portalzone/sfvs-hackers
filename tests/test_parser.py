"""
test_parser.py

Unit tests for tools/input_parser.py — no API calls needed.
Run with:  python tests/test_parser.py
       or: pytest tests/test_parser.py
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.input_parser import parse_triage_input, ParsedInput  # Retains internal module structural naming


# ── Happy-path tests ──────────────────────────────────────────────────────────

def test_clean_numeric_inputs():
    parsed = parse_triage_input(
        note="High-pressure cementing unit — gas detection system triggered.",
        pressure=172, temperature=65.0, vibration=8.4, flow=49
    )
    assert isinstance(parsed, ParsedInput)
    assert parsed.pressure == 172
    assert parsed.temperature == 65.0
    assert parsed.vibration == 8.4
    assert parsed.flow == 49
    assert parsed.warnings == []


def test_string_telemetry_with_units():
    """UI form values arrive as strings with units — should parse cleanly."""
    parsed = parse_triage_input(
        note="High-pressure cementing unit — gas detection system triggered.",
        pressure="172psi", temperature="65.0C", vibration="8.4mms", flow="49%"
    )
    assert parsed.pressure == 172
    assert parsed.temperature == 65.0
    assert parsed.vibration == 8.4
    assert parsed.flow == 49


def test_note_whitespace_stripped():
    parsed = parse_triage_input(
        note="   High-pressure cementing unit — gas detection system triggered.   ",
        pressure=172, temperature=65.0, vibration=8.4, flow=49
    )
    assert not parsed.note.startswith(" ")
    assert not parsed.note.endswith(" ")


def test_note_internal_whitespace_collapsed():
    parsed = parse_triage_input(
        note="High-pressure  cementing   unit\ngas detection system triggered.",
        pressure=172, temperature=65.0, vibration=8.4, flow=49
    )
    assert "  " not in parsed.note
    assert "\n" not in parsed.note


def test_note_curly_braces_removed():
    parsed = parse_triage_input(
        note="Asset log note with {bad} braces inside the text here.",
        pressure=172, temperature=65.0, vibration=8.4, flow=49
    )
    assert "{" not in parsed.note
    assert "}" not in parsed.note
    assert any("brace" in w.lower() for w in parsed.warnings)


def test_note_truncated_at_1000():
    long_note = "x" * 1200
    parsed = parse_triage_input(
        note=long_note,
        pressure=172, temperature=65.0, vibration=8.4, flow=49
    )
    assert len(parsed.note) == 1000
    assert any("truncated" in w.lower() for w in parsed.warnings)


def test_to_dict_keys_match_analyze_signature():
    parsed = parse_triage_input(
        note="High-pressure cementing unit — gas detection system triggered.",
        pressure=172, temperature=65.0, vibration=8.4, flow=49
    )
    d = parsed.to_dict()
    assert set(d.keys()) == {"note", "pressure", "temperature", "vibration", "flow"}


def test_pressure_type_is_int():
    parsed = parse_triage_input(
        note="High-pressure cementing unit — gas detection system triggered.",
        pressure="172psi", temperature=65.0, vibration=8.4, flow=49
    )
    assert isinstance(parsed.pressure, int)


def test_vibration_type_is_float():
    parsed = parse_triage_input(
        note="High-pressure cementing unit — gas detection system triggered.",
        pressure=172, temperature=65.0, vibration="8.4mms", flow=49
    )
    assert isinstance(parsed.vibration, float)


def test_temperature_type_is_float():
    parsed = parse_triage_input(
        note="High-pressure cementing unit — gas detection system triggered.",
        pressure=172, temperature="65.0C", vibration=8.4, flow=49
    )
    assert isinstance(parsed.temperature, float)


# ── Note validation failures ──────────────────────────────────────────────────

def test_empty_note_raises():
    with pytest.raises(ValueError, match="empty"):
        parse_triage_input(
            note="", pressure=172, temperature=65.0, vibration=8.4, flow=49
        )


def test_whitespace_only_note_raises():
    with pytest.raises(ValueError, match="empty"):
        parse_triage_input(
            note="   \n\t  ", pressure=172, temperature=65.0, vibration=8.4, flow=49
        )


def test_note_too_short_raises():
    with pytest.raises(ValueError, match="too short"):
        parse_triage_input(
            note="Leak", pressure=172, temperature=65.0, vibration=8.4, flow=49
        )


def test_non_string_note_raises():
    with pytest.raises(ValueError, match="text string"):
        parse_triage_input(
            note=99999, pressure=172, temperature=65.0, vibration=8.4, flow=49
        )


# ── Telemetry range failures ──────────────────────────────────────────────────

def test_pressure_negative_raises():
    with pytest.raises(ValueError, match="pressure"):
        parse_triage_input(
            note="High-pressure cementing unit — gas detection system triggered.",
            pressure=-15, temperature=65.0, vibration=8.4, flow=49
        )


def test_pressure_too_high_raises():
    with pytest.raises(ValueError, match="pressure"):
        parse_triage_input(
            note="High-pressure cementing unit — gas detection system triggered.",
            pressure=12000, temperature=65.0, vibration=8.4, flow=49
        )


def test_temperature_too_high_raises():
    with pytest.raises(ValueError, match="temperature"):
        parse_triage_input(
            note="High-pressure cementing unit — gas detection system triggered.",
            pressure=172, temperature=650.0, vibration=8.4, flow=49
        )


def test_temperature_too_low_raises():
    with pytest.raises(ValueError, match="temperature"):
        parse_triage_input(
            note="High-pressure cementing unit — gas detection system triggered.",
            pressure=172, temperature=-150.0, vibration=8.4, flow=49
        )


def test_vibration_negative_raises():
    with pytest.raises(ValueError, match="vibration"):
        parse_triage_input(
            note="High-pressure cementing unit — gas detection system triggered.",
            pressure=172, temperature=65.0, vibration=-2.5, flow=49
        )


def test_flow_rate_out_of_bounds_raises():
    with pytest.raises(ValueError, match="flow"):
        parse_triage_input(
            note="High-pressure cementing unit — gas detection system triggered.",
            pressure=172, temperature=65.0, vibration=8.4, flow=125
        )


def test_unparseable_telemetry_raises():
    with pytest.raises(ValueError, match="pressure"):
        parse_triage_input(
            note="High-pressure cementing unit — gas detection system triggered.",
            pressure="critical_high", temperature=65.0, vibration=8.4, flow=49
        )


# ── Boundary conditions ───────────────────────────────────────────────────────

def test_pressure_at_zero_boundary():
    parsed = parse_triage_input(
        note="High-pressure cementing unit — gas detection system triggered.",
        pressure=0, temperature=65.0, vibration=8.4, flow=49
    )
    assert parsed.pressure == 0


def test_flow_at_100_percent():
    parsed = parse_triage_input(
        note="High-pressure cementing unit — gas detection system triggered.",
        pressure=172, temperature=65.0, vibration=8.4, flow=100
    )
    assert parsed.flow == 100


def test_note_exactly_10_chars():
    parsed = parse_triage_input(
        note="Log Entry1",
        pressure=172, temperature=65.0, vibration=8.4, flow=49
    )
    assert len(parsed.note) == 10


def test_note_exactly_1000_chars_no_truncation():
    note = "a" * 1000
    parsed = parse_triage_input(
        note=note, pressure=172, temperature=65.0, vibration=8.4, flow=49
    )
    assert len(parsed.note) == 1000
    assert not any("truncated" in w.lower() for w in parsed.warnings)


# ── Runner for non-pytest usage ───────────────────────────────────────────────

if __name__ == "__main__":
    import traceback

    tests = [
        test_clean_numeric_inputs,
        test_string_telemetry_with_units,
        test_note_whitespace_stripped,
        test_note_internal_whitespace_collapsed,
        test_note_curly_braces_removed,
        test_note_truncated_at_1000,
        test_to_dict_keys_match_analyze_signature,
        test_pressure_type_is_int,
        test_vibration_type_is_float,
        test_temperature_type_is_float,
        test_empty_note_raises,
        test_whitespace_only_note_raises,
        test_note_too_short_raises,
        test_non_string_note_raises,
        test_pressure_negative_raises,
        test_pressure_too_high_raises,
        test_temperature_too_high_raises,
        test_temperature_too_low_raises,
        test_vibration_negative_raises,
        test_flow_rate_out_of_bounds_raises,
        test_unparseable_telemetry_raises,
        test_pressure_at_zero_boundary,
        test_flow_at_100_percent,
        test_note_exactly_10_chars,
        test_note_exactly_1000_chars_no_truncation,
    ]

    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"✓  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗  {t.__name__}: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n{passed}/{passed + failed} tests passed.")
    if failed:
        sys.exit(1)