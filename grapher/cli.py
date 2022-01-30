import argparse
import sys


from grapher.extract import register_parser as register_extract_options
from grapher.extract import run as run_extract
from grapher.graph import register_parser as register_graph_options
from grapher.graph import run as run_graph

VERSION = "0.0.1"


def main(args=sys.argv):
    parser = argparse.ArgumentParser(
        prog="pumpkin-grapher",
        allow_abbrev=False,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + VERSION,
    )

    subparsers = parser.add_subparsers(dest="command")
    register_extract_options(subparsers)
    register_graph_options(subparsers)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    if args.command == "extract":
        run_extract(args)
        return

    if args.command == "graph":
        run_graph(args)
        return
