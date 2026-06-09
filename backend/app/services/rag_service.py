from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from app.config import get_settings
from app.services.embedding_service import get_vectorstore

# Store memory per session
_memories = {}
_chains   = {}


def get_memory(session_id: str) -> ConversationBufferMemory:
    if session_id not in _memories:
        _memories[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )
    return _memories[session_id]


def get_rag_chain(session_id: str) -> ConversationalRetrievalChain:
    if session_id in _chains:
        return _chains[session_id]

    settings = get_settings()

    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_llm_model,
        temperature=0.2,
        streaming=True,
    )

    vectorstore = get_vectorstore(session_id)
    retriever   = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4},
    )

    prompt_template = """You are an expert social media analyst helping creators understand 
their video performance. You have access to transcripts and metadata from two videos: 
Video A (YouTube) and Video B (Instagram Reel).

Use the context below to answer the question. Always cite which video (A or B) your 
answer is based on. Be specific, data-driven, and actionable.

When comparing videos, always mention:
- Engagement rates if relevant
- Specific transcript evidence
- Which video performed better and why

Context from videos:
{context}

Chat history:
{chat_history}

Question: {question}

Answer (always cite Video A or Video B):"""

    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=prompt_template,
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=get_memory(session_id),
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True,
        output_key="answer",
        verbose=False,
    )

    _chains[session_id] = chain
    return chain


def get_sources(source_documents: list) -> list:
    """Extract clean source citations from retrieved documents."""
    sources = []
    seen    = set()
    for doc in source_documents:
        chunk_id = doc.metadata.get("chunk_id", "")
        if chunk_id not in seen:
            seen.add(chunk_id)
            sources.append({
                "video_id": doc.metadata.get("video_id", ""),
                "chunk_id": chunk_id,
                "text":     doc.page_content[:150],
            })
    return sources


def ask(session_id: str, question: str) -> dict:
    """Non-streaming ask — returns answer + sources."""
    chain  = get_rag_chain(session_id)
    result = chain.invoke({"question": question})
    return {
        "answer":  result["answer"],
        "sources": get_sources(result.get("source_documents", [])),
    }
