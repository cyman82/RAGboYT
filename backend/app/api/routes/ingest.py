from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from app.rag.pipelines.ingest_pipeline import (
    run_ingest_pipeline,
    run_ingest_pipeline_from_transcript,
)

router = APIRouter()


class IngestRequest(BaseModel):
    youtube_url: str = Field(..., min_length=1)
    chunk_size: int = Field(1000, ge=1)
    chunk_overlap: int = Field(200, ge=0)


class IngestResponse(BaseModel):
    video_id: str
    segments: int
    chunks: int
    suggested_questions: list[str]


class TranscriptSegmentModel(BaseModel):
    text: str = Field(..., min_length=1)
    start: float = Field(..., ge=0)
    duration: float = Field(..., ge=0)


class IngestTranscriptRequest(BaseModel):
    video_id: str = Field(..., min_length=1)
    transcript: list[TranscriptSegmentModel]
    chunk_size: int = Field(1000, ge=1)
    chunk_overlap: int = Field(200, ge=0)


@router.post("/ingest", response_model=IngestResponse)
async def ingest_transcript(
    request: IngestRequest,
    http_request: Request,
) -> IngestResponse:
    try:
        async with http_request.app.state.store_lock:
            store = http_request.app.state.vector_store
            result = await run_in_threadpool(
                run_ingest_pipeline,
                request.youtube_url,
                store,
                request.chunk_size,
                request.chunk_overlap,
            )
            http_request.app.state.vector_store = result["store"]

        return IngestResponse(
            video_id=result["video_id"],
            segments=result["segments"],
            chunks=result["chunks"],
            suggested_questions=result["suggested_questions"],
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error


@router.post("/ingest_text", response_model=IngestResponse)
async def ingest_transcript_text(
    request: IngestTranscriptRequest,
    http_request: Request,
) -> IngestResponse:
    try:
        async with http_request.app.state.store_lock:
            store = http_request.app.state.vector_store
            result = await run_in_threadpool(
                run_ingest_pipeline_from_transcript,
                request.video_id,
                [segment.model_dump() for segment in request.transcript],
                store,
                request.chunk_size,
                request.chunk_overlap,
            )
            http_request.app.state.vector_store = result["store"]

        return IngestResponse(
            video_id=result["video_id"],
            segments=result["segments"],
            chunks=result["chunks"],
            suggested_questions=result["suggested_questions"],
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
