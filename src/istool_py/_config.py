from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from istool_py._exceptions import CommandValidationError

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, slots=True)
class IstoolConfig:
    executable: Path
    authfile: Path | None = None
    domain: str | None = None
    username: str | None = None
    password: str | None = field(default=None, repr=False)
    verbose: bool = False
    silent: bool = False

    def __post_init__(self) -> None:
        if self.verbose and self.silent:
            msg = "verbose and silent are mutually exclusive"
            raise CommandValidationError(msg)

        has_triple = any(
            x is not None for x in (self.domain, self.username, self.password)
        )
        if self.authfile is not None and has_triple:
            msg = (
                "authfile is mutually exclusive with"
                " the (domain, username, password) credential triple"
            )
            raise CommandValidationError(msg)

        if not self.executable.is_file():
            msg = f"executable does not exist: {self.executable}"
            raise CommandValidationError(msg)

        if self.authfile is not None and not self.authfile.is_file():
            msg = f"authfile does not exist: {self.authfile}"
            raise CommandValidationError(msg)

    def to_auth_args(self) -> tuple[str, ...]:
        if self.authfile is not None:
            return ("-authfile", str(self.authfile))
        args: list[str] = []
        if self.domain is not None:
            args.extend(("-domain", self.domain))
        if self.username is not None:
            args.extend(("-username", self.username))
        if self.password is not None:
            args.extend(("-password", self.password))
        return tuple(args)

    def to_output_args(self) -> tuple[str, ...]:
        if self.verbose:
            return ("-verbose",)
        if self.silent:
            return ("-silent",)
        return ()
