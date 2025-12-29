from pathlib import Path

from codeatlas.store_init import init_workspace
from codeatlas.index import build_or_update
from codeatlas.ctx import build_ctx


def test_ctx_returns_items_and_content(tmp_path: Path):
    (tmp_path / "a.txt").write_text("line1\nline2\nline3\n", encoding="utf-8")
    init_workspace(tmp_path)
    build_or_update(tmp_path)

    out = build_ctx(tmp_path, paths=["a.txt"], ids=[], content=True, head=2, tail=None, max_bytes=None)
    assert out["items"]
    item = out["items"][0]
    assert item["node"]["path"] == "a.txt"
    assert "content" in item
    assert "line1" in item["content"]["text"]
    assert "line3" not in item["content"]["text"]


def test_ctx_max_bytes_truncates(tmp_path: Path):
    (tmp_path / "a.txt").write_text("x" * 1000, encoding="utf-8")
    init_workspace(tmp_path)
    build_or_update(tmp_path)

    out = build_ctx(tmp_path, paths=["a.txt"], ids=[], content=True, head=None, tail=None, max_bytes=50)
    item = out["items"][0]
    assert item["content"]["truncated"] is True
