"""Vector-store helpers for one isolated transcript at a time."""

from uuid import uuid4
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

def build_vector_store(transcript: str) -> Chroma:
    """Build a fresh in-memory collection so videos never contaminate each other."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=160,
        separators=["\n\n", ". ", "? ", "! ", "\n", " "],
    )
    chunks = [chunk.strip() for chunk in splitter.split_text(transcript) if chunk.strip()]
    docs = [Document(page_content=chunk, metadata={"chunk_index": i}) for i, chunk in enumerate(chunks)]
    if not docs:
        raise ValueError("The transcript is empty, so Q&A could not be prepared.")
    return Chroma.from_documents(
        documents=docs,
        embedding=get_embeddings(),
        collection_name=f"transcript_{uuid4().hex}",
    )

def load_vector_store():
    raise RuntimeError("A saved vector store is not reused; analyse the content again.")

def get_retriever(vector_store: Chroma, k: int = 6):
    return vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": max(18, k * 3), "lambda_mult": 0.72},
    )
