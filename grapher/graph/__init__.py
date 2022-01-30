import argparse
import sys
import os
from pathlib import Path
from typing import List

import pygal


def register_parser(main_parser: argparse._SubParsersAction):
    parser = main_parser.add_parser(
        "graph",
        prog="grapher graph",
        allow_abbrev=False,
    )
    parser.add_argument(
        "source",
        type=str,
        help="path to source CSV",
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


def run(args: argparse.Namespace):
    source = Path(args.source)
    if not source.is_file():
        print(f"File '{args.source}' does not exist.")
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

    graph(source, output)


def graph(source: Path, output: Path):
    filename = source.name.replace(".csv", "")
    guild, user, content = filename.split("_")

    with source.open("r") as handle:
        data = [l.strip().split(",") for l in handle.readlines()]

    keys = [k[0] for k in data[1:]]
    since = keys[0]
    until = keys[-1]

    values = [int(v[1]) for v in data[1:]]

    chart = pygal.Line(width=1200, height=600, style=pygal.style.LightStyle)
    chart.title = f"{content}\n{since} \N{EM DASH} {until}"

    chart.x_labels = keys
    chart.x_label_rotation = 90
    chart.x_labels_major_every = 7
    chart.x_labels_major_count = int(len(keys) / 7)
    chart.show_minor_x_labels = False

    chart.add(content, values)
    chart.render_to_file(output)
