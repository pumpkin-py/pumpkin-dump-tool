from typing import Any, Dict
from pathlib import Path

from grapher.extract.scanners import DumpScanner


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
