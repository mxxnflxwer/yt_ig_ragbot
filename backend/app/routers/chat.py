from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models import ChatRequest, ChatResponse, SourceChunk
from app.services.rag_service import get_rag_chain, get_sources
import json

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    """Streaming RAG chat endpoint using SSE."""
    try:
        chain = get_rag_chain(request.session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Session not found: {str(e)}")

    async def stream():
       async def stream():
        try:
            sources      = []
            seen_content = set()

            async for chunk in chain.astream({"question": request.message}):
                if "answer" in chunk:
                    token = chunk["answer"]
                    if token and token not in seen_content:
                        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

                if "source_documents" in chunk:
                    sources = get_sources(chunk["source_documents"])

            yield f"data: {json.dumps({'type': 'sources', 'content': sources})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":               "no-cache",
            "X-Accel-Buffering":           "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.post("/chat/sync", response_model=ChatResponse)
async def chat_sync(request: ChatRequest):
    """Non-streaming fallback for testing."""
    try:
        from app.services.rag_service import ask
        result = ask(request.session_id, request.message)
        return ChatResponse(
            answer=result["answer"],
            sources=[SourceChunk(**s) for s in result["sources"]],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))