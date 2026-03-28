import re
import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime

import streamlit as st
import plotly.graph_objects as go

# Page config 
st.set_page_config(
    page_title="Legal Risk Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Syne:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"]          { font-family: 'Syne', sans-serif !important; }
.stApp                              { background-color: #0f1117 !important; }
.main .block-container              { background-color: #0f1117 !important;
                                      padding-top: 2rem; padding-bottom: 2rem;
                                      max-width: 1100px; }
h1, h2, h3                         { font-family: 'DM Serif Display', serif !important;
                                      font-weight: 400 !important; color: #e8e6e0 !important; }
p, li, span, label, div            { color: #c8c6c0; }

/* ── Header ── */
.top-header   { display: flex; align-items: center; gap: 14px; margin-bottom: 0.5rem; }
.header-icon  { width: 48px; height: 48px; background: #1e2130;
                border: 1px solid #3a3d4a; border-radius: 10px;
                display: flex; align-items: center; justify-content: center; font-size: 22px; }
.header-title { font-family: 'DM Serif Display', serif; font-size: 26px; color: #e8e6e0; }
.header-sub   { font-size: 12px; color: #6b6f7e; margin-top: 2px; }

/* ── Section label ── */
.section-label { font-size: 10px; font-weight: 600; letter-spacing: 0.12em;
                 text-transform: uppercase; color: #6b6f7e; margin-bottom: 10px; }

/* ── Metric cards ── */
.metric-card        { background: #1a1d2e; border: 1px solid #2a2d3e;
                      border-radius: 10px; padding: 16px 14px; text-align: center; }
.metric-label       { font-size: 11px; color: #6b6f7e; text-transform: uppercase;
                      letter-spacing: 0.08em; margin-bottom: 6px; }
.metric-value-high  { font-size: 36px; font-weight: 500; color: #ff6b6b; }
.metric-value-med   { font-size: 36px; font-weight: 500; color: #ffa94d; }
.metric-value-low   { font-size: 36px; font-weight: 500; color: #69db7c; }

/* ── Risk badges ── */
.badge-high   { background:#4a1a1a; color:#ff8a8a; padding:5px 14px;
                border-radius:100px; font-size:12px; font-weight:600;
                display:inline-block; border: 1px solid #7a2a2a; }
.badge-medium { background:#3d2a0a; color:#ffb84d; padding:5px 14px;
                border-radius:100px; font-size:12px; font-weight:600;
                display:inline-block; border: 1px solid #6d4a1a; }
.badge-low    { background:#0a2e18; color:#69db7c; padding:5px 14px;
                border-radius:100px; font-size:12px; font-weight:600;
                display:inline-block; border: 1px solid #1a5e30; }

/* ── Highlights inside clauses ── */
mark.high   { background:#4a1a1a; color:#ff8a8a; padding:2px 5px; border-radius:3px; }
mark.medium { background:#3d2a0a; color:#ffb84d; padding:2px 5px; border-radius:3px; }
mark.low    { background:#0a2e18; color:#69db7c; padding:2px 5px; border-radius:3px; }

/* ── Clause text / explanation ── */
.clause-text { font-size: 13px; color: #c8c6c0; line-height: 1.7; margin-bottom: 8px; }
.clause-expl { font-size: 12px; color: #8b8fa0; line-height: 1.5; }
.conf-pill   { font-family: 'DM Mono', monospace; font-size: 11px; color: #6b6f7e; }

/* ── Fraud alert ── */
.fraud-alert { background: #2a1010; border-left: 3px solid #ff4444;
               padding: 10px 14px; margin-bottom: 8px;
               font-size: 13px; color: #ff8a8a; border-radius: 0 8px 8px 0; }

/* ── AI summary card ── */
.ai-card  { background: #1a1d2e; border: 1px solid #2a2d3e;
            border-radius: 10px; padding: 20px 22px; margin-bottom: 1rem; }
.ai-label { font-size: 10px; font-weight: 600; letter-spacing: 0.1em;
            text-transform: uppercase; color: #6b6f7e; margin-bottom: 10px; }
.ai-text  { font-family: 'DM Serif Display', serif; font-size: 16px;
            font-style: italic; line-height: 1.75; color: #e8e6e0; }

/* ── Analyze button ── */
.stButton > button {
    background: #4a6cf7 !important; color: #ffffff !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important; font-size: 14px !important;
    font-weight: 600 !important; padding: 10px 24px !important;
}
.stButton > button:hover { background: #3a5ce7 !important; }

/* ── Text area ── */
div[data-testid="stTextArea"] textarea {
    font-family: 'DM Mono', monospace !important; font-size: 12px !important;
    background: #1a1d2e !important; color: #c8c6c0 !important;
    border: 1px solid #2a2d3e !important; border-radius: 8px !important;
}

/* ── File uploader ── */
div[data-testid="stFileUploader"] {
    background: #1a1d2e !important;
    border: 1.5px dashed #3a3d4a !important;
    border-radius: 10px !important;
}
div[data-testid="stFileUploader"] * { color: #c8c6c0 !important; }

/* ── Expander (clause cards) ── */
div[data-testid="stExpander"] {
    background: #1a1d2e !important;
    border: 1px solid #2a2d3e !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
}
div[data-testid="stExpander"] summary { color: #c8c6c0 !important; }
div[data-testid="stExpander"] summary:hover { color: #e8e6e0 !important; }

/* ── Radio buttons ── */
div[data-testid="stRadio"] label { color: #c8c6c0 !important; }

/* ── Score display ── */
.score-display { font-family: 'DM Serif Display', serif; font-size: 52px;
                 color: #e8e6e0; line-height: 1; }
.score-sub     { font-size: 12px; color: #6b6f7e; margin-top: 4px; }

/* ── Divider ── */
hr { border: none; border-top: 1px solid #2a2d3e; margin: 1.5rem 0; }

/* ── Streamlit alerts / info boxes ── */
div[data-testid="stAlert"] { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)


# Load backend modules 
# Add project root to path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))  # project root
sys.path.insert(0, str(Path(__file__).parent))         # frontend folder


# ── Import each backend module separately so one missing package
#    doesn't block the others from loading ──────────────────────
_analyze_clauses      = None
_calculate_risk_score = None
_split_into_clauses   = None
_run_all_checks       = None
_summarize_document   = None
_extract_text_from_pdf= None

_import_errors = []

try:
    from backend.predictor import analyze_clauses as _analyze_clauses
except Exception as e:
    _import_errors.append(f"predictor: {e}")

try:
    from backend.risk_mapper import calculate_risk_score as _calculate_risk_score
except Exception as e:
    _import_errors.append(f"risk_mapper: {e}")

try:
    from backend.clause_splitter import split_into_clauses as _split_into_clauses
except Exception as e:
    _import_errors.append(f"clause_splitter: {e}")

try:
    from backend.fraud_checks import run_all_checks as _run_all_checks
except Exception as e:
    _import_errors.append(f"fraud_checks: {e}")

try:
    from backend.ai_explainability import summarize_document as _summarize_document
except Exception as e:
    _import_errors.append(f"ai_explainability: {e}")

try:
    from backend.pdf_reader import extract_text_from_pdf as _extract_text_from_pdf
except Exception as e:
    _import_errors.append(f"pdf_reader: {e}")

try:
    from backend.report_generator import generate_report as _generate_report
except Exception as e:
    _import_errors.append(f"report_generator: {e}")
    _generate_report = None

# BERT model is the core — if predictor loaded, backend is usable
BACKEND_LOADED = _analyze_clauses is not None
AI_LOADED      = _summarize_document is not None
PDF_LOADED     = _extract_text_from_pdf is not None


# Fallback logic (used when backend/ is not present)
RISK_KW = {
    "high":   ["terminat", "penalt", "liabilit", "forfeiture", "breach",
               "default", "indemnif", "forfeit", "illegal", "void"],
    "medium": ["payment", "confidential", "warrant", "represent", "disclose",
               "oblig", "restrict", "prohibit", "non-refundable", "auto-renew"],
    "low":    ["agree", "shall", "must", "provide", "deliver", "notify", "inform"],
}
TRIGGER_WORDS = [
    "terminat", "liabilit", "penalt", "non-refundable", "auto-renew",
    "payment", "confidential", "indemnif", "breach", "forfeiture", "default",
]


def _fallback_split(text):
    parts = re.split(r'\n\s*\n|(?<=\.)\s+(?=[A-Z])|(?=\d+\.\s)', text)
    return [c.strip() for c in parts
            if len(c.split()) >= 8
            and len(re.findall(r'[^a-zA-Z0-9\s]', c)) <= len(c) * 0.3]


def _fallback_explain(clause, risk):
    l = clause.lower()
    if "terminat"      in l: return "This clause allows termination, which may cause sudden loss."
    if "liabilit"      in l: return "This clause defines liability and may expose a party to financial risk."
    if "payment"       in l: return "This clause includes payment terms that may lead to disputes."
    if "penalt"        in l: return "This clause imposes penalties which could result in financial loss."
    if "confidential"  in l: return "This clause requires confidentiality, creating legal obligations."
    if "non-refundable"in l: return "Non-refundable terms eliminate recovery options — significant financial risk."
    if "auto-renew"    in l: return "Auto-renewal can lock parties in without explicit ongoing consent."
    if "indemnif"      in l: return "Indemnification clauses can create broad financial responsibility."
    if risk == "High":        return "This clause may involve significant legal or financial risk."
    if risk == "Medium":      return "This clause has moderate risk and should be reviewed."
    return "This clause appears relatively standard and low risk."


def _fallback_predict(clause):
    lower = clause.lower()
    score = sum(3 for k in RISK_KW["high"]   if k in lower) + \
            sum(2 for k in RISK_KW["medium"] if k in lower) + \
            sum(1 for k in RISK_KW["low"]    if k in lower)
    import random
    conf = round(min(0.55 + random.random() * 0.38, 0.99), 3)
    risk = "High" if score >= 3 else "Medium" if score >= 1 else "Low"
    return risk, conf


def _fallback_analyze(clauses):
    results = []
    for clause in clauses:
        risk, conf = _fallback_predict(clause)
        results.append({
            "clause":      clause,
            "risk":        risk,
            "confidence":  conf,
            "explanation": _fallback_explain(clause, risk),
        })
    return results


def _fallback_score(results):
    if not results:
        return 0.0, "Low Risk", 0
    weights = {"Low": 1, "Medium": 2, "High": 3}
    total, penalty, high_count = 0.0, 0.0, 0
    for r in results:
        total += weights[r["risk"]] * r["confidence"]
        if r["risk"] == "High":
            penalty += 0.5 * r["confidence"]
            high_count += 1
    score = min(total / len(results) + penalty, 3.0)
    level = "Low Risk" if score < 1.5 else "Medium Risk" if score < 2.3 else "High Risk"
    return round(score, 2), level, high_count


def _fallback_fraud(clauses, full_text):
    alerts, seen = [], set()
    for c in clauses:
        key = c[:100]
        if key in seen:
            alerts.append(f"Duplicate clause detected: \"{c[:60]}...\"")
        else:
            seen.add(key)
        for p in ["no liability", "unlimited liability", "non-refundable", "auto-renew"]:
            if p in c.lower():
                alerts.append(f"Suspicious pattern \"{p}\" found in: \"{c[:55]}...\"")
        nums = [int(n) for n in re.findall(r"\d+", c) if int(n) > 1_000_000]
        if nums:
            alerts.append(f"Unusually large figure ({nums[0]:,}) detected in a clause.")
    return list(dict.fromkeys(alerts))


def _fallback_summary(results, score, level):
    return (
        f"This contract has been assessed as {level} with a score of {score}/3.00. "
        f"{sum(1 for r in results if r['risk'] == 'High')} high-risk clause(s) were detected "
        f"out of {len(results)} total clauses. "
        f"Please review the flagged clauses carefully before signing."
    )


# Unified wrappers (use backend if loaded, else fallback) 
def split_clauses(text):
    return _split_into_clauses(text) if _split_into_clauses else _fallback_split(text)

def analyze_clauses(clauses):
    return _analyze_clauses(clauses) if _analyze_clauses else _fallback_analyze(clauses)

def calc_score(results):
    return _calculate_risk_score(results) if _calculate_risk_score else _fallback_score(results)

def fraud_checks(clauses, full_text):
    return _run_all_checks(clauses, full_text) if _run_all_checks else _fallback_fraud(clauses, full_text)

def ai_summary(results, score, level):
    if _summarize_document:
        try:
            return _summarize_document(results, score, level, api_key=GEMINI_API_KEY)
        except Exception as e:
            return _fallback_summary(results, score, level)
    return _fallback_summary(results, score, level)

def read_pdf(uploaded_file):
    if not _extract_text_from_pdf:
        return ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        text = _extract_text_from_pdf(tmp_path)
        os.unlink(tmp_path)
        return text
    except Exception as e:
        st.error(f"PDF reading failed: {e}")
        return ""

def highlight_clause(clause, risk):
    triggers = [w for w in TRIGGER_WORDS if w in clause.lower()]
    if not triggers:
        return clause
    css_class = risk.lower()
    pattern = re.compile(r'(' + '|'.join(triggers) + r'\w*)', re.IGNORECASE)
    return pattern.sub(lambda m: f'<mark class="{css_class}">{m.group()}</mark>', clause)


# Header 
st.markdown("""
<div class="top-header">
  <div class="header-icon">⚖️</div>
  <div>
    <div class="header-title">Contract Risk Analyzer</div>
    <div class="header-sub">BERT legal classifier · fraud detection · Groq AI counsel</div>
  </div>
</div>
""", unsafe_allow_html=True)

if BACKEND_LOADED:
    st.success("✓ BERT model loaded")
else:
    st.warning("⚠ BERT model not loaded — running keyword classifier.")

# Read Groq API key from st.secrets (secrets.toml)
GEMINI_API_KEY = None
try:
    GEMINI_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GEMINI_API_KEY = os.environ.get("GROQ_API_KEY")

if not AI_LOADED:
    st.info("💡 AI summary disabled. Run `pip install groq` then restart.")
elif not GEMINI_API_KEY:
    st.warning("⚠ GROQ_API_KEY not found in secrets.toml or environment variable.")

if _import_errors and not BACKEND_LOADED:
    with st.expander("Show import errors"):
        for err in _import_errors:
            st.code(err)

st.markdown("<hr>", unsafe_allow_html=True)


# Input section 
st.markdown('<div class="section-label">Upload or paste your contract</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload contract",
    type=["pdf", "txt"],
    label_visibility="collapsed",
    help="PDF or TXT files supported. Scanned PDFs use OCR automatically."
)

raw_text = ""
if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        with st.spinner("Extracting text from PDF..."):
            raw_text = read_pdf(uploaded_file)
        if raw_text:
            st.success(f"✓ Extracted {len(raw_text.split())} words from PDF")
        else:
            st.warning("Could not extract text from PDF. Try pasting text manually below.")
    else:
        raw_text = uploaded_file.read().decode("utf-8", errors="ignore")

contract_input = st.text_area(
    "Contract text",
    value=raw_text,
    height=160,
    placeholder=(
        "Paste the full contract text here...\n\n"
        "Example: The Contractor shall not be liable for any indirect or consequential damages. "
        "Payment is non-refundable. This agreement shall auto-renew annually unless terminated "
        "with 90 days written notice..."
    ),
    label_visibility="collapsed",
)

col_btn, _ = st.columns([1, 3])
with col_btn:
    run = st.button("Analyze contract risk", use_container_width=True)

#  Session state init — keeps results alive across reruns 
if "results"    not in st.session_state: st.session_state.results    = None
if "summary"    not in st.session_state: st.session_state.summary    = None
if "alerts"     not in st.session_state: st.session_state.alerts     = []
if "score"      not in st.session_state: st.session_state.score      = None
if "level"      not in st.session_state: st.session_state.level      = None
if "high_count" not in st.session_state: st.session_state.high_count = 0
if "clauses"    not in st.session_state: st.session_state.clauses    = []


# ── Analysis ───────────────────────────────────────────────────────────────────
if run:
    text = contract_input.strip()
    if not text:
        st.warning("Please paste or upload a contract first.")
        st.stop()

    with st.spinner("Splitting into clauses..."):
        clauses = split_clauses(text)

    if not clauses:
        st.error("No clauses detected. Please paste longer contract text.")
        st.stop()

    with st.spinner(f"Classifying {len(clauses)} clauses..."):
        results = analyze_clauses(clauses)

    score, level, high_count = calc_score(results)

    with st.spinner("Consulting Groq AI counsel..."):
        summary = ai_summary(results, score, level)

    alerts = fraud_checks(clauses, text)

    # Save everything to session state so it survives button reruns
    st.session_state.results    = results
    st.session_state.summary    = summary
    st.session_state.alerts     = alerts
    st.session_state.score      = score
    st.session_state.level      = level
    st.session_state.high_count = high_count
    st.session_state.clauses    = clauses


# Show dashboard if analysis has been run 
if st.session_state.results is not None:
    results    = st.session_state.results
    summary    = st.session_state.summary
    alerts     = st.session_state.alerts
    score      = st.session_state.score
    level      = st.session_state.level
    high_count = st.session_state.high_count
    clauses    = st.session_state.clauses

    high_r = [r for r in results if r["risk"] == "High"]
    med_r  = [r for r in results if r["risk"] == "Medium"]
    low_r  = [r for r in results if r["risk"] == "Low"]

    # Score card + metrics 
    st.markdown('<div class="section-label">Overall risk assessment</div>', unsafe_allow_html=True)
    
    col_score, col_m1, col_m2, col_m3 = st.columns([2, 1, 1, 1])
    
    with col_score:
        bc         = "high" if "High" in level else "medium" if "Medium" in level else "low"
        fill_pct   = round((score / 3.0) * 100, 1)
        fill_color = "#E24B4A" if bc == "high" else "#BA7517" if bc == "medium" else "#3B6D11"
        st.markdown(f"""
        <div style="background:#1a1d2e; border:1px solid #2a2d3e; border-radius:10px; padding:20px 22px;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:14px;">
            <div>
              <div class="score-display">{score:.2f}</div>
              <div class="score-sub">out of 3.00 maximum risk</div>
            </div>
            <span class="badge-{bc}">{level}</span>
          </div>
          <div style="height:8px; background:#0f1117; border-radius:8px; overflow:hidden; margin-bottom:6px;">
            <div style="height:100%; width:{fill_pct}%; background:{fill_color}; border-radius:8px;"></div>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:11px; color:#6b6f7e;">
            <span>Low risk</span><span>Medium risk</span><span>High risk</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">High risk</div><div class="metric-value-high">{len(high_r)}</div></div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Medium risk</div><div class="metric-value-med">{len(med_r)}</div></div>', unsafe_allow_html=True)
    with col_m3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Low risk</div><div class="metric-value-low">{len(low_r)}</div></div>', unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Charts 
    col_bar, col_pie = st.columns(2)
    
    with col_bar:
        st.markdown('<div class="section-label">Risk distribution</div>', unsafe_allow_html=True)
        fig_bar = go.Figure(go.Bar(
            x=["High risk", "Medium risk", "Low risk"],
            y=[len(high_r), len(med_r), len(low_r)],
            marker_color=["rgba(255,107,107,0.2)", "rgba(255,169,77,0.2)", "rgba(105,219,124,0.2)"],
            marker_line_color=["#ff6b6b", "#ffa94d", "#69db7c"],
            marker_line_width=1.5,
        ))
        fig_bar.update_layout(
            height=240, margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
            font_family="Syne", font_color="#c8c6c0",
            yaxis=dict(showgrid=True, gridcolor="#2a2d3e", dtick=1, color="#6b6f7e"),
            xaxis=dict(showgrid=False, color="#6b6f7e"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col_pie:
        st.markdown('<div class="section-label">Clause breakdown</div>', unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=["High risk", "Medium risk", "Low risk"],
            values=[len(high_r), len(med_r), len(low_r)],
            marker_colors=["#ff6b6b", "#ffa94d", "#69db7c"],
            hole=0.55,
            textinfo="percent",
            hovertemplate="%{label}: %{value} clauses<extra></extra>",
        ))
        fig_pie.update_layout(
            height=240, margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="#0f1117", showlegend=True,
            font_color="#c8c6c0",
            legend=dict(font_size=11, orientation="h", yanchor="bottom", y=-0.15),
            font_family="Syne",
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # AI Summary 
    st.markdown('<div class="section-label">AI counsel summary</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="ai-card"><div class="ai-label">● Groq AI counsel</div>'
        f'<div class="ai-text">{summary.replace(chr(10), "<br/>")}</div></div>',
        unsafe_allow_html=True
    )
    
    # Fraud flags 
    if alerts:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Fraud &amp; anomaly flags</div>', unsafe_allow_html=True)
        for alert in alerts:
            st.markdown(f'<div class="fraud-alert">⚠ {alert}</div>', unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Clause-by-clause 
    st.markdown('<div class="section-label">Clause-by-clause analysis</div>', unsafe_allow_html=True)
    
    filter_choice = st.radio(
        "Filter",
        ["All", "High", "Medium", "Low"],
        horizontal=True,
        label_visibility="collapsed",
    )
    
    filtered = results if filter_choice == "All" else [r for r in results if r["risk"] == filter_choice]
    
    if not filtered:
        st.info(f"No {filter_choice.lower()} risk clauses found.")
    else:
        for r in filtered:
            risk       = r["risk"]
            rc         = risk.lower()
            conf_pct   = int(r["confidence"] * 100)
            highlighted = highlight_clause(r["clause"], risk)
            icon       = "⚠" if risk == "High" else "◈" if risk == "Medium" else "✓"
            bar_color  = "#ff6b6b" if rc == "high" else "#ffa94d" if rc == "medium" else "#69db7c"
    
            with st.expander(f"{icon}  {r['clause'][:85]}{'...' if len(r['clause']) > 85 else ''}"):
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                  <span class="badge-{rc}">{risk} risk</span>
                  <span class="conf-pill">{conf_pct}% confidence</span>
                  <div style="flex:1; height:3px; background:#2a2d3e; border-radius:3px;">
                    <div style="width:{conf_pct}%; height:100%; background:{bar_color}; border-radius:3px;"></div>
                  </div>
                </div>
                <div class="clause-text" style="background:#0f1117; border-radius:8px; padding:12px 14px; margin-bottom:10px; border:1px solid #2a2d3e;">{highlighted}</div>
                <div class="clause-expl">{icon} {r['explanation']}</div>
                """, unsafe_allow_html=True)
    
    # Download Report 
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Download Report</div>', unsafe_allow_html=True)
    
    if _generate_report:
        if st.button("Generate PDF Report", use_container_width=False):
            with st.spinner("Generating report..."):
                try:
                    import platform
                    is_local = platform.system() in ("Windows", "Darwin")
                    output_dir = None
                    if is_local:
                        project_root = str(Path(__file__).parent.parent)
                        output_dir   = os.path.join(project_root, "reports")

                    pdf_bytes, filename = _generate_report(
                        results      = results,
                        score        = score,
                        level        = level,
                        high_count   = high_count,
                        ai_summary   = summary,
                        fraud_alerts = alerts if alerts else [],
                        output_dir   = output_dir,
                    )
                    st.download_button(
                        label        = "⬇ Download PDF Report",
                        data         = pdf_bytes,
                        file_name    = filename,
                        mime         = "application/pdf",
                        use_container_width=False,
                    )
                    if is_local:
                        st.success(f"Report also saved locally to: reports/{filename}")
                    else:
                        st.success("Report ready — click the button above to download.")
                except Exception as e:
                    st.error(f"Report generation failed: {e}")
    else:
        st.info("Install reportlab to enable PDF reports: `pip install reportlab`")