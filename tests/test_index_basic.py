from pathlib import Path

from codeatlas.store_init import init_workspace
from codeatlas.index import build_or_update
from codeatlas.layout import AtlasPaths
from codeatlas.state import load_json


def test_index_creates_paths_index(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("# title\n", encoding="utf-8")

    init_workspace(tmp_path)
    stats = build_or_update(tmp_path)
    assert stats["ok"] is True

    ap = AtlasPaths(tmp_path)
    idx = load_json(ap.paths_index_path, default={})
    assert "a.txt" in idx
    assert "b.md" in idx
