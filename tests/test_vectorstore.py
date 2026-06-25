from app.rag.vectorstore import Chunk, VectorStore


def test_build_save_load_and_search(tmp_path):
    chunks = [
        Chunk(text="docker builds images", source="docker.md"),
        Chunk(text="terraform manages infrastructure", source="terraform.md"),
        Chunk(text="kubernetes orchestrates containers", source="kubernetes.md"),
    ]
    # Simple 3-dim one-hot embeddings so similarity is deterministic.
    embeddings = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

    store = VectorStore.build(embeddings, chunks)
    store.save(tmp_path)

    loaded = VectorStore.load(tmp_path)
    results = loaded.search([0.0, 0.9, 0.1], top_k=2)
    assert results[0][0].source == "terraform.md"
    assert results[0][1] > results[1][1]  # scores sorted descending
