import streamlit as st
import time
import os
import shutil
import tempfile
try:
    from pipeline import (
        get_files_text,
        get_text_chunks,
        get_vector_store,
        user_input,
        google_api_key,
        groq_api_key,
        groq_api_available,
    )
    PIPELINE_IMPORT_ERROR = None
except Exception as exc:
    # Keep the interface available when an optional AI/backend dependency is
    # missing or damaged; this is useful for local UI previews and diagnosis.
    get_files_text = get_text_chunks = get_vector_store = user_input = None
    PIPELINE_IMPORT_ERROR = str(exc)
    google_api_key = groq_api_key = ""
    groq_api_available = False
from analysis import (
    keyword_frequency_chart,
    document_comparison_chart,
    readability_chart,
    sentence_length_histogram,
    citation_year_timeline,
    chunk_heatmap,
    methodology_card,
    contributions_card,
    limitations_card,
    techstack_card,
    quality_scorecard,
    abstract_comparison_card,
)

# ── Page config ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PaperMind — AI Research Analyst",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;500;600;700&display=swap');

:root {
    --bg:        #080910;
    --bg-1:      #0d0e17;
    --bg-2:      #12131f;
    --bg-3:      #181928;
    --border:    rgba(255,255,255,0.07);
    --border-hi: rgba(255,255,255,0.13);
    --text:      #eceaf8;
    --text-2:    rgba(236,234,248,0.74);
    --text-3:    rgba(236,234,248,0.54);
    --accent:    #7c6fec;
    --accent-2:  #a78bfa;
    --accent-3:  #c4b5fd;
    --teal:      #2dd4bf;
    --green:     #4ade80;
    --red:       #f87171;
    --r-sm:      8px;
    --r-md:      12px;
    --r-lg:      18px;
    --r-xl:      24px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'Geist', sans-serif;
}

[data-testid="stAppViewContainer"] > .main > .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
#MainMenu, footer, header { display: none !important; }
[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 99px; }

/* ── NAVBAR ── */
.pm-nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 9999;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 32px;
    background: rgba(8,9,16,0.8);
    backdrop-filter: blur(24px) saturate(1.4);
    border-bottom: 1px solid var(--border);
}
.pm-nav-logo {
    display: flex;
    align-items: center;
    gap: 10px;
}
.pm-nav-icon {
    width: 28px; height: 28px;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
}
.pm-nav-name {
    font-family: 'Geist', sans-serif;
    font-weight: 700;
    font-size: 16px;
    letter-spacing: -0.4px;
    color: var(--text);
}
.pm-nav-right {
    display: flex;
    align-items: center;
    gap: 12px;
}
.pm-nav-chip {
    font-size: 11px;
    font-weight: 500;
    color: var(--text-2);
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: 99px;
    padding: 4px 12px;
    letter-spacing: 0.3px;
}
.pm-nav-dot {
    width: 6px; height: 6px;
    background: var(--green);
    border-radius: 50%;
    box-shadow: 0 0 6px rgba(74,222,128,0.6);
    display: inline-block;
}
.pm-nav-dot.is-warning {
    background: #fbbf24;
    box-shadow: 0 0 6px rgba(251,191,36,0.55);
}
.pm-nav-dot.is-error {
    background: var(--red);
    box-shadow: 0 0 6px rgba(248,113,113,0.55);
}

/* ── HERO ── */
.pm-hero {
    min-height: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 56px 24px 8px;
    position: relative;
    margin-top: 0;
}
[data-testid="stFileUploader"] {
    margin-bottom: 24px !important;
}
.pm-hero-glow {
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 60% 45% at 50% 0%, rgba(124,111,236,0.14) 0%, transparent 70%),
        radial-gradient(ellipse 35% 35% at 85% 55%, rgba(167,139,250,0.07) 0%, transparent 65%),
        radial-gradient(ellipse 25% 25% at 15% 65%, rgba(45,212,191,0.05) 0%, transparent 60%);
}
.pm-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--accent-2);
    margin-bottom: 20px;
}
.pm-eyebrow-line {
    width: 28px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent));
}
.pm-eyebrow-line.r { background: linear-gradient(90deg, var(--accent), transparent); }

