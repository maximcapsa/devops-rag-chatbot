"""Build the FAISS vector store from the documents in ``data/``.

Run locally or in CI/CD before starting the app:

    python -m app.ingest
"""

from __future__ import annotations

import logging
import sys

from app.config import settings
from app.rag.chunking import load_chunks
from app.rag.embeddings import Embedder
from app.rag.vectorstore import VectorStore

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("ingest")


def main() -> int:
    logger.info("Loading documents from %s/", settings.data_dir)
    chunks = load_chunks(settings.data_dir, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        logger.error("No documents found in %s/. Add .md/.txt files first.", settings.data_dir)
        return 1
    logger.info(
        "Created %d chunks. Embedding with Voyage (%s)...", len(chunks), settings.voyage_model
    )

    embedder = Embedder()
    vectors = embedder.embed_documents([c.text for c in chunks])

    store = VectorStore.build(vectors, chunks)
    store.save(settings.vectorstore_dir)
    logger.info("Saved index to %s/ (%d vectors)", settings.vectorstore_dir, len(vectors))
    return 0


if __name__ == "__main__":
    sys.exit(main())
