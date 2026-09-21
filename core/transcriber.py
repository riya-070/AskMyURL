import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
import os
os.environ["PATH"] += os.pathsep + r"C:\Users\hp\Desktop\ffmpeg\ffmpeg-8.1.2-essentials_build\bin"

import whisper
import requests
from pydub import AudioSegment
<<<<<<< HEAD
from groq import Groq
=======
>>>>>>> 0060a37186cdc4a4742be5b19c12d34f6ac4d31d

# Sarvam's sync STT-translate API rejects audio longer than 30s.
# We slice each chunk into 25s pieces (with a 5s safety margin) before sending.


SARVAM_PIECE_SECONDS = 25
<<<<<<< HEAD
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_STT_MODEL = os.getenv("GROQ_STT_MODEL", "whisper-large-v3-turbo")
=======
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
>>>>>>> 0060a37186cdc4a4742be5b19c12d34f6ac4d31d
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")
_model = None


def load_model():

    global _model  

    if _model is None: 
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")
        _model = whisper.load_model(WHISPER_MODEL) 
        print("Whisper model loaded.")
    return _model 


def transcribe_chunk_whisper(chunk_path: str) -> str:

    model = load_model()  

    result = model.transcribe(chunk_path, task="transcribe")  
    return result["text"]  


<<<<<<< HEAD
def transcribe_chunk_groq(chunk_path: str, language: str = "english") -> str:
    """Transcribe one small audio chunk using Groq's hosted Whisper model."""
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured")
    client = Groq(api_key=GROQ_API_KEY)
    language_code = "hi" if language.lower() == "hinglish" else "en"
    with open(chunk_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            file=(os.path.basename(chunk_path), audio_file.read()),
            model=GROQ_STT_MODEL,
            response_format="text",
            language=language_code,
            temperature=0.0,
        )
    return response if isinstance(response, str) else response.text


=======
>>>>>>> 0060a37186cdc4a4742be5b19c12d34f6ac4d31d
def _send_to_sarvam(piece_path: str) -> str:
    """Send one ≤30s WAV file to Sarvam and return the English transcript."""
    headers = {"api-subscription-key": SARVAM_API_KEY}

    with open(piece_path, "rb") as f:
        files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
        data = {"model": SARVAM_MODEL, "with_diarization": "false"}
        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    if not response.ok:
        print(f"\n❌ Sarvam returned {response.status_code}")
        print(f"Response body: {response.text}\n")
        response.raise_for_status()

    return response.json().get("transcript", "")


def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """
    Sarvam sync API only accepts ≤30s audio. We split this chunk into
    25-second pieces, send each separately, and join the transcripts.
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    audio = AudioSegment.from_wav(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1000

    full_text = ""
    total_pieces = (len(audio) + piece_ms - 1) // piece_ms

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start: start + piece_ms]
        piece_path = f"{chunk_path}_sv_{i}.wav"
        piece.export(piece_path, format="wav")

        try:
            print(f"  → Sarvam piece {i + 1}/{total_pieces} ...")
            full_text += _send_to_sarvam(piece_path) + " "
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()

   



def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    """
    Route one chunk to Whisper or Sarvam depending on language choice.
    - english  → Whisper (local model)
    - hinglish → Sarvam (translates to English while transcribing)
    """
<<<<<<< HEAD
    # Hosted Whisper is much faster and lighter on free deployments. If it is
    # temporarily unavailable, English still has a fully local fallback.
    try:
        return transcribe_chunk_groq(chunk_path, language)
    except Exception as error:
        print(f"Groq transcription unavailable; using fallback: {error}")
        if language.lower() == "hinglish" and SARVAM_API_KEY:
            return transcribe_chunk_sarvam(chunk_path)
        return transcribe_chunk_whisper(chunk_path)
=======
    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path)
    return transcribe_chunk_whisper(chunk_path)
>>>>>>> 0060a37186cdc4a4742be5b19c12d34f6ac4d31d


def transcribe_all(chunks: list, language: str = "english") -> str:

    full_transcript = "" 

<<<<<<< HEAD
    engine = "Groq Whisper (with automatic fallback)"
=======
    engine = "Sarvam AI" if language.lower() == "hinglish" else "Whisper"
>>>>>>> 0060a37186cdc4a4742be5b19c12d34f6ac4d31d
    print(f"Using {engine} for transcription.")

    for i, chunk in enumerate(chunks):  

        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

<<<<<<< HEAD
        try:
            text = transcribe_chunk(chunk, language=language)
            full_transcript += text + " "
        finally:
            # Each chunk can be large; release it immediately after use so a
            # long recording does not fill the deployment's temporary disk.
            if os.path.exists(chunk):
                os.remove(chunk)

    print("Transcription complete.")

    return full_transcript.strip()  
=======
        text = transcribe_chunk(chunk, language=language)  

        full_transcript += text + " "  

    print("Transcription complete.")

    return full_transcript.strip()  
>>>>>>> 0060a37186cdc4a4742be5b19c12d34f6ac4d31d
