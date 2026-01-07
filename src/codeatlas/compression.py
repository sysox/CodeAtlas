from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from codeatlas.layout import AtlasPaths
from codeatlas.state import load_nodes_jsonl
from codeatlas.py_extract import extract_qualname_source

def compress_node(node: Dict[str, Any], root: Optional[Path] = None, expand_content: bool = False) -> Dict[str, Any]:
    """
    Compresses a single node into the Generic Code Tree format.
    """
    out = {}
    
    # ID, Type, Children, Summary, Meta
    out["i"] = node.get("id")
    ntype = node.get("type")
    if ntype == "file": out["t"] = "f"
    elif ntype in ["directory", "project"]: out["t"] = "d"
    elif ntype == "block": out["t"] = "b"
    else: out["t"] = ntype[0] if ntype else "?"
    
    if node.get("children"): out["c"] = node["children"]
    if node.get("summary"): out["s"] = node["summary"]
    if node.get("meta"): out["m"] = node["meta"]

    # Default Content Data (Pointer)
    data = {"t": "ptr", "p": node.get("path")}
    if node.get("anchor"): data["a"] = node["anchor"]
        
    # Expansion Logic (Hybrid Model)
    if expand_content and root and node.get("path"):
        try:
            if ntype == "file":
                # For files, we still expand the whole file for now.
                # A future optimization could be to only expand relevant parts.
                content = (root / node["path"]).read_text(encoding="utf-8")
                data = {"t": "txt", "v": content}
            elif ntype == "block" and node.get("anchor"):
                # For blocks (symbols), we expand just that symbol's code.
                extract_res = extract_qualname_source(root / node["path"], node["anchor"])
                if extract_res.get("ok"):
                    data = {"t": "txt", "v": extract_res["text"]}
        except Exception:
            # Fallback to pointer if resolution fails
            pass

    out["d"] = data
        
    return out

def build_machine_core(root: Path, expand_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generates the compressed 'Machine Core' representation of the project.
    
    Args:
        root: Project root path.
        expand_ids: List of node IDs to expand from Pointers to Text (Inline).
    """
    root = root.resolve()
    ap = AtlasPaths(root)
    
    nodes = load_nodes_jsonl(ap.nodes_path)
    
    compressed_nodes = []
    for n in nodes:
        should_expand = expand_ids and n.get("id") in expand_ids
        compressed_nodes.append(compress_node(n, root=root, expand_content=should_expand))
    
    core = {
        "v": 2,
        "n": compressed_nodes
    }
    
    return core
