from pydantic import BaseModel
from typing import Optional


class IngestRequest(BaseModel):
    youtube_url: str
    instagram_url: str


class VideoMetadata(BaseModel):
    video_id: str
    platform: str
    url: str
    title: str
    creator_name: str
    follower_count: Optional[int] = None
    views: int
    likes: int
    comments: int
    hashtags: list[str]
    upload_date: str
    duration_seconds: int
    engagement_rate: float
    transcript_chunks: int


class IngestResponse(BaseModel):
    success: bool
    session_id: str
    video_a: VideoMetadata
    video_b: VideoMetadata


class ChatRequest(BaseModel):
    session_id: str
    message: str


class SourceChunk(BaseModel):
    video_id: str
    chunk_id: str
    text: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]