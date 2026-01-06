from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from codeatlas.store_init import init_workspace
from codeatlas.index import build_or_update
from codeatlas.resolve import lookup_path, resolve_content, resolve_node
from codeatlas.ctx import build_ctx
from codeatlas.py_symbols import list_python_symbols
from codeatlas.py_extract import extract_qualname_source
from codeatlas.patch_skel import patch_skeleton
from codeatlas.plan import build_plan, build_plan_multi, parse_target, render_prompt_text
from codeatlas.diff import compute_diff
from codeatlas.grep import grep_snippets
from codeatlas.layout import AtlasPaths
from codeatlas.apply import apply_change_packet
from codeatlas.llm import call_llm_api
from codeatlas.state import load_json
from codeatlas.summarize import summarize_symbols, update_spec_with_summaries


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="atlas")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_init = sub.add_parser("init", help="Initialize .atlas/ sidecar in workspace")
    sp_init.add_argument("--root", default=".", help="Workspace root")

    sp_index = sub.add_parser("index", help="Index workspace into .atlas/")
    sp_index.add_argument("--root", default=".", help="Workspace root")

    sp_diff = sub.add_parser("diff", help="Show added/changed/deleted since last index")
    sp_diff.add_argument("--root", default=".", help="Workspace root")

    sp_grep = sub.add_parser("grep", help="Export small regex-matched snippets for LLM context")
    sp_grep.add_argument("--root", default=".", help="Workspace root")
    sp_grep.add_argument("--path", required=True, help="Target relative path")
    sp_grep.add_argument("--pattern", required=True, help="Regex pattern")
    sp_grep.add_argument("--context", type=int, default=2, help="Context lines around match")
    sp_grep.add_argument("--max-matches", type=int, default=20, help="Maximum matches")

    sp_snip = sub.add_parser("py-snippet", help="Extract exact Python symbol source by qualname")
    sp_snip.add_argument("--root", default=".", help="Workspace root")
    sp_snip.add_argument("--path", required=True, help="Python file relative path")
    sp_snip.add_argument("--qualname", required=True, help="Qualname (e.g., f, A.m)")
    sp_snip.add_argument("--context", type=int, default=0, help="Extra context lines")

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

    sp_patch = sub.add_parser("patch", help="Generate BridgePacket skeleton for a change")
    sp_patch.add_argument("--path", required=True, help="Target relative path")
    sp_patch.add_argument("--qualname", default=None, help="Python qualname for replace_symbol (optional)")
    sp_patch.add_argument("--op", default="replace_symbol", choices=["replace_symbol", "replace_file"], help="Skeleton op")
    sp_patch.add_argument("--run", action="append", default=None, help="Command to run after apply (repeatable)")
    sp_patch.add_argument("--commit", default=None, help="Commit message placeholder")

    sp_plan = sub.add_parser("plan", help="One-shot bundle: ctx + py-symbols + patch skeleton")
    sp_plan.add_argument("--root", default=".", help="Workspace root")
    sp_plan.add_argument("--goal", required=True, help="The user's goal for the change")
    sp_plan.add_argument("--target", action="append", default=[], help="Target: path or path::qualname (repeatable)")
    sp_plan.add_argument("--path", default=None, help="Target relative path (legacy)")
    sp_plan.add_argument("--qualname", default=None, help="Python qualname for replace_symbol (legacy)")
    sp_plan.add_argument("--with-llm", action="store_true", help="Call LLM API directly")
    sp_plan.add_argument("--apply", action="store_true", help="Apply the change packet automatically (requires --with-llm)")

    sp_plan.add_argument("--op", default="replace_symbol", choices=["replace_symbol", "replace_file"], help="Skeleton op")
    sp_plan.add_argument("--content", action="store_true", help="Include content text")
    sp_plan.add_argument("--head", type=int, default=None, help="Include only first N lines")
    sp_plan.add_argument("--tail", type=int, default=None, help="Include only last N lines")
    sp_plan.add_argument("--max-bytes", type=int, default=None, help="Cap content bytes (UTF-8); truncates if needed")
    sp_plan.add_argument("--run", action="append", default=None, help="Command to run after apply (repeatable)")
    sp_plan.add_argument("--commit", default=None, help="Commit message placeholder")

    sp_apply = sub.add_parser("apply", help="Apply a change packet to the workspace")
    sp_apply.add_argument("--root", default=".", help="Workspace root")
    sp_apply.add_argument("packet_path", help="Path to the change packet JSON file")

    sp_summ = sub.add_parser("summarize", help="Generate summaries for symbols")
    sp_summ.add_argument("--root", default=".", help="Workspace root")
    sp_summ.add_argument("--path", action="append", default=[], help="Specific paths to summarize (optional)")
    sp_summ.add_argument("--with-llm", action="store_true", help="Call LLM API to generate summaries")

    sp_spec_up = sub.add_parser("spec-update", help="Update CodeAtlas.json with generated summaries")
    sp_spec_up.add_argument("--root", default=".", help="Workspace root")


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

    if args.cmd == "diff":
        init_workspace(root)
        d = compute_diff(root)
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "grep":
        init_workspace(root)
        out = grep_snippets(root=root, path=args.path, pattern=args.pattern, context=args.context, max_matches=args.max_matches)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if out.get("ok") else 2

    if args.cmd == "py-snippet":
        pth = (root / args.path).resolve()
        out = extract_qualname_source(pth, args.qualname, context=args.context)
        # normalize path in output
        if out.get("ok"):
            out["path"] = args.path
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if out.get("ok") else 2

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

    if args.cmd == "patch":
        pkt = patch_skeleton(
            path=args.path,
            qualname=args.qualname,
            op=args.op,
            run=args.run,
            commit=args.commit
        )
        print(json.dumps(pkt, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "plan":
        if args.apply and not args.with_llm:
            print("Error: --apply can only be used with --with-llm.")
            return 1

        ap = AtlasPaths(root)
        run_dir = ap.log_dir / f"run_{time.strftime('%Y%m%d_%H%M%S')}"
        run_dir.mkdir(parents=True, exist_ok=True)

        init_workspace(root)
        if args.target:
            targets = [parse_target(t) for t in args.target]
            bundle = build_plan_multi(
                root=root,
                goal=args.goal,
                targets=targets,
                content=bool(args.content),
                head=args.head,
                tail=args.tail,
                max_bytes=args.max_bytes,
                op=args.op,
                run=args.run,
                commit=args.commit
            )
        else:
            if not args.path:
                print(json.dumps({"ok": False, "error": "provide --target or --path"}, indent=2))
                return 2
            bundle = build_plan(
                root=root,
                goal=args.goal,
                path=args.path,
                qualname=args.qualname,
                content=bool(args.content),
                head=args.head,
                tail=args.tail,
                max_bytes=args.max_bytes,
                op=args.op,
                run=args.run,
                commit=args.commit
            )
        
        bundle_path = run_dir / "bundle.json"
        bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")

        prompt_text = render_prompt_text(bundle)
        prompt_path = run_dir / "prompt.txt"
        prompt_path.write_text(prompt_text, encoding="utf-8")

        response_path = run_dir / "response.json"

        if args.with_llm:
            print("Calling LLM API...")
            llm_cfg_path = ap.atlas_dir / "llm_cfg.json"
            llm_cfg = load_json(llm_cfg_path, default={})
            result = call_llm_api(prompt_text, llm_cfg)
            
            if not result.get("ok"):
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 1

            response_path.write_text(json.dumps(result["response"], ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"LLM response saved to:\n  {response_path}")

            if args.apply:
                print("\nApplying change packet...")
                report = apply_change_packet(root, response_path)
                print(json.dumps(report, ensure_ascii=False, indent=2))
                return 0 if report.get("ok") else 1

        else:
            print(f"Plan generated successfully.")
            print(f"To get the code modification, copy the full content of:\n  {prompt_path}")
            print(f"and paste it into your LLM. Then save the JSON response to:\n  {response_path}")
            print(f"\nOnce the response is saved, apply it by running:\n  atlas apply {response_path}")


        return 0 if bundle.get("ok") else 2
    
    if args.cmd == "apply":
        packet_path = Path(args.packet_path)
        report = apply_change_packet(root, packet_path)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report.get("ok") else 1

    if args.cmd == "summarize":
        init_workspace(root)
        res = summarize_symbols(root, paths=args.path, with_llm=args.with_llm)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res.get("ok") else 1

    if args.cmd == "spec-update":
        init_workspace(root)
        res = update_spec_with_summaries(root)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res.get("ok") else 1

    return 0
