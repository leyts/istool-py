import shlex
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Self

from istool_py._exceptions import CommandValidationError
from istool_py.commands._base import Command

if TYPE_CHECKING:
    from istool_py.commands._base import Selection


@dataclass(frozen=True, slots=True)
class ImportCommand(Command):
    _command_parts: ClassVar[tuple[str, ...]] = ("import",)
    _selections: tuple[Selection, ...] = ()
    archive: Path = Path()
    preview: bool = False
    replace_existing: bool = False

    def datastage(
        self,
        project: str,
        *,
        server: str | None = None,
        include_design: bool = True,
    ) -> Self:
        sel = DataStageImportSelection(
            project=project,
            server=server,
            include_design=include_design,
        )
        return replace(self, _selections=(*self._selections, sel))

    def validate(self) -> None:
        if not self._selections:
            msg = "import requires at least one asset selection"
            raise CommandValidationError(msg)
        for sel in self._selections:
            sel.validate()

    def _command_args(self) -> tuple[str, ...]:
        args: list[str] = ["-archive", str(self.archive)]
        if self.preview:
            args.append("-preview")
        if self.replace_existing:
            args.append("-replace")
        for sel in self._selections:
            args.extend(sel.to_args())
        return tuple(args)


@dataclass(frozen=True, slots=True)
class DataStageImportSelection:
    project: str
    server: str | None = None
    include_design: bool = True

    def validate(self) -> None: ...

    def to_args(self) -> tuple[str, ...]:
        inner: list[str] = []
        if not self.include_design:
            inner.append("-nodesign")
        target = (
            f"{self.server}/{self.project}"
            if self.server is not None
            else self.project
        )
        inner.append(target)
        return ("-datastage", shlex.join(inner))
