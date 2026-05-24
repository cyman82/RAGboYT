import os
from typing import Iterable, List

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()

_MODEL_NAME = "text-embedding-3-small"
_DEFAULT_BATCH_SIZE = 128


def generate_embeddings(
    texts: List[str],
    batch_size: int = _DEFAULT_BATCH_SIZE,
) -> List[List[float]]:
    """
    Generate embeddings for text chunks.
    """

    if not texts:
        return []

    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)

    embeddings: List[List[float]] = []

    try:
        for batch in _iter_batches(texts, batch_size):
            response = client.embeddings.create(
                model=_MODEL_NAME,
                input=batch,
            )
            embeddings.extend(
                item.embedding for item in response.data
            )
    except OpenAIError as error:
        raise RuntimeError(
            f"OpenAI embeddings request failed: {error}"
        ) from error

    return embeddings


def _iter_batches(
    items: List[str],
    batch_size: int,
) -> Iterable[List[str]]:
    for index in range(0, len(items), batch_size):
        yield items[index : index + batch_size]