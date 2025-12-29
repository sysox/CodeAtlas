from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    txt = path.read_text(encoding="utf-8").strip()
    if not txt:
        return default
    return json.loads(txt)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_nodes_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    out: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out


def load_nodes_map(path: Path) -> Dict[str, Dict[str, Any]]:
    nodes = load_nodes_jsonl(path)
    out: Dict[str, Dict[str, Any]] = {}
    for n in nodes:
        nid = n.get("id")
        if isinstance(nid, str):
            out[nid] = n
    return out


def write_nodes_jsonl(path: Path, nodes: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(n, ensure_ascii=False) for n in nodes]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
