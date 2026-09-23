from core.analysis import analyse_transcript


def summarize(transcript: str) -> str:
    return analyse_transcript(transcript)["summary"]


def generate_title(transcript: str) -> str:
    return analyse_transcript(transcript)["title"]



