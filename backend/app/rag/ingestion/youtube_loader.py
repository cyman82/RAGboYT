import re
from typing import Dict, Iterable, List, Optional, TypeAlias
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

TranscriptSegment: TypeAlias = Dict[str, float | str]


def extract_video_id(youtube_url: str) -> str:
    """
    Extract the YouTube video ID from common URL formats.
    """

    if not youtube_url:
        raise ValueError("YouTube URL is required.")

    parsed = urlparse(youtube_url)

    host = parsed.netloc.lower()

    if host in {"www.youtube.com", "youtube.com", "m.youtube.com"}:
        query = parse_qs(parsed.query)
        video_id = query.get("v", [None])[0]
        if video_id:
            return _validate_video_id(video_id)

        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) >= 2 and path_parts[0] in {"shorts", "embed"}:
            return _validate_video_id(path_parts[1])

    if host in {"youtu.be"}:
        path_parts = parsed.path.strip("/").split("/")
        if path_parts and path_parts[0]:
            return _validate_video_id(path_parts[0])

    match = re.search(r"([a-zA-Z0-9_-]{11})", youtube_url)
    if match:
        return _validate_video_id(match.group(1))

    raise ValueError("Invalid YouTube URL or unable to extract video ID.")


def _validate_video_id(video_id: str) -> str:
    if not re.fullmatch(r"[a-zA-Z0-9_-]{11}", video_id):
        raise ValueError("Invalid YouTube video ID format.")

    return video_id


def fetch_transcript(video_id: str) -> List[TranscriptSegment]:
    """
    Fetch transcript using YouTubeTranscriptApi.
    """

    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)
    except TranscriptsDisabled as error:
        raise RuntimeError("Transcripts are disabled for this video.") from error
    except NoTranscriptFound as error:
        raise RuntimeError("No transcript found for this video.") from error
    except VideoUnavailable as error:
        raise RuntimeError("Video is unavailable.") from error
    except Exception as error:
        raise RuntimeError(
            f"Unexpected error while fetching transcript: {error}"
        ) from error

    return _normalize_transcript(transcript)


def _normalize_transcript(
    transcript: Iterable[Dict[str, object] | object],
) -> List[TranscriptSegment]:
    normalized: List[TranscriptSegment] = []

    for segment in transcript:
        text = _extract_text(segment)
        start = _extract_float(segment, "start")
        duration = _extract_float(segment, "duration")

        normalized.append(
            {
                "text": text,
                "start": start,
                "duration": duration,
            }
        )

    return normalized


def _extract_text(segment: Dict[str, object] | object) -> str:
    value = _extract_field(segment, "text")

    if isinstance(value, str):
        return value.strip()

    raise RuntimeError("Transcript segment is missing 'text'.")


def _extract_float(
    segment: Dict[str, object] | object,
    key: str,
) -> float:
    value = _extract_field(segment, key)

    if isinstance(value, (int, float)):
        return float(value)

    raise RuntimeError(f"Transcript segment is missing '{key}'.")


def _extract_field(
    segment: Dict[str, object] | object,
    key: str,
) -> Optional[object]:
    if isinstance(segment, dict):
        return segment.get(key)

    return getattr(segment, key, None)


def load_youtube_transcript(
    youtube_url: str,
) -> List[TranscriptSegment]:
    """
    Complete pipeline:
    URL -> Video ID -> Transcript
    """

    video_id = extract_video_id(youtube_url)

    return fetch_transcript(video_id)