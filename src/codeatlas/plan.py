from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from codeatlas.ctx import build_ctx
from codeatlas.patch_skel import patch_skeleton
from codeatlas.py_symbols import list_python_symbols
from codeatlas.py_extract import extract_qualname_source


@dataclass(frozen=True)
class Target:
    path: str
    qualname: Optional[str] = None


def parse_target(s: str) -> Target:
    """Parse 'path' or 'path::qualname'."""
    if "::" in s:
        p, q = s.split("::", 1)
        p = p.strip()
        q = q.strip()
        return Target(path=p, qualname=(q or None))
    return Target(path=s.strip(), qualname=None)


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
    """Backward-compatible single-target plan."""
    return build_plan_multi(
        root=root,
        targets=[Target(path=path, qualname=qualname)],
        content=content,
        head=head,
        tail=tail,
        max_bytes=max_bytes,
        op=op,
        run=run,
        commit=commit,
    )


def build_plan_multi(
    *,
    root: Path,
    targets: List[Target],
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
      - ctx: minimal context bundle for all target paths
      - py_symbols_by_path: qualnames+spans for each .py path
      - symbol_snippets: exact source text for any target with qualname (token saver)
      - patches: BridgeAI packet skeleton per target
    """
    root = root.resolve()

    # de-dup paths preserving order
    seen = set()
    paths: List[str] = []
    for t in targets:
        if t.path not in seen:
            seen.add(t.path)
            paths.append(t.path)

    ctx = build_ctx(
        root=root,
        paths=paths,
        ids=[],
        content=content,
        head=head,
        tail=tail,
        max_bytes=max_bytes,
    )

    py_symbols_by_path: Dict[str, Any] = {}
    for p in paths:
        if p.lower().endswith(".py"):
            pp = root / p
            if pp.exists():
                py_symbols_by_path[p] = list_python_symbols(pp)

    symbol_snippets: List[Dict[str, Any]] = []
    for t in targets:
        if t.qualname and t.path.lower().endswith(".py"):
            pp = root / t.path
            res = extract_qualname_source(pp, t.qualname, context=0)
            # normalize path back to repo-relative for display
            if res.get("ok"):
                symbol_snippets.append(
                    {
                        "ok": True,
                        "path": t.path,
                        "qualname": t.qualname,
                        "start_line": res["start_line"],
                        "end_line": res["end_line"],
                        "text": res["text"],
                    }
                )
            else:
                symbol_snippets.append({"ok": False, "path": t.path, "qualname": t.qualname, "error": res.get("error")})

    patches: List[Dict[str, Any]] = []
    for t in targets:
        chosen_op = op
        if t.qualname is None and chosen_op == "replace_symbol":
            chosen_op = "replace_file"
        patches.append(
            patch_skeleton(
                path=t.path,
                qualname=t.qualname,
                op=chosen_op,
                run=run,
                commit=commit,
            )
        )

    ok = bool(ctx.get("ok"))
    return {
        "ok": ok,
        "root": str(root),
        "targets": [{"path": t.path, "qualname": t.qualname} for t in targets],
        "ctx": ctx,
        "py_symbols_by_path": py_symbols_by_path,
        "symbol_snippets": symbol_snippets,
        "patches": patches,
    }
