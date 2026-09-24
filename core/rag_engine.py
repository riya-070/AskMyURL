"""Grounded transcript Q&A with Groq and a useful local fallback."""

import os
import re
import time
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from core.vector_store import build_vector_store, get_retriever

DEFAULT_MODELS = ("openai/gpt-oss-20b", "llama-3.1-8b-instant")

def _models() -> list[str]:
    configured = os.getenv("GROQ_MODEL", "").strip()
    return list(dict.fromkeys([configured, *DEFAULT_MODELS])) if configured else list(DEFAULT_MODELS)

def get_llm(model: str | None = None, temperature: float = 0.1):
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")
    return ChatGroq(api_key=api_key, model=model or _models()[0], temperature=temperature, timeout=75, max_retries=2)

def _unique_docs(docs) -> list[str]:
    unique, seen = [], set()
    for doc in docs:
        text = re.sub(r"\s+", " ", doc.page_content).strip()
        fingerprint = text[:240].lower()
        if text and fingerprint not in seen:
            seen.add(fingerprint)
            unique.append(text)
    return unique

def format_docs(docs) -> str:
    return "\n\n".join(f"[Passage {i}] {text}" for i, text in enumerate(_unique_docs(docs), 1))

def _local_answer(docs, question: str) -> str:
    question_terms = {
        word for word in re.findall(r"[a-zA-Z0-9']{3,}", question.lower())
        if word not in {"what", "when", "where", "which", "about", "does", "this", "that", "video"}
    }
    candidates, seen = [], set()
    for text in _unique_docs(docs):
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            sentence = sentence.strip()
            key = re.sub(r"\W+", " ", sentence.lower())[:180]
            if len(sentence.split()) < 6 or key in seen:
                continue
            seen.add(key)
            terms = set(re.findall(r"[a-zA-Z0-9']{3,}", sentence.lower()))
            candidates.append((len(question_terms & terms), sentence))
    ranked = [s for score, s in sorted(candidates, key=lambda item: item[0], reverse=True) if score > 0]
    if not ranked:
        return "I could not find this information in the transcript."
    return "Based on the transcript, " + " ".join(ranked[:4])

PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You answer questions about one video using only the supplied transcript passages. "
     "Give a direct natural-language answer first; do not merely repeat or list passages. "
     "Combine evidence, remove repetition, and retain useful names, numbers, examples, and qualifications. "
     "Use 2-5 sentences unless the user requests a list or detailed explanation. If the answer is absent, "
     "say exactly: I could not find this information in the transcript.\n\nContext:\n{context}"),
    ("human", "Question: {question}"),
])

def build_rag_chain(transcript: str):
    vector_store = build_vector_store(transcript)
    return {"retriever": get_retriever(vector_store, k=6)}

def load_rag_chain():
    raise RuntimeError("Analyse content before asking a question.")

def ask_question(rag_chain, question: str) -> str:
    docs = rag_chain["retriever"].invoke(question)
    context, last_error = format_docs(docs), None
    for model in _models():
        try:
            answer = (PROMPT | get_llm(model=model) | StrOutputParser()).invoke(
                {"context": context, "question": question}
            ).strip()
            if answer:
                return answer
        except Exception as error:
            last_error = error
            print(f"Groq Q&A failed with {model}: {type(error).__name__}: {error}")
            time.sleep(1)
    print(f"All Groq Q&A models unavailable; using extractive answer: {last_error}")
    return _local_answer(docs, question)
