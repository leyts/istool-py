from dataclasses import dataclass, replace
from pathlib import Path
from typing import ClassVar, Self

from istool_py._exceptions import CommandValidationError
from istool_py.commands._base import AssetSelection, Command


@dataclass(frozen=True, slots=True)
class ImportCommand(Command):
    _command_parts: ClassVar[tuple[str, ...]] = ("import",)
    _selections: tuple[AssetSelection, ...] = ()
    archive: Path = Path()
    preview: bool = False
    replace_existing: bool = False
    abort_after_errors: int | None = None

    def datastage(
        self,
        server: str,
        project: str,
        *,
        design_objects: bool = True,
    ) -> Self:
        sel = DataStageImportSelection(
            server=server,
            project=project,
            design_objects=design_objects,
        )
        return replace(self, _selections=(*self._selections, sel))

    def validate(self) -> None:
        if not self._selections:
            msg = "import requires at least one asset selection"
            raise CommandValidationError(msg)
        if self.abort_after_errors is not None and self.abort_after_errors < 1:
            msg = "abort_after_errors must be a positive integer"
            raise CommandValidationError(msg)
        for sel in self._selections:
            sel.validate()

    def _command_args(self) -> tuple[str, ...]:
        args: list[str] = ["-archive", str(self.archive)]
        if self.preview:
            args.append("-preview")
        if self.replace_existing:
            args.append("-replace")
        if self.abort_after_errors is not None:
            args.extend(("-abortAfter", str(self.abort_after_errors)))
        for sel in self._selections:
            args.extend(sel.to_args())
        return tuple(args)


@dataclass(frozen=True, slots=True)
class DataStageImportSelection(AssetSelection):
    _asset_flag: ClassVar[str] = "-datastage"
    server: str
    project: str
    design_objects: bool = True

    def _selection_args(self) -> tuple[str, ...]:
        args: list[str] = []
        if not self.design_objects:
            args.append("-nodesign")
        args.append(f"{self.server}/{self.project}")
        return tuple(args)
