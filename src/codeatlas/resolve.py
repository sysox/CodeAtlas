from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Any

from codeatlas.layout import AtlasPaths
from codeatlas.state import load_json, load_nodes_map


def lookup_path(root: Path, relpath: str) -> Optional[str]:
    ap = AtlasPaths(root.resolve())
    idx = load_json(ap.paths_index_path, default={})
    return idx.get(relpath)


def resolve_node(root: Path, node_id: str) -> Optional[Dict[str, Any]]:
    ap = AtlasPaths(root.resolve())
    nodes = load_nodes_map(ap.nodes_path)
    return nodes.get(node_id)


def resolve_content(root: Path, node_id: str) -> str:
    """v1: node_id for files is ref:path:<relpath> → return whole file text."""
    root = root.resolve()
    prefix = "ref:path:"
    if not node_id.startswith(prefix):
        raise ValueError(f"unsupported node id for v1 resolve_content: {node_id}")
    relpath = node_id[len(prefix):]
    p = root / relpath
    return p.read_text(encoding="utf-8", errors="replace")
