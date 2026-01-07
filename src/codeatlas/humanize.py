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

def render_project_cheatsheet(machine_core: Dict[str, Any], level: int = 1) -> str:
    """
    Renders a YAML cheatsheet of the project structure.
    
    Level 1: Files and their summaries.
    Level 2: Files, Classes, Functions, Signatures, and Summaries.
    """
    nodes = machine_core.get("n", [])
    
    # Reconstruct tree structure
    # Map ID -> Node
    node_map = {n["i"]: n for n in nodes}
    
    # Find root children (files)
    # The root node usually has ID "root" or is the first one
    root_node = next((n for n in nodes if n.get("t") == "d" and n.get("i") == "root"), None)
    if not root_node and nodes:
        # Fallback: assume first node is root if not explicit
        root_node = nodes[0]
        
    if not root_node:
        return "# Empty Project"

    lines = []
    lines.append("# Project Cheatsheet")
    lines.append(f"# Level: {level}")
    lines.append("")
    lines.append("files:")

    def render_node(node_id: str, indent: int):
        node = node_map.get(node_id)
        if not node:
            return
        
        ntype = node.get("t")
        path = node.get("d", {}).get("p")
        anchor = node.get("d", {}).get("a")
        summary = node.get("s", "")
        
        prefix = "  " * indent
        
        if ntype == "f": # File
            lines.append(f"{prefix}- path: {path}")
            if summary:
                lines.append(f"{prefix}  summary: {repr(summary)}")
            
            if level >= 2:
                children = node.get("c", [])
                if children:
                    lines.append(f"{prefix}  symbols:")
                    for child_id in children:
                        render_node(child_id, indent + 2)
                        
        elif ntype == "b": # Block (Symbol)
            # For symbols, we want the name/signature
            # The 'anchor' is the qualname. We can try to extract just the name.
            name = anchor.split('.')[-1] if anchor else "unknown"
            
            # Try to get signature from meta if available (not currently stored, but good for future)
            # For now, just use the name
            lines.append(f"{prefix}- name: {name}")
            if anchor:
                lines.append(f"{prefix}  qualname: {anchor}")
            if summary:
                lines.append(f"{prefix}  summary: {repr(summary)}")
                
            # Render children (nested classes/methods)
            children = node.get("c", [])
            if children:
                lines.append(f"{prefix}  children:")
                for child_id in children:
                    render_node(child_id, indent + 2)

    # Start rendering from root's children
    for child_id in root_node.get("c", []):
        render_node(child_id, 1)
        
    return "\n".join(lines)
