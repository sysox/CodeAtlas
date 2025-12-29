from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from codeatlas.layout import AtlasPaths
from codeatlas.resolve import lookup_path, resolve_node, resolve_content


def _cap_bytes(s: str, max_bytes: Optional[int]) -> Tuple[str, bool]:
    if max_bytes is None:
        return s, False
    b = s.encode("utf-8", errors="replace")
    if len(b) <= max_bytes:
        return s, False
    # truncate by bytes safely
    truncated = b[:max_bytes]
    # ensure valid utf-8
    out = truncated.decode("utf-8", errors="ignore")
    return out + "\n<!--TRUNCATED-->\n", True


def _slice_lines(s: str, head: Optional[int], tail: Optional[int]) -> Tuple[str, bool]:
    if head is None and tail is None:
        return s, False
    lines = s.splitlines(True)  # keep ends
    if head is not None and head < 0:
        head = None
    if tail is not None and tail < 0:
        tail = None

    if head is not None and tail is None:
        out = "".join(lines[:head])
        return out, len(lines) > head

    if tail is not None and head is None:
        out = "".join(lines[-tail:]) if tail != 0 else ""
        return out, len(lines) > tail

    # both
    assert head is not None and tail is not None
    if head + tail >= len(lines):
        return s, False
    out = "".join(lines[:head]) + "\n...\n" + "".join(lines[-tail:])
    return out, True


def build_ctx(
    root: Path,
    paths: List[str],
    ids: List[str],
    content: bool,
    head: Optional[int],
    tail: Optional[int],
    max_bytes: Optional[int],
) -> Dict[str, Any]:
    """Return a JSON-serializable context bundle for LLMs."""
    root = root.resolve()
    ap = AtlasPaths(root)

    selected: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    # resolve node ids from paths
    want_ids: List[str] = []
    for p in paths:
        nid = lookup_path(root, p)
        if nid is None:
            errors.append({"type": "path_not_found", "path": p})
        else:
            want_ids.append(nid)

    want_ids.extend(ids)

    # de-dup preserving order
    seen = set()
    dedup_ids: List[str] = []
    for nid in want_ids:
        if nid in seen:
            continue
        seen.add(nid)
        dedup_ids.append(nid)

    for nid in dedup_ids:
        node = resolve_node(root, nid)
        if node is None:
            errors.append({"type": "id_not_found", "id": nid})
            continue

        item: Dict[str, Any] = {"id": nid, "node": node}

        if content:
            try:
                raw = resolve_content(root, nid)
                sliced, sliced_flag = _slice_lines(raw, head=head, tail=tail)
                capped, capped_flag = _cap_bytes(sliced, max_bytes=max_bytes)
                item["content"] = {
                    "text": capped,
                    "sliced": bool(sliced_flag),
                    "truncated": bool(capped_flag)
                }
            except Exception as e:
                errors.append({"type": "content_error", "id": nid, "error": str(e)})

        selected.append(item)

    return {
        "ok": len(errors) == 0,
        "root": str(root),
        "atlas_dir": str(ap.atlas_dir),
        "request": {
            "paths": paths,
            "ids": ids,
            "content": content,
            "head": head,
            "tail": tail,
            "max_bytes": max_bytes
        },
        "items": selected,
        "errors": errors
    }
