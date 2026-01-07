from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from codeatlas.py_extract import extract_qualname_source

def build_proposal_packet(bundle_path: Path, packet_path: Path) -> Dict[str, Any]:
    """
    Creates a self-contained, causal proposal packet for review.
    """
    if not bundle_path.exists():
        return {"ok": False, "error": f"Bundle file not found: {bundle_path}"}
    if not packet_path.exists():
        return {"ok": False, "error": f"Change packet file not found: {packet_path}"}

    try:
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"Invalid JSON in input files: {e}"}

    goal = bundle.get("goal")
    original_targets = bundle.get("targets", [])
    root_path = Path(bundle.get("root", "."))

    primary_changes = []
    dependent_changes = []

    # Helper to get original code
    def get_before_code(path_str: str, qualname: Optional[str] = None) -> str:
        full_path = root_path / path_str
        if not full_path.exists():
            return "[Original source file not found]"
        
        if qualname:
            data = extract_qualname_source(full_path, qualname)
            return data.get("text", "[Original symbol code not found]")
        else:
            return full_path.read_text(encoding="utf-8")

    # Identify primary vs. dependent changes
    for op in packet:
        path = op.get("path")
        qualname = op.get("qualname")
        is_primary = False
        for target in original_targets:
            if target.get("path") == path and target.get("qualname") == qualname:
                is_primary = True
                break
        
        change_detail = {
            "path": path,
            "qualname": qualname,
            "before_code": get_before_code(path, qualname),
            "after_code": op.get("new_code") if qualname else op.get("content")
        }
        
        if is_primary:
            primary_changes.append(change_detail)
        else:
            # Add a reason for the dependent change
            change_detail["reason"] = f"Updates call site or dependency related to primary target."
            dependent_changes.append(change_detail)

    # If no primary changes were matched, treat all as primary (fallback)
    if not primary_changes and dependent_changes:
        primary_changes = dependent_changes
        dependent_changes = []

    return {
        "ok": True,
        "goal": goal,
        "primary_changes": primary_changes,
        "dependent_changes": dependent_changes
    }
