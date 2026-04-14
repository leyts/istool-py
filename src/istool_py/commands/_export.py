import shlex
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Literal, Self

from istool_py._exceptions import CommandValidationError
from istool_py.commands._base import Command

if TYPE_CHECKING:
    from collections.abc import Sequence

    from istool_py.commands._base import Selection


type ArchiveMode = Literal["overwrite", "update"]


@dataclass(frozen=True, slots=True)
class ExportCommand(Command):
    _command_parts: ClassVar[tuple[str, ...]] = ("export",)
    _selections: tuple[Selection, ...] = ()
    archive: Path = Path()
    mode: ArchiveMode = "overwrite"

    def datastage(
        self,
        paths: Sequence[str],
        *,
        include_dependent: bool = False,
        include_design: bool = True,
        include_executable: bool = False,
    ) -> Self:
        sel = DataStageExportSelection(
            paths=tuple(paths),
            include_dependent=include_dependent,
            include_design=include_design,
            include_executable=include_executable,
        )
        return replace(self, _selections=(*self._selections, sel))

    def validate(self) -> None:
        if not self._selections:
            msg = "export requires at least one asset selection"
            raise CommandValidationError(msg)
        for sel in self._selections:
            sel.validate()

    def _command_args(self) -> tuple[str, ...]:
        args: list[str] = ["-archive", str(self.archive)]
        if self.mode == "update":
            args.append("-updatearchive")
        for sel in self._selections:
            args.extend(sel.to_args())
        return tuple(args)


@dataclass(frozen=True, slots=True)
class DataStageExportSelection:
    paths: tuple[str, ...]
    include_dependent: bool = False
    include_design: bool = True
    include_executable: bool = False

    def validate(self) -> None:
        if not self.paths:
            msg = "DataStage export requires at least one path"
            raise CommandValidationError(msg)
        if any(not p.strip() for p in self.paths):
            msg = "DataStage export paths must be non-empty"
            raise CommandValidationError(msg)

    def to_args(self) -> tuple[str, ...]:
        inner: list[str] = []
        if self.include_dependent:
            inner.append("-includedependent")
        if not self.include_design:
            inner.append("-nodesign")
        if self.include_executable:
            inner.append("-includeexecutable")
        inner.extend(self.paths)
        return ("-datastage", shlex.join(inner))
