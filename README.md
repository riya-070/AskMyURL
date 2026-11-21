# 🔗 AskMyURL

Paste a YouTube link or upload a recording, and AskMyURL gives you a transcript, short notes, and a chat where you can ask questions about it.

🌐 **Live demo:** [Try AskMyURL](https://askmyurl-x4z5vdmsby8a32uppcuzly.streamlit.app/)

## What it does
- Takes a YouTube link or an audio/video file
- Creates a transcript
- Makes a summary, action items, key decisions and open questions
- Lets you ask questions about the video
- Downloads the notes as PDF or DOCX

## Who it's for
- **Students:** turn a long lecture into notes and ask about the parts you missed
- **Professionals:** pull action items and decisions out of a recorded meeting
- **Anyone:** skip a 1-hour video and ask the one question you care about

## Supported input
- YouTube links
- Audio and video files: MP3, WAV, MP4, M4A, WEBM
- Languages: English and Hindi/Hinglish

## How it works
1. Get the transcript (YouTube captions, or audio transcription with Groq Whisper)
2. Send the transcript to an AI model (Groq) to create the notes
3. Store the transcript in ChromaDB, so questions are answered from the video's content (RAG)

## What makes it useful
- **Handles long videos:** recordings are split into 8-minute sections and transcribed one by one
- **Fast when possible:** uses YouTube captions first, and transcribes audio only when captions are missing
- **Answers from the video:** replies come only from the transcript, so it doesn't make things up
- **Keeps working if the AI is down:** it switches to a backup and still gives notes and answers

## Tech stack
Python, Streamlit, FastAPI, LangChain, Groq, ChromaDB, yt-dlp, ffmpeg
