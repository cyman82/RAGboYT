from typing import TypedDict

from app.llm.generator import generate_answer
from app.rag.embeddings.vector_store import FAISSVectorStore, SearchResult
from app.rag.prompting.prompt_builder import build_prompt
from app.rag.retrieval.formatter import (
    format_retrieved_chunks,
    format_timestamp,
)
from app.rag.retrieval.retriever import retrieve_chunks


class QueryPipelineResult(TypedDict):
    answer: str
    context: str
    chunks: list[SearchResult]


def run_query_pipeline(
    question: str,
    store: FAISSVectorStore,
    top_k: int = 5,
    max_chunks: int | None = None,
    time_window_seconds: float | None = None,
    prompt_template: str | None = None,
    model: str | None = None,
) -> QueryPipelineResult:
    """
    Retrieve context, build a grounded prompt, and generate an answer.
    """

    chunks = retrieve_chunks(
        question,
        store,
        top_k=top_k,
        time_window_seconds=time_window_seconds,
    )

    context = format_retrieved_chunks(
        chunks,
        max_chunks=max_chunks,
    )

    confidence_hint = _confidence_hint(chunks)
    evidence_snippets = _build_evidence_snippets(
        chunks,
        max_quotes=2,
    )

    prompt = build_prompt(
        question=question,
        context=context,
        template=prompt_template,
        confidence_hint=confidence_hint,
        evidence_snippets=evidence_snippets,
    )

    answer = generate_answer(
        prompt=prompt,
        model=model,
    )

    return {
        "answer": answer,
        "context": context,
        "chunks": chunks,
    }


def _confidence_hint(chunks: list[SearchResult]) -> str:
    if not chunks:
        return "low"

    scores = sorted(chunk["score"] for chunk in chunks)
    min_score = scores[0]
    max_score = scores[-1]
    spread = max_score - min_score

    if spread <= 0.05:
        return "medium"

    median_score = scores[len(scores) // 2]
    normalized = (median_score - min_score) / spread

    if normalized <= 0.33:
        return "high"
    if normalized <= 0.66:
        return "medium"

    return "low"


def _build_evidence_snippets(
    chunks: list[SearchResult],
    max_quotes: int,
) -> str:
    if not chunks:
        return "- None"

    lines = []
    for chunk in chunks[:max_quotes]:
        start = format_timestamp(chunk["start_time"])
        end = format_timestamp(chunk["end_time"])
        quote = _clip_quote(chunk["content"])
        lines.append(f"- [{start} - {end}] \"{quote}\"")

    return "\n".join(lines)


def _clip_quote(text: str, limit: int = 160) -> str:
    cleaned = " ".join(text.strip().split())
    if len(cleaned) <= limit:
        return cleaned

    return f"{cleaned[:limit].rstrip()}..."
