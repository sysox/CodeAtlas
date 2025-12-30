from pathlib import Path

from codeatlas.py_extract import extract_qualname_source


def test_extract_qualname_source(tmp_path: Path):
    p = tmp_path / "m.py"
    p.write_text(
        """
class A:
    def m(self):
        return 1

def f(x):
    return x + 1
""".lstrip(),
        encoding="utf-8",
    )

    out = extract_qualname_source(p, "f")
    assert out["ok"] is True
    assert "def f" in out["text"]

    out2 = extract_qualname_source(p, "A.m")
    assert out2["ok"] is True
    assert "def m" in out2["text"]
