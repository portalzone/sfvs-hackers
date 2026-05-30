"""
chat_app.py — NL Triage Escalation Agent
Streamlit UI for emergency nurses. Run from project root:
    streamlit run app/chat_app.py
"""

import sys
import os
import time

# Allow imports from project root (tools/, demo/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load .env from project root before importing backend tools
_env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

import streamlit as st
from tools.input_parser import parse_triage_input
from tools.escalation_tool import analyze_triage_note
from demo.sample_notes import DEMO_CASES

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="NL Triage Escalation Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ────────────────────────────────────────────────────

_DEFAULTS = {
    "note":    "",
    "hr":      "",
    "sbp":     "",
    "dbp":     "",
    "rr":      "",
    "o2":      "",
    "temp":    "",
    "gcs":     "",
    "result":  None,
    "error":   None,
    "warnings": [],
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar — branding and demo case loader ───────────────────────────────────

with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg",
        width=80,
    )
    st.markdown("## NL Triage Agent")
    st.caption("Powered by IBM watsonx.ai · llama-3-3-70b")
    st.divider()

    if not os.getenv("WATSONX_API_KEY"):
        st.warning("WATSONX_API_KEY not found — check your .env file.")

    st.markdown("### Load a demo case")
    st.caption("Pre-fills the form with a real synthetic case.")

    for i, case in enumerate(DEMO_CASES):
        flag_badge = "🔴" if case["expected_flag"] == "YES" else "🟢"
        if st.button(
            f"{flag_badge} {case['label']}",
            key=f"demo_{i}",
            use_container_width=True,
        ):
            st.session_state.note  = case["note"]
            st.session_state.hr    = str(case["hr"])
            st.session_state.sbp   = str(case["sbp"])
            st.session_state.dbp   = str(case["dbp"])
            st.session_state.rr    = str(case["rr"])
            st.session_state.o2    = str(case["o2"])
            st.session_state.temp  = str(case["temp"])
            st.session_state.gcs   = ""
            st.session_state.result  = None
            st.session_state.error   = None
            st.session_state.warnings = []
            st.rerun()

    st.divider()
    st.markdown(
        "**Eastern Health** operates 4 acute care sites in NL. "
        "Rural ambulance response times exceed 30 min. "
        "This agent supports triage nurses working without immediate physician backup."
    )

# ── Main layout: form (left) | results (right) ────────────────────────────────

st.markdown("# 🏥 NL Triage Escalation Agent")
st.caption(
    "Enter a triage note and patient vitals, then click **Analyze**. "
    "The agent flags escalation risk and recommends an immediate action."
)
st.divider()

col_form, col_results = st.columns([1.1, 1], gap="large")

# ── LEFT COLUMN: input form ───────────────────────────────────────────────────

with col_form:
    st.markdown("### Patient Presentation")

    note_val = st.text_area(
        "Triage note",
        value=st.session_state.note,
        height=160,
        placeholder=(
            "e.g. 72F, sudden onset facial drooping left side, slurred speech x1hr. "
            "Wife states arm weakness at home. Last known well 1hr ago."
        ),
        key="note_input",
    )

    st.markdown("### Vital Signs")

    v_col1, v_col2, v_col3 = st.columns(3)

    with v_col1:
        hr_val   = st.text_input("HR (bpm)",    value=st.session_state.hr,   placeholder="e.g. 105", key="hr_input")
        sbp_val  = st.text_input("SBP (mmHg)",  value=st.session_state.sbp,  placeholder="e.g. 160", key="sbp_input")

    with v_col2:
        dbp_val  = st.text_input("DBP (mmHg)",  value=st.session_state.dbp,  placeholder="e.g. 108", key="dbp_input")
        rr_val   = st.text_input("RR (br/min)", value=st.session_state.rr,   placeholder="e.g. 22",  key="rr_input")

    with v_col3:
        o2_val   = st.text_input("O2 Sat (%)",  value=st.session_state.o2,   placeholder="e.g. 96",  key="o2_input")
        temp_val = st.text_input("Temp (°C)",   value=st.session_state.temp, placeholder="e.g. 36.5",key="temp_input")

    gcs_val = st.text_input(
        "GCS (optional)",
        value=st.session_state.gcs,
        placeholder="e.g. E4V5M6  — leave blank if not recorded",
        key="gcs_input",
    )

    btn_col, clear_col = st.columns([2, 1])
    analyze_clicked = btn_col.button("🔍 Analyze", type="primary", use_container_width=True)
    clear_clicked   = clear_col.button("🗑 Clear",  use_container_width=True)

    if clear_clicked:
        for k in ("note", "hr", "sbp", "dbp", "rr", "o2", "temp", "gcs",
                  "result", "error", "warnings"):
            st.session_state[k] = _DEFAULTS[k]
        st.rerun()

    if analyze_clicked:
        # Persist current field values so they survive the rerun
        st.session_state.note = note_val
        st.session_state.hr   = hr_val
        st.session_state.sbp  = sbp_val
        st.session_state.dbp  = dbp_val
        st.session_state.rr   = rr_val
        st.session_state.o2   = o2_val
        st.session_state.temp = temp_val
        st.session_state.gcs  = gcs_val
        st.session_state.result  = None
        st.session_state.error   = None
        st.session_state.warnings = []

        with st.spinner("Analyzing with watsonx.ai…"):
            try:
                parsed = parse_triage_input(
                    note=note_val,
                    hr=hr_val,
                    sbp=sbp_val,
                    dbp=dbp_val,
                    rr=rr_val,
                    o2=o2_val,
                    temp=temp_val,
                    gcs=gcs_val if gcs_val.strip() else None,
                )
                st.session_state.warnings = parsed.warnings

                result = analyze_triage_note(**parsed.to_dict())
                st.session_state.result = result

            except ValueError as exc:
                st.session_state.error = str(exc)
            except Exception as exc:
                st.session_state.error = f"Backend error: {exc}"

        st.rerun()

