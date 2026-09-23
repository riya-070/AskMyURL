import html
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

