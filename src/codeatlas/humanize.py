from __future__ import annotations

import difflib
from typing import Any, Dict, List

def _generate_diff(before: str, after: str, filename: str) -> str:
    """Generates a unified diff string."""
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        n=3 # Context lines
    )
    return "".join(diff)

def _render_changes_to_yaml(changes: List[Dict[str, Any]], lines: List[str]):
    """Helper to render a list of changes to YAML lines."""
    changes_by_file = {}
    for p in changes:
        path = p.get("path")
        if path not in changes_by_file:
            changes_by_file[path] = []
        changes_by_file[path].append(p)

    for path, file_changes in changes_by_file.items():
        lines.append(f"  - file: {path}")
        lines.append("    operations:")
        for change in file_changes:
            op_type = "modify_symbol" if change.get("qualname") else "modify_file"
            lines.append(f"      - type: {op_type}")
            if "qualname" in change and change["qualname"]:
                lines.append(f"        symbol: {change['qualname']}")
            if "reason" in change:
                 lines.append(f"        reason: {repr(change['reason'])}")
            
            before_code = change.get("before_code", "")
            after_code = change.get("after_code", "")
            diff_text = _generate_diff(before_code, after_code, path)

            if diff_text:
                lines.append("        diff: |")
                for diff_line in diff_text.splitlines():
                    lines.append(f"          {diff_line}")
            else:
                lines.append("        diff: (no changes)")
        lines.append("")


def render_proposal_yaml(proposal_data: Dict[str, Any]) -> str:
    """
    Renders a human-readable YAML report from a causal proposal packet.
    """
    goal = proposal_data.get("goal", "No goal specified")
    primary_changes = proposal_data.get("primary_changes", [])
    dependent_changes = proposal_data.get("dependent_changes", [])
    
    # Calculate Impact
    all_changes = primary_changes + dependent_changes
    files_touched = set(c.get("path") for c in all_changes)
    symbols_modified = sum(1 for c in all_changes if c.get("qualname"))
    
    lines = []
    lines.append(f"# Proposal Review")
    lines.append(f"goal: {repr(goal)}")
    lines.append("")
    lines.append("impact:")
    lines.append(f"  files_modified: {len(files_touched)}")
    lines.append(f"  symbols_modified: {symbols_modified}")
    lines.append("")
    
    if primary_changes:
        lines.append("primary_changes:")
        _render_changes_to_yaml(primary_changes, lines)
        
    if dependent_changes:
        lines.append("dependent_changes:")
        _render_changes_to_yaml(dependent_changes, lines)

    return "\n".join(lines)
