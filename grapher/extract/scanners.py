from abc import ABC
import contextlib
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from grapher.errors import GrapherError


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
            raise GrapherError(f"Keys for table '{self.table_name}' not found.")

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
            raise GrapherError(
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

        if not data_line:
            return 0

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
