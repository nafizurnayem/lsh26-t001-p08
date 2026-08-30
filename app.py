"""P08 — School Result Processing & GPA Engine (Streamlit UI).

Four tabs map one-to-one onto the four required items, plus an edge gallery
that finds the four hard archetypes automatically.
"""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

import engine

st.set_page_config(
    page_title="P08 — Result Engine",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded",
)

# ── Liquid Glass CSS ──────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ─── Reset & Base ─── */
    html, body, p, label,
    [data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"],
    .stTabs [data-baseweb="tab"], [data-testid="stMetricValue"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Icons are ligature fonts: never override their font-family, or the icon
       name shows up as literal text. */
    [data-testid="stIconMaterial"],
    [data-testid="stExpandSidebarButton"] span,
    [data-testid="stBaseButton-headerNoPadding"] span,
    span.material-symbols-rounded, span.material-icons,
    [class*="material-symbols"], [class*="material-icons"] {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }

    /* ─── Rich animated background ─── */
    .stApp {
        background:
            radial-gradient(ellipse 80% 60% at 20% 10%, rgba(120,80,255,0.35) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 80% 90%, rgba(0,200,255,0.25) 0%, transparent 60%),
            radial-gradient(ellipse 70% 70% at 50% 50%, rgba(0,20,60,0.95) 0%, transparent 100%),
            linear-gradient(160deg, #050d1a 0%, #0a1628 40%, #060e1c 100%);
        min-height: 100vh;
    }

    /* ─── Keyframe shimmer ─── */
    @keyframes shimmer {
        0%   { background-position: -400% 0; }
        100% { background-position: 400% 0; }
    }
    @keyframes glowPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(120,80,255,0.3), 0 8px 32px rgba(0,0,0,0.4); }
        50%       { box-shadow: 0 0 40px rgba(0,200,255,0.25), 0 8px 32px rgba(0,0,0,0.4); }
    }
    @keyframes borderSpin {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ─── Sidebar ─── */
    section[data-testid="stSidebar"] {
        background:
            linear-gradient(160deg, rgba(120,80,255,0.12) 0%, rgba(0,200,255,0.07) 100%),
            rgba(8,16,36,0.92) !important;
        backdrop-filter: blur(24px) saturate(180%);
        -webkit-backdrop-filter: blur(24px) saturate(180%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    section[data-testid="stSidebar"] * {
        color: #e8eef8 !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stCaption p {
        color: #a0b0d0 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stNumberInput label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stCheckbox label {
        color: #c8d8f0 !important;
        font-weight: 500 !important;
    }

    /* ─── Hero Header ─── */
    .lg-hero {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(135deg,
                rgba(120,80,255,0.45) 0%,
                rgba(60,120,255,0.35) 30%,
                rgba(0,200,255,0.30) 60%,
                rgba(180,60,255,0.25) 100%);
        backdrop-filter: blur(20px) saturate(200%);
        -webkit-backdrop-filter: blur(20px) saturate(200%);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 20px;
        padding: 32px 40px;
        margin-bottom: 28px;
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.06) inset,
            0 24px 48px rgba(0,0,0,0.5),
            0 0 80px rgba(120,80,255,0.2);
        animation: glowPulse 4s ease-in-out infinite;
    }
    .lg-hero::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(105deg,
            transparent 35%, rgba(255,255,255,0.08) 50%, transparent 65%);
        background-size: 200% 100%;
        animation: shimmer 4s linear infinite;
        border-radius: 20px;
        pointer-events: none;
    }
    .lg-hero h1 {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
        margin: 0 !important;
        text-shadow: 0 2px 20px rgba(120,80,255,0.5);
    }
    .lg-hero p {
        color: rgba(220,235,255,0.88) !important;
        font-size: 0.88rem !important;
        margin: 10px 0 0 0 !important;
        font-weight: 400 !important;
        letter-spacing: 0.01em;
    }

    /* ─── Glass Card (generic) ─── */
    .lg-card {
        background:
            linear-gradient(135deg, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0.04) 100%);
        backdrop-filter: blur(16px) saturate(160%);
        -webkit-backdrop-filter: blur(16px) saturate(160%);
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 16px;
        padding: 18px 22px;
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.06) inset,
            0 8px 24px rgba(0,0,0,0.35);
        color: #e8eef8;
    }

    /* ─── Tabs ─── */
    .stTabs [data-baseweb="tab-list"] {
        background:
            linear-gradient(135deg, rgba(255,255,255,0.09) 0%, rgba(255,255,255,0.04) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 14px;
        padding: 5px;
        gap: 4px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: #a0b8d8 !important;
        font-weight: 500;
        font-size: 0.875rem;
        padding: 9px 18px;
        border: none !important;
        transition: all 0.25s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background: rgba(255,255,255,0.10);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg,
            rgba(120,80,255,0.55) 0%,
            rgba(60,140,255,0.45) 50%,
            rgba(0,200,255,0.40) 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.2) inset,
            0 4px 16px rgba(120,80,255,0.5) !important;
    }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 24px; }

    /* ─── Metric cards ─── */
    [data-testid="metric-container"] {
        background:
            linear-gradient(135deg, rgba(255,255,255,0.11) 0%, rgba(255,255,255,0.04) 100%);
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 16px;
        padding: 18px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.06) inset;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 16px 40px rgba(120,80,255,0.25), 0 0 0 1px rgba(255,255,255,0.15) inset;
        border-color: rgba(255,255,255,0.25);
    }
    [data-testid="metric-container"] label {
        color: #a0b8d8 !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 20px rgba(120,80,255,0.4);
    }

    /* ─── Dataframe ─── */
    .stDataFrame {
        border-radius: 14px !important;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.12) !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.35) !important;
        backdrop-filter: blur(8px);
    }

    /* ─── Primary Buttons ─── */
    .stButton > button {
        background: linear-gradient(135deg,
            rgba(120,80,255,0.7) 0%,
            rgba(60,140,255,0.65) 50%,
            rgba(0,180,255,0.60) 100%);
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px;
        padding: 10px 22px;
        font-weight: 600;
        font-size: 0.875rem;
        backdrop-filter: blur(8px);
        transition: all 0.25s ease;
        box-shadow: 0 4px 16px rgba(120,80,255,0.4), 0 0 0 1px rgba(255,255,255,0.08) inset;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(120,80,255,0.55), 0 0 0 1px rgba(255,255,255,0.15) inset;
        background: linear-gradient(135deg,
            rgba(140,100,255,0.8) 0%,
            rgba(80,160,255,0.75) 50%,
            rgba(0,200,255,0.70) 100%);
    }
    .stButton > button:active { transform: translateY(0); }

    /* ─── Download Buttons ─── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0.05) 100%);
        color: #c8e0ff !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        border-radius: 12px;
        font-weight: 500;
        backdrop-filter: blur(8px);
        transition: all 0.25s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, rgba(120,80,255,0.3) 0%, rgba(0,180,255,0.25) 100%);
        border-color: rgba(120,200,255,0.4) !important;
        color: #ffffff !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }

    /* ─── Select box ─── */
    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        color: #e8eef8 !important;
        backdrop-filter: blur(8px);
    }
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] div {
        color: #e8eef8 !important;
    }

    /* ─── Multiselect ─── */
    .stMultiSelect [data-baseweb="select"] > div {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        backdrop-filter: blur(8px);
    }
    .stMultiSelect span { color: #e8eef8 !important; }

    /* ─── Number input ─── */
    .stNumberInput input {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #e8eef8 !important;
        border-radius: 10px !important;
    }

    /* ─── Markdown / generic text ─── */
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: #d0ddf0 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff !important;
    }
    .stMarkdown strong { color: #ffffff !important; }
    .stMarkdown code {
        background: rgba(120,80,255,0.2) !important;
        color: #b0d0ff !important;
        border-radius: 4px;
        padding: 1px 5px;
        border: 1px solid rgba(120,80,255,0.3);
    }

    /* ─── Captions ─── */
    .stCaption, .stCaption p { color: #7090b8 !important; font-size: 0.8rem !important; }

    /* ─── Section header widgets ─── */
    .lg-section-header {
        display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
    }
    .lg-badge {
        background: linear-gradient(135deg, rgba(120,80,255,0.7), rgba(0,180,255,0.6));
        color: #ffffff;
        font-size: 0.65rem; font-weight: 800;
        padding: 5px 12px; border-radius: 30px;
        letter-spacing: 0.08em; text-transform: uppercase;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 2px 10px rgba(120,80,255,0.4);
    }
    .lg-section-title {
        color: #ffffff; font-size: 1.2rem; font-weight: 700; margin: 0;
        text-shadow: 0 2px 12px rgba(120,80,255,0.3);
    }

    /* ─── Rules banner ─── */
    .lg-rules-banner {
        background: linear-gradient(135deg, rgba(120,80,255,0.12) 0%, rgba(0,180,255,0.10) 100%);
        border: 1px solid rgba(255,255,255,0.12);
        border-left: 3px solid rgba(120,180,255,0.7);
        border-radius: 0 12px 12px 0;
        padding: 12px 18px;
        margin-bottom: 20px;
        font-size: 0.84rem;
        color: #b8d0f0;
        backdrop-filter: blur(8px);
    }

    /* ─── Alert / info / success / error ─── */
    .stAlert { border-radius: 12px !important; }
    div[data-testid="stNotificationContentSuccess"] { color: #e8fff0 !important; }
    div[data-testid="stNotificationContentInfo"]    { color: #e8f4ff !important; }
    div[data-testid="stNotificationContentWarning"] { color: #fff4e0 !important; }
    div[data-testid="stNotificationContentError"]   { color: #ffe8e8 !important; }

    /* ─── Horizontal rules ─── */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg,
            transparent, rgba(120,180,255,0.3), rgba(120,80,255,0.3), transparent) !important;
        margin: 24px 0 !important;
    }

    /* ─── Scrollbar ─── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, rgba(120,80,255,0.5), rgba(0,180,255,0.5));
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(160,120,255,0.7); }

    /* ─── Sidebar logo ─── */
    .lg-sidebar-logo { text-align: center; padding: 20px 0 12px; }
    .lg-sidebar-logo .icon { font-size: 2.8rem; filter: drop-shadow(0 0 12px rgba(120,80,255,0.6)); }
    .lg-sidebar-logo h2 {
        color: #ffffff !important; font-size: 1.1rem !important;
        font-weight: 800 !important; margin: 8px 0 0 !important;
        text-shadow: 0 0 20px rgba(120,80,255,0.5);
    }
    .lg-sidebar-logo p { color: #7090b8 !important; font-size: 0.75rem !important; margin: 3px 0 0 !important; }

    /* ─── Sidebar stats card ─── */
    .lg-stats-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 14px;
        padding: 14px 18px;
        font-size: 0.82rem;
    }
    .lg-stats-card .label { color: #6888a8; }
    .lg-stats-card .value { color: #e8eef8; font-weight: 700; }
    .lg-stats-card .gold  { color: #fde68a; font-weight: 700; }
    .lg-stats-card .red   { color: #fca5a5; font-weight: 700; }
    .lg-stats-card .head  {
        color: #8aabce; font-size: 0.68rem; font-weight: 800;
        text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px;
    }
    .lg-stats-row { display: flex; justify-content: space-between; margin-bottom: 5px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Extra metric + text contrast overrides (separate block for specificity) ───
st.markdown(
    """
    <style>
    /* ── Metric value: force white on ALL Streamlit versions ── */
    [data-testid="stMetricValue"] > div,
    [data-testid="stMetricValue"] div,
    [data-testid="stMetricValue"],
    div[data-testid="metric-container"] > label + div > div,
    div[data-testid="metric-container"] > label + div,
    .stMetric [data-testid="stMetricValue"],
    .stMetric div div div { color: #ffffff !important; }

    /* ── Metric label ── */
    div[data-testid="metric-container"] > label,
    .stMetric label { color: #9ab0d0 !important; font-size: 0.72rem !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; }

    /* ── Generic text contrast catch-all for dark theme ── */
    .main p, .main span, .main div { color: #d8e8f8; }
    .main strong, .main b { color: #ffffff; }

    /* ── Selectbox dropdown ── */
    [data-baseweb="menu"] { background: rgba(12,22,46,0.97) !important; border: 1px solid rgba(120,80,255,0.3) !important; border-radius: 10px !important; }
    [data-baseweb="menu"] li { color: #e0eaff !important; }
    [data-baseweb="menu"] li:hover { background: rgba(120,80,255,0.2) !important; }

    /* ── Multiselect tag ── */
    [data-baseweb="tag"] { background: rgba(120,80,255,0.3) !important; border: 1px solid rgba(120,80,255,0.5) !important; border-radius: 6px !important; }
    [data-baseweb="tag"] span { color: #e0eaff !important; }

    /* ── Dataframe header ── */
    .dvn-scroller { background: rgba(10,18,40,0.7) !important; }

    /* ── Spinner text ── */
    .stSpinner > div > div { color: #a0c0ff !important; }

    /* ── Success/error/warning text in notifications ── */
    div[data-baseweb="notification"] div { color: #f0f8ff !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── constants ─────────────────────────────────────────────────────────────────
GENERATED = "Generated cohort (seeded)"
CULPRIT_MARK = "  <-- culprit"
EMPTY_FILTER = "No students match the current class filter. Pick a class in the sidebar."

LETTER_COLORS = {
    "A+": ("#fde68a", "rgba(251,191,36,0.18)"),
    "A":  ("#6ee7b7", "rgba(52,211,153,0.15)"),
    "A-": ("#93c5fd", "rgba(96,165,250,0.15)"),
    "B":  ("#c4b5fd", "rgba(167,139,250,0.18)"),
    "C":  ("#fca5a5", "rgba(248,113,113,0.15)"),
    "D":  ("#fdba74", "rgba(251,146,60,0.15)"),
    "F":  ("#f87171", "rgba(239,68,68,0.18)"),
}
GRADE_EMOJI = {"A+": "🏆", "A": "🥇", "A-": "🥈", "B": "🥉", "C": "📘", "D": "📗", "F": "❌"}

# Light tint behind each grade point, so a column reads at a glance.
GP_TINTS = {
    5.0: "rgba(52,211,153,0.30)",
    4.0: "rgba(96,165,250,0.28)",
    3.5: "rgba(129,140,248,0.28)",
    3.0: "rgba(167,139,250,0.26)",
    2.0: "rgba(251,191,36,0.28)",
    1.0: "rgba(251,146,60,0.30)",
    0.0: "rgba(239,68,68,0.38)",
}
NEUTRAL_TINT = "rgba(255,255,255,0.06)"
TEXT_WHITE = "color:#ffffff;"

# Explicit pixel widths keep long values from being cut off with an ellipsis.
RESULT_WIDTHS = {"ID": 80, "Name": 190, "Class": 95, "Optional": 95,
                 "Raw GPA": 100, "GPA": 90, "Letter": 85}
ROSTER_WIDTHS = {"ID": 80, "Name": 190, "Class": 95, "Optional": 95,
                 "Absent in": 120, "Edge case": 300}
TRACE_WIDTHS = {"Subject": 210, "Role": 110, "Mark used": 130,
                "Grade point": 110, "Rule": 80, "Why": 560}
TABLE_HEIGHT = 520
EXAMPLES_PER_ARCHETYPE = 2
LIST_COLORS = [
    ("optional",       "🔄", "Changed by optional rule",  "Optional grade point ≤ 2.0",           "rgba(167,139,250,0.7)", "rgba(167,139,250,0.15)"),
    ("practical_fail", "🔬", "Practical part below 8",    "Failed practical component in any subject", "rgba(248,113,113,0.7)", "rgba(248,113,113,0.12)"),
    ("absent",         "🚫", "Absent in a subject",       "Marked AB in any subject",              "rgba(251,146,60,0.7)",  "rgba(251,146,60,0.12)"),
]
ARCH_COLORS = [
    ("🎯 High Average Failure",        "rgba(248,113,113,0.75)", "rgba(248,113,113,0.12)",
     "Failed compulsory despite strong average (≥ 3.50)",    lambda r: r["high_average_failure"]),
    ("🔬 Practical Fail, Passing Theory", "rgba(251,146,60,0.75)", "rgba(251,146,60,0.12)",
     "Practical below 8 with a passing theory mark",         lambda r: r["practical_fail_passing_theory"]),
    ("📘 Weak Optional",               "rgba(167,139,250,0.75)", "rgba(167,139,250,0.12)",
     "Optional ≤ 2.0 GP — adds nothing to GPA",              lambda r: r["optional_weak"] and not r["compulsory_failed"]),
    ("🚫 Absent Student",              "rgba(96,165,250,0.75)",  "rgba(96,165,250,0.12)",
     "Marked absent (AB) in at least one subject",           lambda r: r["absent"]),
]


# ── helpers ───────────────────────────────────────────────────────────────────

def section_header(badge, title):
    st.markdown(
        f'<div class="lg-section-header">'
        f'<span class="lg-badge">{badge}</span>'
        f'<span class="lg-section-title">{title}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def glass_card(html_content, border_color="rgba(255,255,255,0.14)", bg="rgba(255,255,255,0.07)"):
    st.markdown(
        f"""<div style="background:linear-gradient(135deg,{bg},{bg.replace('0.07','0.03')});
        backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
        border:1px solid {border_color};border-radius:14px;padding:16px 20px;
        box-shadow:0 8px 24px rgba(0,0,0,0.3),0 0 0 1px rgba(255,255,255,0.05) inset;
        margin-bottom:12px;">{html_content}</div>""",
        unsafe_allow_html=True,
    )


# ── data ──────────────────────────────────────────────────────────────────────

@st.cache_data
def load_bundled():
    """The published fixture if it sits beside the app, otherwise None."""
    path = Path(engine.DATA_FILE)
    return engine.load_file(path) if path.exists() else None


@st.cache_data
def parse_upload(raw):
    """A case file supplied by the judge through the sidebar uploader."""
    return json.loads(raw.decode("utf-8"))


@st.cache_data
def build_cohort(seed, size):
    return engine.generate_cohort(seed=seed, size=size, case_id="GEN-{}".format(seed))


@st.cache_data
def score(case):
    return engine.run_case(case)


@st.cache_data
def score_everything(loaded):
    every = engine.run_all(loaded)
    return every, engine.counts(every)


def edge_label(result):
    """Which hard edge this student sits on, blank for an ordinary student."""
    labels = []
    if result["high_average_failure"]:
        labels.append("high-average failure")
    if result["practical_fail_passing_theory"]:
        labels.append("practical fail, passing theory")
    elif result["practical_fail"]:
        labels.append("practical fail")
    if result["optional_weak"]:
        labels.append("weak optional")
    if result["absent"]:
        labels.append("absent")
    return " · ".join(labels)


def roster_frame(case, results):
    """Roster, with the edge case each student illustrates named in its own column.

    "Sat" is how many subjects the student actually turned up for, out of the
    seven they entered, so an absence shows as 6.
    """
    edge_by_id = {r["id"]: edge_label(r) for r in results}
    rows = []
    for s in case["students"]:
        absent_codes = [code for code, mark in s["marks"].items() if mark == engine.ABSENT]
        rows.append({
            "ID": s["id"], "Name": s["name"], "Class": s["class"],
            "Optional": s["optional"],
            "Sat": len(s["marks"]) - len(absent_codes),
            "Absent in": ", ".join(absent_codes),
            "Edge case": edge_by_id.get(s["id"], ""),
        })
    return pd.DataFrame(rows)


def is_gp_column(col):
    return col in engine.COMPULSORY or col.startswith("OPT (")


def text_config(widths):
    """Fixed-width text columns: wide enough that nothing is truncated."""
    return {col: st.column_config.TextColumn(col, width=px) for col, px in widths.items()}


def results_column_config(frame):
    """Two-decimal grade points that still sort as numbers, plus fixed widths."""
    config = {col: st.column_config.NumberColumn(col, format="%.2f", width=78)
              for col in frame.columns if is_gp_column(col)}
    config.update(text_config({col: px for col, px in RESULT_WIDTHS.items()
                               if col in frame.columns}))
    return config


def style_results(frame):
    """White text everywhere, and a light tint that follows the value's band."""
    gp_cols = [c for c in frame.columns if is_gp_column(c)]

    def paint(df):
        css = pd.DataFrame(TEXT_WHITE, index=df.index, columns=df.columns)
        for col in gp_cols:
            css[col] = df[col].map(
                lambda v: TEXT_WHITE + "font-weight:600;background-color:{};".format(
                    GP_TINTS.get(float(v), NEUTRAL_TINT))
            )
        for col in ("Raw GPA", "GPA", "Letter"):
            if col in df.columns:
                css[col] = df["Letter"].map(
                    lambda letter: TEXT_WHITE + "font-weight:700;background-color:{};".format(
                        LETTER_COLORS.get(letter, ("", NEUTRAL_TINT))[1])
                )
        return css

    return frame.style.apply(paint, axis=None)


def results_frame(results):
    rows = []
    for r in results:
        row = {"ID": r["id"], "Name": r["name"], "Class": r["class"], "Optional": r["optional"]}
        for code in engine.COMPULSORY:
            row[code] = r["subject_gps"][code]
        row["OPT ({})".format(r["optional"])] = r["optional_gp"]
        row["Raw GPA"] = r["raw_gpa_str"]
        row["GPA"]     = r["final_gpa_str"]
        row["Letter"]  = r["letter"]
        rows.append(row)
    return pd.DataFrame(rows)


def trace_frame(result, highlight=True):
    rows = []
    for r in result["rows"]:
        subj = "{} ({})".format(r["subject"], r["code"])
        if highlight and r["code"] in result["culprit_subjects"]:
            subj += CULPRIT_MARK
        rows.append({
            "Subject":     subj,
            "Role":        "compulsory" if r["compulsory"] else "optional",
            "Mark used":   r["mark_used"],
            "Grade point": engine.fmt(r["gp"]),
            "Rule":        r["rule"],
            "Why":         r["why"],
        })
    return pd.DataFrame(rows)


def csv_of(results):
    return results_frame(results).to_csv(index=False).encode("utf-8")


def show_trace(result):
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 Raw GPA (before cancellation)", result["raw_gpa_str"])
    c2.metric("🎯 Final GPA",                     result["final_gpa_str"])
    c3.metric("🏅 Letter Grade",                  result["letter"])

    if result["compulsory_failed"]:
        culprits = ", ".join(result["culprit_subjects"])
        st.error(
            "⚠️ **R-13 Applied** — Raw GPA {} was cancelled to {}. "
            "Compulsory subject(s) scoring zero: **{}**.".format(
                result["raw_gpa_str"], result["final_gpa_str"], culprits)
        )
    st.dataframe(
        trace_frame(result),
        width="stretch",
        hide_index=True,
        column_config=text_config(TRACE_WIDTHS),
    )


# ── sidebar ───────────────────────────────────────────────────────────────────

data = load_bundled()

with st.sidebar:
    st.markdown(
        '<div class="lg-sidebar-logo">'
        '<div class="icon">🎓</div>'
        '<h2>P08 Result Engine</h2>'
        '<p>Bangladesh SSC GPA System</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

if st.session_state.pop("_switch_to_generated", False):
    st.session_state["source"] = GENERATED

st.sidebar.markdown("**📂 Case File**")
upload = st.sidebar.file_uploader(
    "Case file (JSON)", type=["json"], label_visibility="collapsed",
    help="Upload P08_school_results_public.json, or any file in the same shape.",
)
if upload is not None:
    data = parse_upload(upload.getvalue())

ids = engine.case_ids(data) if data else []
if not ids:
    st.sidebar.info("No case file loaded — the generated cohort is scored instead.")

st.sidebar.markdown("**📂 Data Source**")
source = st.sidebar.selectbox("Case", ids + [GENERATED], key="source", label_visibility="collapsed")

if source == GENERATED:
    st.sidebar.markdown("**⚙️ Generator**")
    seed = st.sidebar.number_input("Seed",     min_value=0,  max_value=9999, value=7,  step=1)
    size = st.sidebar.number_input("Students", min_value=60, max_value=200,  value=60, step=10)
    case = build_cohort(int(seed), int(size))
else:
    case = engine.load_case(data, source)

results = score(case)
classes = sorted({r["class"] for r in results})

st.sidebar.markdown("**🏫 Class Filter**")
picked = st.sidebar.multiselect("Classes", classes, default=classes, label_visibility="collapsed")
view   = [r for r in results if r["class"] in picked]

# Stats card
st.sidebar.markdown("---")
total_s  = len(results)
shown_s  = len(view)
failed_s = sum(1 for r in view if r["compulsory_failed"])
top_s    = sum(1 for r in view if r["letter"] == "A+")
st.sidebar.markdown(
    f"""<div class="lg-stats-card">
    <div class="head">Case Summary</div>
    <div class="lg-stats-row"><span class="label">Case</span><span class="value">{case['case_id']}</span></div>
    <div class="lg-stats-row"><span class="label">Total students</span><span class="value">{total_s}</span></div>
    <div class="lg-stats-row"><span class="label">Shown</span><span class="value">{shown_s}</span></div>
    <div class="lg-stats-row"><span class="label">🏆 A+ students</span><span class="gold">{top_s}</span></div>
    <div class="lg-stats-row"><span class="label">❌ Failed</span><span class="red">{failed_s}</span></div>
    </div>""",
    unsafe_allow_html=True,
)

# ── Hero header ───────────────────────────────────────────────────────────────

st.markdown(
    """<div class="lg-hero">
        <h1>🎓 P08 — School Result Processing &amp; GPA Engine</h1>
        <p>Bangladesh SSC grading system &nbsp;·&nbsp;
        Rules: <strong>R-12</strong> (absent) → <strong>R-11</strong> (part fail) →
        <strong>R-10</strong> (grade table) → <strong>R-13</strong> (GPA cap &amp; cancellation) →
        <strong>R-29</strong> (office lists)</p>
    </div>""",
    unsafe_allow_html=True,
)

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏫  Cohort", "📊  Results", "🔍  Trace", "📋  Office List", "⚡  Edge Gallery"
])

# ─────────────────────────────────────────────────────────────────────────────
# Tab 1 — Cohort
# ─────────────────────────────────────────────────────────────────────────────

with tab1:
    section_header("Item 1", "Cohort Overview")

    a, b, c, d = st.columns(4)
    a.metric("👥 Students",           len(case["students"]))
    b.metric("🏫 Classes",            len(classes))
    c.metric("📚 Compulsory subjects", len(case["compulsory"]))
    absent_students = sum(1 for r in results if r["absent"])
    d.metric("📝 Subjects each", 7,
             help="Every student enters 7 subjects. {} of them missed one (AB).".format(
                 absent_students))

    hard = [r for r in results if
            r["high_average_failure"] or r["practical_fail_passing_theory"]
            or r["optional_weak"]     or r["absent"]]

    ok_color = "rgba(52,211,153,0.75)" if len(hard) >= 8 else "rgba(248,113,113,0.75)"
    ok_bg    = "rgba(52,211,153,0.12)" if len(hard) >= 8 else "rgba(248,113,113,0.12)"
    ok_icon  = "✅" if len(hard) >= 8 else "⚠️"

    left, right = st.columns([1, 2])
    with left:
        glass_card(
            f'<div style="color:{ok_color};font-weight:700;font-size:0.95rem;">'
            f'{ok_icon} {len(hard)} hard-edge students</div>'
            f'<div style="color:#7090b8;font-size:0.78rem;margin-top:4px;">Minimum required: 8</div>',
            border_color=ok_color.replace("0.75", "0.35"),
            bg=ok_bg,
        )
    with right:
        glass_card(
            f'<span style="color:#93c5fd;font-weight:600;">Compulsory:</span> '
            f'<span style="color:#e0e8f8;">{" · ".join(case["compulsory"])}</span>'
            f'&nbsp; | &nbsp;<span style="color:#93c5fd;font-weight:600;">Optional:</span> '
            f'<span style="color:#e0e8f8;">{" · ".join(engine.OPTIONALS)}</span>'
            f'<br><span style="color:#7090b8;font-size:0.8rem;margin-top:4px;display:block;">'
            f'Practical subjects carry separate theory + practical marks.</span>'
        )

    roster = roster_frame(case, results)
    st.dataframe(
        roster[roster["Class"].isin(picked)],
        width="stretch",
        height=TABLE_HEIGHT,
        hide_index=True,
        column_config=dict(
            text_config(ROSTER_WIDTHS),
            **{"Sat": st.column_config.NumberColumn(
                "Sat", width=75,
                help="Subjects actually attended out of 7 — an absence makes this 6")},
        ),
    )

    st.markdown("---")
    if source == GENERATED:
        st.success("✅ Showing the **generated cohort**. Adjust seed in the sidebar for a new one.")
    else:
        if st.button("🔄 Generate a fresh cohort (all archetypes guaranteed)"):
            st.session_state["_switch_to_generated"] = True
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Tab 2 — Results
# ─────────────────────────────────────────────────────────────────────────────

with tab2:
    section_header("Item 2", "Grade points · GPA · Letter grade per student")

    if not view:
        st.warning(f"⚠️ {EMPTY_FILTER}")
    else:
        frame  = results_frame(view)
        spread = frame["Letter"].value_counts()
        cols   = st.columns(max(len(spread), 1))

        for i, (letter, count) in enumerate(spread.items()):
            fg, bg = LETTER_COLORS.get(letter, ("#e8eef8", "rgba(255,255,255,0.08)"))
            emoji  = GRADE_EMOJI.get(letter, "")
            cols[i].markdown(
                f"""<div style="
                    background:{bg};
                    border:1px solid {fg.replace('0.18','0.35').replace('0.15','0.35').replace('0.12','0.35')};
                    border-radius:14px;padding:14px 10px;text-align:center;
                    backdrop-filter:blur(12px);
                    box-shadow:0 4px 16px rgba(0,0,0,0.3);">
                    <div style="font-size:1.5rem;">{emoji}</div>
                    <div style="color:{fg};font-size:1.6rem;font-weight:800;
                    text-shadow:0 0 16px {fg};">{count}</div>
                    <div style="color:{fg};font-size:0.7rem;font-weight:700;
                    letter-spacing:0.08em;opacity:0.9;">{letter}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("")
        st.dataframe(
            style_results(frame),
            width="stretch",
            height=TABLE_HEIGHT,
            hide_index=True,
            column_config=results_column_config(frame),
        )
        st.download_button(
            "⬇️ Download results CSV",
            csv_of(view),
            file_name="{}_results.csv".format(case["case_id"]),
            mime="text/csv",
        )

# ─────────────────────────────────────────────────────────────────────────────
# Tab 3 — Trace
# ─────────────────────────────────────────────────────────────────────────────

with tab3:
    section_header("Item 3", "Per-student rule trace")

    if not view:
        st.warning(f"⚠️ {EMPTY_FILTER}")
    else:
        labels     = {"{} — {} ({})".format(r["id"], r["name"], r["class"]): r for r in view}
        chosen_key = st.selectbox("🔍 Select a student", list(labels))
        chosen     = labels[chosen_key]

        fg, bg = LETTER_COLORS.get(chosen["letter"], ("#e8eef8", "rgba(255,255,255,0.08)"))
        emoji  = GRADE_EMOJI.get(chosen["letter"], "")

        # Student identity card
        st.markdown(
            f"""<div style="
                display:flex;align-items:center;gap:18px;
                background:linear-gradient(135deg,rgba(255,255,255,0.09) 0%,rgba(255,255,255,0.04) 100%);
                backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
                border:1px solid rgba(255,255,255,0.15);border-radius:16px;
                padding:18px 22px;margin-bottom:18px;
                box-shadow:0 8px 24px rgba(0,0,0,0.35);">
                <div style="
                    background:{bg};
                    border:2px solid {fg.replace('0.18','0.5').replace('0.15','0.5').replace('0.12','0.5')};
                    border-radius:50%;width:56px;height:56px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.7rem;flex-shrink:0;
                    box-shadow:0 0 20px {fg};">{emoji}</div>
                <div style="flex:1;">
                    <div style="color:#ffffff;font-size:1.05rem;font-weight:700;">
                        {chosen['name']}</div>
                    <div style="color:#7090b8;font-size:0.8rem;margin-top:3px;">
                        {chosen['id']} &nbsp;·&nbsp; {chosen['class']} &nbsp;·&nbsp;
                        Optional: <strong style="color:#a0c0e8;">{chosen['optional']}</strong></div>
                </div>
                <div style="text-align:right;">
                    <div style="color:{fg};font-size:2rem;font-weight:800;
                    text-shadow:0 0 20px {fg};">{chosen['letter']}</div>
                    <div style="color:#6080a8;font-size:0.72rem;">Letter grade</div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        show_trace(chosen)

# ─────────────────────────────────────────────────────────────────────────────
# Tab 4 — Office List
# ─────────────────────────────────────────────────────────────────────────────

with tab4:
    section_header("Item 4", "Office checking lists (R-29)")
    st.markdown(
        '<div class="lg-rules-banner">'
        'Three independent passes — a student can appear on <strong>more than one list</strong>.'
        '</div>',
        unsafe_allow_html=True,
    )

    lists = engine.checking_lists(view)

    for key, icon, short_title, description, color, bg in LIST_COLORS:
        members = lists[key]
        st.markdown(
            f"""<div style="
                background:{bg};
                backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
                border:1px solid {color.replace('0.7','0.3')};
                border-left:3px solid {color};
                border-radius:0 14px 14px 0;
                padding:16px 22px;margin-bottom:14px;
                box-shadow:0 6px 20px rgba(0,0,0,0.25);">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:1.3rem;">{icon}</span>
                    <div style="flex:1;">
                        <div style="color:#ffffff;font-weight:700;font-size:0.95rem;">{short_title}</div>
                        <div style="color:#8090b0;font-size:0.8rem;margin-top:2px;">{description}</div>
                    </div>
                    <span style="
                        background:{bg};color:{color};font-weight:800;
                        font-size:1rem;padding:5px 14px;border-radius:30px;
                        border:1px solid {color.replace('0.7','0.4')};
                        box-shadow:0 2px 10px rgba(0,0,0,0.2);">
                        {len(members)} students
                    </span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        if members:
            member_frame = results_frame(members)
            st.dataframe(
                style_results(member_frame),
                width="stretch",
                height=min(TABLE_HEIGHT, 120 + 35 * len(members)),
                hide_index=True,
                column_config=results_column_config(member_frame),
            )
            st.download_button(
                f"⬇️ Download {short_title} CSV",
                csv_of(members),
                file_name="{}_{}.csv".format(case["case_id"], key),
                mime="text/csv",
                key="dl_" + key,
            )
        else:
            st.caption("Nobody on this list for the current selection.")

        st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# Tab 5 — Edge Gallery
# ─────────────────────────────────────────────────────────────────────────────

with tab5:
    section_header("⚡ Edge", "The four hard archetypes — found automatically")

    for title, color, bg, description, test in ARCH_COLORS:
        found = [r for r in view if test(r)]

        st.markdown(
            f"""<div style="
                position:relative;overflow:hidden;
                background:{bg};
                backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
                border:1px solid {color.replace('0.75','0.3')};
                border-radius:16px;padding:18px 22px;margin-bottom:10px;
                box-shadow:0 8px 24px rgba(0,0,0,0.3);">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:5px;">
                    <span style="color:{color};font-size:1rem;font-weight:800;">{title}</span>
                    <span style="
                        margin-left:auto;
                        background:{color.replace('0.75','0.2')};color:{color};
                        font-size:0.72rem;font-weight:800;padding:3px 10px;
                        border-radius:30px;border:1px solid {color.replace('0.75','0.4')};">
                        {len(found)} found
                    </span>
                </div>
                <div style="color:#8090b0;font-size:0.82rem;">{description}</div>
            </div>""",
            unsafe_allow_html=True,
        )

        if not found:
            st.caption("None in this cohort under the current filter.")
        else:
            # Two worked examples per archetype: one is a claim, two is a pattern.
            for n, student in enumerate(found[:EXAMPLES_PER_ARCHETYPE], start=1):
                st.caption(
                    f"Example {n} of {min(len(found), EXAMPLES_PER_ARCHETYPE)} — "
                    f"**{student['id']} — {student['name']}** ({student['class']})"
                )
                show_trace(student)
                if n < min(len(found), EXAMPLES_PER_ARCHETYPE):
                    st.markdown("")

        st.markdown("---")

# ── Verification (sidebar) ────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("---")
    st.markdown("**🔬 Verification**")
    if not data:
        st.caption("Upload a case file to run the invariants over every case.")
    elif st.checkbox("Run all {} cases".format(len(data["cases"]))):
        with st.spinner("Running invariants over every student in the file…"):
            every, got = score_everything(data)
            students   = [s for c in data["cases"] for s in c["students"]]
            engine.invariants(every, students)
        st.success(f"✅ 4 invariants green over {len(every)} students.")
        st.dataframe(
            pd.DataFrame([
                {"Check": k, "Got": v, "Expected": engine.TARGETS[k],
                 "✓": "✅" if v == engine.TARGETS[k] else "❌"}
                for k, v in got.items()
            ]),
            hide_index=True, width="stretch",
        )

