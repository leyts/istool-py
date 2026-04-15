from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, ClassVar, Self

from istool_py._exceptions import CommandValidationError
from istool_py.commands._base import AssetSelection, Command

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True, slots=True)
class DeleteCommand(Command):
    _command_parts: ClassVar[tuple[str, ...]] = ("delete",)
    _selections: tuple[AssetSelection, ...] = ()
    abort_after_errors: int | None = None

    def datastage(
        self,
        server: str,
        project: str,
        folders: Sequence[str],
        asset_name: str,
    ) -> Self:
        sel = DataStageDeleteSelection(
            server=server,
            project=project,
            folders=tuple(folders),
            asset_name=asset_name,
        )
        return replace(self, _selections=(*self._selections, sel))

    def validate(self) -> None:
        if not self._selections:
            msg = "delete requires at least one asset selection"
            raise CommandValidationError(msg)
        if self.abort_after_errors is not None and self.abort_after_errors < 1:
            msg = "abort_after_errors must be a positive integer"
            raise CommandValidationError(msg)
        for sel in self._selections:
            sel.validate()

    def _command_args(self) -> tuple[str, ...]:
        args: list[str] = []
        if self.abort_after_errors is not None:
            args.extend(("-abortIfError", str(self.abort_after_errors)))
        for sel in self._selections:
            args.extend(sel.to_args())
        return tuple(args)


@dataclass(frozen=True, slots=True)
class DataStageDeleteSelection(AssetSelection):
    _asset_flag: ClassVar[str] = "-datastage"
    server: str
    project: str
    folders: tuple[str, ...]
    asset_name: str

    def _selection_args(self) -> tuple[str, ...]:
        path = "/".join(
            (
                self.server,
                self.project,
                *self.folders,
                self.asset_name,
            )
        )
        return (path,)
