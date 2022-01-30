import argparse
import sys
import os
from pathlib import Path
from typing import Any, List

import pygal


def register_parser(main_parser: argparse._SubParsersAction):
    parser = main_parser.add_parser(
        "graph",
        prog="pumpkin-grapher graph",
        allow_abbrev=False,
    )
    parser.add_argument(
        "source",
        type=str,
        help="path to source CSV",
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

    try:
        # assume default filename
        series_name = source.name.split("_")[2].replace(".csv", "")
    except Exception:
        series_name = "data"

    chart = graph(source, series_name=series_name)

    chart.title = source.name + "\n" + chart.title

    save(chart, output)


def prepare_graph(
    *,
    title: str,
    x_axis: List[Any],
) -> pygal.graph.graph.Graph:
    chart = pygal.Line(interpolate="cubic")

    chart.title = title
    chart.width = 1200
    chart.height = 600
    chart.style = pygal.style.LightStyle

    chart.x_labels = x_axis
    chart.x_label_rotation = 90
    chart.x_labels_major_every = 7
    chart.x_labels_major_count = int(len(x_axis) / 7)
    chart.show_minor_x_labels = False

    chart._min = 0

    return chart


def graph(source: Path, series_name: str) -> pygal.graph.graph.Graph:
    with source.open("r") as handle:
        data = [line.strip().split(",") for line in handle.readlines()]

    keys = [k[0] for k in data[1:]]
    since = keys[0]
    until = keys[-1]

    values = [int(v[1]) for v in data[1:]]

    chart = prepare_graph(
        title=f"{since} \N{EM DASH} {until}",
        x_axis=keys,
    )

    chart.add(series_name, values)

    return chart


def save(chart: pygal.graph.graph.Graph, output: Path):
    if output.name.endswith("svg"):
        chart.render_to_file(str(output))
        return

    # https://www.pygal.org/en/stable/documentation/output.html:
    # In case of rendered image turning up black, installing
    # lxml, tinycss and cssselect should fix the issue.
    if output.name.endswith("png"):
        chart.render_to_png(str(output))
        return

    raise ValueError("Only '.svg' and '.png' output is supported.")
