from __future__ import annotations

from typing import Any, Dict, List, Optional


def patch_skeleton(
    *,
    path: str,
    qualname: Optional[str] = None,
    op: str = "replace_symbol",
    run: Optional[List[str]] = None,
    commit: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a BridgeAI packet skeleton.

    - If qualname is provided, op defaults to replace_symbol.
    - If qualname is None, op defaults to replace_file.
    """
    if qualname is None and op == "replace_symbol":
        op = "replace_file"

    ops: List[Dict[str, Any]] = []
    if op == "replace_symbol":
        ops.append({
            "op": "replace_symbol",
            "path": path,
            "qualname": qualname,
            "new_code": "<PASTE_NEW_CODE_HERE>\n"
        })
    elif op == "replace_file":
        ops.append({
            "op": "replace_file",
            "path": path,
            "content": "<PASTE_FULL_FILE_CONTENT_HERE>\n"
        })
    else:
        raise ValueError(f"unsupported skeleton op: {op}")

    pkt: Dict[str, Any] = {
        "v": 1,
        "goal": "<DESCRIBE_CHANGE>",
        "ops": ops,
        "run": run if run is not None else ["pytest -q"],
        "git": {
            "add": [path] if op != "replace_file" else ["."],
            "commit": commit if commit is not None else "<COMMIT_MESSAGE>"
        }
    }
    return pkt
