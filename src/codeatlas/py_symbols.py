from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Sym:
    qualname: str
    kind: str  # class|function|method
    start_line: int
    end_line: int
    ast_node: Optional[ast.AST] = None # Added for enrichment

    def to_dict(self) -> Dict[str, Any]:
        return {
            "qualname": self.qualname,
            "kind": self.kind,
            "start_line": self.start_line,
            "end_line": self.end_line,
        }


class _Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.stack: List[str] = []
        self.out: List[Sym] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        name = node.name
        qn = ".".join(self.stack + [name]) if self.stack else name
        self.out.append(Sym(qn, "class", getattr(node, "lineno", 1), getattr(node, "end_lineno", getattr(node, "lineno", 1)), node))
        self.stack.append(name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self._visit_fn(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        self._visit_fn(node)

    def _visit_fn(self, node: ast.AST) -> Any:
        name = getattr(node, "name", "<fn>")
        qn = ".".join(self.stack + [name]) if self.stack else name
        kind = "method" if self.stack else "function"
        self.out.append(Sym(qn, kind, getattr(node, "lineno", 1), getattr(node, "end_lineno", getattr(node, "lineno", 1)), node))
        self.stack.append(name)
        self.generic_visit(node)
        self.stack.pop()


def list_python_symbols(path: Path) -> List[Dict[str, Any]]:
    """Return symbols (qualnames + line spans). Legacy wrapper."""
    syms = parse_symbols(path)
    return [s.to_dict() for s in syms]

def parse_symbols(path: Path) -> List[Sym]:
    """Return Sym objects with AST nodes attached."""
    src = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    v = _Visitor()
    v.visit(tree)
    v.out.sort(key=lambda s: (s.start_line, s.qualname))
    return v.out
