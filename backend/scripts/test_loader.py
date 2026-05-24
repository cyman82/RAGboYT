import sys
from pathlib import Path

# Add backend root to Python path
project_root = Path(__file__).resolve().parents[1]

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.rag.ingestion.youtube_loader import load_youtube_transcript


def main() -> None:
    youtube_url = input("Enter YouTube URL: ").strip()

    try:
        transcript = load_youtube_transcript(youtube_url)

        print("\nTranscript Loaded Successfully\n")

        for index, segment in enumerate(transcript[:10], start=1):
            print(f"Segment {index}")
            print(f"Start Time : {segment['start']}s")
            print(f"Duration   : {segment['duration']}s")
            print(f"Text       : {segment['text']}")
            print("-" * 50)

    except Exception as error:
        print(f"\nError: {error}")


if __name__ == "__main__":
    main()