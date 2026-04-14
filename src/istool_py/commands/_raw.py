from dataclasses import dataclass
from typing import ClassVar

from istool_py.commands._base import Command


@dataclass(frozen=True, slots=True)
class RawCommand(Command):
    _command_parts: ClassVar[tuple[str, ...]] = ()
    argv: tuple[str, ...] = ()

    def _command_args(self) -> tuple[str, ...]:
        return self.argv
