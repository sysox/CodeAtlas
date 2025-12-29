from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AtlasPaths:
    root: Path

    @property
    def atlas_dir(self) -> Path:
        return self.root / ".atlas"

    @property
    def cfg_path(self) -> Path:
        return self.atlas_dir / "cfg.json"

    @property
    def tree_dir(self) -> Path:
        return self.atlas_dir / "tree"

    @property
    def nodes_path(self) -> Path:
        return self.tree_dir / "nodes.jsonl"

    @property
    def index_dir(self) -> Path:
        return self.tree_dir / "index"

    @property
    def paths_index_path(self) -> Path:
        return self.index_dir / "paths.json"

    @property
    def fingerprints_path(self) -> Path:
        return self.tree_dir / "fingerprints.json"

    @property
    def blobs_dir(self) -> Path:
        return self.tree_dir / "blobs"

    @property
    def log_dir(self) -> Path:
        return self.atlas_dir / "log"

    def ensure_dirs(self) -> None:
        self.atlas_dir.mkdir(parents=True, exist_ok=True)
        self.tree_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.blobs_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
