from __future__ import annotations

from typing import Any, Dict, List

def render_llm_skeleton(machine_core: Dict[str, Any]) -> str:
    """
    Renders a dense, token-efficient skeleton of the project for LLMs.
    Includes signatures, structural blocks, and lightweight I/O.
    """
    nodes = machine_core.get("n", [])
    node_map = {n["i"]: n for n in nodes}
    
    # Find root children (files)
    root_node = next((n for n in nodes if n.get("t") == "d" and n.get("i") == "root"), None)
    if not root_node and nodes:
        root_node = nodes[0]
        
    if not root_node:
        return "# Empty Project"

    lines = []
    
    def render_file(file_node_id: str):
        node = node_map.get(file_node_id)
        if not node or node.get("t") != "f":
            return
            
        path = node.get("d", {}).get("p")
        if not path.endswith(".py"):
            return # Only render Python skeletons for now

        lines.append(f"# === {path} ===")
        
        children = node.get("c", [])
        for child_id in children:
            render_symbol(child_id, indent=0)
        lines.append("") # Blank line between files

    def render_symbol(symbol_id: str, indent: int):
        node = node_map.get(symbol_id)
        if not node:
            return
            
        meta = node.get("m", {})
        qualname = node.get("d", {}).get("a", "")
        name = qualname.split(".")[-1]
        kind = meta.get("kind", "function")
        
        prefix = "    " * indent
        
        # Signature
        sig_meta = meta.get("signature", {})
        sig = f"{prefix}{kind} {name}"
        
        if kind in ("function", "method"):
            args = sig_meta.get("args", [])
            arg_strs = []
            for arg in args:
                a = arg["name"]
                if arg.get("annotation") and arg["annotation"] != "Any":
                    a += f": {arg['annotation']}"
                if arg.get("default"):
                    a += f"={arg['default']}"
                arg_strs.append(a)
            
            ret = sig_meta.get("returns", "Any")
            sig += f"({', '.join(arg_strs)}) -> {ret}:"
            
            # Decorators
            decorators = sig_meta.get("decorators", [])
            for dec in decorators:
                lines.append(f"{prefix}@{dec}")
                
        elif kind == "class":
            bases = sig_meta.get("bases", [])
            if bases:
                sig += f"({', '.join(bases)}):"
            else:
                sig += ":"
            
            # Decorators
            decorators = sig_meta.get("decorators", [])
            for dec in decorators:
                lines.append(f"{prefix}@{dec}")
        
        lines.append(sig)
        
        # Docstring (Summary only)
        doc_summary = meta.get("docstring", {}).get("summary")
        if doc_summary:
            lines.append(f'{prefix}    """{doc_summary}"""')
            
        # Lightweight I/O & Calls
        calls = meta.get("calls_names", [])
        reads = meta.get("reads_definite", [])
        writes = meta.get("writes_definite", [])
        effects = meta.get("effects_flags", [])
        
        annotations = []
        if calls:
            annotations.append(f"Calls: {', '.join(calls[:5])}{'...' if len(calls)>5 else ''}")
        if reads:
            annotations.append(f"Reads: {', '.join(reads[:5])}{'...' if len(reads)>5 else ''}")
        if writes:
            annotations.append(f"Writes: {', '.join(writes[:5])}{'...' if len(writes)>5 else ''}")
        if effects:
            annotations.append(f"Effects: {', '.join(effects)}")
            
        if annotations:
            lines.append(f"{prefix}    # {'; '.join(annotations)}")

        # Children (Nested classes/methods)
        children = node.get("c", [])
        for child_id in children:
            render_symbol(child_id, indent + 1)
            
    # Start rendering
    for child_id in root_node.get("c", []):
        render_file(child_id)
        
    return "\n".join(lines)
