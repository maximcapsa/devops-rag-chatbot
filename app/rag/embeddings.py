"""Voyage AI embeddings client.

Embeddings are computed via Voyage's hosted API (generous free tier) so the
container stays small — no torch / sentence-transformers baked into the image.
"""

from __future__ import annotations

import voyageai

from app.config import settings


class Embedder:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.model = model or settings.voyage_model
        self._client = voyageai.Client(api_key=api_key or settings.voyage_api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of documents (input_type='document')."""
        out: list[list[float]] = []
        # Voyage caps batch size; chunk requests to be safe.
        for i in range(0, len(texts), 96):
            batch = texts[i : i + 96]
            resp = self._client.embed(batch, model=self.model, input_type="document")
            out.extend(resp.embeddings)
        return out

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query (input_type='query')."""
        resp = self._client.embed([text], model=self.model, input_type="query")
        return resp.embeddings[0]
