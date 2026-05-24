import asyncio
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, ingest


def create_app() -> FastAPI:
    app = FastAPI(
        title="YouTube RAG API",
        version="0.1.0",
    )

    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    extra_origins = os.getenv("CORS_ALLOW_ORIGINS")
    if extra_origins:
        allowed_origins.extend(
            origin.strip()
            for origin in extra_origins.split(",")
            if origin.strip()
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=r"chrome-extension://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(ingest.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")

    app.state.vector_store = None
    app.state.store_lock = asyncio.Lock()

    return app


app = create_app()
