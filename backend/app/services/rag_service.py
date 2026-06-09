from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from app.config import get_settings
from app.services.embedding_service import get_vectorstore

_memories = {}
_chains   = {}
_contexts = {}  # stores video metadata per session


def set_video_context(session_id: str, video_a: dict, video_b: dict):
    """Store video metadata so RAG prompt has access to exact numbers."""
    _contexts[session_id] = {
        "video_a": video_a,
        "video_b": video_b,
    }


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

    # Build context string from stored metadata
    ctx = _contexts.get(session_id, {})
    va  = ctx.get("video_a", {})
    vb  = ctx.get("video_b", {})

    meta_context = f"""
VIDEO A (YouTube):
- Title: {va.get('title', 'N/A')}
- Creator: {va.get('creator_name', 'N/A')}
- Followers: {va.get('follower_count', 'N/A')}
- Views: {va.get('views', 'N/A')}
- Likes: {va.get('likes', 'N/A')}
- Comments: {va.get('comments', 'N/A')}
- Engagement Rate: {va.get('engagement_rate', 'N/A')}%
- Duration: {va.get('duration_seconds', 'N/A')}s
- Upload Date: {va.get('upload_date', 'N/A')}
- Hashtags: {', '.join(va.get('hashtags', []))}

VIDEO B (Instagram Reel):
- Title: {vb.get('title', 'N/A')}
- Creator: {vb.get('creator_name', 'N/A')}
- Followers: {vb.get('follower_count', 'N/A')}
- Views: {vb.get('views', 'N/A')}
- Likes: {vb.get('likes', 'N/A')}
- Comments: {vb.get('comments', 'N/A')}
- Engagement Rate: {vb.get('engagement_rate', 'N/A')}%
- Duration: {vb.get('duration_seconds', 'N/A')}s
- Upload Date: {vb.get('upload_date', 'N/A')}
- Hashtags: {', '.join(vb.get('hashtags', []))}
"""

    prompt_template = f"""You are an expert social media analyst helping creators understand their video performance.

EXACT VIDEO METADATA (use these numbers directly in your answers):
{meta_context}

Use the transcript context below for content analysis. Always cite Video A or Video B.
Be specific, data-driven, and actionable. Never say engagement rates are unknown.

Transcript context:
{{context}}

Chat history:
{{chat_history}}

Question: {{question}}

Answer:"""

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
    chain  = get_rag_chain(session_id)
    result = chain.invoke({"question": question})
    return {
        "answer":  result["answer"],
        "sources": get_sources(result.get("source_documents", [])),
    }