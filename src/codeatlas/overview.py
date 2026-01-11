from __future__ import annotations

from typing import Any, Dict, List

def render_human_overview(machine_core: Dict[str, Any]) -> str:
    """
    Renders a high-level Markdown overview of the project for humans.
    Focuses on architectural intent, roles, and workflows.
    """
    nodes = machine_core.get("n", [])
    node_map = {n["i"]: n for n in nodes}
    
    root_node = next((n for n in nodes if n.get("t") == "d" and n.get("i") == "root"), None)
    if not root_node and nodes:
        root_node = nodes[0]
        
    if not root_node:
        return "# Empty Project"

    lines = []
    lines.append("# Project Overview")
    lines.append("")
    lines.append("## Modules")
    lines.append("")

    def render_file_overview(file_node_id: str):
        node = node_map.get(file_node_id)
        if not node or node.get("t") != "f":
            return
            
        path = node.get("d", {}).get("p")
        if not path.endswith(".py"):
            return

        # Use AI summary if available, else docstring summary
        summary = node.get("s", "")
        if not summary:
            # Try to find a module-level docstring (not currently extracted by py_enrich, but good for future)
            pass
        
        lines.append(f"### `{path}`")
        if summary:
            lines.append(f"{summary}")
        lines.append("")
        
        # List key classes/functions
        children = node.get("c", [])
        if children:
            lines.append("| Symbol | Type | Description |")
            lines.append("|---|---|---|")
            for child_id in children:
                child = node_map.get(child_id)
                if not child: continue
                
                qualname = child.get("d", {}).get("a", "")
                name = qualname.split(".")[-1]
                kind = child.get("m", {}).get("kind", "symbol")
                
                # Priority: AI Summary > Docstring Summary > Empty
                child_summary = child.get("s", "")
                if not child_summary:
                    child_summary = child.get("m", {}).get("docstring", {}).get("summary", "")
                
                lines.append(f"| `{name}` | {kind} | {child_summary} |")
            lines.append("")

    for child_id in root_node.get("c", []):
        render_file_overview(child_id)
        
    return "\n".join(lines)
