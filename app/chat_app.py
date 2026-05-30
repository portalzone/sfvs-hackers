"""
chat_app.py — NL Triage Escalation Agent
Minimalistic chatbot UI. Run from project root:
    streamlit run app/chat_app.py
"""

import sys
import os
import re
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load .env before importing backend
_env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

import streamlit as st
from tools.escalation_tool import analyze_triage_note

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Triage Agent",
    page_icon="🏥",
    layout="centered",
)

# ── Minimal CSS — hide Streamlit chrome, style chat ──────────────────────────

st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 2rem; padding-bottom: 0; max-width: 720px; }
  .stChatMessage { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi, I'm the NL Triage Agent.\n\n"
                "Describe the patient — include vitals inline if you have them "
                "(e.g. *HR 105, BP 160/108, RR 22, O2 96%, Temp 36.5°C*) "
                "or just paste the triage note and I'll do my best with what's there."
            ),
        }
    ]

# ── Vital extractor — pulls numbers from free text ────────────────────────────

def _extract(pattern: str, text: str, default):
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return default

def extract_vitals(text: str) -> dict:
    hr   = _extract(r"\bhr[:\s]*(\d+)", text, None) or \
           _extract(r"(\d+)\s*bpm", text, 80)
    bp   = re.search(r"\bbp[:\s]*(\d{2,3})[/\\](\d{2,3})", text, re.IGNORECASE)
    sbp  = float(bp.group(1)) if bp else 120.0
    dbp  = float(bp.group(2)) if bp else 80.0
    rr   = _extract(r"\brr[:\s]*(\d+)", text, None) or \
           _extract(r"resp(?:iratory)?\s*rate[:\s]*(\d+)", text, 16)
    o2   = _extract(r"\bo2[:\s]*(\d+\.?\d*)\s*%?", text, None) or \
           _extract(r"spo2[:\s]*(\d+\.?\d*)", text, None) or \
           _extract(r"sat(?:uration)?[:\s]*(\d+\.?\d*)", text, 98)
    temp = _extract(r"temp(?:erature)?[:\s]*(\d+\.?\d*)", text, 36.8)
    gcs  = None
    gm   = re.search(r"\bgcs[:\s]*([EeVvMm\d\+]+)", text, re.IGNORECASE)
    if gm:
        gcs = gm.group(1).strip()

    return {
        "hr":   int(hr),
        "sbp":  int(sbp),
        "dbp":  int(dbp),
        "rr":   int(rr),
        "o2":   float(o2),
        "temp": float(temp),
        "gcs":  gcs or "Not recorded",
    }

# ── Format the structured result as a clean markdown reply ────────────────────

def format_reply(result: dict) -> str:
    flag     = result.get("escalation_flag", "UNKNOWN")
    acuity   = result.get("acuity_estimate", "N/A")
    signals  = result.get("risk_signals", "None")
    action   = result.get("recommended_action", "Follow standard protocols.")
    reason   = result.get("reasoning", "")

    if flag == "YES":
        verdict = "🚨 **ESCALATE** — Immediate physician review required"
    else:
        verdict = "✅ **ROUTINE** — Standard triage pathway"

    lines = [
        verdict,
        "",
        f"**Acuity:** {acuity}",
        f"**Risk signals:** {signals}",
        "",
        f"**Action:** {action}",
    ]
    if reason:
        lines += ["", f"*{reason}*"]

    return "\n".join(lines)

# ── Render chat history ───────────────────────────────────────────────────────

st.markdown("### 🏥 NL Triage Agent")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Accept new input ──────────────────────────────────────────────────────────

if user_text := st.chat_input("Describe the patient…"):
    # Show user bubble
    with st.chat_message("user"):
        st.markdown(user_text)
    st.session_state.messages.append({"role": "user", "content": user_text})

    # Generate response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("_Analyzing…_")

        try:
            vitals = extract_vitals(user_text)
            result = analyze_triage_note(note=user_text, **vitals)
            reply  = format_reply(result)
        except Exception as exc:
            reply = f"❌ **Error:** {exc}"

        # Stream reply word by word
        streamed = ""
        for word in reply.split(" "):
            streamed += word + " "
            time.sleep(0.03)
            placeholder.markdown(streamed + "▌")
        placeholder.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
