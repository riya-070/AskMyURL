# 🔗 AskMyURL

**AI-Powered URL Summarizer & Question-Answering System**

Paste a YouTube link (or a local audio/video file), and AskMyURL will transcribe it, summarize it, pull out action items and key decisions, and let you chat with the content using Retrieval-Augmented Generation (RAG).

---

## ✨ Features

- 🎙️ **Multi-language transcription** — English (via OpenAI Whisper, local) and Hindi/Hinglish (via Sarvam AI, with built-in translation)
- 📋 **AI summarization** — map-reduce summarization powered by Mistral AI via LangChain
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
       │ (Mistral)  │ │ (Mistral)│ │  (ChromaDB)  │
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
| Speech-to-text | `openai-whisper` (English), Sarvam AI API (Hindi/Hinglish) |
| LLM / Summarization | `LangChain`, `Mistral AI` |
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
