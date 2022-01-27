from abc import ABC
import argparse
import contextlib
import datetime
import sys
import os
from pathlib import Path
from typing import Any, Dict, List

__version__ = "0.0.0"
__name__ = "grapher"

CONTENT = (
    "total-karma",
    "given-karma",
    "taken-karma",
    "total-points",
    "hug",
    "pet",
    "hyperpet",
    "lick",
    "hyperlick",
    "spank",
)


def comma_separated_content() -> str:
    return ", ".join(f"'{c}'" for c in CONTENT)


def scan_directory(directory: Path) -> List[Path]:
    """Get list of found dump files."""
    files = sorted(directory.glob("*.sql"))
    return files


class GrapherException(Exception):
    pass


class BadDumpFile(GrapherException):
    pass


class DumpScanner(ABC):
    table_name: str
    key: str

    parser_keys: List[str]

    __slots__ = (
        # static
        "table_name",
        "key",
        # dynamic
        "parser_keys",
    )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} " f"table_name='{self.table_name}'>"

    def set_parser_keys(self, line: str) -> None:
        key_list: str = line.split("(", 1)[1].split(")", 1)[0]
        self.parser_keys = key_list.split(", ")

    def get_parsed_values(self, line: str) -> Dict[str, Any]:
        if not self.parser_keys:
            raise GrapherException(
                f"Table '{self.table_name}' not found in file '{file}'."
            )

        raw_tokens = line.split("\t")
        tokens: List[Union[str, int]] = []
        for token in raw_tokens:
            with contextlib.suppress(ValueError):
                token = int(token)
            tokens.append(token)

        values = dict(zip(self.parser_keys, tokens))
        return values

    def search(self, guild_id: int, user_id: int, files: List[Path]):
        """Search database dumps for a value."""
        if not self.table_name:
            raise GrapherException(
                f"Scanner '{self.__class__.__name__}' does not have "
                "'table_name' set up."
            )

        data: Dict[datetime.datetime, Any] = {}

        for file in files:
            timestamp = datetime.datetime.strptime(
                file.name, "dump_%Y-%m-%d_%H:%M:%S.sql"
            )
            value = self.search_file(guild_id, user_id, file)
            data[timestamp] = value

        return data

    def search_file(self, guild_id: int, user_id: int, file: Path) -> Any:
        """Search file for seeked value."""
        reading: bool = False
        data_line: Optional[str] = None

        with file.open("r") as handle:
            for line in handle.readlines():
                line = line.strip()
                if line.startswith(f"COPY public.{self.table_name}"):
                    self.set_parser_keys(line)
                    reading = True
                    continue

                if reading is True and line == "":
                    reading = False
                    break

                if not reading:
                    continue

                if str(guild_id) not in line or str(user_id) not in line:
                    continue

                data_line = line
                break

        values: Dict[str, Union[str, int]] = self.get_parsed_values(data_line)
        return values[self.key]


class PointsScanner(DumpScanner):
    table_name: str = "boards_points_users"
    key: str = "points"


class CSVWriter:
    key: str
    data: Dict[str, Any]

    def __init__(self, scanner: DumpScanner, data: Dict[str, Any]):
        self.key = scanner.key
        self.data = data

    def dump(self, file: Path):
        with file.open("w") as handle:
            handle.write(f"timestamp,{self.key}\n")
            for key, value in self.data.items():
                handle.write(f"{key},{value}\n")


def main(args=sys.argv):
    parser = argparse.ArgumentParser(
        prog=__name__,
        allow_abbrev=False,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + __version__,
    )
    #
    parser.add_argument(
        "--user",
        required=True,
        action="store",
        type=int,
        help="Discord user ID",
    )
    parser.add_argument(
        "--guild",
        required=True,
        action="store",
        type=int,
        help="Discord guild ID",
    )
    parser.add_argument(
        "--content",
        required=True,
        action="store",
        type=str,
        help="type of content (" + comma_separated_content() + ")",
    )
    parser.add_argument(
        "directory",
        action="store",
        type=str,
        help="path to dump directory",
        default=".",
    )
    parser.add_argument(
        "output",
        action="store",
        type=str,
        help="path to output file",
    )
    #
    args = parser.parse_args()
    if args.content not in CONTENT:
        print(f"Content '{args.content}' not supported.")
        print(f"Pick one of " + comma_separated_content() + ".")
        sys.exit(os.EX_USAGE)

    directory = Path(args.directory)
    files = scan_directory(directory)
    if not files:
        print(f"No '*.sql' files were found.")
        sys.exit(os.EX_USAGE)

    output = Path(args.output)
    if output.is_file():
        print(f"File '{args.output}' already exists.")
        sys.exit(os.EX_USAGE)

    scanner = PointsScanner()
    data = scanner.search(args.guild, args.user, files)

    writer = CSVWriter(scanner, data)
    writer.dump(output)
