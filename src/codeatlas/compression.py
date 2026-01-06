from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from codeatlas.layout import AtlasPaths
from codeatlas.state import load_nodes_jsonl
from codeatlas.resolve import resolve_content

def compress_node(node: Dict[str, Any], root: Optional[Path] = None, expand_content: bool = False) -> Dict[str, Any]:
    """
    Compresses a single node into the Generic Code Tree format.
    
    Output Format:
    {
      "i": "id",
      "t": "type" (f=file, d=dir, b=block),
      "c": ["child_id", ...],
      "s": "summary",
      "m": { ...metadata... },
      "d": {  // Data / Content
        "t": "ptr" | "txt", // Type of content
        "p": "path",      // for ptr
        "a": "anchor",    // for ptr
        "v": "value"      // for txt
      }
    }
    """
    out = {}
    
    # ID
    out["i"] = node.get("id")
    
    # Type mapping
    ntype = node.get("type")
    if ntype == "file":
        out["t"] = "f"
    elif ntype == "directory" or ntype == "project":
        out["t"] = "d"
    elif ntype == "block":
        out["t"] = "b"
    else:
        out["t"] = ntype[0] if ntype else "?"

    # Children
    children = node.get("children")
    if children:
        out["c"] = children

    # Summary
    summary = node.get("summary")
    if summary:
        out["s"] = summary

    # Metadata (for blocks)
    meta = node.get("meta")
    if meta:
        out["m"] = meta

    # Content Data ("d")
    data = {
        "t": "ptr",
        "p": node.get("path")
    }
    
    anchor = node.get("anchor")
    if anchor:
        data["a"] = anchor
        
    # Expansion Logic (Hybrid Model)
    if expand_content and root and node.get("path"):
        try:
            # We need a more robust resolve_content that can handle anchors for blocks
            # For now, we assume resolve_content can handle file IDs and we expand the whole file
            if ntype == "file":
                content = resolve_content(root, node["id"])
                data = {
                    "t": "txt",
                    "v": content
                }
        except Exception:
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
    
    # Load raw nodes
    nodes = load_nodes_jsonl(ap.nodes_path)
    
    # Compress each node
    compressed_nodes = []
    for n in nodes:
        should_expand = expand_ids and n.get("id") in expand_ids
        compressed_nodes.append(compress_node(n, root=root, expand_content=should_expand))
    
    # Create the core object
    core = {
        "v": 2, # Version 2 for Generic C model
        "n": compressed_nodes
    }
    
    return core

if __name__ == "__main__":
    import sys
    root_path = Path(".")
    if len(sys.argv) > 1:
        root_path = Path(sys.argv[1])
    
    core = build_machine_core(root_path)
    print(json.dumps(core, indent=None, separators=(',', ':')))
