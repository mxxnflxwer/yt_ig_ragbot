import uuid
from fastapi import APIRouter, HTTPException
from app.models import IngestRequest, IngestResponse, VideoMetadata
from app.services.youtube_service import get_youtube_data
from app.services.instagram_service import get_instagram_data
from app.services.embedding_service import chunk_and_embed

router = APIRouter()


def detect_platform(url: str) -> str:
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    if "instagram.com" in url:
        return "instagram"
    raise ValueError(f"Unsupported URL: {url}")


def fetch_video_data(url: str) -> dict:
    platform = detect_platform(url)
    if platform == "youtube":
        return get_youtube_data(url)
    return get_instagram_data(url)


@router.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    session_id = str(uuid.uuid4())

    try:
        data_a = fetch_video_data(request.url_a)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Video A failed: {str(e)}")

    try:
        data_b = fetch_video_data(request.url_b)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Video B failed: {str(e)}")

    try:
        chunks_a = chunk_and_embed(session_id, "A", data_a["transcript"], data_a)
        chunks_b = chunk_and_embed(session_id, "B", data_b["transcript"], data_b)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

    from app.services.rag_service import set_video_context
    set_video_context(session_id, data_a, data_b)

    video_a = VideoMetadata(
        video_id="A",
        platform=data_a["platform"],
        url=data_a["url"],
        title=data_a["title"],
        creator_name=data_a["creator_name"],
        follower_count=data_a.get("follower_count"),
        views=data_a["views"],
        likes=data_a["likes"],
        comments=data_a["comments"],
        hashtags=data_a["hashtags"],
        upload_date=data_a["upload_date"],
        duration_seconds=data_a["duration_seconds"],
        engagement_rate=data_a["engagement_rate"],
        transcript_chunks=chunks_a,
    )

    video_b = VideoMetadata(
        video_id="B",
        platform=data_b["platform"],
        url=data_b["url"],
        title=data_b["title"],
        creator_name=data_b["creator_name"],
        follower_count=data_b.get("follower_count"),
        views=data_b["views"],
        likes=data_b["likes"],
        comments=data_b["comments"],
        hashtags=data_b["hashtags"],
        upload_date=data_b["upload_date"],
        duration_seconds=data_b["duration_seconds"],
        engagement_rate=data_b["engagement_rate"],
        transcript_chunks=chunks_b,
    )

    return IngestResponse(
        success=True,
        session_id=session_id,
        video_a=video_a,
        video_b=video_b,
    )