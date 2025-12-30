from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from codeatlas.py_symbols import list_python_symbols


def extract_qualname_source(path: Path, qualname: str, *, context: int = 0) -> Dict[str, Any]:
    """Extract the exact source slice for a qualname using stored AST spans.

    Returns:
      { ok, path, qualname, start_line, end_line, text }
    """
    if not path.exists():
        return {"ok": False, "error": "file not found", "path": str(path), "qualname": qualname}

    syms = list_python_symbols(path)
    hit = next((s for s in syms if s.get("qualname") == qualname), None)
    if hit is None:
        return {
            "ok": False,
            "error": "qualname not found",
            "path": str(path),
            "qualname": qualname,
            "available": [s.get("qualname") for s in syms],
        }

    start = int(hit.get("start_line", 1))
    end = int(hit.get("end_line", start))

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines(True)  # keepends

    # convert to 0-based slices with optional context
    s0 = max(1, start - context)
    e0 = min(len(lines), end + context)

    snippet = "".join(lines[s0 - 1 : e0])

    return {
        "ok": True,
        "path": str(path),
        "qualname": qualname,
        "start_line": s0,
        "end_line": e0,
        "text": snippet,
    }
