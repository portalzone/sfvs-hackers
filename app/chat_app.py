"""
chat_app.py — Offshore Equipment Escalation Agent  (two-panel layout)
Run from project root:
    streamlit run app/chat_app.py
"""

import sys, os, re, time
from datetime import datetime
import plotly.graph_objects as go

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
    page_title="Offshore Equipment Monitoring Agent",
    page_icon="⚓",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 1.5rem 1.5rem 0; max-width: 100% !important; }

    [data-testid="column"]:first-child {
        border-right: 1px solid #1e293b;
        padding-right: 1.5rem;
    }
    [data-testid="column"]:last-child { padding-left: 1.5rem; }

    /* ── Panel headers ── */
    .panel-header {
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 1rem; padding-bottom: 0.75rem;
        border-bottom: 1px solid #1e293b;
    }
    .panel-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem; font-weight: 600;
        letter-spacing: 0.12em; text-transform: uppercase;
        color: #94a3b8; margin: 0;
    }
    .panel-dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #06b6d4; flex-shrink: 0;
    }
    .panel-dot.red { background: #ef4444; }

    /* ── Stat cards ── */
    .stat-row {
        display: grid; grid-template-columns: repeat(3, 1fr);
        gap: 0.6rem; margin-bottom: 1.2rem;
    }
    .stat-card {
        background: #0f172a; border: 1px solid #1e293b;
        border-radius: 10px; padding: 0.7rem 0.9rem; text-align: center;
    }
    .stat-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.6rem; font-weight: 600; margin: 0; line-height: 1;
    }
    .stat-label {
        font-size: 0.68rem; text-transform: uppercase;
        letter-spacing: 0.08em; color: #64748b; margin-top: 4px;
    }
    .cyan  { color: #06b6d4; }
    .red   { color: #ef4444; }
    .amber { color: #f59e0b; }
    .green { color: #22c55e; }

    /* ── Accordion ── */
    .accordion-header {
        display: flex; justify-content: space-between; align-items: center;
        background: #0f172a; border: 1px solid #1e293b;
        border-radius: 8px; padding: 0.6rem 0.9rem;
        cursor: pointer; margin-bottom: 4px; user-select: none;
    }
    .accordion-header:hover { background: #1e293b; }
    .accordion-label {
        font-size: 0.78rem; font-weight: 600; color: #cbd5e1;
        display: flex; align-items: center; gap: 8px;
    }
    .accordion-meta { font-size: 0.68rem; color: #475569; }
    .accordion-chevron { font-size: 0.65rem; color: #475569; }

    /* ── Submission cards ── */
    .sub-card {
        background: #0f172a; border: 1px solid #1e293b;
        border-radius: 8px; padding: 0.75rem 0.9rem;
        margin-bottom: 4px;
    }
    .sub-card.escalate { border-left: 3px solid #ef4444; }
    .sub-card.routine  { border-left: 3px solid #22c55e; }

    .sub-header {
        display: flex; justify-content: space-between;
        align-items: center; margin-bottom: 0.35rem;
    }
    .sub-rank {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem; color: #475569; font-weight: 600;
    }
    .sub-time { font-size: 0.68rem; color: #475569; }
    .sub-flag {
        font-size: 0.7rem; font-weight: 600;
        padding: 2px 8px; border-radius: 999px;
    }
    .sub-flag.esc { background: #450a0a; color: #fca5a5; }
    .sub-flag.rtn { background: #052e16; color: #86efac; }
    .sub-note {
        font-size: 0.76rem; color: #94a3b8;
        line-height: 1.45; margin: 0.25rem 0 0;
    }
    .severity-badge {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.67rem; padding: 2px 7px;
        border-radius: 4px; background: #1e293b; color: #94a3b8;
    }
    .severity-badge.sev1 { background: #450a0a; color: #fca5a5; }
    .severity-badge.sev2 { background: #431407; color: #fdba74; }
    .severity-badge.sev3 { background: #422006; color: #fde68a; }
    .severity-badge.sev5 { background: #052e16; color: #86efac; }

    /* ── Analytics ── */
    .analytics-grid {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 0.5rem; margin-top: 0.5rem;
    }
    .analytics-row {
        display: flex; justify-content: space-between;
        align-items: center; padding: 0.4rem 0.6rem;
        background: #0f172a; border-radius: 6px;
        border: 1px solid #1e293b; font-size: 0.72rem;
    }
    .analytics-key { color: #64748b; }
    .analytics-val {
        font-family: 'IBM Plex Mono', monospace;
        color: #cbd5e1; font-weight: 600;
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center; padding: 3rem 1rem; color: #334155;
    }
    .empty-state p {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem; margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi, I'm the **Offshore Equipment Intelligence Agent**.\n\n"
                "Describe the log entry or anomaly and include inline metrics if available "
                "(e.g., *Pressure 172 PSI, Temp 65.0 C, Vibration 8.4 mms, Flow 49%*). "
                "I will assess the safety escalation risks and explain my reasoning."
            ),
        }
    ]

if "submissions" not in st.session_state:
    st.session_state.submissions = []

if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract(pattern, text, default):
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        try: return float(m.group(1))
        except ValueError: pass
    return default

def extract_telemetry(text):
    pressure  = _extract(r"(\d+)\s*psi", text, 0) or _extract(r"pressure[:\s]*(\d+)", text, 0)
    temp      = _extract(r"(\d+\.?\d*)\s*c\b", text, 0.0) or _extract(r"temp(?:erature)?[:\s]*(\d+\.?\d*)", text, 0.0)
    vibration = _extract(r"(\d+\.?\d*)\s*mms", text, 0.0) or _extract(r"vibration[:\s]*(\d+\.?\d*)", text, 0.0)
    flow_rate = _extract(r"(\d+)\s*%", text, 100) or _extract(r"flow(?:_rate)?[:\s]*(\d+)", text, 100)
    voltage   = _extract(r"(\d+)\s*v\b", text, 400) or _extract(r"voltage[:\s]*(\d+)", text, 400)
    rpm       = _extract(r"(\d+)\s*rpm", text, 0) or _extract(r"rpm[:\s]*(\d+)", text, 0)
    return {
        "pressure_psi":  int(pressure),
        "temp_c":        float(temp),
        "vibration_mms": float(vibration),
        "flow_rate_pct": int(flow_rate),
        "voltage_v":     int(voltage),
        "rpm":           int(rpm),
    }

# ── Key-bridging helpers (works with both old medical and new offshore response keys) ──

def _get_flag(r):
    v = r.get("safety_flag")
    if v is not None:
        return str(v)
    return "1" if r.get("escalation_flag", "").upper() == "YES" else "0"

def _get_severity(r):
    return str(r.get("severity_level") or r.get("acuity_estimate") or "5")

def _get_category(r):
    cat = r.get("category") or ""
    if cat:
        return cat.replace("_", " ")
    signals = r.get("risk_signals") or ""
    return signals if signals.upper() not in ("", "NONE") else "general anomaly"

def format_reply(result: dict) -> str:
    flag     = _get_flag(result)
    severity = _get_severity(result)
    category = _get_category(result)
    action   = result.get("recommended_action", "Continue monitoring per standard protocols.")
    reason   = result.get("reasoning") or result.get("log_entry") or ""

    if flag == "1":
        opener = (
            "🚨 **This entry has been flagged as a critical safety event.** "
            "Based on the telemetry and log description provided, immediate intervention is recommended."
        )
    else:
        opener = (
            "✅ **No immediate safety concern detected.** "
            "The metrics appear within routine operational parameters."
        )

    detail = f"The situation is assessed at **severity level {severity}**"
    if category:
        detail += f", classified as **{category}**"
    detail += "."

    parts = [opener, detail, f"**What to do next:** {action}"]
    if reason:
        parts.append(reason)
    parts.append(
        "*This is a decision support tool only. "
        "Final operational decisions rest with the platform supervisor.*"
    )
    return "\n\n".join(parts)

def severity_class(sev_str):
    s = str(sev_str)
    if "1" in s: return "sev1"
    if "2" in s: return "sev2"
    if "3" in s: return "sev3"
    return "sev5"

def operational_sort_key(sub):
    flag = 0 if _get_flag(sub["result"]) == "1" else 1
    try:    level = int(_get_severity(sub["result"]))
    except: level = 5
    return (flag, level, -sub["timestamp"])

def render_submissions_panel():
    subs    = sorted(st.session_state.submissions, key=operational_sort_key)
    total   = len(subs)
    n_flags = sum(1 for s in subs if _get_flag(s["result"]) == "1")
    n_high  = sum(1 for s in subs if _get_severity(s["result"]) in ("1", "2"))

    # ── 3-card summary row ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card">
            <p class="stat-value cyan">{total}</p>
            <p class="stat-label">Submissions</p>
        </div>
        <div class="stat-card">
            <p class="stat-value red">{n_flags}</p>
            <p class="stat-label">Warnings</p>
        </div>
        <div class="stat-card">
            <p class="stat-value amber">{n_high}</p>
            <p class="stat-label">High Warnings</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not subs:
        st.markdown("""
        <div class="empty-state">
            <span style="font-size:2rem">⚙️</span>
            <p>No operational logs analyzed yet.<br>Input a telemetry description on the right panel.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Analytics accordion ───────────────────────────────────────────────────
    from collections import Counter
    cat_counts  = Counter(_get_category(s["result"]) for s in subs)
    sev_counts  = Counter(_get_severity(s["result"]) for s in subs)
    flag_rate   = f"{(n_flags/total*100):.0f}%" if total else "0%"
    top_cat     = cat_counts.most_common(1)[0][0].title() if cat_counts else "—"
    avg_sev     = f"{sum(int(_get_severity(s['result'])) for s in subs)/total:.1f}" if total else "—"

    with st.expander("📊  Analytics", expanded=False):
        # ── Shared plot theme ─────────────────────────────────────────────────
        _BG    = "#0f172a"
        _GRID  = "#1e293b"
        _FONT  = dict(family="IBM Plex Mono, monospace", color="#94a3b8", size=10)
        _MARG  = dict(l=10, r=10, t=32, b=10)

        def _base_layout(**kw):
            return dict(paper_bgcolor=_BG, plot_bgcolor=_BG,
                        font=_FONT, margin=_MARG, **kw)

        # ── Row 1: Donut (flag split) + Severity bar ──────────────────────────
        ch1, ch2 = st.columns(2)

        with ch1:
            donut = go.Figure(go.Pie(
                labels=["Critical", "Normal"],
                values=[n_flags, max(total - n_flags, 0)],
                hole=0.62,
                marker=dict(colors=["#ef4444", "#22c55e"],
                            line=dict(color=_BG, width=2)),
                textinfo="none",
                hovertemplate="%{label}: %{value} log(s)<extra></extra>",
            ))
            donut.update_layout(
                **_base_layout(height=210, showlegend=True,
                               legend=dict(orientation="h", y=-0.08,
                                           font=dict(size=10, color="#64748b"))),
                title=dict(text="Flag Split", font=dict(size=11, color="#64748b"), x=0.5),
                annotations=[dict(text=f"<b>{flag_rate}</b><br>flagged",
                                  x=0.5, y=0.5, showarrow=False,
                                  font=dict(size=13, color="#ef4444" if n_flags else "#22c55e"))],
            )
            st.plotly_chart(donut, use_container_width=True, config={"displayModeBar": False})

        with ch2:
            _SEV_META = [
                ("1", "Critical",  "#ef4444"),
                ("2", "Urgent",    "#f97316"),
                ("3", "Elevated",  "#f59e0b"),
                ("4", "Scheduled", "#22c55e"),
                ("5", "Normal",    "#06b6d4"),
            ]
            st.markdown(
                "<p style='font-family:IBM Plex Mono,monospace;font-size:0.72rem;"
                "color:#64748b;text-transform:uppercase;letter-spacing:0.1em;"
                "margin-bottom:0.5rem;'>Severity Levels</p>",
                unsafe_allow_html=True,
            )
            for lvl, label, color in _SEV_META:
                count = sev_counts.get(lvl, 0)
                bar_w = int(count / max(total, 1) * 100)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;
                                color:{color};width:14px;font-weight:700;">
                        {lvl}
                    </div>
                    <div style="font-size:0.7rem;color:#64748b;width:68px;">{label}</div>
                    <div style="flex:1;background:#1e293b;border-radius:4px;height:8px;overflow:hidden;">
                        <div style="width:{bar_w}%;background:{color};height:100%;
                                    border-radius:4px;transition:width 0.3s;"></div>
                    </div>
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;
                                color:#94a3b8;width:20px;text-align:right;">
                        {count}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ── Row 2: Incidents by category (horizontal bar) ─────────────────────
        if cat_counts:
            cats   = [c for c, _ in cat_counts.most_common()]
            counts = [cat_counts[c] for c in cats]
            labels = [c.replace("_", " ").title() for c in cats]

            cat_bar = go.Figure(go.Bar(
                y=labels, x=counts,
                orientation="h",
                marker=dict(color="#06b6d4", opacity=0.85,
                            line=dict(color=_BG, width=1)),
                hovertemplate="%{y}: %{x} log(s)<extra></extra>",
                text=counts, textposition="outside",
                textfont=dict(size=9, color="#64748b"),
            ))
            cat_bar.update_layout(
                **_base_layout(
                    height=max(160, len(cats) * 36 + 60),
                    xaxis=dict(gridcolor=_GRID, zeroline=False,
                               dtick=1, tickformat="d"),
                    yaxis=dict(autorange="reversed", tickfont=dict(size=9)),
                ),
                title=dict(text="Incidents by Category", font=dict(size=11, color="#64748b"), x=0.5),
            )
            st.plotly_chart(cat_bar, use_container_width=True, config={"displayModeBar": False})

        # ── Row 3: Pressure vs Temperature scatter (if telemetry present) ─────
        telem_subs = [s for s in subs
                      if s.get("telemetry") and s["telemetry"].get("pressure_psi", 0) > 0]
        if len(telem_subs) >= 2:
            pressures    = [s["telemetry"]["pressure_psi"]   for s in telem_subs]
            temps        = [s["telemetry"]["temp_c"]          for s in telem_subs]
            flags_s      = [_get_flag(s["result"])            for s in telem_subs]
            dot_colors   = ["#ef4444" if f == "1" else "#22c55e" for f in flags_s]
            hover_labels = [
                f"Pressure: {p} PSI<br>Temp: {t}°C<br>{'⚠ Critical' if f == '1' else '✓ Normal'}"
                for p, t, f in zip(pressures, temps, flags_s)
            ]

            scatter = go.Figure(go.Scatter(
                x=pressures, y=temps,
                mode="markers",
                marker=dict(color=dot_colors, size=10, opacity=0.85,
                            line=dict(color=_BG, width=1)),
                hovertemplate="%{customdata}<extra></extra>",
                customdata=hover_labels,
            ))
            scatter.update_layout(
                **_base_layout(
                    height=220,
                    xaxis=dict(title="Pressure (PSI)", gridcolor=_GRID, zeroline=False),
                    yaxis=dict(title="Temp (°C)",      gridcolor=_GRID, zeroline=False),
                ),
                title=dict(text="Pressure vs Temperature  (🔴 Critical · 🟢 Normal)",
                           font=dict(size=11, color="#64748b"), x=0.5),
            )
            st.plotly_chart(scatter, use_container_width=True, config={"displayModeBar": False})

    # ── Submissions accordion list ────────────────────────────────────────────
    st.markdown("<div style='margin-top:0.5rem;'>", unsafe_allow_html=True)
    for rank, sub in enumerate(subs, 1):
        r         = sub["result"]
        flag      = _get_flag(r)
        severity  = _get_severity(r)
        category  = _get_category(r).title()
        action    = r.get("recommended_action", "")
        note_full = sub["note"]
        note_prev = note_full[:80] + "…" if len(note_full) > 80 else note_full
        ts        = datetime.fromtimestamp(sub["timestamp"]).strftime("%H:%M:%S")
        card_cls  = "escalate" if flag == "1" else "routine"
        flag_cls  = "esc" if flag == "1" else "rtn"
        flag_text = "⚠ CRITICAL" if flag == "1" else "✓ NORMAL"
        sev_cls   = severity_class(severity)

        with st.expander(
            f"{'🚨' if flag == '1' else '✅'}  #{rank} · {category} · {ts}",
            expanded=(flag == "1" and rank <= 3)   # auto-open top critical entries
        ):
            st.markdown(f"""
            <div class="sub-card {card_cls}" style="margin-bottom:0;">
                <div class="sub-header">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span class="sub-flag {flag_cls}">{flag_text}</span>
                        <span class="severity-badge {sev_cls}">Level {severity}</span>
                    </div>
                    <span class="sub-time">{ts}</span>
                </div>
                <p class="sub-note">{note_full}</p>
                {f'<p style="font-size:0.72rem;color:#64748b;margin:0.5rem 0 0;">Action: {action}</p>' if action else ''}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Clear button ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Clear tracker panel", type="secondary", use_container_width=True):
        st.session_state.submissions = []
        st.rerun()

# ── Layout ────────────────────────────────────────────────────────────────────

col_tracker, col_chat = st.columns([1, 1], gap="small")

# ── RIGHT — Chat panel ────────────────────────────────────────────────────────

with col_chat:
    st.markdown("""
    <div class="panel-header">
        <div class="panel-dot"></div>
        <p class="panel-title">Asset Telemetry Diagnostics</p>
    </div>
    """, unsafe_allow_html=True)

    chat_container = st.container(height=520, border=False)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_text = st.text_area("Input log notes or current rig metrics...", height=80, label_visibility="collapsed", key=f"input_box_{st.session_state.input_key}")
    if st.button("Analyze Log", type="primary", use_container_width=True) and user_text.strip():
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_text)
        st.session_state.messages.append({"role": "user", "content": user_text})

        with chat_container:
            with st.chat_message("assistant"):
                placeholder = st.empty()
                placeholder.markdown("_Processing telemetry metrics…_")
                try:
                    telemetry = extract_telemetry(user_text)
                    result = analyze_triage_note(
                        note=user_text,
                        hr=telemetry["pressure_psi"],
                        sbp=telemetry["voltage_v"],
                        dbp=int(telemetry["flow_rate_pct"]),
                        rr=int(telemetry["vibration_mms"]),
                        o2=telemetry["flow_rate_pct"],
                        temp=telemetry["temp_c"],
                        gcs="Not recorded"
                    )
                    reply = format_reply(result)
                    st.session_state.submissions.append({
                        "note":      user_text,
                        "telemetry": telemetry,
                        "result":    result,
                        "timestamp": time.time(),
                    })
                except Exception as exc:
                    result = {}
                    reply  = f"❌ **Error executing analysis engine:** {exc}"

                streamed = ""
                for word in reply.split(" "):
                    streamed += word + " "
                    time.sleep(0.025)
                    placeholder.markdown(streamed + "▌")
                placeholder.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.input_key += 1  # clears the text box on rerun
        st.rerun()

# ── LEFT — Tracker panel ──────────────────────────────────────────────────────

with col_tracker:
    st.markdown("""
    <div class="panel-header">
        <div class="panel-dot red"></div>
        <p class="panel-title">Active Incident Tracker</p>
    </div>
    """, unsafe_allow_html=True)

    render_submissions_panel()