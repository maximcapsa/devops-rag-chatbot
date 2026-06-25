from app.rag.pipeline import RagPipeline
from app.rag.vectorstore import Chunk, VectorStore


class FakeEmbedder:
    def embed_query(self, text: str):
        return [1.0, 0.0]


class FakeLLM:
    def answer(self, question: str, context: str) -> str:
        assert "docker" in context.lower()
        return "Use `docker build`."


def _store():
    chunks = [
        Chunk(text="docker build creates an image", source="docker.md"),
        Chunk(text="git tracks versions", source="git.md"),
    ]
    return VectorStore.build([[1.0, 0.0], [0.0, 1.0]], chunks)


def test_pipeline_returns_answer_and_sources():
    pipe = RagPipeline(_store(), embedder=FakeEmbedder(), llm=FakeLLM())
    result = pipe.query("How do I build a docker image?", top_k=1)
    assert result.answer == "Use `docker build`."
    assert result.sources[0].source == "docker.md"
    assert 0.0 <= result.sources[0].score <= 1.0
