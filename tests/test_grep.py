from pathlib import Path

from codeatlas.grep import grep_snippets


def test_grep_snippets_basic(tmp_path: Path):
    (tmp_path / "a.txt").write_text("one\nhello\ntwo\n", encoding="utf-8")
    out = grep_snippets(root=tmp_path, path="a.txt", pattern="hello", context=1, max_matches=10)
    assert out["ok"] is True
    assert out["matches"]
    m = out["matches"][0]
    assert m["match_line"] == 2
    assert "hello" in m["snippet"]


def test_grep_invalid_regex(tmp_path: Path):
    (tmp_path / "a.txt").write_text("x\n", encoding="utf-8")
    out = grep_snippets(root=tmp_path, path="a.txt", pattern="(")
    assert out["ok"] is False
