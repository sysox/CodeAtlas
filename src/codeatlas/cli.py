import argparse


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="atlas")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")
    sub.add_parser("index")
    sub.add_parser("resolve")

    args = p.parse_args(argv)
    print(f"TODO: {args.cmd}")
    return 0
