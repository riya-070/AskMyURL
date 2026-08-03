import streamlit as st
import time
import os
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question
from utils.export_utils import export_to_docx, export_to_pdf

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AskMyURL",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
    --bg: #faf9ff;
    --surface: #ffffff;
    --surface-2: #f2effc;
    --border: #e5dffc;
    --accent: #8b2fef;
    --accent-glow: #a855f7;
    --accent-2: #06b6d4;
    --text: #14121f;
    --text-muted: #635f7a;
    --success: #00b368;
    --warning: #f59e0b;
    --danger: #ef4444;
    --pink: #ec4899;
    --amber: #f59e0b;
    --blue: #3b82f6;
}

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background: var(--bg) !important; }

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(124, 58, 237, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(124, 58, 237, 0.05) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
    animation: drift 30s linear infinite;
}

.stApp::after {
    content: '';
    position: fixed;
    top: -10%; left: -10%;
    width: 60%; height: 60%;
    background: radial-gradient(circle, rgba(139,47,239,0.18), transparent 70%);
    pointer-events: none;
    z-index: 0;
}

.hero-blob-2 {
    position: fixed;
    top: 20%; right: -15%;
    width: 55%; height: 55%;
    background: radial-gradient(circle, rgba(6,182,212,0.16), transparent 70%);
    pointer-events: none;
    z-index: 0;
}

.hero-blob-3 {
    position: fixed;
    bottom: -15%; left: 30%;
    width: 45%; height: 45%;
    background: radial-gradient(circle, rgba(236,72,153,0.14), transparent 70%);
    pointer-events: none;
    z-index: 0;
}

@keyframes drift {
    0% { background-position: 0 0, 0 0; }
    100% { background-position: 40px 40px, 40px 40px; }
}

.card-cyan:hover  { box-shadow: 0 12px 30px rgba(8,145,178,0.20) !important; }
.card-green:hover { box-shadow: 0 12px 30px rgba(5,150,105,0.20) !important; }
.card-amber:hover { box-shadow: 0 12px 30px rgba(217,119,6,0.20) !important; }
.card-pink:hover  { box-shadow: 0 12px 30px rgba(219,39,119,0.20) !important; }
.card-blue:hover  { box-shadow: 0 12px 30px rgba(37,99,235,0.20) !important; }

.badge-amber  { background: rgba(217,119,6,0.15);  color: var(--amber); border: 1px solid rgba(217,119,6,0.3); }
.badge-pink   { background: rgba(219,39,119,0.12);  color: var(--pink);  border: 1px solid rgba(219,39,119,0.3); }
.badge-blue   { background: rgba(37,99,235,0.12);   color: var(--blue);  border: 1px solid rgba(37,99,235,0.3); }

.stSelectbox > div > div:focus-within,
.stTextInput > div > div:has(input:focus) {
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #8b2fef 0%, #6d28d9 45%, #0891b2 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: #ffffff !important; }
[data-testid="stSidebar"] .hero-title {
    background: none !important;
    -webkit-text-fill-color: #ffffff !important;
    color: #ffffff !important;
}
[data-testid="stSidebar"] .hero-sub { color: rgba(255,255,255,0.75) !important; }
[data-testid="stSidebar"] .progress-wrap { background: rgba(255,255,255,0.18) !important; border-color: rgba(255,255,255,0.25) !important; }
[data-testid="stSidebar"] .progress-label { color: rgba(255,255,255,0.85) !important; }

h1, h2, h3, h4, h5, h6 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent-glow) 50%, var(--accent-2) 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shine 6s ease-in-out infinite;
}

@keyframes shine {
    0%, 100% { background-position: 0% center; }
    50% { background-position: 100% center; }
}

.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.6rem 1.7rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(28,28,40,0.05);
    transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
    animation: fadeInUp 0.5s ease both;
}

.card:hover {
    border-color: var(--accent);
    transform: translateY(-4px);
    box-shadow: 0 16px 36px rgba(124,58,237,0.16);
}

