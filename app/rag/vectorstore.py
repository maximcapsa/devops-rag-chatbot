"""FAISS-backed vector store with a small JSON sidecar for chunk metadata.

The index is built offline by ``app/ingest.py`` and loaded read-only at runtime.
We use inner-product over L2-normalized vectors, which is equivalent to cosine
similarity.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np

INDEX_FILE = "index.faiss"
META_FILE = "meta.json"


@dataclass
class Chunk:
    text: str
    source: str


def _normalize(vectors: np.ndarray) -> np.ndarray:
    vectors = vectors.astype("float32")
    faiss.normalize_L2(vectors)
    return vectors


class VectorStore:
    def __init__(self, index: faiss.Index, chunks: list[Chunk]) -> None:
        self.index = index
        self.chunks = chunks

    # ---- persistence ----------------------------------------------------
    @classmethod
    def build(cls, embeddings: list[list[float]], chunks: list[Chunk]) -> VectorStore:
        if len(embeddings) != len(chunks):
            raise ValueError("embeddings and chunks length mismatch")
        matrix = _normalize(np.array(embeddings, dtype="float32"))
        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)
        return cls(index, chunks)

    def save(self, directory: str | Path) -> None:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(directory / INDEX_FILE))
        meta = [{"text": c.text, "source": c.source} for c in self.chunks]
        (directory / META_FILE).write_text(json.dumps(meta), encoding="utf-8")

    @classmethod
    def load(cls, directory: str | Path) -> VectorStore:
        directory = Path(directory)
        index_path = directory / INDEX_FILE
        meta_path = directory / META_FILE
        if not index_path.exists() or not meta_path.exists():
            raise FileNotFoundError(
                f"Vector store not found in {directory}. Run `python -m app.ingest` first."
            )
        index = faiss.read_index(str(index_path))
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        chunks = [Chunk(text=m["text"], source=m["source"]) for m in meta]
        return cls(index, chunks)

    # ---- query ----------------------------------------------------------
    def search(self, query_embedding: list[float], top_k: int = 4) -> list[tuple[Chunk, float]]:
        vector = _normalize(np.array([query_embedding], dtype="float32"))
        scores, indices = self.index.search(vector, top_k)
        results: list[tuple[Chunk, float]] = []
        for idx, score in zip(indices[0], scores[0], strict=False):
            if idx == -1:
                continue
            results.append((self.chunks[idx], float(score)))
        return results
