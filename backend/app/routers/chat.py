from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse
from app.models import ChatRequest, ChatResponse, SourceChunk
from app.services.rag_service import get_rag_chain, get_sources, ask
import json

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        chain = get_rag_chain(request.session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    async def stream():
       async def stream():
        try:
            sources      = []
            full_answer  = ""

            async for chunk in chain.astream({"question": request.message}):
                if "answer" in chunk and chunk["answer"]:
                    token = chunk["answer"]
                    # Skip if this chunk IS the full answer (dedup)
                    if token != full_answer:
                        full_answer += token
                        yield {
                            "data": json.dumps({
                                "type":    "token",
                                "content": token,
                            })
                        }
                if "source_documents" in chunk:
                    sources = get_sources(chunk["source_documents"])

            yield {"data": json.dumps({"type": "sources", "content": sources})}
            yield {"data": json.dumps({"type": "done"})}

        except Exception as e:
            yield {"data": json.dumps({"type": "error", "content": str(e)})}

@router.post("/chat/sync", response_model=ChatResponse)
async def chat_sync(request: ChatRequest):
    try:
        result = ask(request.session_id, request.message)
        return ChatResponse(
            answer=result["answer"],
            sources=[SourceChunk(**s) for s in result["sources"]],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))