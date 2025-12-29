from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Iterable, List


def _match_any(path_posix: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(path_posix, pat) for pat in patterns)


def scan_files(root: Path, include: List[str], exclude: List[str]) -> List[str]:
    """Return list of relative POSIX paths to index (stable sorted)."""
    root = root.resolve()
    out: List[str] = []

    for dirpath, dirnames, filenames in os.walk(root):
        drel = Path(dirpath).resolve().relative_to(root)
        drel_posix = drel.as_posix() if str(drel) != "." else ""

        # prune excluded directories
        pruned = []
        for dn in list(dirnames):
            rel = (drel / dn).as_posix()
            rel = rel if rel else dn
            if _match_any(rel + "/", exclude) or _match_any(rel, exclude):
                pruned.append(dn)
        for dn in pruned:
            dirnames.remove(dn)

        for fn in filenames:
            relp = (drel / fn).as_posix()
            # include/exclude checks
            if include and not _match_any(relp, include):
                continue
            if exclude and (_match_any(relp, exclude) or _match_any(relp + "/", exclude)):
                continue
            out.append(relp)

    out.sort()
    return out
