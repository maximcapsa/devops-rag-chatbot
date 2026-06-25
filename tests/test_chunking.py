from app.rag.chunking import load_chunks, split_text


def test_split_text_respects_size_and_overlap():
    text = "para one.\n\n" + ("word " * 400)
    chunks = split_text(text, chunk_size=200, overlap=40)
    assert len(chunks) > 1
    assert all(len(c) <= 240 for c in chunks)  # size + slack for boundary search


def test_split_text_empty():
    assert split_text("   ", chunk_size=100, overlap=10) == []


def test_load_chunks_reads_data_dir(tmp_path):
    (tmp_path / "a.md").write_text("# Title\n\n" + ("alpha " * 100), encoding="utf-8")
    (tmp_path / "b.txt").write_text("beta " * 100, encoding="utf-8")
    chunks = load_chunks(tmp_path, chunk_size=150, overlap=20)
    assert chunks
    sources = {c.source for c in chunks}
    assert sources == {"a.md", "b.txt"}
