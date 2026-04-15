import shlex
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Protocol

from istool_py._exceptions import IstoolRunError

if TYPE_CHECKING:
    from istool_py._config import IstoolConfig
    from istool_py._runner import CommandResult, Runner


class Selection(Protocol):
    def validate(self) -> None: ...

    def to_args(self) -> tuple[str, ...]: ...


@dataclass(frozen=True, slots=True)
class Command:
    _command_parts: ClassVar[tuple[str, ...]] = ()
    _config: IstoolConfig
    _runner: Runner
    extra_args: tuple[str, ...] = ()

    def validate(self) -> None:
        """Override in subclasses; raise on invalid state."""

    def to_args(self) -> tuple[str, ...]:
        self.validate()
        return (
            str(self._config.executable),
            *self._command_parts,
            *self._config.to_auth_args(),
            *self._config.to_output_args(),
            *self._command_args(),
            *self.extra_args,
        )

    def render(self) -> str:
        return shlex.join(self.to_args())

    def run(self) -> CommandResult:
        result = self._runner.run(self.to_args())
        IstoolRunError.raise_if_failed(result)
        return result

    def _command_args(self) -> tuple[str, ...]:
        raise NotImplementedError
