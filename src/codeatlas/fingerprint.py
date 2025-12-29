from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple


def fingerprint_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_fingerprints(root: Path, relpaths: Iterable[str]) -> Dict[str, str]:
    root = root.resolve()
    return {rp: fingerprint_file(root / rp) for rp in relpaths}


def diff_fingerprints(old: Dict[str, str], new: Dict[str, str]) -> Dict[str, List[str]]:
    old_keys: Set[str] = set(old)
    new_keys: Set[str] = set(new)

    added = sorted(list(new_keys - old_keys))
    deleted = sorted(list(old_keys - new_keys))
    changed = sorted([k for k in (old_keys & new_keys) if old.get(k) != new.get(k)])
    unchanged = sorted([k for k in (old_keys & new_keys) if old.get(k) == new.get(k)])

    return {"added": added, "deleted": deleted, "changed": changed, "unchanged": unchanged}
