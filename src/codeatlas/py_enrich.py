from __future__ import annotations

import ast
from typing import Any, Dict, List, Optional, Set, Tuple

def get_annotation(node: ast.AST) -> str:
    """Recursively stringifies a type annotation node."""
    if node is None:
        return "Any"
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{get_annotation(node.value)}.{node.attr}"
    if isinstance(node, ast.Subscript):
        value = get_annotation(node.value)
        slice_val = get_annotation(node.slice)
        return f"{value}[{slice_val}]"
    if isinstance(node, ast.Constant):
        return repr(node.value)
    if isinstance(node, ast.Tuple):
        return f"({', '.join(get_annotation(e) for e in node.elts)})"
    if isinstance(node, ast.List):
        return f"[{', '.join(get_annotation(e) for e in node.elts)}]"
    # Fallback for complex types
    try:
        return ast.unparse(node)
    except AttributeError:
        return "ComplexType"

class EnrichmentVisitor(ast.NodeVisitor):
    def __init__(self):
        self.calls: Set[str] = set()
        self.reads: Set[str] = set()
        self.writes: Set[str] = set()
        self.effects: Set[str] = set()
        
    def visit_Call(self, node: ast.Call):
        # Extract called name (e.g., 'func', 'mod.func', 'self.method')
        name = self._get_call_name(node.func)
        if name:
            self.calls.add(name)
            self._check_effects(name)
        self.generic_visit(node)

    def _get_call_name(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = self._get_call_name(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        return None

    def _check_effects(self, name: str):
        """Heuristic for side effects based on called names."""
        lower_name = name.lower()
        if "open" in lower_name or "read" in lower_name or "write" in lower_name or "path" in lower_name:
            self.effects.add("fs")
        if "subprocess" in lower_name or "popen" in lower_name or "system" in lower_name:
            self.effects.add("subprocess")
        if "request" in lower_name or "http" in lower_name or "socket" in lower_name:
            self.effects.add("network")
        if "git" in lower_name:
            self.effects.add("git")
        if "db" in lower_name or "sql" in lower_name or "cursor" in lower_name:
            self.effects.add("db")

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Store):
            self.writes.add(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.reads.add(node.id)
        # Del is ignored for now

def enrich_symbol(node: ast.AST) -> Dict[str, Any]:
    """
    Analyzes an AST node (FunctionDef or ClassDef) to extract rich metadata.
    """
    meta = {
        "meta_version": 1,
        "signature": {
            "args": [],
            "returns": "Any",
            "decorators": []
        },
        "docstring": {
            "summary": "",
            "raw": None
        },
        "calls_names": [],
        "reads_definite": [],
        "writes_definite": [],
        "effects_flags": []
    }

    # Docstring extraction
    raw_doc = ast.get_docstring(node)
    if raw_doc:
        meta["docstring"]["raw"] = raw_doc
        meta["docstring"]["summary"] = raw_doc.strip().split('\n')[0]

    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        # 1. Signature
        # Decorators
        for dec in node.decorator_list:
            meta["signature"]["decorators"].append(get_annotation(dec))

        # Args
        # Handle defaults: they align with the end of the args list
        defaults = node.args.defaults
        num_args = len(node.args.args)
        num_defaults = len(defaults)
        
        for i, arg in enumerate(node.args.args):
            arg_meta = {"name": arg.arg, "annotation": "Any", "default": None}
            if arg.annotation:
                arg_meta["annotation"] = get_annotation(arg.annotation)
            
            # Check if this arg has a default
            if i >= num_args - num_defaults:
                default_idx = i - (num_args - num_defaults)
                try:
                    arg_meta["default"] = ast.unparse(defaults[default_idx])
                except AttributeError:
                    arg_meta["default"] = "..."
            
            meta["signature"]["args"].append(arg_meta)
        
        # Returns
        if node.returns:
            meta["signature"]["returns"] = get_annotation(node.returns)

        # 2. Body Analysis (Calls, Reads, Writes, Effects)
        visitor = EnrichmentVisitor()
        # Visit body only (skip args/decorators to avoid noise)
        for stmt in node.body:
            visitor.visit(stmt)
            
        meta["calls_names"] = sorted(list(visitor.calls))
        meta["reads_definite"] = sorted(list(visitor.reads))
        meta["writes_definite"] = sorted(list(visitor.writes))
        meta["effects_flags"] = sorted(list(visitor.effects))

    elif isinstance(node, ast.ClassDef):
        # For classes, we capture bases
        meta["signature"]["bases"] = [get_annotation(b) for b in node.bases]
        for dec in node.decorator_list:
            meta["signature"]["decorators"].append(get_annotation(dec))
        
    return meta
