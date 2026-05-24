import re
from typing import List, Optional

from app.rag.embeddings.embedder import generate_embeddings
from app.rag.embeddings.vector_store import FAISSVectorStore, SearchResult

_TIME_WINDOW_SECONDS = 45.0
_SEMANTIC_OVERSAMPLE = 3
_KEYWORD_WEIGHT = 0.4
_TIME_WEIGHT = 0.7
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "how",
    "if",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "we",
    "what",
    "when",
    "where",
    "why",
    "with",
}


def retrieve_chunks(
    query: str,
    store: FAISSVectorStore,
    top_k: int = 5,
    time_window_seconds: float | None = None,
) -> List[SearchResult]:
    """
    Embed a user query and retrieve the most similar chunks.
    """

    if top_k <= 0:
        raise ValueError("top_k must be > 0")

    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    timestamp = _extract_timestamp_seconds(cleaned_query)
    if timestamp is not None:
        window = _TIME_WINDOW_SECONDS
        if time_window_seconds is not None:
            if time_window_seconds <= 0:
                raise ValueError("time_window_seconds must be > 0")
            window = time_window_seconds

        time_results = store.search_by_time(
            timestamp,
            window_seconds=window,
            top_k=top_k,
        )
        if time_results:
            return _rerank_time_results(
                cleaned_query,
                time_results,
                timestamp,
                window,
            )

    try:
        embeddings = generate_embeddings([cleaned_query])
    except Exception as error:
        raise RuntimeError(
            f"Failed to generate query embedding: {error}"
        ) from error

    if not embeddings:
        return []

    oversample = max(top_k * _SEMANTIC_OVERSAMPLE, top_k)
    semantic_results = store.search(
        embeddings[0],
        top_k=oversample,
    )

    if not semantic_results:
        return []

    return _rerank_semantic_results(
        cleaned_query,
        semantic_results,
        top_k,
    )


def _extract_timestamp_seconds(query: str) -> Optional[float]:
    match = re.search(
        r"\b(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\.(\d{1,3}))?\b",
        query,
    )

    if not match:
        return None

    first = int(match.group(1))
    second = int(match.group(2))
    third = match.group(3)
    millis = match.group(4)

    if third is not None:
        hours = first
        minutes = second
        seconds = int(third)
    else:
        hours = 0
        minutes = first
        seconds = second

    total_seconds = hours * 3600 + minutes * 60 + seconds

    if millis is not None:
        total_seconds += int(millis.ljust(3, "0")) / 1000

    return float(total_seconds)


def _rerank_semantic_results(
    query: str,
    results: List[SearchResult],
    top_k: int,
) -> List[SearchResult]:
    keyword_scores = _keyword_scores(query, results)
    distances = [result["score"] for result in results]
    min_distance = min(distances)
    max_distance = max(distances)

    reranked: List[SearchResult] = []

    for result in results:
        distance = result["score"]
        distance_norm = _normalize(distance, min_distance, max_distance)
        semantic_similarity = 1 - distance_norm
        keyword_score = keyword_scores.get(
            _chunk_key(result),
            0.0,
        )

        combined_similarity = (
            (1 - _KEYWORD_WEIGHT) * semantic_similarity
            + _KEYWORD_WEIGHT * keyword_score
        )

        combined_distance = 1 - combined_similarity
        reranked.append(
            {
                "content": result["content"],
                "start_time": result["start_time"],
                "end_time": result["end_time"],
                "score": float(combined_distance),
            }
        )

    reranked.sort(key=lambda item: item["score"])
    return reranked[:top_k]


def _rerank_time_results(
    query: str,
    results: List[SearchResult],
    timestamp: float,
    window_seconds: float,
) -> List[SearchResult]:
    keyword_scores = _keyword_scores(query, results)
    reranked: List[SearchResult] = []

    for result in results:
        midpoint = (result["start_time"] + result["end_time"]) / 2
        time_distance = abs(timestamp - midpoint)
        time_similarity = 1 - min(time_distance / window_seconds, 1.0)
        keyword_score = keyword_scores.get(
            _chunk_key(result),
            0.0,
        )

        combined_similarity = (
            _TIME_WEIGHT * time_similarity
            + (1 - _TIME_WEIGHT) * keyword_score
        )

        combined_distance = 1 - combined_similarity
        reranked.append(
            {
                "content": result["content"],
                "start_time": result["start_time"],
                "end_time": result["end_time"],
                "score": float(combined_distance),
            }
        )

    reranked.sort(key=lambda item: item["score"])
    return reranked


def _keyword_scores(
    query: str,
    results: List[SearchResult],
) -> dict[str, float]:
    query_terms = _tokenize(query)
    if not query_terms:
        return {}

    scores: dict[str, float] = {}
    for result in results:
        content_terms = _tokenize(result["content"])
        if not content_terms:
            scores[_chunk_key(result)] = 0.0
            continue

        overlap = query_terms.intersection(content_terms)
        scores[_chunk_key(result)] = len(overlap) / len(query_terms)

    return scores


def _tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {token for token in tokens if token not in _STOPWORDS}


def _normalize(value: float, min_value: float, max_value: float) -> float:
    if max_value == min_value:
        return 0.0

    return (value - min_value) / (max_value - min_value)


def _chunk_key(result: SearchResult) -> str:
    return f"{result['start_time']}-{result['end_time']}"
