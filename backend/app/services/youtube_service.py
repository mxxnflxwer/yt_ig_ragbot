import re
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from app.config import get_settings


def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11})",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url}")


def parse_duration(duration: str) -> int:
    """Convert ISO 8601 duration (PT1H2M3S) to seconds."""
    match = re.match(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration
    )
    if not match:
        return 0
    hours   = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def get_youtube_data(url: str) -> dict:
    settings = get_settings()
    video_id = extract_video_id(url)

    youtube = build("youtube", "v3", developerKey=settings.youtube_api_key)

    # Single API call fetches snippet + statistics + contentDetails
    response = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=video_id
    ).execute()

    if not response.get("items"):
        raise ValueError(f"No video found for ID: {video_id}")

    item      = response["items"][0]
    snippet   = item["snippet"]
    stats     = item.get("statistics", {})
    content   = item["contentDetails"]

    # Hashtags from tags
    tags     = snippet.get("tags") or []
    hashtags = [t for t in tags if t.startswith("#")]
    if not hashtags:
        hashtags = [f"#{t}" for t in tags[:5]]

    # Channel subscriber count — needs separate call
    channel_id = snippet.get("channelId")
    follower_count = None
    if channel_id:
        ch_response = youtube.channels().list(
            part="statistics",
            id=channel_id
        ).execute()
        if ch_response.get("items"):
            ch_stats = ch_response["items"][0].get("statistics", {})
            follower_count = int(ch_stats.get("subscriberCount") or 0)

    # Get transcript
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id)
        transcript = " ".join(snippet.text for snippet in fetched)
    except Exception:
        transcript = ""

    return {
        "platform":         "youtube",
        "url":              url,
        "title":            snippet.get("title", "Unknown"),
        "creator_name":     snippet.get("channelTitle", "Unknown"),
        "follower_count":   follower_count,
        "views":            int(stats.get("viewCount") or 0),
        "likes":            int(stats.get("likeCount") or 0),
        "comments":         int(stats.get("commentCount") or 0),
        "hashtags":         hashtags,
        "upload_date":      snippet.get("publishedAt", "")[:10],
        "duration_seconds": parse_duration(content.get("duration", "")),
        "transcript":       transcript,
    }