.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 6px;
    background: linear-gradient(90deg, var(--accent), var(--accent-glow), var(--accent-2));
    border-radius: 18px 18px 0 0;
}
.card::after {
    content: '';
    position: absolute;
    top: -40%; right: -20%;
    width: 55%; height: 140%;
    background: radial-gradient(circle, rgba(139,47,239,0.08), transparent 70%);
    pointer-events: none;
}

.search-card {
    border: 2px solid transparent !important;
    background:
        linear-gradient(var(--surface), var(--surface)) padding-box,
        linear-gradient(90deg, var(--accent), var(--accent-2), var(--pink), var(--amber)) border-box !important;
    box-shadow: 0 8px 24px rgba(139,47,239,0.15) !important;
}
.search-card::before {
    background: linear-gradient(90deg, var(--accent), var(--accent-2), var(--pink), var(--amber)) !important;
    height: 6px !important;
}

.card-cyan::before   { background: linear-gradient(90deg, var(--accent-2), var(--blue), #60a5fa); }
.card-green::before  { background: linear-gradient(90deg, var(--success), #34d399, #6ee7b7); }
.card-amber::before  { background: linear-gradient(90deg, var(--amber), #fbbf24, #fde047); }
.card-pink::before   { background: linear-gradient(90deg, var(--pink), #f472b6, #f9a8d4); }
.card-blue::before   { background: linear-gradient(90deg, var(--blue), #60a5fa, #93c5fd); }

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}

.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-content {
    font-size: 0.9rem;
    line-height: 1.75;
    color: var(--text);
}

.badge {
    display: inline-block;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.badge-purple { background: rgba(124,58,237,0.2); color: var(--accent-glow); border: 1px solid rgba(124,58,237,0.3); }
.badge-cyan   { background: rgba(6,182,212,0.15); color: var(--accent-2);    border: 1px solid rgba(6,182,212,0.3); }
.badge-green  { background: rgba(16,185,129,0.15); color: var(--success);    border: 1px solid rgba(16,185,129,0.3); }

.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.65rem 1.6rem !important;
    transition: all 0.2s !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 28px rgba(124,58,237,0.35) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}
.stDownloadButton > button {
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* ── Progress / Status ── */
.status-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--surface-2);
    border-radius: 8px;
    margin: 0.4rem 0;
    border: 1px solid var(--border);
    font-size: 0.8rem;
    transition: border-color 0.3s, background 0.3s;
}
.status-bar.is-active { border-color: var(--accent); background: rgba(124,58,237,0.08); }
.status-bar.is-done    { border-color: rgba(16,185,129,0.4); }

.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.dot-active   { background: var(--accent-glow); box-shadow: 0 0 8px var(--accent-glow); animation: pulse 1.2s infinite; }
.dot-done     { background: var(--success); box-shadow: 0 0 6px var(--success); }
.dot-pending  { background: var(--border); }

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(1.3); }
}

.status-check {
    margin-left: auto;
    font-size: 0.8rem;
    color: var(--success);
    opacity: 0;
    animation: popIn 0.3s ease forwards;
}
@keyframes popIn {
    from { opacity: 0; transform: scale(0.5); }
    to   { opacity: 1; transform: scale(1); }
}

.progress-wrap {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 999px;
    height: 10px;
    overflow: hidden;
    margin: 0.75rem 0 1.25rem 0;
}
.progress-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--accent), var(--pink), var(--accent-2), var(--amber));
    background-size: 300% 100%;
    animation: flow 2.5s linear infinite;
    transition: width 0.6s ease;
}
@keyframes flow {
    0% { background-position: 0% 0; }
    100% { background-position: 200% 0; }
}

.progress-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    display: flex;
    justify-content: space-between;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    border-bottom: none;
    padding-bottom: 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    background: var(--surface-2);
    border-radius: 999px;
    padding: 0.6rem 1.3rem;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.8rem;
    color: var(--text-muted);
    border: 1px solid var(--border);
    transition: all 0.2s;
}
.stTabs [data-baseweb="tab"]:hover {
    border-color: var(--accent);
    color: var(--accent);
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
    color: white !important;
    border-color: transparent !important;
    box-shadow: 0 6px 16px rgba(124,58,237,0.3);
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }

/* ── Footer ── */
.app-footer {
    text-align: center;
    padding: 2rem 0 1rem 0;
    color: var(--text-muted);
    font-size: 0.75rem;
    letter-spacing: 0.05em;
}
.chat-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    max-height: 420px;
    overflow-y: auto;
    margin-bottom: 1rem;
}
.chat-msg {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    animation: fadeInUp 0.35s ease both;
}
.chat-row { display: flex; align-items: flex-end; gap: 0.5rem; }
.chat-avatar {
    width: 26px; height: 26px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem;
    flex-shrink: 0;
}
.avatar-user { background: rgba(124,58,237,0.18); }
.avatar-bot  { background: rgba(6,182,212,0.15); }
.chat-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.chat-bubble {
    display: inline-block;
    padding: 0.6rem 1rem;
    border-radius: 10px;
    font-size: 0.85rem;
    line-height: 1.6;
    max-width: 90%;
}
.user-label  { color: var(--accent-glow); }
.bot-label   { color: var(--accent-2); }
.user-bubble { background: rgba(124,58,237,0.15); border: 1px solid rgba(124,58,237,0.25); align-self: flex-end; }
.bot-bubble  { background: rgba(6,182,212,0.1);  border: 1px solid rgba(6,182,212,0.2);   align-self: flex-start; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }

.transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
    font-size: 0.82rem;
    line-height: 1.8;
    max-height: 300px;
    overflow-y: auto;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
}

