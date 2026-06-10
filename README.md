# RAG Video Analyst

I built this as a technical screening project — a full-stack RAG chatbot that lets you compare two social media videos using AI. You paste in any two URLs (YouTube or Instagram Reels), and it pulls all the metadata, transcribes the audio, and lets you chat with an AI about both videos.

## What it does

You give it two video URLs. It fetches the metadata (views, likes, comments, follower count, hashtags, upload date, duration), transcribes the audio using Whisper, and stores everything in a vector database. Then you can ask questions like "why did Video A perform better?" or "what's the engagement rate of each?" and get answers that cite exactly which video and transcript chunk they came from.

Engagement rate is calculated as: `((likes + comments) / views) × 100`

## Why I chose this stack

**Groq instead of OpenAI** — Groq's free tier runs Llama 3.3 70B and it's genuinely fast. For a RAG task where the model is mostly summarizing retrieved context, it performs as well as GPT-4o at a fraction of the cost. At scale this matters a lot.

**HuggingFace embeddings instead of OpenAI** — `all-MiniLM-L6-v2` runs locally, costs nothing, and is good enough for semantic similarity on transcript chunks. No API calls, no latency, no cost.

**ChromaDB instead of Pinecone** — For a demo and small scale, ChromaDB is perfect. It runs in-process and persists to disk. At 1000 creators/day I'd migrate to Qdrant Cloud or Pinecone.

**Whisper for transcription** — Free, runs locally, works well for speech. For scale I'd switch to the Groq Whisper API which is also free and much faster.

**YouTube Data API v3 instead of yt-dlp** — yt-dlp kept failing with YouTube's bot detection. The official API is more reliable and has 10k free units/day which is more than enough.

**Apify for Instagram** — Instagram blocks scrapers aggressively. Apify is the most reliable option with a free trial. I use two actors — one for post data and one for follower count.

**FastAPI** — Native async, works great with streaming, and the Python ecosystem makes LangChain integration easy.

**React + Vite** — Simple SPA, no SSR needed. Vite is faster than CRA and the bundle is lighter than Next.js for this use case.

## Running it locally

### What you need
- Python 3.11
- Node.js 18+
- ffmpeg installed and added to PATH

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# fill in your API keys
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

## API Keys needed

Check `.env.example` — you need:
- `GROQ_API_KEY` → free at console.groq.com
- `YOUTUBE_API_KEY` → free at Google Cloud Console
- `APIFY_API_TOKEN` → free trial at apify.com

## Cost at scale — 1000 creators/day

| What | Now | At scale |
|---|---|---|
| LLM | Free (Groq) | ~$1/day (Together.ai) |
| Embeddings | Free (local) | Still free |
| Transcription | Free (local Whisper) | Free (Groq Whisper API) |
| Vector DB | Free (ChromaDB) | ~$70/month (Qdrant Cloud) |
| Instagram scraping | ~$0.005/run | ~$50/month (Apify paid) |
| YouTube API | Free (quota) | ~$10/month |
| **Total** | **~$0.01/pair** | **~$150/month** |

The biggest cost driver at scale is the vector DB and Instagram scraping. Everything else stays cheap because I avoided OpenAI for both embeddings and the LLM.

## Things I'd improve for production

- Add a job queue (Celery + Redis) so ingestion runs async and doesn't block the HTTP request
- Cache embeddings so the same video URL doesn't get re-processed
- Add rate limiting on the API
- Move Whisper to a GPU or use Groq's Whisper API for faster transcription
- Add support for TikTok

## How to use it

Paste two video URLs, wait about 60-90 seconds for processing, then ask:

- What is the engagement rate of each video?
- Who is the creator of Video B and what is their follower count?
- Compare the hooks in the first 5 seconds of each video
- Why did Video A get more engagement than Video B?
- Suggest improvements for the lower performing video based on what worked in the other one
