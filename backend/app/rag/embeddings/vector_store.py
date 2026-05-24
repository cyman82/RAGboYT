from typing import List, TypedDict

import faiss
import numpy as np


class ChunkMetadata(TypedDict):
    content: str
    start_time: float
    end_time: float


class SearchResult(ChunkMetadata):
    score: float


class FAISSVectorStore:

    def __init__(self, dimension: int):
        if dimension <= 0:
            raise ValueError("dimension must be > 0")

        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata: List[ChunkMetadata] = []

    def add_embeddings(
        self,
        embeddings: List[List[float]],
        chunks: List[ChunkMetadata],
    ) -> None:
        if not embeddings:
            return

        if len(embeddings) != len(chunks):
            raise ValueError("embeddings and chunks must have same length")

        vectors = np.array(embeddings, dtype="float32")

        if vectors.ndim != 2 or vectors.shape[1] != self.dimension:
            raise ValueError(
                "Embedding dimension mismatch with FAISS index"
            )

        self.index.add(vectors)
        self.metadata.extend(chunks)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[SearchResult]:
        if top_k <= 0:
            raise ValueError("top_k must be > 0")

        if self.index.ntotal == 0:
            return []

        query_vector = np.array(
            [query_embedding],
            dtype="float32",
        )

        if query_vector.shape[1] != self.dimension:
            raise ValueError(
                "Query embedding dimension mismatch with FAISS index"
            )

        distances, indices = self.index.search(
            query_vector,
            top_k,
        )

        results: List[SearchResult] = []

        for idx, distance in zip(
            indices[0],
            distances[0],
        ):
            if idx == -1:
                continue

            result: SearchResult = {
                "content": self.metadata[idx]["content"],
                "start_time": self.metadata[idx]["start_time"],
                "end_time": self.metadata[idx]["end_time"],
                "score": float(distance),
            }

            results.append(result)

        return results

    def search_by_time(
        self,
        center_time: float,
        window_seconds: float,
        top_k: int = 5,
    ) -> List[SearchResult]:
        if top_k <= 0:
            raise ValueError("top_k must be > 0")

        if window_seconds < 0:
            raise ValueError("window_seconds must be >= 0")

        window_start = max(0.0, center_time - window_seconds)
        window_end = center_time + window_seconds

        matches: List[SearchResult] = []

        for chunk in self.metadata:
            if chunk["start_time"] <= window_end and chunk["end_time"] >= window_start:
                midpoint = (chunk["start_time"] + chunk["end_time"]) / 2
                distance = abs(center_time - midpoint)
                matches.append(
                    {
                        "content": chunk["content"],
                        "start_time": chunk["start_time"],
                        "end_time": chunk["end_time"],
                        "score": float(distance),
                    }
                )

        matches.sort(key=lambda item: item["score"])
        return matches[:top_k]