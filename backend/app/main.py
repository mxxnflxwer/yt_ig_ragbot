from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import ingest, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"[startup] LLM model       : {settings.groq_llm_model}")
    print(f"[startup] embedding model : {settings.embedding_model}")
    print(f"[startup] chroma path     : {settings.chroma_persist_dir}")
    yield
    print("[shutdown] server stopped")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="RAG Chatbot API",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(ingest.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()