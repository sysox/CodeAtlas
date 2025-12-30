from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def grep_snippets(
    *,
    root: Path,
    path: str,
    pattern: str,
    context: int = 2,
    max_matches: int = 20,
) -> Dict[str, Any]:
    root = root.resolve()
    p = (root / path)
    if not p.exists():
        return {"ok": False, "error": "file not found", "path": path}

    text = p.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines(True)  # keepends

    try:
        rx = re.compile(pattern)
    except re.error as e:
        return {"ok": False, "error": f"invalid regex: {e}", "pattern": pattern}

    hits: List[Dict[str, Any]] = []
    for i, ln in enumerate(lines):
        if rx.search(ln):
            start = max(0, i - context)
            end = min(len(lines), i + context + 1)
            snippet = "".join(lines[start:end])
            hits.append({
                "match_line": i + 1,
                "range": {"start_line": start + 1, "end_line": end},
                "snippet": snippet,
            })
            if len(hits) >= max_matches:
                break

    return {
        "ok": True,
        "path": path,
        "pattern": pattern,
        "context": context,
        "max_matches": max_matches,
        "matches": hits,
        "truncated": len(hits) >= max_matches,
    }
