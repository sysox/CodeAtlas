from pathlib import Path

from codeatlas.store_init import init_workspace
from codeatlas.index import build_or_update
from codeatlas.resolve import lookup_path, resolve_content


def test_resolve_returns_file_content(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello\n", encoding="utf-8")

    init_workspace(tmp_path)
    build_or_update(tmp_path)

    nid = lookup_path(tmp_path, "a.txt")
    assert nid is not None

    content = resolve_content(tmp_path, nid)
    assert content == "hello\n"
