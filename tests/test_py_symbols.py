from pathlib import Path

from codeatlas.py_symbols import list_python_symbols


def test_py_symbols_basic(tmp_path: Path):
    p = tmp_path / "m.py"
    p.write_text(
        """
class A:
    def m(self):
        pass

def f():
    return 1
""".lstrip(),
        encoding="utf-8"
    )
    syms = list_python_symbols(p)
    qns = [s["qualname"] for s in syms]
    assert "A" in qns
    assert "A.m" in qns
    assert "f" in qns
