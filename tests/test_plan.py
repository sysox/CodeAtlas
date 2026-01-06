from pathlib import Path

from codeatlas.store_init import init_workspace
from codeatlas.index import build_or_update
from codeatlas.plan import build_plan


def test_plan_includes_machine_core_and_patch(tmp_path: Path):
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
        goal="test goal",
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
    
    # Assert new structure
    assert "machine_core" in out
    assert "patches" in out
    
    # Assert old, redundant keys are gone
    assert "ctx" not in out
    assert "py_symbols_by_path" not in out
    assert "symbol_snippets" not in out

    # Check that the machine core has expanded content
    core = out["machine_core"]
    nodes = core.get("n", [])
    file_node = next((n for n in nodes if n.get("d", {}).get("p") == "m.py"), None)
    assert file_node is not None
    assert file_node["d"]["t"] == "txt" # Should be expanded
    assert "class A" in file_node["d"]["v"]

    # Check patch skeleton
    assert out["patches"][0]["ops"][0]["op"] == "replace_symbol"
    assert out["patches"][0]["ops"][0]["qualname"] == "f"
