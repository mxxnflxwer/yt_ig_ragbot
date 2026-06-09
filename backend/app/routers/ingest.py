import uuid
from fastapi import APIRouter, HTTPException
from app.models import IngestRequest, IngestResponse, VideoMetadata
from app.services.youtube_service import get_youtube_data
from app.services.instagram_service import get_instagram_data
from app.services.embedding_service import chunk_and_embed

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    session_id = str(uuid.uuid4())

    # Extract YouTube data
    try:
        yt_data = get_youtube_data(request.youtube_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"YouTube extraction failed: {str(e)}")

    # Extract Instagram data
    try:
        ig_data = get_instagram_data(request.instagram_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Instagram extraction failed: {str(e)}")

    # Chunk and embed both transcripts
    try:
        print(f"[debug] yt_data keys: {list(yt_data.keys())}")
        print(f"[debug] ig_data keys: {list(ig_data.keys())}")
        yt_chunks = chunk_and_embed(session_id, "A", yt_data["transcript"], yt_data)
        ig_chunks = chunk_and_embed(session_id, "B", ig_data["transcript"], ig_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

    video_a = VideoMetadata(
        video_id="A",
        platform=yt_data["platform"],
        url=yt_data["url"],
        title=yt_data["title"],
        creator_name=yt_data["creator_name"],
        follower_count=yt_data.get("follower_count"),
        views=yt_data["views"],
        likes=yt_data["likes"],
        comments=yt_data["comments"],
        hashtags=yt_data["hashtags"],
        upload_date=yt_data["upload_date"],
        duration_seconds=yt_data["duration_seconds"],
        engagement_rate=yt_data["engagement_rate"],
        transcript_chunks=yt_chunks,
    )

    video_b = VideoMetadata(
        video_id="B",
        platform=ig_data["platform"],
        url=ig_data["url"],
        title=ig_data["title"],
        creator_name=ig_data["creator_name"],
        follower_count=ig_data.get("follower_count"),
        views=ig_data["views"],
        likes=ig_data["likes"],
        comments=ig_data["comments"],
        hashtags=ig_data["hashtags"],
        upload_date=ig_data["upload_date"],
        duration_seconds=ig_data["duration_seconds"],
        engagement_rate=ig_data["engagement_rate"],
        transcript_chunks=ig_chunks,
    )

    return IngestResponse(
        success=True,
        session_id=session_id,
        video_a=video_a,
        video_b=video_b,
    )