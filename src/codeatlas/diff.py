from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from codeatlas.layout import AtlasPaths
from codeatlas.scan import scan_files
from codeatlas.fingerprint import build_fingerprints, diff_fingerprints
from codeatlas.state import load_json


def compute_diff(root: Path) -> Dict[str, Any]:
    root = root.resolve()
    ap = AtlasPaths(root)

    cfg = load_json(ap.cfg_path, default={})
    include = cfg.get("include", ["*"])
    exclude = cfg.get("exclude", [".git/**", ".atlas/**", ".venv/**"])

    relpaths = scan_files(root, include=include, exclude=exclude)

    old_fp: Dict[str, str] = load_json(ap.fingerprints_path, default={})
    new_fp: Dict[str, str] = build_fingerprints(root, relpaths)
    d = diff_fingerprints(old_fp, new_fp)

    return {
        "ok": True,
        "files_total": len(relpaths),
        "diff": d
    }
