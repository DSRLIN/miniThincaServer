from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum


class LogLevel(IntEnum):
    ERROR = 0
    INFO = 1
    DEBUG = 2


@dataclass
class Logger:
    level: LogLevel = LogLevel.DEBUG

    def log(self, content: str, lvl: LogLevel = LogLevel.DEBUG) -> None:
        if self.level >= lvl:
            print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}][{lvl.name}]{content}")


logger = Logger()
