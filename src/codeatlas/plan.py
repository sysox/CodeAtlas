from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from codeatlas.ctx import build_ctx
from codeatlas.patch_skel import patch_skeleton
from codeatlas.py_symbols import list_python_symbols


def build_plan(
    *,
    root: Path,
    path: str,
    qualname: Optional[str],
    content: bool,
    head: Optional[int],
    tail: Optional[int],
    max_bytes: Optional[int],
    op: str,
    run: Optional[List[str]],
    commit: Optional[str],
) -> Dict[str, Any]:
    """Build a single JSON bundle intended to be pasted to an LLM.

    Includes:
      - ctx: minimal context bundle (node+meta and optional truncated content)
      - py_symbols: Python qualnames+spans (if path endswith .py)
      - patch: BridgeAI packet skeleton
    """
    root = root.resolve()

    ctx = build_ctx(
        root=root,
        paths=[path],
        ids=[],
        content=content,
        head=head,
        tail=tail,
        max_bytes=max_bytes,
    )

    py_syms = None
    if path.lower().endswith(".py"):
        pth = (root / path)
        if pth.exists():
            py_syms = list_python_symbols(pth)

    patch = patch_skeleton(
        path=path,
        qualname=qualname,
        op=op,
        run=run,
        commit=commit,
    )

    ok = bool(ctx.get("ok"))
    return {
        "ok": ok,
        "root": str(root),
        "path": path,
        "qualname": qualname,
        "ctx": ctx,
        "py_symbols": py_syms,
        "patch": patch,
    }
