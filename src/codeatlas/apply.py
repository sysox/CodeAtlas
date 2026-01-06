from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

def apply_change_packet(root: Path, packet_path: Path) -> Dict[str, Any]:
    """
    Validates and applies a change packet to the workspace.
    """
    if not packet_path.exists():
        return {"ok": False, "error": f"Packet file not found: {packet_path}"}

    try:
        with open(packet_path, 'r', encoding='utf-8') as f:
            packet = json.load(f)
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"Invalid JSON in packet file: {e}"}

    # Basic validation
    if not isinstance(packet, list):
        return {"ok": False, "error": "Change packet must be a list of operations."}

    results = []
    for i, op in enumerate(packet):
        op_type = op.get("op")
        path_str = op.get("path")

        if not op_type or not path_str:
            results.append({"ok": False, "op_index": i, "error": "Operation missing 'op' or 'path' field."})
            continue

        target_path = root / path_str
        
        try:
            if op_type == "replace_file":
                content = op.get("content")
                if content is None:
                    results.append({"ok": False, "op_index": i, "error": "replace_file operation missing 'content' field."})
                    continue
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(content, encoding="utf-8")
                results.append({"ok": True, "op_index": i, "path": path_str, "status": "replaced"})

            elif op_type == "replace_symbol":
                # In this phase, we will treat replace_symbol as a placeholder.
                # A full implementation requires AST parsing to replace a specific symbol,
                # which is a good candidate for a future enhancement.
                # For now, we can simulate it or just acknowledge it.
                new_code = op.get("new_code")
                qualname = op.get("qualname")
                if new_code is None or qualname is None:
                    results.append({"ok": False, "op_index": i, "error": "replace_symbol operation missing 'new_code' or 'qualname' field."})
                    continue
                
                # Placeholder: We'll just note that this operation is recognized.
                # A real implementation would go here.
                results.append({"ok": True, "op_index": i, "path": path_str, "qualname": qualname, "status": "recognized (not applied - placeholder)"})

            else:
                results.append({"ok": False, "op_index": i, "error": f"Unsupported operation type: {op_type}"})

        except Exception as e:
            results.append({"ok": False, "op_index": i, "error": str(e)})

    final_ok = all(r.get("ok", False) for r in results)
    return {"ok": final_ok, "results": results}