# ── RIGHT COLUMN: results display ────────────────────────────────────────────

with col_results:
    st.markdown("### Analysis Result")

    # Validation warnings (non-fatal)
    if st.session_state.warnings:
        for w in st.session_state.warnings:
            st.warning(w)

    # Fatal validation error
    if st.session_state.error:
        st.error(f"**Input Error:** {st.session_state.error}")
        st.stop()

    result = st.session_state.result

    if result is None:
        st.info(
            "Fill in the triage note and vitals on the left, then click **Analyze**.\n\n"
            "Use the sidebar to load one of the 7 demo cases instantly."
        )
    else:
        flag = result.get("escalation_flag", "UNKNOWN")
        acuity = result.get("acuity_estimate", "N/A")
        signals = result.get("risk_signals", "None flagged")
        action  = result.get("recommended_action", "Follow standard protocols.")
        reasoning = result.get("reasoning", "No breakdown provided.")

        # ── Escalation verdict banner ─────────────────────────────────────────
        if flag == "YES":
            st.markdown(
                """
                <div style="background:#b91c1c;color:#fff;padding:18px 24px;
                            border-radius:10px;margin-bottom:16px;">
                  <span style="font-size:2rem;">🚨</span>
                  <span style="font-size:1.5rem;font-weight:700;margin-left:10px;">
                    ESCALATE — Immediate Physician Review Required
                  </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="background:#15803d;color:#fff;padding:18px 24px;
                            border-radius:10px;margin-bottom:16px;">
                  <span style="font-size:2rem;">✅</span>
                  <span style="font-size:1.5rem;font-weight:700;margin-left:10px;">
                    ROUTINE — Standard Triage Pathway
                  </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── CTAS badge ────────────────────────────────────────────────────────
        ctas_colors = {
            "CTAS 1": "#7f1d1d",
            "CTAS 2": "#9a3412",
            "CTAS 3": "#854d0e",
            "CTAS 4": "#166534",
            "CTAS 5": "#1e3a5f",
        }
        ctas_key = acuity.strip().upper() if acuity else ""
        ctas_bg  = ctas_colors.get(ctas_key, "#374151")

        st.markdown(
            f"""
            <div style="display:inline-block;background:{ctas_bg};color:#fff;
                        padding:6px 18px;border-radius:20px;font-weight:600;
                        font-size:1.1rem;margin-bottom:16px;">
              Estimated Acuity: {acuity}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Risk signals ──────────────────────────────────────────────────────
        st.markdown("#### ⚠ Risk Signals")
        if signals and signals.upper() != "NONE":
            for sig in signals.split(","):
                sig = sig.strip()
                if sig:
                    st.markdown(f"- {sig}")
        else:
            st.markdown("*No specific risk signals identified.*")

        # ── Recommended action ────────────────────────────────────────────────
        st.markdown("#### 📋 Recommended Action")
        st.info(action)

        # ── Clinical reasoning ────────────────────────────────────────────────
        st.markdown("#### 🧠 Clinical Reasoning")
        st.markdown(reasoning)

        st.divider()
        with st.expander("Raw model response"):
            st.code(result.get("raw_response", ""), language=None)
