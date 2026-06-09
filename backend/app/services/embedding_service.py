import os
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.config import get_settings

# Single embedding model instance — expensive to load, reuse it
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        settings = get_settings()
        print(f"[embeddings] loading model: {settings.embedding_model}")
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


def get_vectorstore(session_id: str) -> Chroma:
    """Get or create a ChromaDB collection for this session."""
    settings = get_settings()
    return Chroma(
        collection_name=f"session_{session_id}",
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )


def chunk_and_embed(
    session_id: str,
    video_id: str,       # "A" or "B"
    transcript: str,
    metadata: dict,      # all video metadata to store alongside chunks
) -> int:
    """
    Chunk transcript, embed, store in ChromaDB.
    Returns number of chunks created.
    """
    if not transcript or not transcript.strip():
        print(f"[embeddings] video {video_id} has no transcript, skipping")
        return 0

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       # ~500 chars per chunk
        chunk_overlap=50,     # 50 char overlap for context continuity
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_text(transcript)
    print(f"[embeddings] video {video_id}: {len(chunks)} chunks created")

    vectorstore = get_vectorstore(session_id)

    # Build documents and metadata for each chunk
    ids       = []
    metadatas = []
    texts     = []

    for i, chunk in enumerate(chunks):
        chunk_id = f"{video_id}_chunk_{i}"
        ids.append(chunk_id)
        texts.append(chunk)
        metadatas.append({
            "video_id":         video_id,
            "chunk_id":         chunk_id,
            "platform":         metadata.get("platform", ""),
            "title":            metadata.get("title", ""),
            "creator_name":     metadata.get("creator_name", ""),
            "views":            str(metadata.get("views", 0)),
            "likes":            str(metadata.get("likes", 0)),
            "comments":         str(metadata.get("comments", 0)),
            "engagement_rate":  str(metadata.get("engagement_rate", 0)),
            "upload_date":      metadata.get("upload_date", ""),
            "duration_seconds": str(metadata.get("duration_seconds", 0)),
            "url":              metadata.get("url", ""),
        })

    vectorstore.add_texts(
        texts=texts,
        metadatas=metadatas,
        ids=ids,
    )

    print(f"[embeddings] video {video_id}: stored in ChromaDB session {session_id}")
    return len(chunks)