.pm-h1 {
    font-family: 'Geist', sans-serif;
    font-weight: 700;
    font-size: clamp(36px, 5.5vw, 68px);
    line-height: 1.08;
    letter-spacing: -2.5px;
    color: var(--text);
    margin-bottom: 14px;
    max-width: 760px;
}
/* Streamlit adds a permalink control beside Markdown headings. */
[data-testid="stHeaderActionElements"] { display: none !important; }
.pm-h1 em {
    font-family: 'Instrument Serif', serif;
    font-style: italic;
    font-weight: 400;
    background: linear-gradient(110deg, var(--accent-3) 0%, var(--accent) 50%, var(--teal) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
}
.pm-sub {
    font-size: 17px;
    font-weight: 300;
    line-height: 1.75;
    color: var(--text-2);
    max-width: 500px;
    margin-bottom: 28px;
}
.pm-pills {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    justify-content: center;
    margin: 18px auto 0;
    max-width: 760px;
}
.pm-pill {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-3);
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border);
    border-radius: 99px;
    padding: 5px 13px;
}
.pm-pill span {
    color: var(--accent-2);
    margin-right: 5px;
}

/* ── UPLOAD CARD ── */
.pm-upload-wrap {
    width: 100%;
    max-width: 680px;
    margin: 0 auto;
}
.st-key-upload-card {
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: var(--r-xl);
    padding: 24px 28px;
    width: 100%;
    max-width: 840px;
    margin: 0 auto;
    position: relative;
    overflow: hidden;
}
.st-key-upload-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 10%, var(--accent) 50%, transparent 90%);
    opacity: 0.4;
}
.pm-upload-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-3);
    margin-bottom: 20px;
    display: block;
}
.pm-file-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 12px 0;
}
.pm-file-tag {
    font-size: 12px;
    font-weight: 500;
    color: var(--accent-3);
    background: rgba(124,111,236,0.1);
    border: 1px solid rgba(124,111,236,0.2);
    border-radius: 99px;
    padding: 4px 12px;
    display: flex;
    align-items: center;
    gap: 5px;
}

/* ── STAT BAR ── */
.pm-stat-bar {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--border);
    border-radius: var(--r-md);
    overflow: hidden;
    margin-bottom: 28px;
}
.pm-stat {
    background: var(--bg-1);
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.pm-stat-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-3);
}
.pm-stat-value {
    font-family: 'Geist', sans-serif;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -1px;
    color: var(--accent-3);
}

/* ── WORKSPACE SECTION HEADER ── */
.pm-workspace-title {
    font-family: 'Geist', sans-serif;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.7px;
    color: var(--text);
    margin-bottom: 4px;
}
.pm-section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}
.pm-section-title {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: -0.2px;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 8px;
}
.pm-section-badge {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    padding: 3px 9px;
    border-radius: 99px;
}
.pm-badge-green {
    color: var(--green);
    background: rgba(74,222,128,0.08);
    border: 1px solid rgba(74,222,128,0.15);
}
.pm-badge-purple {
    color: var(--accent-2);
    background: rgba(124,111,236,0.1);
    border: 1px solid rgba(124,111,236,0.2);
}

/* ── CHAT AREA ── */
.pm-chat-panel {
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: var(--r-xl);
    overflow: hidden;
}
.pm-chat-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.pm-chat-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 60px 24px;
    text-align: center;
}
.pm-chat-empty-icon {
    width: 52px; height: 52px;
    background: rgba(124,111,236,0.08);
    border: 1px solid rgba(124,111,236,0.15);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    margin-bottom: 6px;
}
.pm-chat-empty-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-2);
    letter-spacing: -0.3px;
}
.pm-chat-empty-sub {
    font-size: 13px;
    font-weight: 300;
    color: var(--text-3);
    max-width: 220px;
    line-height: 1.6;
}

/* ── MESSAGES ── */
.msg-wrap-user {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 10px;
}
.msg-wrap-ai {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 10px;
}
.msg-user {
    max-width: 78%;
    background: linear-gradient(135deg, rgba(124,111,236,0.22), rgba(167,139,250,0.15));
    border: 1px solid rgba(124,111,236,0.22);
    border-radius: 16px 16px 4px 16px;
    padding: 11px 15px;
    font-size: 14px;
    line-height: 1.55;
    color: var(--text);
}
.msg-ai-wrap {
    max-width: 88%;
}
.msg-ai-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--accent);
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 6px;
    padding-left: 2px;
}
.msg-ai-dot {
    width: 5px; height: 5px;
    background: var(--accent);
    border-radius: 50%;
    animation: aipulse 2.2s ease-in-out infinite;
}
@keyframes aipulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.75); }
}
.msg-ai {
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: 4px 16px 16px 16px;
    padding: 12px 15px;
    font-size: 14px;
    font-weight: 300;
    line-height: 1.7;
    color: rgba(236,234,248,0.82);
}

