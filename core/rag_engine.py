import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from core.vector_store import build_vector_store, load_vector_store, get_retriever

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        api_key=api_key,
        temperature=0.3,
    )

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

def build_rag_chain(transcript:str):

    vector_store = build_vector_store(transcript)

    retriever = get_retriever(vector_store, k = 4)

    try:
        llm = get_llm()
    except Exception as error:
        print(f"Groq Q&A setup unavailable; retrieval fallback enabled: {error}")
        return {"chain": None, "retriever": retriever}

    prompt = ChatPromptTemplate.from_messages(

        [(
            "system",
            """You are an expert meeting assistant. Answer the user's question 
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say: 
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}""",
        ),
        ("human", "{question}"),
    ]
    )

    #full LCEL Rag pipeline 

    rag_chain = (

        {"context" : retriever | RunnableLambda(format_docs),
         "question": RunnablePassthrough()
         }
         |prompt|llm|StrOutputParser()
    )

    return {"chain": rag_chain, "retriever": retriever}


def load_rag_chain():
    vector_store = load_vector_store()
    vector_store = load_vector_store()
    retriver = get_retriever(vector_store)

    try:
        llm = get_llm()
    except Exception as error:
        print(f"Groq Q&A setup unavailable; retrieval fallback enabled: {error}")
        return {"chain": None, "retriever": retriver}
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting assistant. Answer the user's question 
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say: 
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}""",
        ),
        ("human", "{question}"),
    ])

    rag_chain = (
        {
            "context":  retriver| RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return {"chain": rag_chain, "retriever": retriver}


def ask_question(rag_chain, question:str) -> str:
    print(f"Question : {question}")
    try:
        if rag_chain["chain"] is None:
            raise RuntimeError("Groq Q&A is not configured")
        answer = rag_chain["chain"].invoke(question)
    except Exception as error:
        print(f"Groq Q&A unavailable; returning transcript passages: {error}")
        docs = rag_chain["retriever"].invoke(question)
        excerpts = [doc.page_content.strip() for doc in docs[:3] if doc.page_content.strip()]
        answer = (
            "Relevant transcript passages:\n\n" + "\n\n".join(excerpts)
            if excerpts
            else "I could not find relevant information in the transcript."
        )
    print(f"answer :{answer}")
    return answer
