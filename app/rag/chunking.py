"""Simple, dependency-free text chunking for Markdown source docs."""

from __future__ import annotations

from pathlib import Path

from app.rag.vectorstore import Chunk


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Character-based sliding window with overlap, preferring paragraph breaks."""
    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        # Try to break on a paragraph/sentence boundary near the window end.
        if end < n:
            window = text[start:end]
            for sep in ("\n\n", "\n", ". "):
                pos = window.rfind(sep)
                if pos > chunk_size * 0.5:
                    end = start + pos + len(sep)
                    break
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks


def load_chunks(data_dir: str | Path, chunk_size: int, overlap: int) -> list[Chunk]:
    """Read every .md/.txt file under ``data_dir`` and split into chunks."""
    data_dir = Path(data_dir)
    files = sorted([*data_dir.rglob("*.md"), *data_dir.rglob("*.txt")])
    chunks: list[Chunk] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for piece in split_text(text, chunk_size, overlap):
            chunks.append(Chunk(text=piece, source=path.name))
    return chunks
