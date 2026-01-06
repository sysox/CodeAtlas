from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from codeatlas.layout import AtlasPaths
from codeatlas.scan import scan_files
from codeatlas.py_symbols import list_python_symbols
from codeatlas.py_extract import extract_qualname_source
from codeatlas.llm import call_llm_api
from codeatlas.state import load_json


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
    Scans for symbols and generates summary prompts.
    If with_llm is True, calls the LLM API to get the summaries.
    Otherwise, saves the prompts to files.
    """
    root = root.resolve()
    ap = AtlasPaths(root)
    
    # Load config for scan
    cfg = load_json(ap.cfg_path, default={})
    include = cfg.get("include", ["*"])
    exclude = cfg.get("exclude", [".git/**", ".atlas/**", ".venv/**"])

    # Determine paths to scan
    if paths:
        relpaths = paths
    else:
        relpaths = scan_files(root, include=include, exclude=exclude)

    # Filter for Python files
    py_paths = [p for p in relpaths if p.endswith(".py")]

    summaries_dir = ap.atlas_dir / "summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)

    results = []
    llm_cfg = {}
    if with_llm:
        llm_cfg = load_json(ap.atlas_dir / "llm_cfg.json", default={})

    for rp in py_paths:
        full_path = root / rp
        if not full_path.exists():
            continue

        symbols = list_python_symbols(full_path)
        
        for sym in symbols:
            qualname = sym["qualname"]

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
    Reads generated summaries and updates CodeAtlas.json.
    """
    root = root.resolve()
    ap = AtlasPaths(root)
    summaries_dir = ap.atlas_dir / "summaries"
    
    if not summaries_dir.exists():
        return {"ok": False, "error": "No summaries directory found. Run 'atlas summarize' first."}

    # Load CodeAtlas.json
    codeatlas_json_path = root / "CodeAtlas.json"
    if not codeatlas_json_path.exists():
        return {"ok": False, "error": "CodeAtlas.json not found."}

    try:
        spec = json.loads(codeatlas_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"ok": False, "error": "Invalid CodeAtlas.json."}

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

    # Iterate through nodes in spec and update summaries
    # Note: CodeAtlas.json currently only has file-level nodes and "blocks" which are manually defined.
    # To fully support this, we need to map the "qualname" from the summary to the "id" or "anchor" in the spec.
    # The current spec uses IDs like "B_cli_main" and anchors like "main".
    # We will try to match by file path and anchor/qualname.

    nodes = spec.get("nodes", [])
    for node in nodes:
        if node.get("type") == "block":
            # Find parent file? The spec structure is flat list, but children are referenced by ID.
            # We need to find the file this block belongs to.
            # In the current spec, the "path" field is present on the block node itself!
            # e.g. "path": "src/codeatlas/cli.py", "anchor": "main"

            path = node.get("path")
            anchor = node.get("anchor")

            if path and anchor:
                # Try to find a summary for this path and anchor (qualname)
                summary = summary_map.get((path, anchor))
                if summary:
                    node["summary"] = summary
                    updated_count += 1

    # Write back
    codeatlas_json_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    
    return {"ok": True, "updated_count": updated_count}
