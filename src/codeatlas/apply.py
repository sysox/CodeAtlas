from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
import libcst as cst

class SymbolReplacer(cst.CSTTransformer):
    """
    A LibCST transformer to replace a specific function or class definition.
    """
    def __init__(self, qualname: str, new_code: str):
        self.qualname_parts = qualname.split('.')
        self.new_code_str = new_code
        self.current_qualname_stack: List[str] = []
        self.replacement_done = False

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        self.current_qualname_stack.append(node.name.value)
        return True  # Continue visiting children

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.CSTNode:
        self.current_qualname_stack.pop()
        return self._leave_definable_node(original_node, updated_node)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        self.current_qualname_stack.append(node.name.value)
        return True

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.CSTNode:
        self.current_qualname_stack.pop()
        return self._leave_definable_node(original_node, updated_node)

    def _leave_definable_node(self, original_node: cst.CSTNode, updated_node: cst.CSTNode) -> cst.CSTNode:
        """
        Checks if the current node matches the target qualname and replaces it.
        """
        current_qualname = ".".join(self.current_qualname_stack)
        target_qualname = ".".join(self.qualname_parts)

        if current_qualname == target_qualname:
            self.replacement_done = True
            # Parse the new code into a CST module and get the first body element
            new_module = cst.parse_module(self.new_code_str)
            if new_module.body:
                # Return the new node. LibCST will handle replacing it in the tree.
                return new_module.body[0]
        
        return updated_node

def apply_with_cst(source_code: str, qualname: str, new_code: str) -> Tuple[str, bool]:
    """
    Applies a symbol replacement using LibCST.
    Returns (new_source_code, was_successful).
    """
    try:
        source_tree = cst.parse_module(source_code)
        transformer = SymbolReplacer(qualname, new_code)
        modified_tree = source_tree.visit(transformer)
        
        if transformer.replacement_done:
            return modified_tree.code, True
        else:
            # This case means we parsed the file but didn't find the symbol
            return source_code, False
    except Exception:
        # Parsing failed
        return source_code, False

def apply_change_packet(root: Path, packet_path: Path) -> Dict[str, Any]:
    """
    Validates and applies a change packet to the workspace, using CST by default.
    """
    if not packet_path.exists():
        return {"ok": False, "error": f"Packet file not found: {packet_path}"}

    try:
        with open(packet_path, 'r', encoding='utf-8') as f:
            packet = json.load(f)
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"Invalid JSON in packet file: {e}"}

    if not isinstance(packet, list):
        return {"ok": False, "error": "Change packet must be a list of operations."}

    # Group operations by file to implement in-memory caching
    ops_by_file = defaultdict(list)
    for i, op in enumerate(packet):
        op["op_index"] = i
        path_str = op.get("path")
        if path_str:
            ops_by_file[path_str].append(op)

    results = [None] * len(packet)
    
    for path_str, ops in ops_by_file.items():
        target_path = root / path_str
        if not target_path.exists():
            for op in ops:
                results[op["op_index"]] = {"ok": False, "op_index": op["op_index"], "error": f"File not found: {path_str}"}
            continue

        current_source = target_path.read_text(encoding="utf-8")
        
        # Apply all symbol replacements for this file in memory
        for op in ops:
            if op.get("op") == "replace_symbol":
                qualname = op.get("qualname")
                new_code = op.get("new_code")
                
                if not qualname or new_code is None:
                    results[op["op_index"]] = {"ok": False, "op_index": op["op_index"], "error": "replace_symbol missing 'qualname' or 'new_code'."}
                    continue

                # Default to CST
                new_source, success = apply_with_cst(current_source, qualname, new_code)
                
                if success:
                    current_source = new_source
                    results[op["op_index"]] = {"ok": True, "op_index": op["op_index"], "path": path_str, "qualname": qualname, "status": "symbol_replaced_cst"}
                else:
                    # Fallback or error
                    # For now, we'll just report an error for simplicity. A real fallback would be more complex.
                    results[op["op_index"]] = {"ok": False, "op_index": op["op_index"], "error": f"CST replacement failed for '{qualname}'. The symbol might not exist or the file has syntax errors."}
            
            elif op.get("op") == "replace_file":
                # This op should ideally be the only one for a file if it exists
                content = op.get("content")
                if content is None:
                    results[op["op_index"]] = {"ok": False, "op_index": op["op_index"], "error": "replace_file missing 'content'."}
                    continue
                current_source = content
                results[op["op_index"]] = {"ok": True, "op_index": op["op_index"], "path": path_str, "status": "file_replaced"}

        # Write the final modified source code once per file
        target_path.write_text(current_source, encoding="utf-8")

    final_ok = all(r and r.get("ok", False) for r in results)
    return {"ok": final_ok, "results": [r for r in results if r]}
