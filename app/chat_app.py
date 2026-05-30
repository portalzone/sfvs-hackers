"""
chat_app.py — NL Triage Escalation Agent  (two-panel layout)
Run from project root:
    streamlit run app/chat_app.py
"""

import sys, os, re, time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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
    page_title="NL Triage Agent",
    page_icon="🏥",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 1.5rem 1.5rem 0; max-width: 100% !important; }

    /* ── Divider between columns ── */
    [data-testid="column"]:first-child {
        border-right: 1px solid #1e293b;
        padding-right: 1.5rem;
    }
    [data-testid="column"]:last-child {
        padding-left: 1.5rem;
    }
    /* ── Fix chat column height so input stays pinned ── */
    [data-testid="column"]:first-child [data-testid="stVerticalBlock"] {
        height: calc(100vh - 8rem);
        display: flex;
        flex-direction: column;
    }

    /* Chat history scrolls, input stays at bottom */
    [data-testid="column"]:first-child [data-testid="stChatMessageContainer"] {
        flex: 1;
        overflow-y: auto;
    }

    /* ── Panel headers ── */
    .panel-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #1e293b;
    }
    .panel-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #94a3b8;
        margin: 0;
    }
    .panel-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #06b6d4;
        flex-shrink: 0;
    }
    .panel-dot.red { background: #ef4444; }

    /* ── Stat cards ── */
    .stat-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.6rem;
        margin-bottom: 1.2rem;
    }
    .stat-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 0.7rem 0.9rem;
        text-align: center;
    }
    .stat-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.6rem;
        font-weight: 600;
        margin: 0;
        line-height: 1;
    }
    .stat-label {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        margin-top: 4px;
    }
    .cyan   { color: #06b6d4; }
    .red    { color: #ef4444; }
    .amber  { color: #f59e0b; }
    .green  { color: #22c55e; }
    .slate  { color: #94a3b8; }

    /* ── Submission cards ── */
    .sub-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.5rem;
        position: relative;
        transition: border-color 0.2s;
    }
    .sub-card.escalate { border-left: 3px solid #ef4444; }
    .sub-card.routine  { border-left: 3px solid #22c55e; }

    .sub-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.4rem;
    }
    .sub-rank {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        color: #475569;
        font-weight: 600;
    }
    .sub-time {
        font-size: 0.68rem;
        color: #475569;
    }
    .sub-flag {
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 999px;
    }
    .sub-flag.esc  { background: #450a0a; color: #fca5a5; }
    .sub-flag.rtn  { background: #052e16; color: #86efac; }
    .sub-note {
        font-size: 0.78rem;
        color: #94a3b8;
        line-height: 1.45;
        margin: 0.3rem 0;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .sub-signals {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        margin-top: 0.4rem;
    }
    .signal-tag {
        font-size: 0.65rem;
        background: #1e293b;
        color: #94a3b8;
        border-radius: 4px;
        padding: 1px 6px;
    }
    .signal-tag.hot {
        background: #431407;
        color: #fdba74;
    }
    .acuity-badge {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        padding: 2px 7px;
        border-radius: 4px;
        background: #1e293b;
        color: #94a3b8;
    }
    .acuity-badge.ctas1 { background: #450a0a; color: #fca5a5; }
    .acuity-badge.ctas2 { background: #431407; color: #fdba74; }
    .acuity-badge.ctas3 { background: #422006; color: #fde68a; }
    .acuity-badge.ctas5 { background: #052e16; color: #86efac; }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #334155;
    }
    .empty-state p {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi, I'm the **NL Triage Agent** — powered by IBM Granite.\n\n"
                "Describe the patient and include vitals inline if available "
                "(e.g. *HR 105, BP 160/108, RR 22, O2 96%, Temp 36.5°C*). "
                "I'll assess escalation risk and explain my reasoning."
            ),
        }
    ]

if "submissions" not in st.session_state:
    st.session_state.submissions = []   # list of dicts, newest first

# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract(pattern, text, default):
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        try: return float(m.group(1))
        except ValueError: pass
    return default

def extract_vitals(text):
    hr   = _extract(r"\bhr[:\s]*(\d+)", text, None) or _extract(r"(\d+)\s*bpm", text, 80)
    bp   = re.search(r"\bbp[:\s]*(\d{2,3})[/\\](\d{2,3})", text, re.IGNORECASE)
    sbp  = float(bp.group(1)) if bp else 120.0
    dbp  = float(bp.group(2)) if bp else 80.0
    rr   = _extract(r"\brr[:\s]*(\d+)", text, None) or _extract(r"resp(?:iratory)?\s*rate[:\s]*(\d+)", text, 16)
    o2   = _extract(r"\bo2[:\s]*(\d+\.?\d*)\s*%?", text, None) or _extract(r"spo2[:\s]*(\d+\.?\d*)", text, None) or _extract(r"sat(?:uration)?[:\s]*(\d+\.?\d*)", text, 98)
    temp = _extract(r"temp(?:erature)?[:\s]*(\d+\.?\d*)", text, 36.8)
    gcs  = None
    gm   = re.search(r"\bgcs[:\s]*([EeVvMm\d\+]+)", text, re.IGNORECASE)
    if gm: gcs = gm.group(1).strip()
    return {"hr": int(hr), "sbp": int(sbp), "dbp": int(dbp), "rr": int(rr), "o2": float(o2), "temp": float(temp), "gcs": gcs or "Not recorded"}

def format_reply(result):
    flag   = result.get("escalation_flag", "UNKNOWN")
    acuity = result.get("acuity_estimate", "N/A")
    signals= result.get("risk_signals", "None")
    action = result.get("recommended_action", "Follow standard protocols.")
    reason = result.get("reasoning", "")
    verdict = "🚨 **ESCALATE** — Immediate physician review required" if flag == "YES" else "✅ **ROUTINE** — Standard triage pathway"
    lines = [verdict, "", f"**Acuity:** {acuity}", f"**Risk signals:** {signals}", "", f"**Action:** {action}"]
    if reason: lines += ["", f"*{reason}*"]
    return "\n".join(lines)

def acuity_class(acuity_str):
    a = acuity_str.upper()
    if "1" in a: return "ctas1"
    if "2" in a: return "ctas2"
    if "3" in a: return "ctas3"
    return "ctas5"

def escalation_sort_key(sub):
    """Sort: escalations first, then by CTAS acuity level, then by time (newest)."""
    flag  = 0 if sub["result"].get("escalation_flag") == "YES" else 1
    acuity_str = sub["result"].get("acuity_estimate", "5")
    try:    level = int(re.search(r"\d", acuity_str).group())
    except: level = 5
    return (flag, level, -sub["timestamp"])

def render_submissions_panel():
    subs = sorted(st.session_state.submissions, key=escalation_sort_key)
    total   = len(subs)
    n_esc   = sum(1 for s in subs if s["result"].get("escalation_flag") == "YES")
    n_ctas1 = sum(1 for s in subs if "1" in s["result"].get("acuity_estimate",""))
    n_ctas2 = sum(1 for s in subs if "2" in s["result"].get("acuity_estimate",""))

    # Stat cards
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card">
            <p class="stat-value cyan">{total}</p>
            <p class="stat-label">Submitted</p>
        </div>
        <div class="stat-card">
            <p class="stat-value red">{n_esc}</p>
            <p class="stat-label">Escalations</p>
        </div>
        <div class="stat-card">
            <p class="stat-value amber">{n_ctas1}</p>
            <p class="stat-label">CTAS 1</p>
        </div>
        <div class="stat-card">
            <p class="stat-value amber">{n_ctas2}</p>
            <p class="stat-label">CTAS 2</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not subs:
        st.markdown("""
        <div class="empty-state">
            <span style="font-size:2rem">📋</span>
            <p>No cases submitted yet.<br>Describe a patient in the chat.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Submission cards ranked by priority
    for rank, sub in enumerate(subs, 1):
        r       = sub["result"]
        flag    = r.get("escalation_flag", "?")
        acuity  = r.get("acuity_estimate", "N/A")
        signals = [s.strip() for s in r.get("risk_signals", "").split(",") if s.strip()]
        action  = r.get("recommended_action", "")
        note_preview = sub["note"][:140] + "…" if len(sub["note"]) > 140 else sub["note"]
        ts      = datetime.fromtimestamp(sub["timestamp"]).strftime("%H:%M:%S")
        card_cls  = "escalate" if flag == "YES" else "routine"
        flag_cls  = "esc" if flag == "YES" else "rtn"
        flag_text = "⚠ ESCALATE" if flag == "YES" else "✓ ROUTINE"
        ac_cls    = acuity_class(acuity)

        # Highlight first 2 signals as "hot" if escalation
        signal_html = ""
        for i, sig in enumerate(signals[:6]):
            hot = "hot" if (flag == "YES" and i < 2) else ""
            signal_html += f'<span class="signal-tag {hot}">{sig}</span>'

        st.markdown(f"""
        <div class="sub-card {card_cls}">
            <div class="sub-header">
                <div style="display:flex;align-items:center;gap:8px;">
                <span class="sub-rank">#{rank}</span>
                <span class="sub-flag {flag_cls}">{flag_text}</span>
                <span class="acuity-badge {ac_cls}">{acuity}</span>
                </div>
                <span class="sub-time">{ts}</span>
            </div>
            <p class="sub-note">{note_preview}</p>
            {f'<p style="font-size:0.72rem;color:#64748b;margin:0.3rem 0 0.2rem;">Action: {action}</p>' if action else ''}
            <div class="sub-signals">{signal_html}</div>
        </div>
        """, unsafe_allow_html=True)

    # Clear button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Clear all submissions", type="secondary", use_container_width=True):
        st.session_state.submissions = []
        st.rerun()

# ── Layout ────────────────────────────────────────────────────────────────────

col_tracker, col_chat = st.columns([1, 1], gap="small")

# ── RIGHT — Chat panel ─────────────────────────────────────────────────────────

with col_chat:
    st.markdown("""
    <div class="panel-header">
        <div class="panel-dot"></div>
        <p class="panel-title">Triage Chat</p>
    </div>
    """, unsafe_allow_html=True)

    chat_container = st.container(height=520, border=False)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_text = st.text_area("Describe the patient…", height=80, label_visibility="collapsed", key="input_box")
    if st.button("Analyze", type="primary", use_container_width=True) and user_text.strip():
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_text)
        st.session_state.messages.append({"role": "user", "content": user_text})

        with chat_container:
            with st.chat_message("assistant"):
                placeholder = st.empty()
                placeholder.markdown("_Analyzing…_")
                try:
                    vitals = extract_vitals(user_text)
                    result = analyze_triage_note(note=user_text, **vitals)
                    reply  = format_reply(result)

                    st.session_state.submissions.append({
                        "note":      user_text,
                        "vitals":    vitals,
                        "result":    result,
                        "timestamp": time.time(),
                    })

                except Exception as exc:
                    result = {}
                    reply  = f"❌ **Error:** {exc}"

                streamed = ""
                for word in reply.split(" "):
                    streamed += word + " "
                    time.sleep(0.025)
                    placeholder.markdown(streamed + "▌")
                placeholder.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# ── LEFT — Submission tracker panel ─────────────────────────────────────────

with col_tracker:
    st.markdown("""
    <div class="panel-header">
        <div class="panel-dot red"></div>
        <p class="panel-title">Submission Tracker</p>
    </div>
    """, unsafe_allow_html=True)

    render_submissions_panel()