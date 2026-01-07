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

    # --- Pass 1: Create all nodes (files and symbols) with empty children ---
    
    all_nodes: List[Node] = []
    path_index: Dict[str, str] = {}
    symbols_to_process: List[Dict[str, Any]] = []

    for rp in relpaths:
        p = root / rp
        try:
            if not p.is_file(): continue
            size = p.stat().st_size
            if size > max_file_bytes: continue
        except FileNotFoundError:
            continue

        file_id = make_id("path", rp)
        path_index[rp] = file_id
        
        meta = {"kind": _kind_from_path(rp), "bytes": int(size), "sha256": new_fp.get(rp)}
        all_nodes.append(Node(id=file_id, type="file", path=rp, children=[], meta=meta))

        if _kind_from_path(rp) == "py":
            try:
                py_symbols = list_python_symbols(p)
                for sym in py_symbols:
                    qualname = sym["qualname"]
                    symbol_id = make_id("symbol", rp, qualname)
                    
                    symbol_node = Node(
                        id=symbol_id,
                        type="block",
                        path=rp,
                        anchor=qualname,
                        children=[],
                        meta={
                            "kind": sym["kind"],
                            "start_line": sym["start_line"],
                            "end_line": sym["end_line"],
                        }
                    )
                    all_nodes.append(symbol_node)
                    # Store the symbol data along with its path for the linking pass
                    symbols_to_process.append({**sym, "path": rp})
            except Exception as e:
                print(f"Warning: Could not parse symbols in {rp}: {e}")

    # --- Pass 2: Create a map for easy lookup and link children ---

    node_map = {n.id: n for n in all_nodes}
    sym_id_map = {make_id("symbol", s["path"], s["qualname"]): s for s in symbols_to_process}

    # Link symbols to their parents
    for symbol_id, sym_data in sym_id_map.items():
        qualname = sym_data["qualname"]
        path = sym_data["path"]
        
        if "." in qualname:
            parent_qualname = qualname.rsplit(".", 1)[0]
            parent_id = make_id("symbol", path, parent_qualname)
            if parent_id in node_map:
                node_map[parent_id].children.append(symbol_id)
            else: # Fallback to file
                file_id = make_id("path", path)
                if file_id in node_map:
                    node_map[file_id].children.append(symbol_id)
        else: # Top-level symbol
            file_id = make_id("path", path)
            if file_id in node_map:
                node_map[file_id].children.append(symbol_id)

    # --- Pass 3: Create the final root node and serialize ---

    root_children_ids = [make_id("path", rp) for rp in relpaths]
    root_node = Node(id="root", type="project", path=".", summary="workspace root", children=root_children_ids)
    
    final_node_list = [root_node.to_dict()] + [n.to_dict() for n in all_nodes]

    write_nodes_jsonl(ap.nodes_path, final_node_list)
    write_json(ap.paths_index_path, path_index)
    write_json(ap.fingerprints_path, new_fp)

    return {
        "ok": True,
        "files_total": len(relpaths),
        "nodes_indexed": len(final_node_list),
        "diff": diff,
        "atlas_dir": str(ap.atlas_dir)
    }
