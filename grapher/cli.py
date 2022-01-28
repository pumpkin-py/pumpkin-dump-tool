import argparse
import sys

from grapher import __version__

from grapher.extract import register_parser as register_extract_options
from grapher.extract import run as run_extract


def main(args=sys.argv):
    parser = argparse.ArgumentParser(
        prog="grapher",
        allow_abbrev=False,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + __version__,
    )

    subparsers = parser.add_subparsers(dest="command")
    register_extract_options(subparsers)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    if args.command == "extract":
        run_extract(args)
        return
