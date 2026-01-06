from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from codeatlas.patch_skel import patch_skeleton
from codeatlas.py_symbols import list_python_symbols
from codeatlas.py_extract import extract_qualname_source
from codeatlas.compression import build_machine_core
from codeatlas.resolve import lookup_path


@dataclass(frozen=True)
class Target:
    path: str
    qualname: Optional[str] = None


def parse_target(s: str) -> Target:
    """Parse 'path' or 'path::qualname'."""
    if "::" in s:
        p, q = s.split("::", 1)
        p = p.strip()
        q = q.strip()
        return Target(path=p, qualname=(q or None))
    return Target(path=s.strip(), qualname=None)


def build_plan(
    *,
    root: Path,
    goal: str,
    path: str,
    qualname: Optional[str],
    content: bool,
    head: Optional[int],
    tail: Optional[int],
    max_bytes: Optional[int],
    op: str,
    run: Optional[List[str]],
    commit: Optional[str],
) -> Dict[str, Any]:
    """Backward-compatible single-target plan."""
    return build_plan_multi(
        root=root,
        goal=goal,
        targets=[Target(path=path, qualname=qualname)],
        content=content,
        head=head,
        tail=tail,
        max_bytes=max_bytes,
        op=op,
        run=run,
        commit=commit,
    )


def build_plan_multi(
    *,
    root: Path,
    goal: str,
    targets: List[Target],
    content: bool,
    head: Optional[int],
    tail: Optional[int],
    max_bytes: Optional[int],
    op: str,
    run: Optional[List[str]],
    commit: Optional[str],
) -> Dict[str, Any]:
    """Build a single JSON bundle intended to be pasted to an LLM.

    Includes:
      - machine_core: compressed structural representation of the project, 
                      with target nodes expanded into inline text.
      - py_symbols_by_path: qualnames+spans for each .py path
      - symbol_snippets: exact source text for any target with qualname (token saver)
      - patches: BridgeAI packet skeleton per target
    """
    root = root.resolve()

    # Resolve target paths to node IDs for expansion
    expand_ids = []
    paths: List[str] = []
    seen = set()
    
    for t in targets:
        if t.path not in seen:
            seen.add(t.path)
            paths.append(t.path)
            
        # Lookup node ID for the file
        nid = lookup_path(root, t.path)
        if nid:
            expand_ids.append(nid)
            # Note: Ideally we would also expand specific symbol IDs if t.qualname is set,
            # but our current lookup_path only handles files. 
            # Since we expand the whole file, the symbol is included.

    # Build Machine Core with selective expansion
    # This creates the Hybrid View: mostly pointers, but text for targets.
    machine_core = build_machine_core(root, expand_ids=expand_ids if content else None)

    py_symbols_by_path: Dict[str, Any] = {}
    for p in paths:
        if p.lower().endswith(".py"):
            pp = root / p
            if pp.exists():
                py_symbols_by_path[p] = list_python_symbols(pp)

    symbol_snippets: List[Dict[str, Any]] = []
    for t in targets:
        if t.qualname and t.path.lower().endswith(".py"):
            pp = root / t.path
            res = extract_qualname_source(pp, t.qualname, context=0)
            # normalize path back to repo-relative for display
            if res.get("ok"):
                symbol_snippets.append(
                    {
                        "ok": True,
                        "path": t.path,
                        "qualname": t.qualname,
                        "start_line": res["start_line"],
                        "end_line": res["end_line"],
                        "text": res["text"],
                    }
                )
            else:
                symbol_snippets.append({"ok": False, "path": t.path, "qualname": t.qualname, "error": res.get("error")})

    patches: List[Dict[str, Any]] = []
    for t in targets:
        chosen_op = op
        if t.qualname is None and chosen_op == "replace_symbol":
            chosen_op = "replace_file"
        patches.append(
            patch_skeleton(
                path=t.path,
                qualname=t.qualname,
                op=chosen_op,
                run=run,
                commit=commit,
            )
        )

    return {
        "ok": True,
        "root": str(root),
        "goal": goal,
        "targets": [{"path": t.path, "qualname": t.qualname} for t in targets],
        "machine_core": machine_core,
        "py_symbols_by_path": py_symbols_by_path,
        "symbol_snippets": symbol_snippets,
        "patches": patches,
    }

def render_prompt_text(bundle: Dict[str, Any]) -> str:
    """Render the JSON bundle into a text prompt for an LLM."""
    patches_skeleton = bundle.get("patches", [])
    machine_core = bundle.get("machine_core", {})
    goal = bundle.get("goal", "Not specified")

    prompt = f"""
You are an expert software developer. Your task is to complete the JSON object below to modify a codebase.

The user's goal is: "{goal}"

### Project Context (Machine Core)
The following JSON object is the "Machine Core" of the project. It is a tree structure where:
- `t`: type (f=file, d=dir, b=block)
- `d`: data/content
    - `t`: content type (`ptr`=pointer to file, `txt`=inline text, `sum`=summary)
    - `v`: the actual text content (if `t`=`txt`)

Relevant files have been expanded into `txt` format within this tree. Use this context to understand the code and plan your changes.

```json
{json.dumps(machine_core, indent=None, separators=(',', ':'))}
```

### Task
Based on the user's goal and the provided context, complete the following JSON "change packet" skeleton. 
Fill in the `<PASTE_..._HERE>` placeholders with the exact code or content required. 
Do not modify the structure of the skeleton.

```json
{json.dumps(patches_skeleton, indent=2)}
```
"""
    return prompt.strip()
