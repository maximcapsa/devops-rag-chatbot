"""RAG orchestration: retrieve relevant chunks, then ask the LLM."""

from __future__ import annotations

from dataclasses import dataclass

from app.config import settings
from app.rag.embeddings import Embedder
from app.rag.llm import LLM
from app.rag.vectorstore import VectorStore


@dataclass
class Source:
    source: str
    score: float
    snippet: str


@dataclass
class RagResult:
    answer: str
    sources: list[Source]


def build_context(results: list[tuple]) -> str:
    blocks = []
    for i, (chunk, _score) in enumerate(results, start=1):
        blocks.append(f"[{i}] (from {chunk.source})\n{chunk.text}")
    return "\n\n".join(blocks)


class RagPipeline:
    def __init__(
        self,
        store: VectorStore,
        embedder: Embedder | None = None,
        llm: LLM | None = None,
    ) -> None:
        self.store = store
        self.embedder = embedder or Embedder()
        self.llm = llm or LLM()

    @classmethod
    def from_disk(cls) -> RagPipeline:
        store = VectorStore.load(settings.vectorstore_dir)
        return cls(store)

    def query(self, question: str, top_k: int | None = None) -> RagResult:
        k = top_k or settings.top_k
        query_vec = self.embedder.embed_query(question)
        results = self.store.search(query_vec, top_k=k)
        if not results:
            return RagResult(
                answer="I don't have enough information in my knowledge base to answer that.",
                sources=[],
            )
        context = build_context(results)
        answer = self.llm.answer(question, context)
        sources = [
            Source(source=c.source, score=round(s, 3), snippet=c.text[:200].strip())
            for c, s in results
        ]
        return RagResult(answer=answer, sources=sources)
