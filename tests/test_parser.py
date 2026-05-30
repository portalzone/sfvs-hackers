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

from tools.input_parser import parse_triage_input, ParsedInput


# ── Happy-path tests ──────────────────────────────────────────────────────────

def test_clean_numeric_inputs():
    parsed = parse_triage_input(
        note="72F, sudden facial drooping and slurred speech.",
        hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
    )
    assert isinstance(parsed, ParsedInput)
    assert parsed.hr == 105
    assert parsed.sbp == 160
    assert parsed.o2 == 96.0
    assert parsed.temp == 36.5
    assert parsed.gcs == "Not recorded"
    assert parsed.warnings == []


def test_string_vitals_with_units():
    """UI form values arrive as strings with units — should parse cleanly."""
    parsed = parse_triage_input(
        note="72F, sudden facial drooping and slurred speech.",
        hr="105bpm", sbp="160", dbp="108mmHg", rr="22", o2="96%", temp="36.5C"
    )
    assert parsed.hr == 105
    assert parsed.sbp == 160
    assert parsed.dbp == 108
    assert parsed.rr == 22
    assert parsed.o2 == 96.0
    assert parsed.temp == 36.5


def test_gcs_provided():
    parsed = parse_triage_input(
        note="72F, sudden facial drooping and slurred speech.",
        hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5,
        gcs="E4V5M6"
    )
    assert parsed.gcs == "E4V5M6"


def test_gcs_empty_string_defaults():
    parsed = parse_triage_input(
        note="72F, sudden facial drooping and slurred speech.",
        hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5,
        gcs="   "
    )
    assert parsed.gcs == "Not recorded"


def test_gcs_none_defaults():
    parsed = parse_triage_input(
        note="72F, sudden facial drooping and slurred speech.",
        hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5,
        gcs=None
    )
    assert parsed.gcs == "Not recorded"


def test_note_whitespace_stripped():
    parsed = parse_triage_input(
        note="   72F, sudden facial drooping and slurred speech.   ",
        hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
    )
    assert not parsed.note.startswith(" ")
    assert not parsed.note.endswith(" ")


def test_note_internal_whitespace_collapsed():
    parsed = parse_triage_input(
        note="72F,  sudden   facial\ndrooping and  slurred speech.",
        hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
    )
    assert "  " not in parsed.note
    assert "\n" not in parsed.note


def test_note_curly_braces_removed():
    parsed = parse_triage_input(
        note="Patient note with {bad} braces inside the text here.",
        hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
    )
    assert "{" not in parsed.note
    assert "}" not in parsed.note
    assert any("brace" in w.lower() for w in parsed.warnings)


def test_note_truncated_at_1000():
    long_note = "x" * 1200
    parsed = parse_triage_input(
        note=long_note,
        hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
    )
    assert len(parsed.note) == 1000
    assert any("truncated" in w.lower() for w in parsed.warnings)


def test_to_dict_keys_match_analyze_signature():
    parsed = parse_triage_input(
        note="72F, sudden facial drooping and slurred speech.",
        hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
    )
    d = parsed.to_dict()
    assert set(d.keys()) == {"note", "hr", "sbp", "dbp", "rr", "o2", "temp", "gcs"}


def test_hr_type_is_int():
    parsed = parse_triage_input(
        note="72F, sudden facial drooping and slurred speech.",
        hr="105bpm", sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
    )
    assert isinstance(parsed.hr, int)


def test_o2_type_is_float():
    parsed = parse_triage_input(
        note="72F, sudden facial drooping and slurred speech.",
        hr=105, sbp=160, dbp=108, rr=22, o2="96%", temp=36.5
    )
    assert isinstance(parsed.o2, float)


def test_temp_type_is_float():
    parsed = parse_triage_input(
        note="72F, sudden facial drooping and slurred speech.",
        hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp="36.5C"
    )
    assert isinstance(parsed.temp, float)


# ── Note validation failures ──────────────────────────────────────────────────

def test_empty_note_raises():
    with pytest.raises(ValueError, match="empty"):
        parse_triage_input(
            note="", hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
        )


def test_whitespace_only_note_raises():
    with pytest.raises(ValueError, match="empty"):
        parse_triage_input(
            note="   \n\t  ", hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
        )


def test_note_too_short_raises():
    with pytest.raises(ValueError, match="too short"):
        parse_triage_input(
            note="Hi there", hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
        )


def test_non_string_note_raises():
    with pytest.raises(ValueError, match="text string"):
        parse_triage_input(
            note=12345, hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
        )


# ── Vital range failures ──────────────────────────────────────────────────────

def test_hr_too_low_raises():
    with pytest.raises(ValueError, match="HR"):
        parse_triage_input(
            note="72F, sudden facial drooping and slurred speech.",
            hr=10, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
        )


def test_hr_too_high_raises():
    with pytest.raises(ValueError, match="HR"):
        parse_triage_input(
            note="72F, sudden facial drooping and slurred speech.",
            hr=350, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
        )