/* ── SUGGESTION CHIPS ── */
.pm-sugg-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-3);
    padding: 0 2px;
    margin-bottom: 8px;
}

/* ── ANALYSIS PANEL ── */
.pm-analysis-panel {
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: var(--r-xl);
    overflow: hidden;
}
.pm-analysis-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.pm-analysis-promo {
    background: linear-gradient(135deg, rgba(124,111,236,0.07), rgba(45,212,191,0.04));
    border: 1px solid rgba(124,111,236,0.13);
    border-radius: var(--r-lg);
    padding: 32px 24px;
    text-align: center;
    margin: 20px;
}
.pm-promo-icon {
    font-size: 32px;
    margin-bottom: 14px;
    display: block;
}
.pm-promo-title {
    font-size: 16px;
    font-weight: 700;
    letter-spacing: -0.4px;
    color: var(--text);
    margin-bottom: 8px;
}
.pm-promo-sub {
    font-size: 13px;
    font-weight: 300;
    line-height: 1.65;
    color: var(--text-2);
    max-width: 340px;
    margin: 0 auto 20px;
}

/* ── BUTTONS ── */
.stButton > button {
    font-family: 'Geist', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: -0.2px !important;
    border-radius: var(--r-md) !important;
    padding: 10px 20px !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
}

/* Primary variant — applied via key naming convention */
.stButton[data-testid*="primary"] > button,
button[kind="primary"] {
    background: linear-gradient(135deg, #7c6fec, #a78bfa) !important;
    color: #0d0e17 !important;
    border: none !important;
}
button[kind="primary"]:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(124,111,236,0.35) !important;
}

/* Default ghost buttons */
.stButton > button {
    background: rgba(255,255,255,0.03) !important;
    color: var(--text-2) !important;
    border: 1px solid var(--border) !important;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.06) !important;
    border-color: var(--border-hi) !important;
    color: var(--text) !important;
}
.stButton > button:active {
    transform: scale(0.985) !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInputContainer"] {
    padding: 12px 16px !important;
    background: var(--bg-2) !important;
    border-top: 1px solid var(--border) !important;
}
[data-testid="stChatInput"] {
    background: var(--bg-3) !important;
    border: 1px solid var(--border-hi) !important;
    border-radius: var(--r-md) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--text) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 14px !important;
    font-weight: 300 !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--text-3) !important; }

/* ── PROVIDER KEY INPUTS ── */
[data-testid="stTextInput"] label {
    color: var(--text-2) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 13px !important;
}
[data-testid="stTextInput"] input {
    color: var(--text) !important;
    background: var(--bg-3) !important;
    border-color: var(--border-hi) !important;
}
[data-testid="stTextInput"] input::placeholder { color: var(--text-3) !important; }
[data-testid="stTextInput"] button {
    color: var(--text-2) !important;
    background: transparent !important;
    border: 0 !important;
}
label {
    color: var(--text-2) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 13px !important;
}
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid*="TextInput"] label {
    color: var(--text-2) !important;
}
[data-baseweb="input"],
[data-baseweb="base-input"] {
    background: var(--bg-3) !important;
    border-color: var(--border-hi) !important;
}
input[type="password"],
input[type="text"],
input[type="email"] {
    color: var(--text) !important;
    background: var(--bg-3) !important;
    border-color: var(--border-hi) !important;
}
input[type="password"]::placeholder,
input[type="text"]::placeholder,
input[type="email"]::placeholder { color: var(--text-3) !important; }
form button:not([aria-label]) {
    color: #0d0e17 !important;
    background: linear-gradient(135deg, #7c6fec, #a78bfa) !important;
    border: 0 !important;
    border-radius: var(--r-md) !important;
    min-height: 42px;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] section {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed rgba(124,111,236,0.25) !important;
    border-radius: var(--r-md) !important;
}
[data-testid="stFileUploader"] label { display: none !important; }
[data-testid="stFileUploader"] * { color: var(--text-2) !important; }
[data-testid="stFileUploaderDropzone"] {
    padding: 28px 20px !important;
}
[data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stFileUploaderDropzoneInstructions"] * {
    color: var(--text-2) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 13px !important;
    font-weight: 400 !important;
}
[data-testid="stFileUploaderDropzone"] button {
    color: var(--text) !important;
    background: var(--bg-3) !important;
    border: 1px solid var(--border-hi) !important;
}
[data-testid="stFileUploader"] button {
    color: var(--text) !important;
    background: var(--bg-3) !important;
    border: 1px solid var(--border-hi) !important;
}
[data-testid="stFileUploaderDropzone"] button * {
    color: inherit !important;
    background: transparent !important;
    border: 0 !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] { background: transparent !important; }
[data-testid="stMetricValue"] {
    font-family: 'Geist', sans-serif !important;
    font-weight: 700 !important;
    font-size: 26px !important;
    letter-spacing: -1px !important;
    color: var(--accent-3) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: var(--text-3) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    padding: 3px !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px !important;
    color: var(--text-3) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 5px 12px !important;
    letter-spacing: -0.1px !important;
    border: none !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(124,111,236,0.15) !important;
    color: var(--accent-3) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 16px 0 0 !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.015) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Geist', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--text) !important;
    background: var(--bg-2) !important;
    padding: 14px 18px !important;
}
[data-testid="stExpander"] summary:hover { background: var(--bg-3) !important; }

