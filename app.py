import html
import os
import time

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Streamlit Cloud normally exposes root-level secrets as environment variables,
# but copy them explicitly as well so every imported service sees the same values.
try:
    for secret_name in ("GROQ_API_KEY", "GROQ_MODEL", "GROQ_STT_MODEL", "SARVAM_API_KEY"):
        if not os.getenv(secret_name) and secret_name in st.secrets:
            os.environ[secret_name] = str(st.secrets[secret_name]).strip()
except Exception:
    pass

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
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root {--ink:#172033;--muted:#697386;--brand:#4f46e5;--dark:#3730a3;--line:#e5e9f0;--page:#f7f8fb}
html,body,[class*="css"]{font-family:Inter,sans-serif;color:var(--ink)}
html,body,.stApp,[data-testid="stAppViewContainer"]{max-width:100%;overflow-x:hidden}
*,*::before,*::after{box-sizing:border-box}
.stApp{background:var(--page);color:var(--ink)}
.block-container{width:100%;max-width:980px;padding:2rem 2rem 3rem;margin:0 auto}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none!important}
[data-testid="stAppViewContainer"], [data-testid="stMain"]{background:var(--page);color:var(--ink)}
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3, [data-testid="stMarkdownContainer"] h4,
[data-testid="stWidgetLabel"] p, label, .hero h1 {color:var(--ink)!important}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p{color:var(--muted)!important}
.brand{display:flex;align-items:center;gap:.7rem;margin-bottom:1.7rem}
.mark{width:38px;height:38px;border-radius:10px;background:var(--brand);color:white;display:flex;align-items:center;justify-content:center;font-weight:700}
.brand-name{font-weight:700}.brand-note{font-size:.75rem;color:var(--muted);margin-top:.1rem}
.hero{margin-bottom:1.4rem}.eyebrow{font-size:2rem;font-weight:800;color:var(--brand);letter-spacing:-.03em;text-transform:none;line-height:1.15}
.hero h1{font-size:clamp(2rem,3.2vw,2.65rem);letter-spacing:-.035em;line-height:1.12;margin:.4rem 0 .7rem;white-space:normal;overflow-wrap:anywhere}
.hero p{color:var(--muted);max-width:720px;line-height:1.65}
.panel,.metric,.step{background:#fff;border:1px solid var(--line);border-radius:13px}
.panel{padding:1.25rem;margin:1rem 0;box-shadow:0 5px 18px rgba(23,32,51,.04)}
.label{font-size:.75rem;font-weight:700;color:var(--muted);letter-spacing:.07em;text-transform:uppercase;margin-bottom:.65rem}
.result-title{font-size:1.3rem;font-weight:700}.copy{line-height:1.75;white-space:pre-wrap;font-size:.93rem}
.metric{padding:1rem;min-height:88px}.metric-value{font-size:1.4rem;font-weight:700}.metric-label{font-size:.77rem;color:var(--muted);margin-top:.25rem}
.empty{background:#fff;border:1px dashed #cdd3de;border-radius:14px;text-align:center;padding:2.4rem 1rem;margin-top:1rem}
.empty h3{margin:.6rem 0 .35rem}.empty p{color:var(--muted);max-width:540px;margin:auto;line-height:1.6}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem;margin-top:.9rem}.step{padding:1rem}
.step-no{font-size:.76rem;color:var(--brand);font-weight:700}.step-title{font-size:.88rem;font-weight:650;margin:.35rem 0}.step-copy{font-size:.77rem;color:var(--muted);line-height:1.45}
.progress-row{display:flex;justify-content:space-between;font-size:.76rem;color:var(--muted);margin:.7rem 0 .4rem}
.progress-track{height:6px;background:#eceff4;border-radius:99px;overflow:hidden}.progress-fill{height:100%;background:var(--brand)}
.transcript{background:#f8f9fb;border:1px solid var(--line);border-radius:10px;padding:1rem;max-height:360px;overflow:auto;white-space:pre-wrap;line-height:1.7;font-size:.87rem}
.chat{display:flex;margin:.7rem 0}.chat.user{justify-content:flex-end}.bubble{max-width:78%;padding:.75rem .9rem;border-radius:12px;background:#eef0f4;font-size:.9rem;line-height:1.55}
.chat.user .bubble{background:var(--brand);color:#fff}.who{font-size:.68rem;color:var(--muted);margin-bottom:.2rem}.chat.user .who{color:#d9dcff}
.stTextInput input,[data-baseweb="select"]>div,[data-testid="stFileUploaderDropzone"]{background:#fff!important;color:var(--ink)!important;border-color:#d8dde7!important;border-radius:10px!important}
.stTextInput input::placeholder{color:#8a93a3!important}
[data-baseweb="select"] span,[data-baseweb="select"] svg{color:var(--ink)!important;fill:var(--ink)!important}
[data-testid="stFileUploaderDropzone"] button{background:#fff!important;color:var(--ink)!important;border:1px solid #d8dde7!important}
.stButton>button,[data-testid="stBaseButton-secondary"]{background:#fff!important;color:var(--ink)!important;border:1px solid #d8dde7!important;border-radius:10px!important;font-weight:600!important;min-height:42px}
.stButton>button p,[data-testid="stBaseButton-secondary"] p{color:var(--ink)!important}
.stButton>button[kind="primary"],[data-testid="stBaseButton-primary"]{background:var(--brand)!important;color:#fff!important;border-color:var(--brand)!important}
.stButton>button[kind="primary"] p,[data-testid="stBaseButton-primary"] p{color:#fff!important}
.stButton>button[kind="primary"]:hover,[data-testid="stBaseButton-primary"]:hover{background:var(--dark)!important;border-color:var(--dark)!important}
div[data-testid="stDownloadButton"] button{background:var(--brand)!important;color:#fff!important;border:1px solid var(--brand)!important;border-radius:10px!important;font-weight:700!important;min-height:48px!important}
div[data-testid="stDownloadButton"] button p,div[data-testid="stDownloadButton"] button span,div[data-testid="stDownloadButton"] button svg{color:#fff!important;fill:#fff!important}
div[data-testid="stDownloadButton"] button:hover{background:var(--dark)!important;border-color:var(--dark)!important}
footer{visibility:hidden}
@media(max-width:1100px){.block-container{max-width:100%;padding-left:1.5rem;padding-right:1.5rem}.hero h1{font-size:2.15rem}}
@media(max-width:760px){.steps{grid-template-columns:1fr}.block-container{padding:1.2rem 1rem 2rem}.hero h1{font-size:1.8rem}}
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
    st.markdown('<div class="brand"><div class="mark">↗</div><div><div class="brand-name">AskMyURL</div><div class="brand-note">Video notes, made useful</div></div></div>', unsafe_allow_html=True)
    st.markdown("**What it does**")
    st.caption("Turns a YouTube video or recording into a transcript, concise notes, and searchable Q&A.")
    st.markdown("**Supported input**")
    st.caption("YouTube links · MP3 · WAV · MP4 · M4A · WEBM")
    st.markdown("**Languages**")
    st.caption("English and Hindi/Hinglish")
    if st.session_state.pipeline_steps:
        st.divider()
        st.markdown("**Current progress**")
        render_progress(st.session_state.pipeline_steps)

st.markdown("""
<section class="hero">
  <div class="eyebrow">AskMyURL</div>
  <h1>One link. Clear notes. Quick answers.</h1>
  <p>Paste a YouTube link or upload a recording to generate a transcript, useful summaries, and answers grounded in the original content.</p>
</section>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("#### Add your content")
    source = st.text_input("YouTube link", placeholder="https://www.youtube.com/watch?v=...")
    file_col, language_col = st.columns([3, 1])
    with file_col:
        uploaded_file = st.file_uploader("Or upload an audio/video file", type=["mp3", "wav", "mp4", "m4a", "webm"])
    with language_col:
        language = st.selectbox("Audio language", ["english", "hinglish"], format_func=lambda x: "English" if x == "english" else "Hindi / Hinglish")
    button_col, note_col = st.columns([1.2, 3.8], vertical_alignment="center")
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
                "fallback_reason": analysis.get("fallback_reason", ""),
            }
            st.session_state.pipeline_done = True
            live_area.success("Your notes are ready.")
            time.sleep(.4)
            st.rerun()
        except Exception as error:
            live_area.empty()
            message = str(error)
            if "403" in message or "Forbidden" in message or "blocked audio" in message:
                st.error(
                    "YouTube blocked this video's audio download from the cloud server. "
                    "This usually happens when the video has no usable captions. "
                    "Download the audio/video to your device, then upload it above; "
                    "AskMyURL will transcribe and analyse the uploaded file."
                )
            else:
                st.error(f"We couldn't process this content: {message}")

if st.session_state.result:
    result = st.session_state.result
    if result.get("used_fallback"):
        reason = result.get("fallback_reason") or "The AI provider could not complete the request."
        st.warning(
            f"{reason} AskMyURL created extractive notes so the request was not lost. "
            "Check the GROQ_API_KEY secret or retry after a short wait for full AI-generated notes."
        )
    title_col, new_col = st.columns([5, 1])
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
            "⬇ Download complete PDF",
            export_to_pdf(result),
            f"{filename}.pdf",
            "application/pdf",
            use_container_width=True,
        )
    with export_2:
        st.download_button(
            "⬇ Download editable DOCX",
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
    <div class="empty"><div style="font-size:1.7rem">▤</div><h3>Your notes will appear here</h3>
    <p>Start with a link or recording above. AskMyURL will organise the content into sections you can read, download, and question.</p></div>
    <div class="steps">
      <div class="step"><div class="step-no">01</div><div class="step-title">Add content</div><div class="step-copy">Paste a YouTube link or upload a supported media file.</div></div>
      <div class="step"><div class="step-no">02</div><div class="step-title">Review the notes</div><div class="step-copy">Read the summary, action items, decisions, and transcript.</div></div>
      <div class="step"><div class="step-no">03</div><div class="step-title">Ask follow-up questions</div><div class="step-copy">Search the recording conversationally using grounded Q&A.</div></div>
    </div>
    """, unsafe_allow_html=True)

st.caption("AskMyURL · Streamlit, Groq Whisper, LangChain, and ChromaDB · Long-form build 3.1")
