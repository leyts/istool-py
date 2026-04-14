from datetime import timedelta
from typing import TYPE_CHECKING

import pytest

from istool_py._exceptions import IstoolExecutableNotFoundError
from istool_py._runner import CommandResult, Runner

if TYPE_CHECKING:
    from pathlib import Path


def test_result_is_frozen_and_slotted() -> None:
    result = CommandResult(
        argv=("/bin/echo",),
        returncode=0,
        stdout="",
        stderr="",
        duration=timedelta(seconds=0),
    )
    with pytest.raises(AttributeError):
        result.returncode = 1  # pyright: ignore[reportAttributeAccessIssue] # ty: ignore[invalid-assignment]


def test_run_captures_stdout_and_exit_zero(fake_istool: Path) -> None:
    runner = Runner()
    result = runner.run((str(fake_istool), "hello"))
    assert result.returncode == 0
    assert "argv: hello" in result.stdout
    assert result.argv == (str(fake_istool), "hello")
    assert result.duration > timedelta(0)


def test_run_captures_nonzero_without_raising(
    fake_istool: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_ISTOOL_EXIT_CODE", "3")
    monkeypatch.setenv("FAKE_ISTOOL_STDERR", "boom")
    runner = Runner()
    result = runner.run((str(fake_istool),))
    assert result.returncode == 3
    assert "boom" in result.stderr


def test_run_missing_executable_raises_not_found(tmp_path: Path) -> None:
    runner = Runner()
    with pytest.raises(IstoolExecutableNotFoundError):
        runner.run((str(tmp_path / "nope.sh"),))
