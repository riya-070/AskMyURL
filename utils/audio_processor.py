import yt_dlp
from pydub import AudioSegment
import os
import shutil

# Works on your PC (uses local ffmpeg folder) AND on Streamlit Cloud
# (falls back to the ffmpeg installed via packages.txt automatically).
FFMPEG_LOCAL_PATH = r"C:\Users\hp\Desktop\ffmpeg\ffmpeg-8.1.2-essentials_build\bin"

if os.path.exists(FFMPEG_LOCAL_PATH):
    FFMPEG_LOCATION = FFMPEG_LOCAL_PATH
    AudioSegment.converter = os.path.join(FFMPEG_LOCAL_PATH, "ffmpeg.exe")
    AudioSegment.ffprobe = os.path.join(FFMPEG_LOCAL_PATH, "ffprobe.exe")
else:
    FFMPEG_LOCATION = shutil.which("ffmpeg")  # e.g. /usr/bin/ffmpeg on the cloud

DOWNLOAD_DIR = 'downloades'
COOKIES_PATH = "cookies.txt"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "cookiefile": COOKIES_PATH if os.path.exists(COOKIES_PATH) else None,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
        "ffmpeg_location": FFMPEG_LOCATION,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        base, _ = os.path.splitext(ydl.prepare_filename(info))
        filename = base + ".wav"
    return filename
    


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # 16khz
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start: start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)
    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks
from youtube_transcript_api import YouTubeTranscriptApi
import re


def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})", url)
    if not match:
        raise ValueError("Could not extract YouTube video ID from URL")
    return match.group(1)


def get_youtube_transcript_direct(url: str) -> str:
    """Fetch YouTube's own captions directly. Free, works from any server
    (including cloud-hosted apps), since it's not the download endpoint
    that YouTube blocks — just the subtitle data."""
    video_id = extract_video_id(url)
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id, languages=["en", "en-US", "en-GB", "hi"]
        )
    except Exception as e:
        raise RuntimeError(f"No captions available for this video: {e}")
    return " ".join(entry["text"] for entry in transcript_list)

if __name__ == "__main__":
    result = process_input("https://youtu.be/-0uJMbWOjEc?si=Qd6KKF1SvN-22dm_")
    print(result)