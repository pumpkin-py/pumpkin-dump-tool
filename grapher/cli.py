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
    "karma",
    "karma-given",
    "karma-taken",
    "points",
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


class RelationsScanner(DumpScanner):
    table_name: str = "fun_fun_relations"
    key: str = "value"
    constraint: str

    parser_keys: List[str]

    def search_file(self, guild_id: int, user_id: int, file: Path) -> Any:
        """Search file for seeked value."""
        reading: bool = False
        counter: int = 0

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

                if (
                    str(guild_id) not in line
                    or str(user_id) not in line
                    or self.constraint not in line
                ):
                    continue

                values: Dict = self.get_parsed_values(line)
                counter += values["value"]

        return counter


class PointsScanner(DumpScanner):
    table_name: str = "boards_points_users"
    key: str = "points"


class KarmaValueScanner(DumpScanner):
    table_name: str = "boards_karma_members"
    key: str = "value"


class KarmaGivenScanner(DumpScanner):
    table_name: str = "boards_karma_members"
    key: str = "given"


class KarmaTakenScanner(DumpScanner):
    table_name: str = "boards_karma_members"
    key: str = "taken"


class RelationsHugScanner(RelationsScanner):
    constraint: str = "hug"


class RelationsPetScanner(RelationsScanner):
    constraint: str = "pet"


class RelationsHyperpetScanner(RelationsScanner):
    constraint: str = "hyperpet"


class RelationsHighfiveScanner(RelationsScanner):
    constraint: str = "highfive"


class RelationsSpankScanner(RelationsScanner):
    constraint: str = "spank"


class RelationsSlapScanner(RelationsScanner):
    constraint: str = "slap"


class RelationsBonkScanner(RelationsScanner):
    constraint: str = "bonk"


class RelationsWhipScanner(RelationsScanner):
    constraint: str = "whip"


class RelationsLickScanner(RelationsScanner):
    constraint: str = "lick"


class RelationsHyperlickScanner(RelationsScanner):
    constraint: str = "hyperlick"


def get_scanner(content: str):
    if content == "karma":
        return KarmaValueScanner()
    if content == "given-karma":
        return KarmaGivenScanner()
    if content == "taken-karma":
        return KarmaTakenScanner()
    if content == "points":
        return PointsScanner()
    if content == "hug":
        return RelationsHugScanner()
    if content == "pet":
        return RelationsPetScanner()
    if content == "highfive":
        return RelationsHighfiveScanner()
    if content == "spank":
        return RelationsSpankScanner()
    if content == "slap":
        return RelationsSlapScanner()
    if content == "bonk":
        return RelationsBonkScanner()
    if content == "whip":
        return RelationsWhipScanner()
    if content == "hyperpet":
        return RelationsHyperpetScanner()
    if content == "lick":
        return RelationsLickScanner()
    if content == "hyperlick":
        return RelationsHyperlickScanner()
    raise ValueError(f"Unsupported content '{content}'.")


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
                key_: str = key.strftime("%Y-%m-%d")
                handle.write(f"{key_},{value}\n")


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
    parser.add_argument(
        "--allow-overwrite",
        action="store_true",
        help="overwrite old files without asking",
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
