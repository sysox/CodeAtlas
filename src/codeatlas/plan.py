from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from codeatlas.patch_skel import patch_skeleton
from codeatlas.compression import build_machine_core
from codeatlas.resolve import lookup_path
from codeatlas.analysis import find_usages_with_grep
from codeatlas.model import make_id

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


def build_plan_multi(
    *,
    root: Path,
    goal: str,
    targets: List[Target],
    content: bool, # 'content' now means "expand context intelligently"
    op: str,
    run: Optional[List[str]],
    commit: Optional[str],
    # Deprecated args, kept for compatibility but ignored
    head: Optional[int] = None,
    tail: Optional[int] = None,
    max_bytes: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Builds an intelligent context bundle for an LLM.
    """
    root = root.resolve()

    # Set of node IDs to expand into full text content
    expand_ids: Set[str] = set()

    if content:
        for t in targets:
            # Always expand the primary target file
            target_file_nid = lookup_path(root, t.path)
            if target_file_nid:
                expand_ids.add(target_file_nid)

            # If the target is a symbol, find its usages and expand them too
            if t.qualname:
                # The symbol itself needs to be identified for expansion
                symbol_nid = make_id("symbol", t.path, t.qualname)
                expand_ids.add(symbol_nid)

                # Find usages of the symbol's name
                symbol_name = t.qualname.split('.')[-1]
                usages = find_usages_with_grep(root, symbol_name)
                
                for usage in usages:
                    # Find the node ID of the file where the usage occurred
                    usage_file_nid = lookup_path(root, usage["path"])
                    if usage_file_nid:
                        expand_ids.add(usage_file_nid)
                        # In a more advanced system, we could find the specific
                        # function (block) node containing the usage and expand only that.
                        # For now, expanding the whole file is a safe and effective strategy.

    # Build the Machine Core with intelligent context expansion
    machine_core = build_machine_core(root, expand_ids=list(expand_ids))

    # Create patch skeletons
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
- `m`: metadata (start/end lines, kind)
- `d`: data/content
    - `t`: content type (`ptr`=pointer to file, `txt`=inline text, `sum`=summary)
    - `v`: the actual text content (if `t`=`txt`)

Relevant files and dependencies have been expanded into `txt` format within this tree. Use this context to understand the code and plan your changes.

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
