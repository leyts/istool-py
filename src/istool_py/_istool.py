from typing import TYPE_CHECKING, Any

from istool_py._config import IstoolConfig
from istool_py._runner import Runner
from istool_py.commands import (
    ArchiveMode,
    ExportCommand,
    ImportCommand,
    RawCommand,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


class Istool:
    def __init__(
        self,
        config: IstoolConfig | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        self._config = config or IstoolConfig(**kwargs)
        self._runner = Runner()

    def export(
        self,
        archive: Path,
        *,
        mode: ArchiveMode = "overwrite",
        extra_args: Sequence[str] = (),
    ) -> ExportCommand:
        return ExportCommand(
            _config=self._config,
            _runner=self._runner,
            archive=archive,
            mode=mode,
            extra_args=tuple(extra_args),
        )

    def import_(
        self,
        archive: Path,
        *,
        preview: bool = False,
        replace_existing: bool = False,
        extra_args: Sequence[str] = (),
    ) -> ImportCommand:
        return ImportCommand(
            _config=self._config,
            _runner=self._runner,
            archive=archive,
            preview=preview,
            replace_existing=replace_existing,
            extra_args=tuple(extra_args),
        )

    def raw(self, *args: str) -> RawCommand:
        return RawCommand(
            _config=self._config,
            _runner=self._runner,
            argv=args,
        )