def test_sbp_too_low_raises():
    with pytest.raises(ValueError, match="SBP"):
        parse_triage_input(
            note="72F, sudden facial drooping and slurred speech.",
            hr=105, sbp=30, dbp=20, rr=22, o2=96.0, temp=36.5
        )


def test_dbp_too_high_raises():
    with pytest.raises(ValueError, match="DBP"):
        parse_triage_input(
            note="72F, sudden facial drooping and slurred speech.",
            hr=105, sbp=160, dbp=250, rr=22, o2=96.0, temp=36.5
        )


def test_rr_too_low_raises():
    with pytest.raises(ValueError, match="RR"):
        parse_triage_input(
            note="72F, sudden facial drooping and slurred speech.",
            hr=105, sbp=160, dbp=108, rr=2, o2=96.0, temp=36.5
        )


def test_o2_too_low_raises():
    with pytest.raises(ValueError, match="O2"):
        parse_triage_input(
            note="72F, sudden facial drooping and slurred speech.",
            hr=105, sbp=160, dbp=108, rr=22, o2=30.0, temp=36.5
        )


def test_temp_too_high_raises():
    with pytest.raises(ValueError, match="Temp"):
        parse_triage_input(
            note="72F, sudden facial drooping and slurred speech.",
            hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=50.0
        )


def test_temp_too_low_raises():
    with pytest.raises(ValueError, match="Temp"):
        parse_triage_input(
            note="72F, sudden facial drooping and slurred speech.",
            hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=20.0
        )


def test_unparseable_vital_raises():
    with pytest.raises(ValueError, match="HR"):
        parse_triage_input(
            note="72F, sudden facial drooping and slurred speech.",
            hr="fast", sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
        )


# ── Cross-field validation ────────────────────────────────────────────────────

def test_dbp_exceeds_sbp_raises():
    with pytest.raises(ValueError, match="DBP.*must be less than SBP"):
        parse_triage_input(
            note="72F, sudden facial drooping and slurred speech.",
            hr=105, sbp=100, dbp=120, rr=22, o2=96.0, temp=36.5
        )


def test_dbp_equals_sbp_raises():
    with pytest.raises(ValueError, match="DBP.*must be less than SBP"):
        parse_triage_input(
            note="72F, sudden facial drooping and slurred speech.",
            hr=105, sbp=120, dbp=120, rr=22, o2=96.0, temp=36.5
        )


# ── Boundary conditions ───────────────────────────────────────────────────────

def test_hr_at_lower_boundary():
    parsed = parse_triage_input(
        note="72F, sudden facial drooping and slurred speech.",
        hr=20, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
    )
    assert parsed.hr == 20


def test_hr_at_upper_boundary():
    parsed = parse_triage_input(
        note="72F, sudden facial drooping and slurred speech.",
        hr=300, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
    )
    assert parsed.hr == 300


def test_o2_at_100():
    parsed = parse_triage_input(
        note="72F, sudden facial drooping and slurred speech.",
        hr=105, sbp=160, dbp=108, rr=22, o2=100.0, temp=36.5
    )
    assert parsed.o2 == 100.0


def test_note_exactly_10_chars():
    parsed = parse_triage_input(
        note="1234567890",
        hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
    )
    assert len(parsed.note) == 10


def test_note_exactly_1000_chars_no_truncation():
    note = "a" * 1000
    parsed = parse_triage_input(
        note=note, hr=105, sbp=160, dbp=108, rr=22, o2=96.0, temp=36.5
    )
    assert len(parsed.note) == 1000
    assert not any("truncated" in w.lower() for w in parsed.warnings)


# ── Runner for non-pytest usage ───────────────────────────────────────────────

if __name__ == "__main__":
    import traceback

    tests = [
        test_clean_numeric_inputs,
        test_string_vitals_with_units,
        test_gcs_provided,
        test_gcs_empty_string_defaults,
        test_gcs_none_defaults,
        test_note_whitespace_stripped,
        test_note_internal_whitespace_collapsed,
        test_note_curly_braces_removed,
        test_note_truncated_at_1000,
        test_to_dict_keys_match_analyze_signature,
        test_hr_type_is_int,
        test_o2_type_is_float,
        test_temp_type_is_float,
        test_empty_note_raises,
        test_whitespace_only_note_raises,
        test_note_too_short_raises,
        test_non_string_note_raises,
        test_hr_too_low_raises,
        test_hr_too_high_raises,
        test_sbp_too_low_raises,
        test_dbp_too_high_raises,
        test_rr_too_low_raises,
        test_o2_too_low_raises,
        test_temp_too_high_raises,
        test_temp_too_low_raises,
        test_unparseable_vital_raises,
        test_dbp_exceeds_sbp_raises,
        test_dbp_equals_sbp_raises,
        test_hr_at_lower_boundary,
        test_hr_at_upper_boundary,
        test_o2_at_100,
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
