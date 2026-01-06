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
      "d": {  // Data / Content
        "t": "ptr" | "txt" | "sum", // Type of content
        "p": "path",      // for ptr
        "a": "anchor",    // for ptr
        "v": "value"      // for txt or sum
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

    # Content Data ("d")
    # By default, we create a Pointer ("ptr")
    data = {
        "t": "ptr",
        "p": node.get("path")
    }
    
    anchor = node.get("anchor")
    if anchor:
        data["a"] = anchor
        
    # If we have a summary, we can include it as metadata or potentially as the primary content type
    # For now, let's keep summary as a separate field 's' for quick scanning, 
    # but the 'd' field represents the "body" of the node.
    summary = node.get("summary")
    if summary:
        out["s"] = summary

    # Expansion Logic (Hybrid Model)
    # If expand_content is True, we resolve the pointer and become "txt"
    if expand_content and root and node.get("path"):
        try:
            # This is a simplification. Real expansion needs to handle anchors (slicing).
            # For now, we only expand files or blocks if we can resolve them.
            # resolve_content currently only handles files.
            if ntype == "file":
                content = resolve_content(root, node["id"])
                data = {
                    "t": "txt",
                    "v": content
                }
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
