from __future__ import annotations

import json
import subprocess
import shlex
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

def run_command(cmd: str, cwd: Path) -> Dict[str, Any]:
    """Runs a shell command and returns the result."""
    try:
        # Use shlex.split to handle quoted arguments correctly
        args = shlex.split(cmd)
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False # We don't want to raise an exception on non-zero exit code
        )
        return {
            "command": cmd,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {
            "command": cmd,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e)
        }

def apply_change_packet(root: Path, packet_path: Path) -> Dict[str, Any]:
    """
    Validates and applies a change packet to the workspace, using CST by default.
    Also executes 'run' commands and 'git' operations if present.
    """
    if not packet_path.exists():
        return {"ok": False, "error": f"Packet file not found: {packet_path}"}

    try:
        with open(packet_path, 'r', encoding='utf-8') as f:
            packet_data = json.load(f)
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"Invalid JSON in packet file: {e}"}

    # Handle both list (legacy) and dict (new format with 'ops', 'run', 'git')
    if isinstance(packet_data, list):
        ops = packet_data
        run_cmds = []
        git_ops = {}
    elif isinstance(packet_data, dict):
        ops = packet_data.get("ops", [])
        run_cmds = packet_data.get("run", [])
        git_ops = packet_data.get("git", {})
    else:
        return {"ok": False, "error": "Change packet must be a list or a dict with 'ops'."}

    # Group operations by file to implement in-memory caching
    ops_by_file = defaultdict(list)
    for i, op in enumerate(ops):
        op["op_index"] = i
        path_str = op.get("path")
        if path_str:
            ops_by_file[path_str].append(op)

    results = [None] * len(ops)
    
    # 1. Apply Code Changes
    for path_str, file_ops in ops_by_file.items():
        target_path = root / path_str
        
        # Handle file creation if it doesn't exist (for replace_file)
        # But for replace_symbol, it must exist.
        if not target_path.exists():
            # Check if any op is NOT replace_file
            if any(op.get("op") != "replace_file" for op in file_ops):
                 for op in file_ops:
                    if op.get("op") != "replace_file":
                        results[op["op_index"]] = {"ok": False, "op_index": op["op_index"], "error": f"File not found: {path_str}"}
                 # Continue to next file, but maybe process replace_file ops?
                 # Let's simplify: if file doesn't exist, we can only do replace_file (which creates it)
                 pass
        
        if target_path.exists():
            current_source = target_path.read_text(encoding="utf-8")
        else:
            current_source = ""
        
        # Apply all symbol replacements for this file in memory
        for op in file_ops:
            if op.get("op") == "replace_symbol":
                qualname = op.get("qualname")
                new_code = op.get("new_code")
                
                if not qualname or new_code is None:
                    results[op["op_index"]] = {"ok": False, "op_index": op["op_index"], "error": "replace_symbol missing 'qualname' or 'new_code'."}
                    continue

                if not target_path.exists():
                     # Already handled above, but double check
                     continue

                # Default to CST
                new_source, success = apply_with_cst(current_source, qualname, new_code)
                
                if success:
                    current_source = new_source
                    results[op["op_index"]] = {"ok": True, "op_index": op["op_index"], "path": path_str, "qualname": qualname, "status": "symbol_replaced_cst"}
                else:
                    results[op["op_index"]] = {"ok": False, "op_index": op["op_index"], "error": f"CST replacement failed for '{qualname}'."}
            
            elif op.get("op") == "replace_file":
                content = op.get("content")
                if content is None:
                    results[op["op_index"]] = {"ok": False, "op_index": op["op_index"], "error": "replace_file missing 'content'."}
                    continue
                current_source = content
                # Ensure parent dirs exist
                (root / path_str).parent.mkdir(parents=True, exist_ok=True)
                results[op["op_index"]] = {"ok": True, "op_index": op["op_index"], "path": path_str, "status": "file_replaced"}

        # Write the final modified source code once per file
        # Only write if we have successful operations or if it's a new file
        if any(r and r.get("ok") for r in results if r in [results[op["op_index"]] for op in file_ops]):
             target_path.write_text(current_source, encoding="utf-8")

    code_ok = all(r and r.get("ok", False) for r in results)
    
    # 2. Run Commands (only if code changes were successful)
    run_results = []
    if code_ok and run_cmds:
        for cmd in run_cmds:
            res = run_command(cmd, cwd=root)
            run_results.append(res)
            if res["exit_code"] != 0:
                # Stop on first failure? Or continue?
                # Usually stop is safer.
                return {"ok": False, "results": [r for r in results if r], "run_results": run_results, "error": f"Command failed: {cmd}"}

    # 3. Git Operations (only if run commands were successful)
    git_results = {}
    if code_ok and git_ops:
        # Git Add
        files_to_add = git_ops.get("add", [])
        if files_to_add:
            add_cmd = f"git add {' '.join(files_to_add)}"
            git_results["add"] = run_command(add_cmd, cwd=root)
        
        # Git Commit
        commit_msg = git_ops.get("commit")
        if commit_msg:
            # Use quotes for the message
            commit_cmd = f'git commit -m "{commit_msg}"'
            git_results["commit"] = run_command(commit_cmd, cwd=root)

    return {
        "ok": code_ok, 
        "results": [r for r in results if r], 
        "run_results": run_results,
        "git_results": git_results
    }
