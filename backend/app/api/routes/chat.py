from typing import List

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from app.rag.embeddings.vector_store import SearchResult
from app.rag.pipelines.query_pipeline import run_query_pipeline

router = APIRouter()


class SearchResultModel(BaseModel):
    content: str
    start_time: float
    end_time: float
    score: float


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1)
    max_chunks: int | None = Field(None, ge=1)
    time_window_seconds: float | None = Field(
        default=None,
        ge=1,
        json_schema_extra={"example": None},
    )
    model: str | None = Field(
        default=None,
        json_schema_extra={"example": None},
    )
    prompt_template: str | None = Field(
        default=None,
        json_schema_extra={"example": None},
    )


class ChatResponse(BaseModel):
    answer: str
    context: str
    chunks: List[SearchResultModel]


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    http_request: Request,
) -> ChatResponse:
    store = http_request.app.state.vector_store
    if store is None:
        raise HTTPException(
            status_code=400,
            detail="Vector store is empty. Ingest a transcript first.",
        )

    try:
        model = _normalize_optional_string(request.model)
        prompt_template = _normalize_optional_string(
            request.prompt_template
        )

        result = await run_in_threadpool(
            run_query_pipeline,
            request.question,
            store,
            request.top_k,
            request.max_chunks,
            request.time_window_seconds,
            prompt_template,
            model,
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

    return ChatResponse(
        answer=result["answer"],
        context=result["context"],
        chunks=[
            SearchResultModel(**chunk)
            for chunk in result["chunks"]
        ],
    )


def _normalize_optional_string(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()
    if not cleaned or cleaned == "string":
        return None

    return cleaned