/* ── SPINNER ── */
[data-testid="stSpinner"] p {
    font-family: 'Geist', sans-serif !important;
    font-size: 12px !important;
    color: var(--text-3) !important;
}

/* ── ALERTS / INFO ── */
.stAlert {
    background: rgba(124,111,236,0.07) !important;
    border: 1px solid rgba(124,111,236,0.15) !important;
    border-radius: var(--r-md) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 13px !important;
    color: var(--text-2) !important;
}

/* ── STATUS WIDGET ── */
[data-testid="stStatusWidget"] {
    background: var(--bg-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important;
    font-family: 'Geist', sans-serif !important;
    color: var(--text-2) !important;
}

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; margin: 0 !important; }

/* ── PLOTLY BACKGROUND FIX ── */
.js-plotly-plot .plotly,
.plot-container,
.plotly-graph-div { background: transparent !important; }

/* ── CAPTION ── */
[data-testid="stCaptionContainer"] {
    font-family: 'Geist', sans-serif !important;
    font-size: 12px !important;
    color: var(--text-3) !important;
}

/* ── CHAT MESSAGE OVERRIDE ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 0 !important;
    gap: 10px !important;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
    font-family: 'Geist', sans-serif !important;
    font-size: 14px !important;
    font-weight: 300 !important;
    line-height: 1.7 !important;
    color: rgba(236,234,248,0.82) !important;
}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stMarkdownContainer"] p {
    color: var(--text) !important;
    font-weight: 400 !important;
}

/* Keep keyboard focus visible across Streamlit controls. */
button:focus-visible,
a:focus-visible,
input:focus-visible,
textarea:focus-visible,
summary:focus-visible,
[role="tab"]:focus-visible {
    outline: 2px solid var(--accent-3) !important;
    outline-offset: 3px !important;
    box-shadow: 0 0 0 4px rgba(167,139,250,0.18) !important;
}
.stButton > button:disabled {
    color: var(--text-2) !important;
    opacity: 0.72 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

@media (max-width: 640px) {
    .pm-nav {
        height: 54px;
        padding: 0 16px;
    }
    .pm-nav-right { gap: 7px; }
    .pm-nav-chip {
        max-width: calc(100vw - 132px);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 10px;
        padding: 4px 9px;
    }
    .pm-hero { padding: 78px 18px 8px; }
    .pm-h1 {
        font-size: clamp(34px, 9vw, 46px);
        letter-spacing: -1.4px;
    }
    .pm-sub { font-size: 15px; line-height: 1.65; }
    .st-key-upload-card {
        padding: 18px 16px;
        border-radius: 18px;
    }
    [data-testid="stFileUploaderDropzone"] { padding: 20px 12px !important; }
    .pm-pill { font-size: 11px; padding: 5px 10px; }
    .pm-workspace-title { font-size: 21px; }
    .pm-section-header { align-items: flex-start; gap: 8px; }
    .pm-section-badge { white-space: nowrap; }
    [data-testid="stMetricValue"] { font-size: 22px !important; }
    [data-testid="stMetricLabel"] {
        font-size: 10px !important;
        letter-spacing: 0.4px !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 0 0 auto !important;
        font-size: 11px !important;
        padding: 5px 9px !important;
        white-space: nowrap !important;
    }
    .pm-chat-empty { padding: 36px 16px; }
    .stButton > button { min-height: 44px; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        scroll-behavior: auto !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
""", unsafe_allow_html=True)


# ── Session state ────────────────────────────────────────────────────────────────
_defaults = {
    "chat_history":       [],
    "file_stats":         [],
    "combined_text":      "",
    "total_chunks":       0,
    "retrieved_chunks":   [],
    "show_workspace":     False,
    "vector_store_dir":   None,
    # Analysis result cache — prevents re-firing on tab switch
    "cache_methodology":  None,
    "cache_contributions":None,
    "cache_limitations":  None,
    "cache_techstack":    None,
    "cache_quality":      None,
    "cache_abstract":     None,
    "deep_analysis_run":  False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state.vector_store_dir:
    st.session_state.vector_store_dir = tempfile.mkdtemp(prefix="papermind-index-")


def _active_google_key():
    return st.session_state.get("google_api_key_input", "").strip() or google_api_key


def _active_groq_key():
    return st.session_state.get("groq_api_key_input", "").strip() or groq_api_key


def _session_user_input(question):
    return user_input(
        question,
        google_key=_active_google_key(),
        groq_key=_active_groq_key(),
        index_dir=st.session_state.vector_store_dir,
    )


GOOGLE_API_CONFIGURED = bool(_active_google_key())
GROQ_API_CONFIGURED = bool(_active_groq_key()) and groq_api_available


# ── Navbar (always shown) ────────────────────────────────────────────────────────
if PIPELINE_IMPORT_ERROR:
    backend_status = "AI backend unavailable"
    backend_status_class = "is-error"
elif not GOOGLE_API_CONFIGURED:
    backend_status = "Google API key needed"
    backend_status_class = "is-warning"
else:
    backend_status = "Gemini key configured"
    if GROQ_API_CONFIGURED:
        backend_status += " · Groq fallback configured"
    backend_status_class = ""

st.markdown(f"""
<div class="pm-nav">
    <div class="pm-nav-logo">
        <div class="pm-nav-icon">🧠</div>
        <span class="pm-nav-name">PaperMind</span>
    </div>
    <div class="pm-nav-right">
        <span class="pm-nav-chip">{backend_status}</span>
        <span class="pm-nav-dot {backend_status_class}"></span>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("🔑 Configure AI provider keys", expanded=not GOOGLE_API_CONFIGURED):
    with st.form("provider_keys_form"):
        st.text_input(
            "Google Gemini API key",
            type="password",
            key="google_api_key_input",
            placeholder="Paste your Google AI Studio key",
            help="Required for document embeddings and the primary AI responses.",
        )
        st.text_input(
            "Groq API key (optional fallback)",
            type="password",
            key="groq_api_key_input",
            placeholder="Paste your Groq key to enable fallback",
            help="Used for answer generation if Gemini's response hits quota. Gemini is still required for document and query embeddings.",
        )
        keys_submitted = st.form_submit_button("Save keys for this session", type="primary", use_container_width=True)
    st.caption("Keys stay in this app session and are not written to project files. Paper text is sent to Gemini for embeddings and answers; a per-session local index is used for retrieval. If Gemini's answer generation hits quota, retrieved text and your question are sent to Groq when a fallback key is configured. Gemini is still needed to create embeddings. When hosted remotely, use HTTPS and a host you trust.")
    if keys_submitted:
        if not GOOGLE_API_CONFIGURED:
            st.warning("A Google Gemini key is required to create document embeddings. Groq alone cannot index papers.")
        elif _active_groq_key() and not groq_api_available:
            st.warning("The Groq key is saved for this session, but the Groq integration is unavailable in this environment.")
        elif GROQ_API_CONFIGURED:
            st.success("Gemini and Groq keys are available for this session.")
        else:
            st.success("Gemini key is available for this session. Groq fallback is optional.")


# ════════════════════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════════════════════
if not st.session_state.show_workspace:

    # No spacer here as hero has its own padding and flex centering

    st.markdown("""
    <div class="pm-hero">
        <div class="pm-hero-glow"></div>
        <div class="pm-eyebrow">
            <span class="pm-eyebrow-line"></span>
            AI-Powered Research Intelligence
            <span class="pm-eyebrow-line r"></span>
        </div>
        <h1 class="pm-h1">Understand papers,<br/><em>not just read them</em></h1>
        <p class="pm-sub">Upload your research PDFs or DOCX files and get instant deep analysis, methodology breakdowns, and an AI chat assistant trained on your documents.</p>
    </div>
    """, unsafe_allow_html=True)

    # Upload card — full-width wrapper with a centered max-width card
    col_center = st.container()
    with col_center:
        with st.container(key="upload-card"):
            st.markdown('<div class="pm-upload-title">Drop Your Research Papers</div>', unsafe_allow_html=True)

            uploaded_files = st.file_uploader(
                "Upload files",
                accept_multiple_files=True,
                type=["pdf", "docx"],
                label_visibility="collapsed",
                disabled=PIPELINE_IMPORT_ERROR is not None,
            )

            st.caption("PDF or DOCX · Up to 200 MB per file")
            st.caption("After upload, PaperMind extracts the text and builds a searchable index for analysis and chat. Document text is sent to Google Gemini for embeddings and answers.")

            if PIPELINE_IMPORT_ERROR:
                st.error("The document-processing backend could not be loaded, so uploads and analysis are unavailable.")
                with st.expander("Technical details"):
                    st.code(PIPELINE_IMPORT_ERROR)
            elif not GOOGLE_API_CONFIGURED:
                st.warning("Add a Google Gemini key in “Configure AI provider keys” to enable analysis. Groq alone cannot create the document embeddings needed for search.")

            if uploaded_files:
                tags_html = "".join(
                    f'<span class="pm-file-tag">📄 {f.name}</span>'
                    for f in uploaded_files
                )
                st.markdown(f'<div class="pm-file-tags">{tags_html}</div>', unsafe_allow_html=True)
                st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

            if st.button(
                "⚡  Analyze Papers",
                disabled=not uploaded_files or PIPELINE_IMPORT_ERROR is not None or not GOOGLE_API_CONFIGURED,
                type="primary",
                use_container_width=True,
            ):
                with st.status("Processing your research papers…", expanded=True) as status:
                    st.write("📄 Extracting text from documents…")
                    raw_text = get_files_text(uploaded_files)

                    st.write("✂️ Splitting into semantic chunks…")
                    text_chunks = get_text_chunks(raw_text)

                    st.write("🔗 Building vector embeddings…")
                    index_ready = get_vector_store(
                        text_chunks,
                        google_key=_active_google_key(),
                        index_dir=st.session_state.vector_store_dir,
                    )

                    if text_chunks and index_ready:
                        st.session_state.combined_text = raw_text
                        st.session_state.total_chunks  = len(text_chunks)
                        st.session_state.show_workspace = True
                        status.update(label="✅ Ready — opening workspace…", state="complete", expanded=False)
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.error("PaperMind could not finish indexing these papers. Check that the files contain readable text and that the Google API key is valid, then try again.")
                        status.update(label="⚠️ Indexing failed — workspace not opened.", state="error")

    st.markdown("""
    <div class="pm-pills">
        <span class="pm-pill"><span>◈</span>Methodology Extraction</span>
        <span class="pm-pill"><span>◈</span>Key Contributions</span>
        <span class="pm-pill"><span>◈</span>Research Gaps</span>
        <span class="pm-pill"><span>◈</span>Quality Scorecard</span>
        <span class="pm-pill"><span>◈</span>Tech Stack Mapping</span>
    </div>
    """, unsafe_allow_html=True)

    # Bottom breathing room
    st.markdown('<div style="height:48px;"></div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# WORKSPACE
# ════════════════════════════════════════════════════════════════════════════════
else:
    st.markdown('<div style="height:72px;"></div>', unsafe_allow_html=True)

    # ── Outer padding wrapper ──────────────────────────────────────────────────
    with st.container():
        _, inner, _ = st.columns([0.03, 0.94, 0.03])
        with inner:

            st.markdown('<div class="pm-workspace-title">Research workspace</div>', unsafe_allow_html=True)
            st.caption("Your uploaded papers are indexed for chat and analysis. Use the document list to check which sources are included.")

            if st.session_state.file_stats:
                with st.expander(f"📚 Indexed papers · {len(st.session_state.file_stats)}", expanded=False):
                    for paper in st.session_state.file_stats:
                        with st.container(border=True):
                            st.text(paper.get("name", "Untitled document"))
                            st.caption(f"{paper.get('word_count', 0):,} words")

            # ── Stats bar ─────────────────────────────────────────────────────
            word_count = len(st.session_state.combined_text.split()) if st.session_state.combined_text else 0
            c1, c2, c3, c4 = st.columns(4, gap="small")
            with c1:
                st.metric("Words",  f"{word_count:,}" if word_count else "—")
            with c2:
                st.metric("Chunks", st.session_state.total_chunks or "—")
            with c3:
                st.metric("Files",  len(st.session_state.file_stats) or "—")
            with c4:
                st.metric("Turns",  len(st.session_state.chat_history) or "—")

            st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
            st.divider()
            st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

            # ── Two columns ───────────────────────────────────────────────────
            col_chat, col_analysis = st.columns([1, 1], gap="large")

            # ================================================================
            # LEFT — CHAT
            # ================================================================
            with col_chat:
                st.markdown("""
                <div class="pm-section-header">
                    <span class="pm-section-title">💬 Chat Assistant</span>
                    <span class="pm-section-badge pm-badge-green">● Indexed</span>
                </div>
                """, unsafe_allow_html=True)

                # Chat history container
                chat_box = st.container(height=440, border=False)
                with chat_box:
                    if not st.session_state.chat_history:
                        st.markdown("""
                        <div class="pm-chat-empty">
                            <div class="pm-chat-empty-icon">🧠</div>
                            <div class="pm-chat-empty-title">Ready to answer your questions</div>
                            <div class="pm-chat-empty-sub">Your documents are indexed. Ask anything below or pick a suggestion.</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        for question, answer in st.session_state.chat_history:
                            # User bubble
                            st.markdown(f"""
                            <div class="msg-wrap-user">
                                <div class="msg-user">{question}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            # AI bubble
                            st.markdown(f"""
                            <div class="msg-wrap-ai">
                                <div class="msg-ai-wrap">
                                    <div class="msg-ai-label">
                                        <span class="msg-ai-dot"></span> PaperMind
                                    </div>
                                    <div class="msg-ai">{answer}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                # Suggested queries — only when empty
                if not st.session_state.chat_history:
                    st.markdown('<div class="pm-sugg-label">Suggested questions</div>', unsafe_allow_html=True)
                    suggestions = [
                        "Compare the methodologies used across the documents",
                        "What are the key contributions of each paper?",
                        "What limitations or research gaps are mentioned?",
                        "Summarize the technical approach in plain language",
                    ]
                    for s in suggestions:
                        if st.button(s, key=f"sugg_{s}", use_container_width=True):
                            with st.spinner(""):
                                _session_user_input(s)
                            st.rerun()

                # Chat input — at bottom of panel (Streamlit renders this at page bottom)
                st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
                user_query = st.chat_input("Ask anything about your research papers…")
                if user_query:
                    with st.spinner(""):
                        _session_user_input(user_query)
                    st.rerun()

                # Action row
                st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
                a1, a2 = st.columns(2, gap="small")
                with a1:
                    if st.button("🗑  Clear Chat", use_container_width=True, key="clear_chat"):
                        st.session_state.chat_history    = []
                        st.session_state.retrieved_chunks = []
                        st.rerun()
                with a2:
                    if st.button("↩  New Session", use_container_width=True, key="new_session"):
                        old_index_dir = st.session_state.get("vector_store_dir")
                        if old_index_dir and os.path.basename(old_index_dir).startswith("papermind-index-"):
                            shutil.rmtree(old_index_dir, ignore_errors=True)
                        for k, v in _defaults.items():
                            st.session_state[k] = v
                        st.rerun()

            # ================================================================
            # RIGHT — ANALYSIS
            # ================================================================
            with col_analysis:
                st.markdown("""
                <div class="pm-section-header">
                    <span class="pm-section-title">📊 Deep Analysis</span>
                    <span class="pm-section-badge pm-badge-purple">6 insight views</span>
                </div>
                """, unsafe_allow_html=True)

                doc_names = [f.get("name", "Unknown") for f in st.session_state.file_stats]

                # ── Promo state ────────────────────────────────────────────
                if not st.session_state.deep_analysis_run:
                    st.markdown("""
                    <div class="pm-analysis-promo">
                        <span class="pm-promo-icon">🔬</span>
                        <div class="pm-promo-title">AI Technical Analysis</div>
                        <div class="pm-promo-sub">Extract methodology, key contributions, research gaps, tech stack, quality scores, and structured abstracts — in one click.</div>
                        <div class="pm-promo-sub">Analysis is generated on demand and may take a little while for longer papers.</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🔍  Run Deep Analysis", type="primary", use_container_width=True, key="run_analysis"):
                        # Clear cached results so fresh run is triggered
                        for key in ["cache_methodology","cache_contributions","cache_limitations",
                                    "cache_techstack","cache_quality","cache_abstract"]:
                            st.session_state[key] = None
                        st.session_state.deep_analysis_run = True
                        st.rerun()

                # ── Analysis tabs ──────────────────────────────────────────
                else:
                    tabs = st.tabs(["🧪 Method", "🏆 Contributions", "⚠️ Gaps", "🛠 Tech Stack", "📈 Quality", "📝 Abstract"])

                    with tabs[0]:
                        if st.session_state.cache_methodology is None:
                            with st.spinner("Analyzing methodology…"):
                                methodology_card(_session_user_input, doc_names)
                            st.session_state.cache_methodology = True
                        else:
                            methodology_card(_session_user_input, doc_names)

                    with tabs[1]:
                        if st.session_state.cache_contributions is None:
                            with st.spinner("Extracting contributions…"):
                                contributions_card(_session_user_input, doc_names)
                            st.session_state.cache_contributions = True
                        else:
                            contributions_card(_session_user_input, doc_names)

                    with tabs[2]:
                        if st.session_state.cache_limitations is None:
                            with st.spinner("Identifying limitations…"):
                                limitations_card(_session_user_input, doc_names)
                            st.session_state.cache_limitations = True
                        else:
                            limitations_card(_session_user_input, doc_names)

                    with tabs[3]:
                        if st.session_state.cache_techstack is None:
                            with st.spinner("Mapping tech stack…"):
                                techstack_card(_session_user_input, doc_names)
                            st.session_state.cache_techstack = True
                        else:
                            techstack_card(_session_user_input, doc_names)

                    with tabs[4]:
                        if st.session_state.cache_quality is None:
                            with st.spinner("Scoring quality…"):
                                quality_scorecard(_session_user_input, doc_names)
                            st.session_state.cache_quality = True
                        else:
                            quality_scorecard(_session_user_input, doc_names)

                    with tabs[5]:
                        if st.session_state.cache_abstract is None:
                            with st.spinner("Building abstracts…"):
                                abstract_comparison_card(_session_user_input, doc_names)
                            st.session_state.cache_abstract = True
                        else:
                            abstract_comparison_card(_session_user_input, doc_names)

                    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
                    if st.button("🔄  Refresh Analysis", use_container_width=True, key="refresh_analysis"):
                        for key in ["cache_methodology","cache_contributions","cache_limitations",
                                    "cache_techstack","cache_quality","cache_abstract"]:
                            st.session_state[key] = None
                        st.rerun()

                # ── Statistical charts ─────────────────────────────────────
                st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)
                with st.expander("📈 Statistical Analysis"):
                    chart_tabs = st.tabs(["Keywords", "Documents", "Readability", "Sentences", "Chunks"])

                    with chart_tabs[0]:
                        fig = keyword_frequency_chart(st.session_state.combined_text)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Not enough keywords detected.")

                    with chart_tabs[1]:
                        fig = document_comparison_chart(st.session_state.file_stats)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Need at least two documents to compare.")

                    with chart_tabs[2]:
                        fig = readability_chart(st.session_state.file_stats)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                            st.caption("Flesch Reading Ease — 0–30: very difficult · 60–70: standard · 90+: very easy")
                        else:
                            st.info("Not enough text to calculate readability.")

                    with chart_tabs[3]:
                        fig1 = sentence_length_histogram(st.session_state.combined_text)
                        if fig1:
                            st.plotly_chart(fig1, use_container_width=True)
                        fig2 = citation_year_timeline(st.session_state.combined_text)
                        if fig2:
                            st.plotly_chart(fig2, use_container_width=True)
                        else:
                            st.info("Not enough citation years detected.")

                    with chart_tabs[4]:
                        fig = chunk_heatmap(
                            st.session_state.get("total_chunks", 0),
                            st.session_state.get("retrieved_chunks", []),
                        )
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                            st.caption("Purple cells = chunks retrieved for your last question.")
                        else:
                            st.info("Ask a question first to see the retrieval map.")

        # Bottom padding
        st.markdown('<div style="height:60px;"></div>', unsafe_allow_html=True)
