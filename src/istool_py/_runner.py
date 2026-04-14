import subprocess
import time
from dataclasses import dataclass
from datetime import timedelta

from istool_py._exceptions import IstoolExecutableNotFoundError


@dataclass(frozen=True, slots=True)
class CommandResult:
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    duration: timedelta


class Runner:
    def __init__(self, *, encoding: str = "utf-8") -> None:
        self._encoding = encoding

    def __repr__(self) -> str:
        return f"{type(self).__name__}(encoding={self._encoding!r})"

    def run(self, argv: tuple[str, ...]) -> CommandResult:
        start = time.perf_counter()
        try:
            completed = subprocess.run(  # noqa: S603
                argv,
                capture_output=True,
                text=True,
                encoding=self._encoding,
                check=False,
            )
        except FileNotFoundError as exc:
            raise IstoolExecutableNotFoundError(argv[0]) from exc

        return CommandResult(
            argv=argv,
            returncode=completed.returncode,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            duration=timedelta(seconds=time.perf_counter() - start),
        )
