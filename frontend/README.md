# YT x IG RAG Chatbot

A full-stack RAG chatbot that takes two social media video URLs (YouTube or Instagram Reels) and lets you have an AI-powered conversation about them.

## What it does

- Takes any two video URLs as input
- Extracts metadata: views, likes, comments, followers, hashtags, upload date, duration
- Computes engagement rate: ((likes + comments) / views) × 100
- Transcribes audio using Whisper
- Chunks and embeds transcripts into ChromaDB
- Lets you chat with an AI that cites which video and chunk it's answering from
- Streams responses in real time

## Tech Stack and Why

- **FastAPI** — async Python backend, perfect for streaming and ML tooling
- **React + Vite** — lightweight SPA, no SSR needed, fast dev experience
- **Groq (Llama 3.3 70B)** — free, faster than OpenAI, strong reasoning for RAG
- **HuggingFace all-MiniLM-L6-v2** — free local embeddings, zero API cost
- **ChromaDB** — zero infrastructure vector DB, persists to disk
- **LangChain** — handles RAG chain, conversation memory, retrieval
- **Whisper (base)** — free local audio transcription
- **YouTube Data API v3** — official, reliable, 10k free units/day
- **Apify Instagram Scraper** — most reliable Instagram data source

## Cost at Scale — 1000 Creators/Day

| Component | Demo Cost | At Scale Solution | Cost |
|---|---|---|---|
| LLM | Free (Groq) | Together.ai Llama | ~$1/day |
| Embeddings | Free (local) | Keep local or batch | $0 |
| Transcription | Free (local Whisper) | Groq Whisper API | ~$0.50/day |
| Vector DB | Free (ChromaDB) | Qdrant Cloud | ~$70/month |
| Instagram Data | ~$0.005/run (Apify) | Apify paid plan | ~$50/month |
| YouTube Data | Free (API quota) | Paid quota increase | ~$10/month |
| **Total** | **~$0.01/pair** | | **~$150/month** |

This stack is the most cost-efficient because:
- Groq is 97% cheaper than GPT-4o for the same RAG quality
- Local embeddings eliminate the biggest hidden cost at scale
- Local Whisper is free vs $0.00025/min on AssemblyAI

## Setup

### Requirements
- Python 3.11
- Node.js 18+
- ffmpeg in system PATH

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# add your API keys to .env
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

See `.env.example` for all required keys:
- `GROQ_API_KEY` — from console.groq.com
- `YOUTUBE_API_KEY` — from Google Cloud Console
- `APIFY_API_TOKEN` — from apify.com

## Sample Questions

- What is the engagement rate of each video?
- Who is the creator of Video B and what is their follower count?
- Compare the hooks in the first 5 seconds
- Why did Video A get more engagement than Video B?
- Suggest improvements for the lower performing video

## Architecture

```
URL → Platform Detection → Metadata Extraction → Whisper Transcription
    → Chunking (200 chars, 30 overlap) → HuggingFace Embeddings
    → ChromaDB (tagged video_id A/B) → LangChain RAG Chain
    → Groq Llama 3.3 70B → SSE Streaming → React Frontend
```