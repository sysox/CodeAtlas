from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from codeatlas.layout import AtlasPaths


DEFAULT_CFG: Dict[str, Any] = {
    "include": ["*"],
    "exclude": [
        ".git/**",
        ".venv/**",
        ".atlas/**",
        "__pycache__/**",
        "dist/**",
        "build/**",
        "*.egg-info/**"
    ],
    "max_file_bytes": 2_000_000
}

DEFAULT_LLM_CFG: Dict[str, Any] = {
    "provider": "openai",
    "model": "gpt-4-turbo-preview",
    "api_key_env_var": "OPENAI_API_KEY",
    "endpoint_url": "https://api.openai.com/v1/chat/completions"
}


def init_workspace(root: Path) -> AtlasPaths:
    """Create .atlas layout and default cfg.json if missing."""
    root = root.resolve()
    ap = AtlasPaths(root)
    ap.ensure_dirs()

    if not ap.cfg_path.exists():
        ap.cfg_path.write_text(json.dumps(DEFAULT_CFG, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    llm_cfg_path = ap.atlas_dir / "llm_cfg.json"
    if not llm_cfg_path.exists():
        llm_cfg_path.write_text(json.dumps(DEFAULT_LLM_CFG, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not ap.nodes_path.exists():
        ap.nodes_path.write_text("", encoding="utf-8")

    if not ap.paths_index_path.exists():
        ap.paths_index_path.write_text("{}\n", encoding="utf-8")

    if not ap.fingerprints_path.exists():
        ap.fingerprints_path.write_text("{}\n", encoding="utf-8")

    return ap
