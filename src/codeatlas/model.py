from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Node:
    id: str
    type: str
    path: str
    anchor: Optional[str] = None
    summary: Optional[str] = None
    children: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            "path": self.path,
            "children": list(self.children),
        }
        if self.anchor is not None:
            d["anchor"] = self.anchor
        if self.summary is not None:
            d["summary"] = self.summary
        if self.meta:
            d["meta"] = dict(self.meta)
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Node":
        return Node(
            id=d["id"],
            type=d["type"],
            path=d["path"],
            anchor=d.get("anchor"),
            summary=d.get("summary"),
            children=list(d.get("children", [])),
            meta=dict(d.get("meta", {})),
        )


def make_id(kind: str, relpath: str, anchor: str | None = None) -> str:
    """Deterministic IDs. v1 uses file-level ids; later add kind+anchor schemes."""
    if anchor:
        return f"ref:{kind}:{relpath}::{anchor}"
    return f"ref:{kind}:{relpath}"
