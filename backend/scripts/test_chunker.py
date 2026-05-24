import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.rag.ingestion.youtube_loader import (
    load_youtube_transcript,
)

from app.rag.ingestion.chunker import create_chunks


def main() -> None:

    youtube_url = input(
        "Enter YouTube URL: "
    ).strip()

    transcript = load_youtube_transcript(
        youtube_url
    )

    chunks = create_chunks(transcript)

    print(f"\nTotal Chunks: {len(chunks)}\n")

    for index, chunk in enumerate(chunks[:3], start=1):

        print(f"Chunk {index}")
        print(
            f"Start Time: {chunk['start_time']}s"
        )

        print(
            f"End Time: {chunk['end_time']}s"
        )

        print("\nContent:\n")

        print(chunk["content"])

        print("-" * 80)


if __name__ == "__main__":
    main()