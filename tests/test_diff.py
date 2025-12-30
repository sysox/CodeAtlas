from pathlib import Path

from codeatlas.store_init import init_workspace
from codeatlas.index import build_or_update
from codeatlas.diff import compute_diff


def test_diff_added_changed_deleted(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello\n", encoding="utf-8")

    init_workspace(tmp_path)
    build_or_update(tmp_path)

    # no changes
    d = compute_diff(tmp_path)
    assert d["diff"]["added"] == []
    assert d["diff"]["deleted"] == []
    assert d["diff"]["changed"] == []

    # change file
    (tmp_path / "a.txt").write_text("hello2\n", encoding="utf-8")
    d = compute_diff(tmp_path)
    assert "a.txt" in d["diff"]["changed"]

    # add file
    (tmp_path / "b.txt").write_text("x\n", encoding="utf-8")
    d = compute_diff(tmp_path)
    assert "b.txt" in d["diff"]["added"]

    # delete file
    (tmp_path / "a.txt").unlink()
    d = compute_diff(tmp_path)
    assert "a.txt" in d["diff"]["deleted"]
