from __future__ import annotations

import argparse
import json
from pathlib import Path

from codeatlas.store_init import init_workspace
from codeatlas.index import build_or_update
from codeatlas.resolve import lookup_path, resolve_content, resolve_node
from codeatlas.ctx import build_ctx
from codeatlas.py_symbols import list_python_symbols


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

    sp_show = sub.add_parser("show", help="Show node JSON")
    sp_show.add_argument("--root", default=".", help="Workspace root")
    g2 = sp_show.add_mutually_exclusive_group(required=True)
    g2.add_argument("--path", help="Relative path in workspace")
    g2.add_argument("--id", help="Node id")

    sp_ctx = sub.add_parser("ctx", help="Export minimal structured context for LLMs")
    sp_ctx.add_argument("--root", default=".", help="Workspace root")
    sp_ctx.add_argument("--path", action="append", default=[], help="Relative path to include (repeatable)")
    sp_ctx.add_argument("--id", action="append", default=[], help="Node id to include (repeatable)")
    sp_ctx.add_argument("--content", action="store_true", help="Include content text")
    sp_ctx.add_argument("--head", type=int, default=None, help="Include only first N lines")
    sp_ctx.add_argument("--tail", type=int, default=None, help="Include only last N lines")
    sp_ctx.add_argument("--max-bytes", type=int, default=None, help="Cap content bytes (UTF-8); truncates if needed")

    sp_syms = sub.add_parser("py-symbols", help="List Python symbols (qualnames + line spans)")
    sp_syms.add_argument("--root", default=".", help="Workspace root")
    sp_syms.add_argument("--path", required=True, help="Python file relative path")

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
            print(content, end="" if content.endswith("\n") else "\n")
            return 0

        print(json.dumps({"ok": True, "id": node_id}, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "show":
        init_workspace(root)
        if args.path:
            node_id = lookup_path(root, args.path)
            if node_id is None:
                print(json.dumps({"ok": False, "error": "path not found", "path": args.path}, indent=2))
                return 2
        else:
            node_id = args.id

        node = resolve_node(root, node_id)
        if node is None:
            print(json.dumps({"ok": False, "error": "node not found", "id": node_id}, indent=2))
            return 2
        print(json.dumps({"ok": True, "node": node}, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "ctx":
        init_workspace(root)
        bundle = build_ctx(
            root=root,
            paths=list(args.path or []),
            ids=list(args.id or []),
            content=bool(args.content),
            head=args.head,
            tail=args.tail,
            max_bytes=args.max_bytes
        )
        print(json.dumps(bundle, ensure_ascii=False, indent=2))
        return 0 if bundle.get("ok") else 2

    if args.cmd == "py-symbols":
        pth = (root / args.path).resolve()
        if not pth.exists():
            print(json.dumps({"ok": False, "error": "file not found", "path": args.path}, indent=2))
            return 2
        syms = list_python_symbols(pth)
        print(json.dumps({"ok": True, "path": args.path, "symbols": syms}, ensure_ascii=False, indent=2))
        return 0

    return 0
