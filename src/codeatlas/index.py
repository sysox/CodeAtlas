from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from codeatlas.layout import AtlasPaths
from codeatlas.model import Node, make_id
from codeatlas.scan import scan_files
from codeatlas.fingerprint import build_fingerprints, diff_fingerprints
from codeatlas.state import load_json, write_json, write_nodes_jsonl


def build_or_update(root: Path) -> Dict[str, Any]:
    """MVP: file-level index. Writes nodes.jsonl + paths.json + fingerprints.json."""
    root = root.resolve()
    ap = AtlasPaths(root)
    ap.ensure_dirs()

    cfg = load_json(ap.cfg_path, default={})
    include = cfg.get("include", ["**/*"])
    exclude = cfg.get("exclude", [".git/**", ".atlas/**", ".venv/**"])
    max_file_bytes = int(cfg.get("max_file_bytes", 2_000_000))

    relpaths = scan_files(root, include=include, exclude=exclude)

    old_fp: Dict[str, str] = load_json(ap.fingerprints_path, default={})
    new_fp: Dict[str, str] = build_fingerprints(root, relpaths)
    diff = diff_fingerprints(old_fp, new_fp)

    nodes: List[Dict[str, Any]] = []
    path_index: Dict[str, str] = {}

    # root node
    root_id = "root"
    file_ids: List[str] = []

    for rp in relpaths:
        p = root / rp
        try:
            if p.is_file() and p.stat().st_size > max_file_bytes:
                # skip very large files in v1
                continue
        except FileNotFoundError:
            continue

        nid = make_id("path", rp)
        file_ids.append(nid)
        path_index[rp] = nid
        n = Node(id=nid, type="file", path=rp, summary=None, children=[])
        nodes.append(n.to_dict())

    nodes.insert(0, Node(id=root_id, type="project", path=".", summary="workspace root", children=file_ids).to_dict())

    write_nodes_jsonl(ap.nodes_path, nodes)
    write_json(ap.paths_index_path, path_index)
    write_json(ap.fingerprints_path, new_fp)

    return {
        "ok": True,
        "files_total": len(relpaths),
        "files_indexed": len(file_ids),
        "diff": diff,
        "atlas_dir": str(ap.atlas_dir)
    }
