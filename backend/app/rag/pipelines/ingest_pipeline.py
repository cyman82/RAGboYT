from typing import List, Optional, TypedDict

from app.llm.generator import generate_suggested_questions
from app.rag.embeddings.embedder import generate_embeddings
from app.rag.embeddings.vector_store import FAISSVectorStore, ChunkMetadata
from app.rag.ingestion.chunker import (
    TranscriptChunk,
    TranscriptSegment,
    create_chunks,
)
from app.rag.ingestion.youtube_loader import (
    extract_video_id,
    fetch_transcript,
)


class IngestResult(TypedDict):
    store: FAISSVectorStore
    video_id: str
    segments: int
    chunks: int
    suggested_questions: List[str]


def run_ingest_pipeline(
    youtube_url: str,
    store: Optional[FAISSVectorStore],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> IngestResult:
    """
    Load transcript, chunk it, embed, and store in FAISS.
    """

    video_id = extract_video_id(youtube_url)
    transcript = fetch_transcript(video_id)

    return _build_store_from_transcript(
        video_id,
        transcript,
        store,
        chunk_size,
        chunk_overlap,
    )


def run_ingest_pipeline_from_transcript(
    video_id: str,
    transcript: List[TranscriptSegment],
    store: Optional[FAISSVectorStore],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> IngestResult:
    """
    Use a provided transcript, chunk it, embed, and store in FAISS.
    """

    if not transcript:
        raise RuntimeError("Transcript is empty.")

    return _build_store_from_transcript(
        video_id,
        transcript,
        store,
        chunk_size,
        chunk_overlap,
    )


def _build_store_from_transcript(
    video_id: str,
    transcript: List[TranscriptSegment],
    store: Optional[FAISSVectorStore],
    chunk_size: int,
    chunk_overlap: int,
) -> IngestResult:
    chunks: List[TranscriptChunk] = create_chunks(
        transcript,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    if not chunks:
        raise RuntimeError("No chunks produced from transcript.")

    texts = [chunk["content"] for chunk in chunks]
    embeddings = generate_embeddings(texts)

    if not embeddings:
        raise RuntimeError("Failed to generate embeddings.")

    if store is None:
        store = FAISSVectorStore(dimension=len(embeddings[0]))

    store.add_embeddings(
        embeddings,
        chunks,
    )

    suggestions = _build_suggested_questions(chunks)

    return {
        "store": store,
        "video_id": video_id,
        "segments": len(transcript),
        "chunks": len(chunks),
        "suggested_questions": suggestions,
    }


def _build_suggested_questions(
    chunks: List[TranscriptChunk],
) -> List[str]:
    if not chunks:
        return []

    sample = "\n".join(
        chunk["content"] for chunk in chunks[:4]
    )
    sample = sample.strip()[:1200]

    try:
        return generate_suggested_questions(sample)
    except RuntimeError:
        return []
