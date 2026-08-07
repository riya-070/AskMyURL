"""
FastAPI backend for AI Video Assistant.

This exposes the exact same pipeline used by app.py as a standalone HTTP API,
so the AI logic is decoupled from the Streamlit UI. Any frontend (Streamlit,
React, mobile app, curl) can now use this project by calling these endpoints
instead of importing the Python modules directly.

Run with:
    uvicorn backend.main:app --reload --port 8000

Docs are auto-generated at:
    http://127.0.0.1:8000/docs
"""
import uuid
from dotenv import load_dotenv

load_dotenv()  # MUST be before any core/ imports

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question
from utils.export_utils import export_to_pdf, export_to_docx

app = FastAPI(title="AI Video Assistant API", version="1.0.0")

# Allow the Streamlit app (or any frontend) running on a different port/origin to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your real frontend URL before going to production
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store: session_id -> {"result": {...}, "rag_chain": ...}
# NOTE: this resets whenever the server restarts. Swap for Redis/DB for real persistence.
SESSIONS: dict[str, dict] = {}


class AnalyzeRequest(BaseModel):
    source: str          # YouTube URL or local file path
    language: str = "english"   # "english" (Whisper) or "hinglish" (Sarvam)


class AnalyzeResponse(BaseModel):
    session_id: str
    title: str
    transcript: str
    summary: str
    action_items: str
    key_decisions: str
    open_questions: str


class AskRequest(BaseModel):
    session_id: str
    question: str


class AskResponse(BaseModel):
    answer: str


@app.get("/")
def health_check():
    return {"status": "ok", "service": "AI Video Assistant API"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    """Run the full pipeline: download/transcribe -> summarize -> extract -> build RAG index."""
    try:
        chunks = process_input(req.source)
        transcript = transcribe_all(chunks, req.language)
        title = generate_title(transcript)
        summary = summarize(transcript)
        action_items = extract_action_items(transcript)
        decisions = extract_key_decisions(transcript)
        questions = extract_questions(transcript)
        rag_chain = build_rag_chain(transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    session_id = str(uuid.uuid4())
    result = {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": decisions,
        "open_questions": questions,
    }
    SESSIONS[session_id] = {"result": result, "rag_chain": rag_chain}

    return AnalyzeResponse(session_id=session_id, **result)


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """Ask a question about a previously analyzed session's transcript."""
    session = SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Run /analyze first.")
    try:
        answer = ask_question(session["rag_chain"], req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return AskResponse(answer=answer)


@app.get("/session/{session_id}")
def get_session(session_id: str):
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session["result"]


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    if session_id in SESSIONS:
        del SESSIONS[session_id]
        return {"deleted": session_id}
    raise HTTPException(status_code=404, detail="Session not found.")

    from fastapi.responses import FileResponse

@app.post("/download-youtube")
def download_youtube(req: AnalyzeRequest):
    """Downloads YouTube audio using THIS machine's IP (your home PC),
    so it bypasses YouTube's cloud-IP blocking. Called remotely by the
    deployed Streamlit app via the ngrok tunnel."""
    from utils.audio_processor import download_youtube_audio
    try:
        wav_path = download_youtube_audio(req.source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return FileResponse(wav_path, media_type="audio/wav", filename=os.path.basename(wav_path))