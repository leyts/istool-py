import shlex
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from istool_py._exceptions import IstoolRunError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from istool_py._config import IstoolConfig
    from istool_py._runner import CommandResult, Runner


def istool_quote(token: str) -> str:
    r"""Quote a token for istool's nested argument parser.

    istool uses double quotes (not POSIX single quotes) to group tokens and
    `\"` to escape an embedded double quote within a quoted token.
    """
    if not any(c.isspace() or c == '"' for c in token):
        return token
    escaped = token.replace('"', '\\"')
    return f'"{escaped}"'


def istool_join(tokens: Iterable[str]) -> str:
    """Join tokens into a single istool nested-argument string."""
    return " ".join(istool_quote(t) for t in tokens)


class AssetSelection:
    _asset_flag: ClassVar[str]

    def validate(self) -> None:
        """Override in subclasses; raise on invalid state."""

    def to_args(self) -> tuple[str, ...]:
        return (self._asset_flag, istool_join(self._selection_args()))

    def _selection_args(self) -> tuple[str, ...]:
        raise NotImplementedError


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
