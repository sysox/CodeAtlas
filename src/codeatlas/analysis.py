from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

def find_usages_with_grep(root: Path, symbol: str) -> List[Dict[str, Any]]:
    """
    Finds potential usages of a symbol using a smart grep.
    
    This is a basic implementation. A more robust solution would use
    a proper language server or static analysis tool.
    
    Returns a list of matches, where each match is a dict with:
    - path: The file where the usage was found.
    - line: The line number of the match.
    - code: The content of the matching line.
    """
    results = []
    
    # Use word boundary grep to avoid matching substrings
    # e.g., searching for "foo" shouldn't match "foobar"
    pattern = f"\\b{symbol}\\b"
    
    try:
        # We use git grep as it's fast and respects .gitignore
        cmd = ["git", "grep", "-n", "-w", pattern]
        result = subprocess.run(
            cmd,
            cwd=root,
            capture_output=True,
            text=True,
            check=True
        )
        
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split(':', 2)
            if len(parts) == 3:
                path, line_num, code = parts
                results.append({
                    "path": path,
                    "line": int(line_num),
                    "code": code.strip()
                })
                
    except (subprocess.CalledProcessError, FileNotFoundError):
        # git grep will return non-zero if no matches are found, which is fine.
        # Or if git is not installed.
        pass
        
    return results
