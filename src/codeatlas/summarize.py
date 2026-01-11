from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from codeatlas.layout import AtlasPaths
from codeatlas.py_extract import extract_qualname_source
from codeatlas.llm import call_llm_api
from codeatlas.state import load_json, load_nodes_jsonl, write_nodes_jsonl


def generate_summary_prompt(symbol_name: str, symbol_code: str) -> str:
    return f"""
You are an expert software developer.
Please provide a concise, one-sentence summary for the following Python symbol (function or class).
The summary should describe its purpose, inputs, and outputs.

Symbol: {symbol_name}

Code:
```python
{symbol_code}
```

Return a JSON object with a single key "summary" containing the summary text.
Example: {{ "summary": "Calculates the factorial of a number." }}
""".strip()


def summarize_symbols(
    root: Path,
    paths: Optional[List[str]] = None,
    with_llm: bool = False,
) -> Dict[str, Any]:
    """
    Iterates over indexed symbol nodes and generates summary prompts.
    If with_llm is True, calls the LLM API to get the summaries.
    Otherwise, saves the prompts to files.
    """
    root = root.resolve()
    ap = AtlasPaths(root)

    # Load nodes from index
    nodes = load_nodes_jsonl(ap.nodes_path)
    if not nodes:
        return {"ok": False, "error": "No nodes found. Run 'atlas index' first."}

    summaries_dir = ap.atlas_dir / "summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)

    results = []
    llm_cfg = {}
    if with_llm:
        llm_cfg = load_json(ap.atlas_dir / "llm_cfg.json", default={})

    # Filter for symbol nodes (type="block")
    # If paths are provided, filter by path
    target_nodes = [n for n in nodes if n.get("type") == "block"]
    
    if paths:
        target_nodes = [n for n in target_nodes if n.get("path") in paths]

    for node in target_nodes:
        rp = node.get("path")
        qualname = node.get("anchor")

        if not rp or not qualname:
            continue

        full_path = root / rp
        if not full_path.exists():
            continue

        # Extract source code
        extract_res = extract_qualname_source(full_path, qualname)
        if not extract_res.get("ok"):
            continue

        code_text = extract_res["text"]
        prompt = generate_summary_prompt(qualname, code_text)

        # Create a safe filename for the symbol
        safe_name = f"{rp.replace('/', '_').replace('.', '_')}__{qualname.replace('.', '_')}"

        if with_llm:
            print(f"Summarizing {qualname} in {rp}...")
            llm_res = call_llm_api(prompt, llm_cfg)
            if llm_res.get("ok"):
                response_data = llm_res["response"]
                summary_text = response_data.get("summary", "")

                # Save the summary
                out_file = summaries_dir / f"{safe_name}.json"
                out_data = {
                    "file": rp,
                    "qualname": qualname,
                    "summary": summary_text
                }
                out_file.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
                results.append({"ok": True, "symbol": qualname, "file": rp, "status": "summarized"})
            else:
                results.append({"ok": False, "symbol": qualname, "file": rp, "error": llm_res.get("error")})
        else:
            # Manual mode: save prompt
            prompt_file = summaries_dir / f"{safe_name}.txt"
            prompt_file.write_text(prompt, encoding="utf-8")
            results.append({"ok": True, "symbol": qualname, "file": rp, "status": "prompt_saved", "path": str(prompt_file)})

    return {"ok": True, "results": results, "output_dir": str(summaries_dir)}


def update_spec_with_summaries(root: Path) -> Dict[str, Any]:
    """
    Reads generated summaries and updates CodeAtlas.json AND nodes.jsonl.
    """
    root = root.resolve()
    ap = AtlasPaths(root)
    summaries_dir = ap.atlas_dir / "summaries"

    if not summaries_dir.exists():
        return {"ok": False, "error": "No summaries directory found. Run 'atlas summarize' first."}

    # Load CodeAtlas.json (The Spec)
    codeatlas_json_path = root / "CodeAtlas.json"
    spec = {}
    if codeatlas_json_path.exists():
        try:
            spec = json.loads(codeatlas_json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    # Load nodes.jsonl (The Runtime State)
    nodes = load_nodes_jsonl(ap.nodes_path)

    # Load all summaries into a map: (file_path, qualname) -> summary
    summary_map = {}
    for f in summaries_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            key = (data.get("file"), data.get("qualname"))
            if key[0] and key[1]:
                summary_map[key] = data.get("summary")
        except:
            continue

    updated_count = 0

    # Update nodes.jsonl
    for node in nodes:
        if node.get("type") == "block":
            path = node.get("path")
            anchor = node.get("anchor")
            if path and anchor:
                summary = summary_map.get((path, anchor))
                if summary:
                    node["summary"] = summary
                    updated_count += 1

    # Write back nodes.jsonl
    write_nodes_jsonl(ap.nodes_path, nodes)

    # Update CodeAtlas.json (if it exists and has nodes)
    if spec and "nodes" in spec:
        spec_nodes = spec["nodes"]
        for node in spec_nodes:
            if node.get("type") == "block":
                path = node.get("path")
                anchor = node.get("anchor")
                if path and anchor:
                    summary = summary_map.get((path, anchor))
                    if summary:
                        node["summary"] = summary
        
        codeatlas_json_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {"ok": True, "updated_count": updated_count}
