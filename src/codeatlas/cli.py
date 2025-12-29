from __future__ import annotations

import argparse
import json
from pathlib import Path

from codeatlas.store_init import init_workspace
from codeatlas.index import build_or_update
from codeatlas.resolve import lookup_path, resolve_content


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="atlas")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_init = sub.add_parser("init", help="Initialize .atlas/ sidecar in workspace")
    sp_init.add_argument("--root", default=".", help="Workspace root")

    sp_index = sub.add_parser("index", help="Index workspace into .atlas/")
    sp_index.add_argument("--root", default=".", help="Workspace root")

    sp_res = sub.add_parser("resolve", help="Resolve a node and optionally print content")
    sp_res.add_argument("--root", default=".", help="Workspace root")
    g = sp_res.add_mutually_exclusive_group(required=True)
    g.add_argument("--path", help="Relative path in workspace")
    g.add_argument("--id", help="Node id")
    sp_res.add_argument("--content", action="store_true", help="Print resolved content (v1: whole file)")

    args = p.parse_args(argv)
    root = Path(getattr(args, "root", ".")).resolve()

    if args.cmd == "init":
        ap = init_workspace(root)
        out = {"ok": True, "atlas_dir": str(ap.atlas_dir)}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "index":
        init_workspace(root)
        stats = build_or_update(root)
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "resolve":
        init_workspace(root)
        if args.path:
            node_id = lookup_path(root, args.path)
            if node_id is None:
                print(json.dumps({"ok": False, "error": "path not found", "path": args.path}, indent=2))
                return 2
        else:
            node_id = args.id

        if args.content:
            content = resolve_content(root, node_id=node_id)
            # content is printed raw for user convenience
            print(content, end="" if content.endswith("\n") else "\n")
            return 0

        print(json.dumps({"ok": True, "id": node_id}, ensure_ascii=False, indent=2))
        return 0

    return 0
