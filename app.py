<<<<<<< HEAD
﻿import html
import os
import time

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

if "COOKIES_TXT_CONTENT" in os.environ:
    with open("cookies.txt", "w", encoding="utf-8") as cookie_file:
        cookie_file.write(os.environ["COOKIES_TXT_CONTENT"])

from core.analysis import analyse_transcript
from core.rag_engine import ask_question, build_rag_chain
from core.transcriber import transcribe_all
from utils.audio_processor import process_input
from utils.export_utils import export_to_docx, export_to_pdf

st.set_page_config(
    page_title="AskMyURL",
    page_icon="ðŸ”—",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root{
    --ink:#172033;
    --muted:#697386;
    --brand:#4f46e5;
    --brand-dark:#3730a3;
    --brand-light:#eef2ff;
    --line:#e1e5ed;
    --page:#f7f8fb;
    --white:#ffffff;
}

/* Base styling */

*,
*::before,
*::after{
    box-sizing:border-box;
}

html,
body,
.stApp,
[data-testid="stAppViewContainer"]{
    max-width:100%;
    overflow-x:hidden;
}

html,
body,
[class*="css"]{
    font-family:Inter,Arial,sans-serif;
    color:var(--ink);
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"]{
    background:var(--page);
    color:var(--ink);
}

.block-container{
    width:100%;
    max-width:1240px;
    padding:1.5rem 2rem 3rem;
    margin:0 auto;
}

/* Hide default Streamlit interface */

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"],
[data-testid="collapsedControl"]{
    display:none !important;
}

footer{
    visibility:hidden;
}

/* Text and headings */

[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stWidgetLabel"] p,
label{
    color:var(--ink) !important;
}

h1,
h2,
h3,
h4,
[data-testid="stMarkdownContainer"] h4{
    font-family:Inter,Arial,sans-serif !important;
}

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p{
    color:var(--muted) !important;
}

/* Optional sidebar brand classes */

.brand{
    display:flex;
    align-items:center;
    gap:.7rem;
    margin-bottom:1.7rem;
}

.mark{
    width:38px;
    height:38px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:var(--brand);
    color:#ffffff;
    border-radius:10px;
    font-weight:700;
}

.brand-name{
    font-weight:700;
}

.brand-note{
    margin-top:.1rem;
    color:var(--muted);
    font-size:.75rem;
}

/* Hero section */

.hero{
    padding:.25rem 0 1.25rem;
    margin-bottom:1.25rem;
}

.eyebrow{
    color:var(--brand);
    font-size:2.6rem;
    font-weight:800;
    letter-spacing:-.025em;
    line-height:1.15;
    text-transform:none;
}

.hero h1 {
    font-size: clamp(1.8rem, 2.5vw, 2.35rem);
    font-weight: 600;
    letter-spacing: -0.025em;
    line-height: 1.2;
    max-width: 1050px;
    margin: 1rem 0;
}

.hero p{
    max-width:820px;
    margin:0;
    color:var(--muted) !important;
    font-size:1rem;
    line-height:1.65;
}

/* Feature labels */

.feature-row{
    display:flex;
    flex-wrap:wrap;
    gap:10px;
    margin-top:18px;
}

.feature-pill{
    display:inline-flex;
    align-items:center;
    padding:8px 14px;
    background:var(--brand-light);
    color:#4338ca;
    border:1px solid #dfe3ff;
    border-radius:999px;
    font-size:13px;
    font-weight:600;
}

/* Streamlit bordered containers */

div[data-testid="stVerticalBlockBorderWrapper"]{
    padding:8px 10px;
    background:var(--white) !important;
    border:1px solid var(--line) !important;
    border-radius:16px !important;
    box-shadow:0 8px 26px rgba(23,32,51,.045);
}

/* Inputs */

.stTextInput input,
[data-baseweb="select"] > div,
[data-testid="stFileUploaderDropzone"]{
    background:var(--white) !important;
    color:var(--ink) !important;
    border-color:#d8dde7 !important;
    border-radius:11px !important;
}

.stTextInput input{
    min-height:48px;
}

.stTextInput input::placeholder{
    color:#8a93a3 !important;
}

.stTextInput input:focus{
    border-color:var(--brand) !important;
    box-shadow:0 0 0 3px rgba(79,70,229,.10) !important;
}

[data-baseweb="select"] span,
[data-baseweb="select"] svg{
    color:var(--ink) !important;
    fill:var(--ink) !important;
}

[data-testid="stFileUploaderDropzone"]{
    min-height:78px;
    display:flex;
    align-items:center;
}

[data-testid="stFileUploaderDropzone"] button{
    background:var(--white) !important;
    color:var(--ink) !important;
    border:1px solid #d8dde7 !important;
}

/* Standard buttons */

.stButton > button,
[data-testid="stBaseButton-secondary"]{
    min-height:48px;
    background:var(--white) !important;
    color:var(--ink) !important;
    border:1px solid #d8dde7 !important;
    border-radius:10px !important;
    font-weight:600 !important;
    transition:
        transform .15s ease,
        box-shadow .15s ease,
        background .15s ease;
}

.stButton > button p,
[data-testid="stBaseButton-secondary"] p{
    color:var(--ink) !important;
}

.stButton > button[kind="primary"],
[data-testid="stBaseButton-primary"]{
    background:var(--brand) !important;
    color:#ffffff !important;
    border-color:var(--brand) !important;
}

.stButton > button[kind="primary"] p,
[data-testid="stBaseButton-primary"] p{
    color:#ffffff !important;
}

.stButton > button:hover{
    transform:translateY(-1px);
    box-shadow:0 7px 18px rgba(79,70,229,.18);
}

.stButton > button[kind="primary"]:hover,
[data-testid="stBaseButton-primary"]:hover{
    background:var(--brand-dark) !important;
    border-color:var(--brand-dark) !important;
}

/* Download buttons */

div[data-testid="stDownloadButton"] button{
    min-height:48px !important;
    background:var(--brand) !important;
    color:#ffffff !important;
    border:1px solid var(--brand) !important;
    border-radius:10px !important;
    font-weight:700 !important;
}

div[data-testid="stDownloadButton"] button p,
div[data-testid="stDownloadButton"] button span,
div[data-testid="stDownloadButton"] button svg{
    color:#ffffff !important;
    fill:#ffffff !important;
}

div[data-testid="stDownloadButton"] button:hover{
    background:var(--brand-dark) !important;
    border-color:var(--brand-dark) !important;
}

/* Result cards */

.panel,
.metric,
.step{
    background:var(--white);
    border:1px solid var(--line);
    border-radius:13px;
}

.panel{
    padding:1.25rem;
    margin:1rem 0;
    box-shadow:0 5px 18px rgba(23,32,51,.04);
}

.label{
    margin-bottom:.65rem;
    color:var(--muted);
    font-size:.75rem;
    font-weight:700;
    letter-spacing:.07em;
    text-transform:uppercase;
}

.result-title{
    font-size:1.3rem;
    font-weight:700;
}

.copy{
    font-size:.93rem;
    line-height:1.75;
    white-space:pre-wrap;
}

.metric{
    min-height:88px;
    padding:1rem;
}

.metric-value{
    font-size:1.4rem;
    font-weight:700;
}

.metric-label{
    margin-top:.25rem;
    color:var(--muted);
    font-size:.77rem;
}

/* Empty state */

.empty{
    padding:2.2rem 1.5rem;
    margin-top:1.8rem;
    background:var(--white);
    border:1px dashed #cdd3de;
    border-radius:14px;
    text-align:center;
    box-shadow:0 6px 22px rgba(23,32,51,.035);
}

.empty h3{
    margin:.6rem 0 .35rem;
}

.empty p{
    max-width:540px;
    margin:auto;
    color:var(--muted);
    line-height:1.6;
}

/* Steps */

.steps{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:1rem;
    margin-top:1rem;
}

.step{
    min-height:120px;
    padding:1.15rem;
    transition:
        transform .15s ease,
        box-shadow .15s ease;
}

.step:hover{
    transform:translateY(-2px);
    box-shadow:0 8px 22px rgba(23,32,51,.06);
}

.step-no{
    color:var(--brand);
    font-size:.76rem;
    font-weight:700;
}

.step-title{
    margin:.35rem 0;
    font-size:.88rem;
    font-weight:650;
}

.step-copy{
    color:var(--muted);
    font-size:.77rem;
    line-height:1.45;
}

/* Progress indicator */

.progress-row{
    display:flex;
    justify-content:space-between;
    margin:.7rem 0 .4rem;
    color:var(--muted);
    font-size:.76rem;
}

.progress-track{
    height:6px;
    background:#eceff4;
    border-radius:99px;
    overflow:hidden;
}

.progress-fill{
    height:100%;
    background:var(--brand);
}

/* Transcript */

.transcript{
    max-height:360px;
    padding:1rem;
    overflow:auto;
    background:#f8f9fb;
    border:1px solid var(--line);
    border-radius:10px;
    font-size:.87rem;
    line-height:1.7;
    white-space:pre-wrap;
}

/* Chat */

.chat{
    display:flex;
    margin:.7rem 0;
}

.chat.user{
    justify-content:flex-end;
}

.bubble{
    max-width:78%;
    padding:.75rem .9rem;
    background:#eef0f4;
    border-radius:12px;
    font-size:.9rem;
    line-height:1.55;
}

.chat.user .bubble{
    background:var(--brand);
    color:#ffffff;
}

.who{
    margin-bottom:.2rem;
    color:var(--muted);
    font-size:.68rem;
}

.chat.user .who{
    color:#d9dcff;
}

/* Responsive layout */

@media(max-width:1100px){
    .block-container{
        max-width:100%;
        padding-right:1.5rem;
        padding-left:1.5rem;
    }

    .hero h1{
        font-size:2.4rem;
    }
}

@media(max-width:760px){
    .block-container{
        padding:1.2rem 1rem 2rem;
    }

    .hero{
        padding-top:0;
    }

    .hero h1{
        font-size:1.85rem;
    }

    .eyebrow{
        font-size:1.65rem;
    }

    .feature-row{
        gap:7px;
    }

    .feature-pill{
        padding:7px 11px;
        font-size:12px;
    }

    .steps{
        grid-template-columns:1fr;
    }

    .empty{
        padding:1.7rem 1rem;
    }

    .bubble{
        max-width:90%;
    }
}
</style>
""", unsafe_allow_html=True)

for key, default in {"result": None, "chat_history": [], "pipeline_done": False, "pipeline_steps": {}}.items():
    if key not in st.session_state:
        st.session_state[key] = default

STEPS = [
    ("audio", "Preparing audio"), ("transcript", "Creating transcript"),
    ("analysis", "Creating notes"), ("rag", "Preparing Q&A"),
]

def safe(value):
    return html.escape(str(value)).replace("\n", "<br>")

def render_progress(steps):
    done = sum(steps.get(key) == "done" for key, _ in STEPS)
    label = next((label for key, label in STEPS if steps.get(key) == "active"), "Getting started")
    percent = round(done / len(STEPS) * 100)
    st.markdown(f'<div class="progress-row"><span>{label}</span><span>{percent}%</span></div><div class="progress-track"><div class="progress-fill" style="width:{percent}%"></div></div>', unsafe_allow_html=True)

def reset_workspace():
    st.session_state.result = None
    st.session_state.chat_history = []
    st.session_state.pipeline_done = False
    st.session_state.pipeline_steps = {}

with st.sidebar:
    st.markdown('<div class="brand"><div class="mark">â†—</div><div><div class="brand-name">AskMyURL</div><div class="brand-note">Video notes, made useful</div></div></div>', unsafe_allow_html=True)
    st.markdown("**What it does**")
    st.caption("Turns a YouTube video or recording into a transcript, concise notes, and searchable Q&A.")
    st.markdown("**Supported input**")
    st.caption("YouTube links Â· MP3 Â· WAV Â· MP4 Â· M4A Â· WEBM")
    st.markdown("**Languages**")
    st.caption("English and Hindi/Hinglish")
    if st.session_state.pipeline_steps:
        st.divider()
        st.markdown("**Current progress**")
        render_progress(st.session_state.pipeline_steps)

st.markdown("""
<section class="hero">
  <div class="eyebrow" style="font-size:36px !important; font-weight:800;">
    AskMyURL
  </div>

  <h1>Turn long videos into notes you’ll actually use.</h1>

  <p>
    Paste a YouTube link or upload a recording. Get a clear transcript,
    useful notes, and answers without replaying the whole thing.
  </p>

  <div class="feature-row">
    <span class="feature-pill">YouTube & uploads</span>
    <span class="feature-pill">English & Hinglish</span>
    <span class="feature-pill">PDF & DOCX reports</span>
  </div>
</section>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("#### Add your content")
    source = st.text_input("YouTube link", placeholder="https://www.youtube.com/watch?v=...")
    file_col, language_col = st.columns([2.3, 1], gap="large")
    with file_col:
        uploaded_file = st.file_uploader("Or upload an audio/video file", type=["mp3", "wav", "mp4", "m4a", "webm"])
    with language_col:
        language = st.selectbox("Audio language", ["english", "hinglish"], format_func=lambda x: "English" if x == "english" else "Hindi / Hinglish")
    button_col, note_col = st.columns([1, 2.8], gap="large", vertical_alignment="center")
    with button_col:
        run_btn = st.button("Analyse content", type="primary", use_container_width=True)
    with note_col:
        st.caption("Long recordings are processed in smaller sections. Keep this tab open until completion.")

if run_btn:
    if not source.strip() and uploaded_file is None:
        st.error("Add a YouTube link or upload a file before starting.")
    else:
        reset_workspace()
        live_area = st.empty()
        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state
            with live_area.container():
                render_progress(st.session_state.pipeline_steps)
        try:
            update_step("audio", "active")
            if uploaded_file is not None:
                os.makedirs("downloads", exist_ok=True)
                temp_path = os.path.join("downloads", os.path.basename(uploaded_file.name))
                with open(temp_path, "wb") as uploaded_output:
                    uploaded_output.write(uploaded_file.getbuffer())
                chunks = process_input(temp_path)
                update_step("audio", "done")
                update_step("transcript", "active")
                transcript = transcribe_all(chunks, language)
            else:
                from utils.audio_processor import get_youtube_transcript_direct
                update_step("audio", "done")
                update_step("transcript", "active")
                try:
                    # Captions are the fastest path and work well for long videos.
                    transcript = get_youtube_transcript_direct(source.strip())
                    if len(transcript.split()) < 20:
                        raise RuntimeError("The available captions were empty or incomplete")
                except Exception as caption_error:
                    # Videos without usable captions fall back to downloading the
                    # audio and transcribing every 8-minute chunk.
                    print(f"Caption fetch unavailable; using audio transcription: {caption_error}")
                    update_step("audio", "active")
                    chunks = process_input(source.strip())
                    update_step("audio", "done")
                    update_step("transcript", "active")
                    transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")
            update_step("analysis", "active")
            analysis = analyse_transcript(transcript)
            title = analysis["title"]
            summary = analysis["summary"]
            action_items = analysis["action_items"]
            decisions = analysis["key_decisions"]
            questions = analysis["open_questions"]
            update_step("analysis", "done")
            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")
            st.session_state.result = {
                "title": title, "transcript": transcript, "summary": summary,
                "action_items": action_items, "key_decisions": decisions,
                "open_questions": questions, "rag_chain": rag_chain,
                "used_fallback": analysis.get("used_fallback", False),
            }
            st.session_state.pipeline_done = True
            live_area.success("Your notes are ready.")
            time.sleep(.4)
            st.rerun()
        except Exception as error:
            live_area.empty()
            st.error(f"We couldn't process this content: {error}")

if st.session_state.result:
    result = st.session_state.result
    if result.get("used_fallback"):
        st.info("Groq was unavailable, so AskMyURL created these notes using its built-in offline fallback.")
    title_col, new_col = st.columns([4, 1], gap="large")
    with title_col:
        st.markdown(f'<div class="panel"><div class="label">Generated title</div><div class="result-title">{safe(result["title"])}</div></div>', unsafe_allow_html=True)
    with new_col:
        st.write("")
        if st.button("New analysis", use_container_width=True):
            reset_workspace()
            st.rerun()
    word_count = len(str(result["transcript"]).split())
    metric_data = [(f"{word_count:,}", "Words transcribed"), (f"~{max(1, round(word_count/180))} min", "Reading time"), ("Ready", "Content Q&A")]
    for column, (value, label) in zip(st.columns(3), metric_data):
        with column:
            st.markdown(f'<div class="metric"><div class="metric-value">{value}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
    st.markdown("### Download your report")
    st.caption("Export the complete title, summary, action items, decisions, questions, and transcript.")
    export_1, export_2 = st.columns(2)
    filename = "".join(c for c in str(result["title"])[:40] if c.isalnum() or c in " -_").strip() or "askmyurl-notes"
    with export_1:
        st.download_button(
            "â¬‡ Download complete PDF",
            export_to_pdf(result),
            f"{filename}.pdf",
            "application/pdf",
            use_container_width=True,
        )
    with export_2:
        st.download_button(
            "â¬‡ Download editable DOCX",
            export_to_docx(result),
            f"{filename}.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    tabs = st.tabs(["Summary", "Action items", "Key decisions", "Open questions", "Transcript"])
    contents = [result["summary"], result["action_items"], result["key_decisions"], result["open_questions"]]
    for tab, heading, content in zip(tabs[:4], ["Summary", "Action items", "Key decisions", "Open questions"], contents):
        with tab:
            st.markdown(f'<div class="panel"><div class="label">{heading}</div><div class="copy">{safe(content)}</div></div>', unsafe_allow_html=True)
    with tabs[4]:
        st.markdown(f'<div class="transcript">{safe(result["transcript"])}</div>', unsafe_allow_html=True)
    st.markdown("### Ask about this content")
    st.caption("Answers are generated from the transcript, so you can find details without replaying the full video.")
    for message in st.session_state.chat_history:
        role = "user" if message["role"] == "user" else "assistant"
        name = "You" if role == "user" else "AskMyURL"
        st.markdown(f'<div class="chat {role}"><div class="bubble"><div class="who">{name}</div>{safe(message["content"])}</div></div>', unsafe_allow_html=True)
    question_col, send_col = st.columns([5, 1])
    with question_col:
        user_question = st.text_input("Question", placeholder="Ask a question about the transcript...", label_visibility="collapsed")
    with send_col:
        send_btn = st.button("Ask", type="primary", use_container_width=True)
    if send_btn and user_question.strip():
        with st.spinner("Finding the answer..."):
            answer = ask_question(result["rag_chain"], user_question.strip())
        st.session_state.chat_history.extend([{"role": "user", "content": user_question.strip()}, {"role": "assistant", "content": answer}])
        st.rerun()
    if st.session_state.chat_history and st.button("Clear conversation"):
        st.session_state.chat_history = []
        st.rerun()
else:
    st.markdown("""
    <div class="empty"><div style="font-size:1.7rem">▤</div><h3>Your notes will show up here</h3>
    <p>Add a link or recording above. Once it is ready, you can review the summary, search the transcript, and download the complete report.</p></div> 
    <div class="steps">
      <div class="step"><div class="step-no">01</div><div class="step-title">Add content</div><div class="step-copy">Paste a YouTube link or upload a supported media file.</div></div>
      <div class="step"><div class="step-no">02</div><div class="step-title">Review the notes</div><div class="step-copy">Read the summary, action items, decisions, and transcript.</div></div>
      <div class="step"><div class="step-no">03</div><div class="step-title">Ask follow-up questions</div><div class="step-copy">Search the recording conversationally using grounded Q&A.</div></div>
    </div>
    """, unsafe_allow_html=True)

st.caption("AskMyURL · Making long-form content easier to understand")

=======
import streamlit as st
import time
import os
from dotenv import load_dotenv
load_dotenv()   # MUST be before any core/ imports

if "COOKIES_TXT_CONTENT" in os.environ:
    with open("cookies.txt", "w") as f:
        f.write(os.environ["COOKIES_TXT_CONTENT"])
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question
from utils.export_utils import export_to_docx, export_to_pdf

RELAY_URL = os.getenv("RELAY_URL")  # set this only on Streamlit Cloud, points to your ngrok URL

def process_youtube_via_relay(url: str) -> list:
    """Sends the YouTube URL to your home PC (via ngrok) to download,
    since your home IP isn't blocked by YouTube like the cloud server is."""
    import requests
    from utils.audio_processor import chunk_audio
    resp = requests.post(
        f"{RELAY_URL}/download-youtube",
        json={"source": url, "language": "english"},
        timeout=300,
    )
    resp.raise_for_status()
    os.makedirs("downloades", exist_ok=True)
    wav_path = os.path.join("downloades", "relay_download.wav")
    with open(wav_path, "wb") as f:
        f.write(resp.content)
    return chunk_audio(wav_path)
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
    uploaded_file = st.file_uploader("Or upload an audio/video file", type=["mp3", "wav", "mp4", "m4a", "webm"])
with in_col2:
    language = st.selectbox("Language", ["english", "hinglish"], index=0, label_visibility="collapsed")
with in_col3:
    run_btn = st.button("⚡ Analyse", use_container_width=True)
st.caption("🌐 English audio → **english**  |  Hindi/mixed audio → **hinglish**")
st.markdown('</div>', unsafe_allow_html=True)

# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip() and uploaded_file is None:
        st.error("Please enter a YouTube URL or upload a file.")
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
            if uploaded_file is not None:
                update_step("audio", "active")
                os.makedirs("downloades", exist_ok=True)
                temp_path = os.path.join("downloades", uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                chunks = process_input(temp_path)
                update_step("audio", "done")

                update_step("transcript", "active")
                transcript = transcribe_all(chunks, language)
                update_step("transcript", "done")
            else:
                from utils.audio_processor import get_youtube_transcript_direct
                update_step("audio", "active")
                update_step("audio", "done")

                update_step("transcript", "active")
                transcript = get_youtube_transcript_direct(source)
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
>>>>>>> 0060a37186cdc4a4742be5b19c12d34f6ac4d31d
