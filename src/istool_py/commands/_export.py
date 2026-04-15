from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Literal, Self

from istool_py._exceptions import CommandValidationError
from istool_py.commands._base import AssetSelection, Command

if TYPE_CHECKING:
    from collections.abc import Sequence


type ArchiveMode = Literal["overwrite", "update"]


@dataclass(frozen=True, slots=True)
class ExportCommand(Command):
    _command_parts: ClassVar[tuple[str, ...]] = ("export",)
    _selections: tuple[AssetSelection, ...] = ()
    archive: Path = Path()
    mode: ArchiveMode = "overwrite"
    abort_after_errors: int | None = None

    def datastage(
        self,
        paths: Sequence[str],
        *,
        dependencies: bool = False,
        design_objects: bool = True,
        executables: bool = False,
    ) -> Self:
        sel = DataStageExportSelection(
            paths=tuple(paths),
            dependencies=dependencies,
            design_objects=design_objects,
            executables=executables,
        )
        return replace(self, _selections=(*self._selections, sel))

    def validate(self) -> None:
        if not self._selections:
            msg = "export requires at least one asset selection"
            raise CommandValidationError(msg)
        if self.abort_after_errors is not None and self.abort_after_errors < 1:
            msg = "abort_after_errors must be a positive integer"
            raise CommandValidationError(msg)

    def _command_args(self) -> tuple[str, ...]:
        args: list[str] = []
        if self.mode == "update":
            args.append("-updatearchive")
        if self.abort_after_errors is not None:
            args.extend(("-abortIfError", str(self.abort_after_errors)))
        args.extend(("-archive", str(self.archive)))
        for sel in self._selections:
            args.extend(sel.to_args())
        return tuple(args)


@dataclass(frozen=True, slots=True)
class DataStageExportSelection(AssetSelection):
    _asset_flag: ClassVar[str] = "-datastage"
    paths: tuple[str, ...]
    dependencies: bool = False
    design_objects: bool = True
    executables: bool = False

    def validate(self) -> None:
        if not self.paths:
            msg = "DataStage export requires at least one path"
            raise CommandValidationError(msg)
        if any(not p.strip() for p in self.paths):
            msg = "DataStage export paths must be non-empty"
            raise CommandValidationError(msg)

    def _selection_args(self) -> tuple[str, ...]:
        args: list[str] = []
        if self.dependencies:
            args.append("-includedependent")
        if not self.design_objects:
            args.append("-nodesign")
        if self.executables:
            args.append("-includeexecutable")
        return (*args, *self.paths)
