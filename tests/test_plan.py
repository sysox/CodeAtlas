from pathlib import Path

from codeatlas.store_init import init_workspace
from codeatlas.index import build_or_update
from codeatlas.plan import build_plan


def test_plan_includes_ctx_symbols_and_patch(tmp_path: Path):
    (tmp_path / "m.py").write_text(
        """
class A:
    def m(self):
        return 1

def f(x):
    return x + 1
""".lstrip(),
        encoding="utf-8"
    )

    init_workspace(tmp_path)
    build_or_update(tmp_path)

    out = build_plan(
        root=tmp_path,
        path="m.py",
        qualname="f",
        content=True,
        head=20,
        tail=None,
        max_bytes=2000,
        op="replace_symbol",
        run=["pytest -q"],
        commit="test"
    )

    assert out["ok"] is True
    assert out["ctx"]["items"][0]["node"]["path"] == "m.py"
    assert out["py_symbols"] is not None
    qns = [s["qualname"] for s in out["py_symbols"]]
    assert "A" in qns and "A.m" in qns and "f" in qns
    assert out["patch"]["ops"][0]["op"] == "replace_symbol"
    assert out["patch"]["ops"][0]["qualname"] == "f"
