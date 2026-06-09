import os
import httpx
import time
import whisper
import yt_dlp
from app.config import get_settings
from app.utils.engagement import compute_engagement_rate

# Absolute path for audio file
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
AUDIO_PATH = os.path.join(BASE_DIR, "reel_audio")
FFMPEG_BIN = r"C:\Users\mathimalar\Downloads\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin"


def download_reel_audio(video_url: str) -> str:
    ydl_opts = {
        "format":          "bestaudio/best",
        "outtmpl":         f"{AUDIO_PATH}.%(ext)s",
        "quiet":           True,
        "ffmpeg_location": FFMPEG_BIN,
        "postprocessors":  [{
            "key":            "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    mp3_path = f"{AUDIO_PATH}.mp3"
    print(f"[whisper] file exists: {os.path.exists(mp3_path)} at {mp3_path}")
    return mp3_path


def transcribe_audio(file_path: str) -> str:
    model  = whisper.load_model("base")
    result = model.transcribe(file_path)
    return result["text"].strip()


def get_instagram_data(url: str) -> dict:
    settings = get_settings()

    # Step 1: Start Apify actor run
    run_response = httpx.post(
        "https://api.apify.com/v2/acts/apify~instagram-scraper/runs",
        headers={"Authorization": f"Bearer {settings.apify_api_token}"},
        json={
            "directUrls":    [url],
            "resultsType":   "posts",
            "resultsLimit":  1,
            "addParentData": True,
        },
        timeout=30,
    )
    run_response.raise_for_status()
    run_id = run_response.json()["data"]["id"]
    print(f"[instagram] actor run started: {run_id}")

    # Step 2: Poll until finished
    status_response = None
    for attempt in range(24):
        time.sleep(5)
        status_response = httpx.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}",
            headers={"Authorization": f"Bearer {settings.apify_api_token}"},
            timeout=15,
        )
        status = status_response.json()["data"]["status"]
        print(f"[instagram] attempt {attempt + 1}: status = {status}")
        if status == "SUCCEEDED":
            break
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise RuntimeError(f"Apify actor failed: {status}")
    else:
        raise RuntimeError("Apify actor timed out")

    # Step 3: Fetch results
    dataset_id = status_response.json()["data"]["defaultDatasetId"]
    results    = httpx.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items",
        headers={"Authorization": f"Bearer {settings.apify_api_token}"},
        timeout=15,
    ).json()

    if not results:
        raise ValueError("Apify returned no results for this Instagram URL")

    post    = results[0]
    caption = post.get("caption") or ""
    hashtags = [word for word in caption.split() if word.startswith("#")]

    # Step 4: Whisper transcription
    video_url  = post.get("videoUrl") or post.get("url") or ""
    transcript = ""
    audio_file = None

    if video_url:
        try:
            print("[instagram] downloading reel audio...")
            audio_file = download_reel_audio(video_url)
            print("[instagram] transcribing with Whisper...")
            transcript = transcribe_audio(audio_file)
            print(f"[instagram] transcript: {transcript[:100]}")
        except Exception as e:
            print(f"[instagram] whisper failed, falling back to caption: {e}")
            transcript = caption
        finally:
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
    else:
        transcript = caption

    views    = int(post.get("videoViewCount") or post.get("playCount") or 0)
    likes    = int(post.get("likesCount") or post.get("likes") or 0)
    comments = int(post.get("commentsCount") or post.get("comments") or 0)

    return {
        "platform":         "instagram",
        "url":              url,
        "title":            caption[:100] if caption else "Instagram Reel",
        "creator_name":     post.get("ownerUsername") or post.get("owner", {}).get("username", "Unknown"),
        "follower_count":   post.get("ownerFollowersCount") or post.get("owner", {}).get("followersCount"),
        "views":            views,
        "likes":            likes,
        "comments":         comments,
        "hashtags":         hashtags,
        "upload_date":      (post.get("timestamp") or "")[:10],
        "duration_seconds": int(post.get("videoDuration") or 0),
        "transcript":       transcript if len(transcript) > 50 else caption,
        "engagement_rate":  compute_engagement_rate(likes, comments, views),
    }