"""Single-call transcript analysis with an API-free fallback."""

import json
import os
import re
from collections import Counter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
MAX_ANALYSIS_CHARS = int(os.getenv("MAX_ANALYSIS_CHARS", "80000"))


def get_llm(temperature: float = 0.2):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")
    return ChatGroq(api_key=api_key, model=GROQ_MODEL, temperature=temperature)


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if len(part.split()) >= 5]


def _numbered(items: list[str], empty_message: str) -> str:
    normalized = []
    for item in items:
        if isinstance(item, dict):
            text = "; ".join(f"{key.replace('_', ' ').title()}: {value}" for key, value in item.items())
        else:
            text = str(item)
        if text.strip():
            normalized.append(text.strip())
    unique = list(dict.fromkeys(normalized))
    return "\n".join(f"{index}. {item}" for index, item in enumerate(unique[:8], 1)) or empty_message


def _as_text(value, bullet_lists: bool = False) -> str:
    if isinstance(value, list):
        if bullet_lists:
            return "\n".join(f"• {str(item).strip()}" for item in value if str(item).strip())
        return _numbered(value, "No items found.")
    if isinstance(value, dict):
        return "\n".join(f"{key.replace('_', ' ').title()}: {item}" for key, item in value.items())
    return str(value or "")


def _prepare_long_transcript(transcript: str) -> str:
    """Keep coverage across a long transcript while staying inside one LLM call."""
    transcript = transcript.strip()
    if len(transcript) <= MAX_ANALYSIS_CHARS:
        return transcript

    section_count = 10
    section_size = MAX_ANALYSIS_CHARS // section_count
    source_step = max(1, len(transcript) // section_count)
    excerpts = []
    for index in range(section_count):
        start = index * source_step
        excerpt = transcript[start : start + section_size]
        if start > 0:
            first_break = excerpt.find(" ")
            if first_break != -1:
                excerpt = excerpt[first_break + 1 :]
        excerpts.append(f"[Transcript section {index + 1}]\n{excerpt.strip()}")
    return "\n\n".join(excerpts)


def analyse_without_api(transcript: str) -> dict:
    """Create useful extractive notes when the hosted LLM is unavailable."""
    sentences = _sentences(transcript)
    if not sentences:
        return {
            "title": "Video notes",
            "summary": transcript[:1200] or "No transcript content was available.",
            "action_items": "No action items found.",
            "key_decisions": "No key decisions found.",
            "open_questions": "No open questions found.",
            "used_fallback": True,
        }

    stop_words = {
        "about", "after", "again", "also", "because", "been", "before", "being",
        "between", "could", "from", "have", "into", "just", "more", "most", "other",
        "should", "some", "such", "than", "that", "their", "there", "these", "they",
        "this", "those", "through", "very", "what", "when", "where", "which", "while",
        "with", "would", "your", "will", "were", "then", "them", "only", "over",
    }
    words = re.findall(r"[a-zA-Z][a-zA-Z'-]{2,}", transcript.lower())
    frequencies = Counter(word for word in words if word not in stop_words)
    scored = []
    for index, sentence in enumerate(sentences):
        sentence_words = re.findall(r"[a-zA-Z][a-zA-Z'-]{2,}", sentence.lower())
        score = sum(frequencies[word] for word in sentence_words) / max(len(sentence_words), 1)
        scored.append((score, index, sentence))
    chosen = sorted(sorted(scored, reverse=True)[: min(12, len(scored))], key=lambda item: item[1])
    summary = "\n".join(f"• {sentence}" for _, _, sentence in chosen)

    action_pattern = re.compile(r"\b(need to|needs to|must|should|will|action item|follow up|deadline|assigned)\b", re.I)
    decision_pattern = re.compile(r"\b(decided|agreed|approved|finalized|selected|chosen|confirmed)\b", re.I)
    actions = [sentence for sentence in sentences if action_pattern.search(sentence)]
    decisions = [sentence for sentence in sentences if decision_pattern.search(sentence)]
    questions = [sentence for sentence in sentences if "?" in sentence or re.search(r"\b(unresolved|need to clarify|open question)\b", sentence, re.I)]

    title_words = [word.title() for word, _ in frequencies.most_common(5)]
    title = " ".join(title_words[:5]) or "Video notes"
    return {
        "title": title,
        "summary": summary,
        "action_items": _numbered(actions, "No action items found."),
        "key_decisions": _numbered(decisions, "No key decisions found."),
        "open_questions": _numbered(questions, "No open questions found."),
        "used_fallback": True,
    }


def _parse_json_response(raw: str) -> dict:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.I)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Groq returned an invalid analysis response")
    data = json.loads(cleaned[start : end + 1])
    required = {"title", "summary", "action_items", "key_decisions", "open_questions"}
    if not required.issubset(data):
        raise ValueError("Groq response is missing required fields")
    data["title"] = _as_text(data["title"]).splitlines()[0][:120] or "Video notes"
    data["summary"] = _as_text(data["summary"], bullet_lists=True)
    for key in required - {"title", "summary"}:
        if isinstance(data[key], (list, dict)):
            data[key] = _as_text(data[key])
        else:
            data[key] = str(data[key] or f"No {key.replace('_', ' ')} found.")
    data["used_fallback"] = False
    return data


def analyse_transcript(transcript: str) -> dict:
    """Analyse a transcript in one Groq request; fall back locally on any API failure."""
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You analyse video transcripts. Return valid JSON only with exactly these keys: "
            "title (maximum 8 words), summary (a detailed list of 8-12 bullet points covering "
            "the main arguments, explanations, examples, conclusions, and important facts), action_items (array), "
            "key_decisions (array), and open_questions (array). Do not invent facts. "
            "Use an empty array when a category has no items. Preserve useful names, numbers, "
            "deadlines, and technical terms from the transcript.",
        ),
        ("human", "Transcript:\n{transcript}"),
    ])
    try:
        chain = prompt | get_llm() | StrOutputParser()
        raw = chain.invoke({"transcript": _prepare_long_transcript(transcript)})
        return _parse_json_response(raw)
    except Exception as error:
        print(f"Groq analysis unavailable; using local fallback: {error}")
        return analyse_without_api(transcript)
