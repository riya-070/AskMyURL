import yt_dlp
from pydub import AudioSegment
import os
import shutil
import re
from youtube_transcript_api import YouTubeTranscriptApi

FFMPEG_LOCAL_PATH = r"C:\Users\hp\Desktop\ffmpeg\ffmpeg-8.1.2-essentials_build\bin"

if os.path.exists(FFMPEG_LOCAL_PATH):
    FFMPEG_LOCATION = FFMPEG_LOCAL_PATH
    AudioSegment.converter = os.path.join(FFMPEG_LOCAL_PATH, "ffmpeg.exe")
    AudioSegment.ffprobe = os.path.join(FFMPEG_LOCAL_PATH, "ffprobe.exe")
else:
    FFMPEG_LOCATION = shutil.which("ffmpeg")

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

COOKIES_PATH = "cookies.txt"


def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")
    base_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
        "outtmpl": output_path,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
        "ffmpeg_location": FFMPEG_LOCATION,
        "noplaylist": True,
        "cachedir": False,
        "retries": 3,
        "fragment_retries": 3,
        "socket_timeout": 30,
        "source_address": "0.0.0.0",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }

    # A stale cookies secret is a common cause of 403. Try the public route
    # first, cookies second (needed for some restricted videos), then an
    # alternate supported player-client configuration.
    attempts = [{}]
    if os.path.isfile(COOKIES_PATH) and os.path.getsize(COOKIES_PATH) > 0:
        attempts.append({"cookiefile": COOKIES_PATH})
    attempts.append({
        "extractor_args": {
            "youtube": {"player_client": ["default", "-android_sdkless"]}
        }
    })

    errors = []
    for extra_opts in attempts:
        ydl_opts = {**base_opts, **extra_opts}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                base, _ = os.path.splitext(ydl.prepare_filename(info))
                filename = base + ".wav"
                if not os.path.isfile(filename):
                    raise RuntimeError("Audio conversion did not create a WAV file")
                return filename
        except Exception as error:
            errors.append(str(error))

    final_error = errors[-1] if errors else "unknown download error"
    if any("403" in item or "Forbidden" in item or "Sign in" in item for item in errors):
        raise RuntimeError(
            "YouTube rejected the cloud download after multiple attempts. "
            "Please upload the audio/video file instead."
        )
    raise RuntimeError(f"YouTube audio download failed: {final_error}")


def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})", url)
    if not match:
        raise ValueError("Could not extract YouTube video ID from URL")
    return match.group(1)


def get_youtube_transcript_direct(url: str) -> str:
    """Fetch YouTube's own captions directly. Free, and generally avoids
    the aggressive blocking that the full audio-download endpoint hits
    on cloud IPs (though not guaranteed immune)."""
    video_id = extract_video_id(url)
    try:
        languages = ["en", "en-US", "en-GB", "hi", "hi-IN"]
        # Support both the current and older youtube-transcript-api interfaces.
        if hasattr(YouTubeTranscriptApi, "get_transcript"):
            fetched = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        else:
            fetched = YouTubeTranscriptApi().fetch(video_id, languages=languages)
        entries = fetched.to_raw_data() if hasattr(fetched, "to_raw_data") else fetched
        transcript = " ".join(
            e["text"] if isinstance(e, dict) else e.text for e in entries
        )
        transcript = re.sub(r"\s+", " ", transcript).strip()
        if len(transcript.split()) < 20:
            raise RuntimeError("Captions were empty or incomplete")
        return transcript
    except Exception as e:
        raise RuntimeError(f"No captions available for this video: {e}")


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 8) -> list:
    """Split media into API-friendly pieces.

    Eight-minute mono/16 kHz WAV files stay comfortably below hosted speech
    API upload limits while allowing recordings much longer than ten minutes.
    """
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


if __name__ == "__main__":
    text = get_youtube_transcript_direct("https://youtu.be/-0uJMbWOjEc")
    print(text)