.stProgress > div > div > div { background: var(--accent) !important; }
.stSpinner > div { border-top-color: var(--accent) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
label { color: var(--text-muted) !important; font-size: 0.8rem !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-blob-2"></div><div class="hero-blob-3"></div>', unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

PIPELINE_STEPS = [
    ("audio",      "🔊", "Audio Processing"),
    ("transcript", "📝", "Transcription"),
    ("title",      "🏷️", "Title Generation"),
    ("summary",    "📋", "Summarisation"),
    ("extract",    "🔍", "Extraction"),
    ("rag",        "🧠", "RAG Engine"),
]

# ─── Helpers ────────────────────────────────────────────────────────────────────
def step_status(steps: dict, key: str) -> str:
    return steps.get(key, "pending")

def render_step_bar(label: str, key: str, icon: str, steps: dict):
    state = step_status(steps, key)
    dot_css = {"active": "dot-active", "done": "dot-done"}.get(state, "dot-pending")
    bar_css = {"active": "is-active", "done": "is-done"}.get(state, "")
    check = '<span class="status-check">✓</span>' if state == "done" else ""
    st.markdown(f"""
    <div class="status-bar {bar_css}">
        <div class="status-dot {dot_css}"></div>
        <span>{icon} {label}</span>
        {check}
    </div>""", unsafe_allow_html=True)

def render_progress_bar(steps: dict):
    total = len(PIPELINE_STEPS)
    done = sum(1 for k, _, _ in PIPELINE_STEPS if steps.get(k) == "done")
    active_label = next((lbl for k, _, lbl in PIPELINE_STEPS if steps.get(k) == "active"), "Starting…")
    pct = int((done / total) * 100)
    st.markdown(f"""
    <div class="progress-label"><span>{active_label}</span><span>{pct}%</span></div>
    <div class="progress-wrap"><div class="progress-fill" style="width:{pct}%"></div></div>
    """, unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:1.6rem">🔗 AskMy<br>URL</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">AI Summarizer & Q&A</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption("👈 This is AskMyURL. Enter your link on the main page to get started.")

    if st.session_state.pipeline_steps:
        st.markdown("---")
        st.markdown('<span class="badge badge-green">Working…</span>', unsafe_allow_html=True)
        render_progress_bar(st.session_state.pipeline_steps)

# ─── Main Area ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:1.1rem;border-bottom:1px solid var(--border);padding-bottom:1.5rem;margin-bottom:1.5rem">
    <div style="width:60px;height:60px;border-radius:16px;flex-shrink:0;
                background:linear-gradient(135deg, var(--accent), var(--accent-glow), var(--accent-2), var(--pink));
                display:flex;align-items:center;justify-content:center;font-size:1.8rem;
                box-shadow:0 8px 22px rgba(139,47,239,0.4)">🔗</div>
    <div>
        <div class="hero-title">AskMyURL</div>
        <div class="hero-sub">AI-Powered URL Summarizer &amp; Question Answering System</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Main input bar ──────────────────────────────────────────────────────────────
st.markdown('<div class="card search-card" style="padding:1.4rem 1.6rem">', unsafe_allow_html=True)
in_col1, in_col2, in_col3 = st.columns([5, 2, 1.5], gap="medium")
with in_col1:
    source = st.text_input(
        "YouTube URL or File Path",
        placeholder="🔗 Paste a YouTube URL or local file path…",
        label_visibility="collapsed",
    )
with in_col2:
    language = st.selectbox("Language", ["english", "hinglish"], index=0, label_visibility="collapsed")
with in_col3:
    run_btn = st.button("⚡ Analyse", use_container_width=True)
st.caption("🌐 English audio → **english**  |  Hindi/mixed audio → **hinglish**")
st.markdown('</div>', unsafe_allow_html=True)

# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Please enter a YouTube URL or file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        live_area = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state
            with live_area.container():
                render_progress_bar(st.session_state.pipeline_steps)

        try:
            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items  = extract_action_items(transcript)
            decisions     = extract_key_decisions(transcript)
            questions     = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            live_area.success("✅ Analysis complete!")
            time.sleep(0.6)
            live_area.empty()
            st.rerun()

        except Exception as e:
            for k, _, _ in PIPELINE_STEPS:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            live_area.error(f"❌ Error: {e}")

# ── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    title_col, reset_col = st.columns([5, 1])
    with title_col:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📌 Session Title</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:var(--text)">
                {r['title']}
            </div>
        </div>""", unsafe_allow_html=True)
    with reset_col:
        st.write("")
        if st.button("🔄 New", use_container_width=True, type="secondary"):
            st.session_state.result = None
            st.session_state.chat_history = []
            st.session_state.pipeline_done = False
            st.session_state.pipeline_steps = {}
            st.rerun()

    word_count = len(r["transcript"].split())
    read_minutes = max(1, round(word_count / 130))
    s1, s2, s3 = st.columns(3, gap="medium")
    with s1:
        st.markdown(f"""
        <div class="card card-blue" style="text-align:center;padding:1rem">
            <div style="font-size:1.6rem;font-weight:800;color:var(--blue)">{word_count:,}</div>
            <div class="card-title" style="justify-content:center;margin-bottom:0">Words Transcribed</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="card card-cyan" style="text-align:center;padding:1rem">
            <div style="font-size:1.6rem;font-weight:800;color:var(--accent-2)">~{read_minutes} min</div>
            <div class="card-title" style="justify-content:center;margin-bottom:0">Est. Read Time</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="card card-green" style="text-align:center;padding:1rem">
            <div style="font-size:1.6rem;font-weight:800;color:var(--success)">✓ Ready</div>
            <div class="card-title" style="justify-content:center;margin-bottom:0">Chat Enabled</div>
        </div>""", unsafe_allow_html=True)

    dl_col1, dl_col2, dl_spacer = st.columns([1, 1, 4])
    with dl_col1:
        st.download_button(
            "⬇️ Download PDF",
            data=export_to_pdf(r),
            file_name=f"{r['title'][:40] or 'meeting-report'}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with dl_col2:
        st.download_button(
            "⬇️ Download DOCX",
            data=export_to_docx(r),
            file_name=f"{r['title'][:40] or 'meeting-report'}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )

    tab_summary, tab_actions, tab_decisions, tab_questions, tab_transcript = st.tabs(
        ["📋 Summary", "✅ Action Items", "🔑 Key Decisions", "❓ Open Questions", "📝 Transcript"]
    )

    with tab_summary:
        st.markdown(f"""
        <div class="card card-cyan">
            <div class="card-content">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)

    with tab_actions:
        st.markdown(f"""
        <div class="card card-green">
            <div class="card-content">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)

    with tab_decisions:
        st.markdown(f"""
        <div class="card card-amber">
            <div class="card-content">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)

    with tab_questions:
        st.markdown(f"""
        <div class="card card-pink">
            <div class="card-content">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    with tab_transcript:
        st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── RAG Chat ──────────────────────────────────────────────────────────────
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:1.2rem;font-weight:700;margin-bottom:1rem">💬 Chat with your Meeting</div>', unsafe_allow_html=True)

    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-end">
                    <span class="chat-label user-label">You</span>
                    <div class="chat-row" style="flex-direction:row-reverse">
                        <div class="chat-avatar avatar-user">🙋</div>
                        <div class="chat-bubble user-bubble">{msg['content']}</div>
                    </div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-start">
                    <span class="chat-label bot-label">Assistant</span>
                    <div class="chat-row">
                        <div class="chat-avatar avatar-bot">🤖</div>
                        <div class="chat-bubble bot-bubble">{msg['content']}</div>
                    </div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:2rem">
            <div style="font-size:2rem;margin-bottom:0.5rem">💬</div>
            <div style="color:var(--text-muted);font-size:0.85rem">Ask anything about your meeting transcript</div>
        </div>""", unsafe_allow_html=True)

    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input("Your question", placeholder="What were the main decisions made?", label_visibility="collapsed")
    with chat_col2:
        send_btn = st.button("Send →", use_container_width=True)

    if not st.session_state.chat_history:
        st.caption("💡 Try: \"Summarize the key points\" · \"What action items were assigned?\" · \"Any deadlines mentioned?\"")

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user",      "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:5rem 2rem;text-align:center">
        <div style="font-size:4rem;margin-bottom:1rem">🔗</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:700;color:var(--text);margin-bottom:0.5rem">
            Ready to Analyse
        </div>
        <div style="color:var(--text-muted);font-size:0.85rem;max-width:380px;line-height:1.7">
            Paste a YouTube URL or local file path in the sidebar, choose your language, and hit <strong>Analyse</strong> to get started.
        </div>
        <div style="margin-top:2rem;display:flex;gap:1rem;flex-wrap:wrap;justify-content:center">
            <span class="badge badge-purple">Transcription</span>
            <span class="badge badge-cyan">Summarisation</span>
            <span class="badge badge-green">RAG Chat</span>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    h1, h2, h3 = st.columns(3, gap="medium")
    with h1:
        st.markdown("""
        <div class="card card-blue" style="text-align:center">
            <div style="font-size:1.6rem">1️⃣</div>
            <div class="card-title" style="justify-content:center;margin-top:0.5rem">Paste a link</div>
            <div class="card-content" style="color:var(--text-muted);font-size:0.8rem">
                Drop a YouTube URL or local file path in the sidebar.
            </div>
        </div>""", unsafe_allow_html=True)
    with h2:
        st.markdown("""
        <div class="card card-amber" style="text-align:center">
            <div style="font-size:1.6rem">2️⃣</div>
            <div class="card-title" style="justify-content:center;margin-top:0.5rem">Pick language & click Analyse</div>
            <div class="card-content" style="color:var(--text-muted);font-size:0.8rem">
                English or Hinglish — then wait a couple of minutes.
            </div>
        </div>""", unsafe_allow_html=True)
    with h3:
        st.markdown("""
        <div class="card card-pink" style="text-align:center">
            <div style="font-size:1.6rem">3️⃣</div>
            <div class="card-title" style="justify-content:center;margin-top:0.5rem">Read, download, or chat</div>
        </div>""", unsafe_allow_html=True)

st.markdown("""
<div class="app-footer">
    🔗 AskMyURL &nbsp;·&nbsp; Built with Streamlit, Whisper, Sarvam AI &amp; Mistral
</div>""", unsafe_allow_html=True)