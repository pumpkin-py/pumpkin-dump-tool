import argparse
import sys
import os
from pathlib import Path
from typing import List

from grapher import CONTENT, comma_separated_content
from grapher.extract.scanners import get_scanner
from grapher.extract.writers import CSVWriter


def register_parser(main_parser: argparse._SubParsersAction):
    parser = main_parser.add_parser(
        "extract",
        prog="grapher extract",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--guild",
        required=True,
        type=int,
        help="Discord guild ID",
    )
    parser.add_argument(
        "--user",
        required=True,
        type=int,
        help="Discord user ID",
    )
    parser.add_argument(
        "--content",
        required=True,
        type=str,
        help="type of content (" + comma_separated_content() + ")",
    )
    parser.add_argument(
        "directory",
        type=str,
        help="path to dump directory",
        default=".",
    )
    parser.add_argument(
        "output",
        type=str,
        help="path to output file",
    )
    parser.add_argument(
        "--allow-overwrite",
        action="store_true",
        help="overwrite old files without asking",
    )
    return main_parser


def _scan_directory(directory: Path) -> List[Path]:
    """Get list of found dump files."""
    files = sorted(directory.glob("*.sql"))
    return files


def run(args: argparse.Namespace):
    if args.content not in CONTENT:
        print(f"Content '{args.content}' not supported.")
        print("Pick one of " + comma_separated_content() + ".")
        sys.exit(os.EX_USAGE)

    directory = Path(args.directory)
    files = _scan_directory(directory)
    if not files:
        print("No '*.sql' files were found.")
        sys.exit(os.EX_USAGE)

    output = Path(args.output)
    if output.is_file() and not args.allow_overwrite:
        print(f"File '{args.output}' already exists.")
        force: bool = None
        while force is None:
            overwrite = input("Overwrite? (yes/no) ")
            if overwrite.lower() in ("y", "yes"):
                force = True
            if overwrite in ("n", "no"):
                force = False
        if not force:
            sys.exit(os.EX_USAGE)

    scanner = get_scanner(args.content)
    data = scanner.search(args.guild, args.user, files)

    writer = CSVWriter(scanner, data)
    writer.dump(output)
