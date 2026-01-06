from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

def find_node_in_core(core: Dict[str, Any], path: str, qualname: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Finds a specific node in a Machine Core by path and optional qualname."""
    nodes = core.get("n", [])
    for node in nodes:
        node_data = node.get("d", {})
        if node_data.get("p") == path:
            if qualname:
                if node.get("t") == "b" and node_data.get("a") == qualname:
                    return node
            elif node.get("t") == "f": # If no qualname, we are looking for the file node
                return node
    return None

def build_proposal_packet(bundle_path: Path, packet_path: Path) -> Dict[str, Any]:
    """
    Creates a self-contained proposal packet for review.
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

    proposals = []
    machine_core = bundle.get("machine_core")
    goal = bundle.get("goal")

    if not machine_core:
        return {"ok": False, "error": "Machine Core not found in bundle."}

    for op in packet:
        op_type = op.get("op")
        path = op.get("path")
        qualname = op.get("qualname")
        
        if op_type == "replace_symbol":
            # Find the "before" state from the bundle's Machine Core
            original_node = find_node_in_core(machine_core, path, qualname)
            if not original_node:
                # This could happen if the core in the bundle wasn't expanded for this symbol.
                # For now, we'll mark it as an error. A future improvement could be to
                # re-run the extraction logic here.
                proposals.append({
                    "path": path,
                    "qualname": qualname,
                    "error": "Could not find original state in the provided bundle."
                })
                continue

            # The content of a symbol is its children's content, or its own if it's a leaf.
            # This is complex. A simpler way is to re-use py_extract.
            # Let's assume for now the bundle has the original text.
            # The expanded file node should have it.
            file_node = find_node_in_core(machine_core, path)
            if file_node and file_node.get("d", {}).get("t") == "txt":
                from codeatlas.py_extract import extract_qualname_source
                # We need the root path to do this. It's in the bundle.
                root_path = Path(bundle.get("root", "."))
                full_path = root_path / path
                
                # We can't just use the text in the node, as it's the whole file.
                # We need to re-extract the specific symbol text.
                # This highlights a dependency: we need the original source on disk.
                if full_path.exists():
                    before_data = extract_qualname_source(full_path, qualname)
                    before_text = before_data.get("text", "[Original code not found]")
                else:
                    before_text = "[Original source file not found]"
            else:
                before_text = "[Original file content not found in bundle]"

            proposals.append({
                "path": path,
                "qualname": qualname,
                "before_code": before_text,
                "after_code": op.get("new_code")
            })
            
        elif op_type == "replace_file":
            file_node = find_node_in_core(machine_core, path)
            before_text = "[File content not expanded in bundle]"
            if file_node and file_node.get("d", {}).get("t") == "txt":
                before_text = file_node["d"].get("v", "")
                
            proposals.append({
                "path": path,
                "before_code": before_text,
                "after_code": op.get("content")
            })

    return {
        "ok": True,
        "goal": goal,
        "proposals": proposals
    }
