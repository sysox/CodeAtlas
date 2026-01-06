from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from codeatlas.layout import AtlasPaths
from codeatlas.model import Node, make_id
from codeatlas.scan import scan_files
from codeatlas.fingerprint import build_fingerprints, diff_fingerprints
from codeatlas.state import load_json, write_json, write_nodes_jsonl
from codeatlas.py_symbols import list_python_symbols


def _kind_from_path(relpath: str) -> str:
    rp = relpath.lower()
    if rp.endswith(".py"):
        return "py"
    if rp.endswith(".md"):
        return "md"
    if rp.endswith(".tex"):
        return "tex"
    if rp.endswith(".json"):
        return "json"
    if rp.endswith(".yaml") or rp.endswith(".yml"):
        return "yaml"
    if rp.endswith(".toml"):
        return "toml"
    if rp.endswith(".txt"):
        return "txt"
    return "other"


def build_or_update(root: Path) -> Dict[str, Any]:
    """
    Performs a deep index of the workspace, creating nodes for files and symbols.
    Writes nodes.jsonl, paths.json, and fingerprints.json.
    """
    root = root.resolve()
    ap = AtlasPaths(root)
    ap.ensure_dirs()

    cfg = load_json(ap.cfg_path, default={})
    include = cfg.get("include", ["*"])
    exclude = cfg.get("exclude", [".git/**", ".atlas/**", ".venv/**"])
    max_file_bytes = int(cfg.get("max_file_bytes", 2_000_000))

    relpaths = scan_files(root, include=include, exclude=exclude)

    old_fp: Dict[str, str] = load_json(ap.fingerprints_path, default={})
    new_fp: Dict[str, str] = build_fingerprints(root, relpaths)
    diff = diff_fingerprints(old_fp, new_fp)

    all_nodes: List[Dict[str, Any]] = []
    path_index: Dict[str, str] = {}

    # root node
    root_id = "root"
    root_children_ids: List[str] = []

    for rp in relpaths:
        p = root / rp
        try:
            if not p.is_file():
                continue
            size = p.stat().st_size
            if size > max_file_bytes:
                continue
        except FileNotFoundError:
            continue

        file_id = make_id("path", rp)
        root_children_ids.append(file_id)
        path_index[rp] = file_id
        
        file_children_ids = []
        
        # If it's a Python file, perform deep symbol indexing
        if _kind_from_path(rp) == "py":
            try:
                symbols = list_python_symbols(p)
                
                # Map qualname -> symbol_id for parent lookup
                sym_id_map = {}
                
                # First pass: Create IDs and Nodes for all symbols
                for sym in symbols:
                    qualname = sym["qualname"]
                    symbol_id = make_id("symbol", rp, qualname)
                    sym_id_map[qualname] = symbol_id
                    
                    symbol_node = Node(
                        id=symbol_id,
                        type="block",
                        path=rp,
                        anchor=qualname,
                        summary=None,
                        children=[], # Will fill in second pass
                        meta={
                            "kind": sym["kind"],
                            "start_line": sym["start_line"],
                            "end_line": sym["end_line"],
                        }
                    )
                    all_nodes.append(symbol_node.to_dict())

                # Second pass: Link children to parents
                # We need to find the node objects we just created to update their children list.
                # Since all_nodes is a list of dicts, let's make a temporary map for easy access.
                node_map = {n["id"]: n for n in all_nodes if n["path"] == rp and n["type"] == "block"}

                for sym in symbols:
                    qualname = sym["qualname"]
                    current_id = sym_id_map[qualname]
                    
                    if "." in qualname:
                        # It's a nested symbol (e.g., Class.method)
                        parent_qualname = qualname.rsplit(".", 1)[0]
                        parent_id = sym_id_map.get(parent_qualname)
                        
                        if parent_id and parent_id in node_map:
                            # Add to parent symbol's children
                            node_map[parent_id]["children"].append(current_id)
                        else:
                            # Parent not found (shouldn't happen if symbols are complete), fallback to file
                            file_children_ids.append(current_id)
                    else:
                        # It's a top-level symbol, add to file's children
                        file_children_ids.append(current_id)

            except Exception:
                # Ignore files that fail to parse
                pass

        meta = {
            "kind": _kind_from_path(rp),
            "bytes": int(size),
            "sha256": new_fp.get(rp)
        }

        file_node = Node(id=file_id, type="file", path=rp, summary=None, children=file_children_ids, meta=meta)
        all_nodes.append(file_node.to_dict())

    # Add the project root node at the beginning
    root_node = Node(id=root_id, type="project", path=".", summary="workspace root", children=root_children_ids)
    all_nodes.insert(0, root_node.to_dict())

    write_nodes_jsonl(ap.nodes_path, all_nodes)
    write_json(ap.paths_index_path, path_index)
    write_json(ap.fingerprints_path, new_fp)

    return {
        "ok": True,
        "files_total": len(relpaths),
        "nodes_indexed": len(all_nodes),
        "diff": diff,
        "atlas_dir": str(ap.atlas_dir)
    }
