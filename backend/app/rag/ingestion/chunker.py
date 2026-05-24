from typing import List, TypedDict


class TranscriptSegment(TypedDict):
    text: str
    start: float
    duration: float


class TranscriptChunk(TypedDict):
    content: str
    start_time: float
    end_time: float


def create_chunks(
    transcript: List[TranscriptSegment],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[TranscriptChunk]:
    """
    Convert transcript segments into chunks while preserving timestamps.

    Chunking is character-based to keep it simple and predictable, but the
    chunk boundaries always align with transcript segments to maintain
    continuity.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    if not transcript:
        return []

    chunks: List[TranscriptChunk] = []
    current_segments: List[TranscriptSegment] = []
    current_length = 0

    for segment in transcript:
        text = segment["text"].strip()
        if not text:
            continue

        segment_length = len(text)

        if current_segments and current_length + segment_length > chunk_size:
            chunks.append(_build_chunk(current_segments))

            current_segments, current_length = _apply_overlap(
                current_segments,
                chunk_overlap,
            )

        current_segments.append(
            {
                "text": text,
                "start": float(segment["start"]),
                "duration": float(segment["duration"]),
            }
        )

        current_length += segment_length

        if segment_length >= chunk_size:
            chunks.append(_build_chunk(current_segments))
            current_segments = []
            current_length = 0

    if current_segments:
        chunks.append(_build_chunk(current_segments))

    return chunks


def _apply_overlap(
    segments: List[TranscriptSegment],
    chunk_overlap: int,
) -> tuple[List[TranscriptSegment], int]:
    if chunk_overlap == 0:
        return [], 0

    overlap_segments: List[TranscriptSegment] = []
    overlap_length = 0

    for segment in reversed(segments):
        overlap_segments.insert(0, segment)
        overlap_length += len(segment["text"])

        if overlap_length >= chunk_overlap:
            break

    return overlap_segments, overlap_length


def _build_chunk(
    segments: List[TranscriptSegment],
) -> TranscriptChunk:
    content = " ".join(segment["text"] for segment in segments)

    start_time = segments[0]["start"]
    last_segment = segments[-1]
    end_time = last_segment["start"] + last_segment["duration"]

    return {
        "content": content,
        "start_time": round(start_time, 2),
        "end_time": round(end_time, 2),
    }