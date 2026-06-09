import os
import yt_dlp
import whisper

FFMPEG_BIN = r"C:\Users\mathimalar\Downloads\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin"
AUDIO_PATH = r"C:\Users\mathimalar\Downloads\yt_ig_ragbot\backend\reel_audio"

# Use a direct video URL — paste the Instagram video direct URL here
VIDEO_URL = "https://www.instagram.com/reel/DXLb7Yak35n/?igsh=bzVndndydWJqajZk"

print("Step 1: downloading audio...")
ydl_opts = {
    "format":          "bestaudio/best",
    "outtmpl":         f"{AUDIO_PATH}.%(ext)s",
    "quiet":           False,
    "ffmpeg_location": FFMPEG_BIN,
    "postprocessors":  [{
        "key":            "FFmpegExtractAudio",
        "preferredcodec": "mp3",
    }],
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([VIDEO_URL])

mp3 = f"{AUDIO_PATH}.mp3"
print(f"Step 2: file exists? {os.path.exists(mp3)}")
print(f"Step 3: transcribing...")
model  = whisper.load_model("base")
result = model.transcribe(mp3)
print(f"Transcript: {result['text']}")