# 🔗 AskMyURL

**AI-Powered URL Summarizer & Question-Answering System**

Paste a YouTube link (or a local audio/video file), and AskMyURL will transcribe it, summarize it, pull out action items and key decisions, and let you chat with the content using Retrieval-Augmented Generation (RAG).

---

<<<<<<< HEAD
## Groq setup

1. Create a Groq API key at `https://console.groq.com/`.
2. Copy `.env.example` to `.env`.
3. Put your real key in the local `.env` file:

```env
GROQ_API_KEY=your_real_key
GROQ_MODEL=openai/gpt-oss-20b
GROQ_STT_MODEL=whisper-large-v3-turbo
WHISPER_MODEL=base
```

4. Install dependencies and run the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The footer should show `Long-form build 3.1`. If it does not, an older copy of
the project is still running. Stop that Streamlit terminal and start the app
from the newly extracted folder.

For Streamlit Community Cloud, add `GROQ_API_KEY` and `GROQ_MODEL` in the
app's Secrets settings. Never commit `.env` or `cookies.txt` to GitHub.

If Groq is unavailable, AskMyURL automatically falls back to local extractive
notes and transcript retrieval, so the deployed app remains usable.

---

## ✨ Features

- 🎙️ **Long-form transcription** — recordings are split into 8-minute sections and processed with Groq Whisper; local Whisper remains available as a fallback
- ▶️ **YouTube fallback** — uses complete captions when available, otherwise downloads and transcribes the full audio in chunks
- 📋 **AI summarization** — single-call structured analysis powered by Groq via LangChain
- 🛟 **Offline fallback** — creates extractive notes and transcript matches if Groq is unavailable
=======
## ✨ Features

- 🎙️ **Multi-language transcription** — English (via OpenAI Whisper, local) and Hindi/Hinglish (via Sarvam AI, with built-in translation)
- 📋 **AI summarization** — map-reduce summarization powered by Mistral AI via LangChain
>>>>>>> 0060a37186cdc4a4742be5b19c12d34f6ac4d31d
- ✅ **Structured extraction** — automatically pulls out action items, key decisions, and open questions
- 💬 **Chat with your transcript** — RAG-based Q&A using ChromaDB + HuggingFace embeddings
- 📄 **Export reports** — download results as PDF or DOCX
- 🖥️ **Two interfaces** — a Streamlit web UI, and a decoupled FastAPI backend (REST API) for programmatic access

---

## 🏗️ Architecture

```
                 ┌────────────────────┐
   YouTube URL   │                    │
   or local file │   Audio Processor  │  (yt-dlp + pydub/ffmpeg)
   ────────────► │                    │
                 └─────────┬──────────┘
                           │  chunked WAV audio
                           ▼
                 ┌────────────────────┐
                 │    Transcriber     │  (Whisper — English)
                 │                    │  (Sarvam AI — Hindi/Hinglish)
                 └─────────┬──────────┘
                           │  transcript text
              ┌────────────┼─────────────┐
              ▼            ▼             ▼
       ┌────────────┐ ┌──────────┐ ┌──────────────┐
       │ Summarizer │ │ Extractor│ │  RAG Engine  │
<<<<<<< HEAD
       │   (Groq)   │ │  (Groq)  │ │  (ChromaDB)  │
=======
       │ (Mistral)  │ │ (Mistral)│ │  (ChromaDB)  │
>>>>>>> 0060a37186cdc4a4742be5b19c12d34f6ac4d31d
       └──────┬─────┘ └────┬─────┘ └──────┬───────┘
              │            │              │
              ▼            ▼              ▼
       ┌─────────────────────────────────────────┐
       │   Streamlit UI   /   FastAPI Backend     │
       └─────────────────────────────────────────┘
```

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Audio processing | `yt-dlp`, `pydub`, `ffmpeg` |
<<<<<<< HEAD
| Speech-to-text | Groq Whisper (hosted), with local OpenAI Whisper fallback |
| LLM / Summarization | `LangChain`, `Groq` |
=======
| Speech-to-text | `openai-whisper` (English), Sarvam AI API (Hindi/Hinglish) |
| LLM / Summarization | `LangChain`, `Mistral AI` |
>>>>>>> 0060a37186cdc4a4742be5b19c12d34f6ac4d31d
| RAG / Vector search | `ChromaDB`, `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Backend API | `FastAPI`, `Pydantic`, `uvicorn` |
| Frontend | `Streamlit` |
| Document export | `python-docx`, `fpdf2` |
| Config | `python-dotenv` |

---

## 📦 Project Structure

```
Agent/
├── app.py                  # Streamlit web app (main UI)
├── main.py                 # CLI entry point (terminal usage)
├── backend/
│   └── main.py              # FastAPI backend (REST API)
├── core/
│   ├── transcriber.py        # Whisper + Sarvam AI transcription
│   ├── summarizer.py         # LLM summarization + title generation
│   ├── extractor.py          # Action items / decisions / questions
│   ├── vector_store.py       # ChromaDB vector store setup
│   └── rag_engine.py         # RAG Q&A chain
├── utils/
│   ├── audio_processor.py    # YouTube download + audio chunking
│   └── export_utils.py       # PDF / DOCX report generation
├── Requirements.txt
├── packages.txt             # System packages for cloud deployment (ffmpeg)
└── .env                     # API keys (not committed — see below)
```

---
