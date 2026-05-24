from typing import Iterable, List

from app.rag.embeddings.vector_store import SearchResult


def format_retrieved_chunks(
    results: Iterable[SearchResult],
    max_chunks: int | None = None,
) -> str:
    """
    Format retrieved chunks into LLM-ready grounded context.
    """

    formatted: List[str] = []

    for index, chunk in enumerate(results, start=1):
        if max_chunks is not None and index > max_chunks:
            break

        start_time = format_timestamp(chunk["start_time"])
        end_time = format_timestamp(chunk["end_time"])
        score = _format_score(chunk["score"])
        content = chunk["content"].strip()

        if not content:
            continue

        formatted.append(
            "\n".join(
                [
                    f"[Chunk {index}] {start_time} - {end_time} | score={score}",
                    content,
                ]
            )
        )

    return "\n\n".join(formatted)


def format_timestamp(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0

    total_seconds = int(seconds)
    millis = int(round((seconds - total_seconds) * 1000))

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    return f"{minutes:02d}:{secs:02d}.{millis:03d}"


def _format_score(score: float) -> str:
    if score < 0:
        score = 0.0

    return f"{score:.4f}"
