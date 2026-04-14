from datetime import timedelta

import pytest

from istool_py._exceptions import (
    IstoolConnectionError,
    IstoolInvalidArchive,
    IstoolOperationFailed,
    IstoolOptionsFileError,
    IstoolPartialFailure,
    IstoolPreviewFailed,
    IstoolResponseFileError,
    IstoolRunError,
    IstoolSyntaxError,
    IstoolWarning,
)
from istool_py._runner import CommandResult


def _result(returncode: int) -> CommandResult:
    return CommandResult(
        argv=("istool",),
        returncode=returncode,
        stdout="",
        stderr="",
        duration=timedelta(0),
    )


@pytest.mark.parametrize(
    ("code", "exc_type"),
    [
        (1, IstoolWarning),
        (2, IstoolPartialFailure),
        (3, IstoolOperationFailed),
        (4, IstoolPreviewFailed),
        (5, IstoolInvalidArchive),
        (6, IstoolOptionsFileError),
        (7, IstoolResponseFileError),
        (8, IstoolResponseFileError),
        (9, IstoolResponseFileError),
        (10, IstoolConnectionError),
        (11, IstoolSyntaxError),
    ],
)
def test_raise_for_maps_exit_code_to_subclass(
    code: int, exc_type: type[IstoolRunError]
) -> None:
    result = _result(code)
    with pytest.raises(exc_type) as excinfo:
        IstoolRunError.raise_for(result)
    assert excinfo.value.result is result


def test_raise_for_zero_is_noop() -> None:
    result = _result(0)
    IstoolRunError.raise_for(result)


def test_raise_for_unknown_code_raises_base() -> None:
    result = _result(99)
    with pytest.raises(IstoolRunError) as excinfo:
        IstoolRunError.raise_for(result)
    assert type(excinfo.value) is IstoolRunError


def test_registry_maps_all_documented_exit_codes() -> None:
    assert IstoolRunError._registry == {
        1: IstoolWarning,
        2: IstoolPartialFailure,
        3: IstoolOperationFailed,
        4: IstoolPreviewFailed,
        5: IstoolInvalidArchive,
        6: IstoolOptionsFileError,
        7: IstoolResponseFileError,
        8: IstoolResponseFileError,
        9: IstoolResponseFileError,
        10: IstoolConnectionError,
        11: IstoolSyntaxError,
    }


def test_registry_rejects_duplicate_exit_codes() -> None:
    with pytest.raises(RuntimeError, match="already registered"):

        class _Dup(IstoolRunError, exit_codes=1):  # noqa: N818
            pass
