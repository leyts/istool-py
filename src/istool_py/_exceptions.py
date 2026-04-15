from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from istool_py._runner import CommandResult


class IstoolError(Exception):
    """Base for all istool errors."""


class CommandValidationError(IstoolError):
    """A command cannot be rendered to a valid CLI invocation."""


class IstoolExecutableNotFoundError(IstoolError):
    def __init__(self, executable: str) -> None:
        self.executable = executable
        super().__init__(f"istool executable not found: {executable}")


class IstoolRunError(IstoolError):
    """Base for any non-zero exit from istool.

    Subclasses register their exit codes via the ``exit_codes`` class
    keyword, e.g. ``class IstoolWarning(IstoolRunError, exit_codes=1)``.
    """

    _registry: ClassVar[dict[int, type[IstoolRunError]]] = {}

    def __init_subclass__(
        cls,
        *,
        exit_codes: int | tuple[int, ...] | None = None,
        **kwargs: object,
    ) -> None:
        super().__init_subclass__(**kwargs)
        if exit_codes is None:
            return
        codes = (exit_codes,) if isinstance(exit_codes, int) else exit_codes
        for code in codes:
            if code in cls._registry:
                owner = cls._registry[code].__name__
                msg = f"exit code {code} already registered to {owner}"
                raise RuntimeError(msg)
        for code in codes:
            cls._registry[code] = cls

    def __init__(self, result: CommandResult) -> None:
        self.result = result
        stderr = result.stderr.strip()
        msg = f"istool exited with code {result.returncode}"
        if stderr:
            msg += f": {stderr}"
        super().__init__(msg)

    @classmethod
    def raise_if_failed(cls, result: CommandResult) -> None:
        """Raise the matching subclass for result.returncode, pass on 0."""
        rc = result.returncode
        if rc == 0:
            return
        sub = cls._registry.get(rc, cls)
        raise sub(result=result)


# Subclass names follow istool's documented exit-code categories rather
# than the generic `Error` suffix convention.
class IstoolWarning(IstoolRunError, exit_codes=1):  # noqa: N818
    """Operation completed with warnings (exit 1)."""


class IstoolPartialFailure(IstoolRunError, exit_codes=2):  # noqa: N818
    """Some assets processed, some failed (exit 2)."""


class IstoolOperationFailed(IstoolRunError, exit_codes=3):  # noqa: N818
    """The requested operation failed to complete (exit 3)."""


class IstoolPreviewFailed(IstoolRunError, exit_codes=4):  # noqa: N818
    """A ``-preview`` invocation failed (exit 4)."""


class IstoolInvalidArchive(IstoolRunError, exit_codes=5):  # noqa: N818
    """The archive file is malformed or could not be read (exit 5)."""


class IstoolOptionsFileError(IstoolRunError, exit_codes=6):
    """Failed to read or parse an options file (exit 6)."""


class IstoolResponseFileError(IstoolRunError, exit_codes=(7, 8, 9)):
    """Failed to parse, read or write a response file (exits 7, 8, 9)."""


class IstoolConnectionError(IstoolRunError, exit_codes=10):
    """Could not connect to the Information Server (exit 10)."""


class IstoolSyntaxError(IstoolRunError, exit_codes=11):
    """Malformed command invocation or unknown option (exit 11)."""
