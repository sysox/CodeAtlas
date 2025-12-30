from pathlib import Path

from codeatlas.store_init import init_workspace
from codeatlas.index import build_or_update
from codeatlas.plan import build_plan_multi, Target


def test_plan_multi_two_targets(tmp_path: Path):
    (tmp_path / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# hi\n", encoding="utf-8")

    init_workspace(tmp_path)
    build_or_update(tmp_path)

    out = build_plan_multi(
        root=tmp_path,
        targets=[Target("a.py", "f"), Target("README.md", None)],
        content=True,
        head=50,
        tail=None,
        max_bytes=5000,
        op="replace_symbol",
        run=["pytest -q"],
        commit="x"
    )

    assert out["ok"] is True
    paths = [it["node"]["path"] for it in out["ctx"]["items"]]
    assert "a.py" in paths and "README.md" in paths
    assert "a.py" in out["py_symbols_by_path"]
    assert len(out["patches"]) == 2
    assert out["patches"][0]["ops"][0]["op"] == "replace_symbol"
    assert out["patches"][1]["ops"][0]["op"] == "replace_file"
