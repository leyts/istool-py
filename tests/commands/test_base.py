import shlex
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

import pytest

from istool_py._config import IstoolConfig
from istool_py._exceptions import CommandValidationError, IstoolWarning
from istool_py._runner import CommandResult, Runner
from istool_py.commands._base import Command

if TYPE_CHECKING:
    from pathlib import Path


def _exe(tmp_path: Path) -> Path:
    exe = tmp_path / "istool.sh"
    exe.write_text("#!/usr/bin/env bash\nexit 0\n")
    return exe


@dataclass(frozen=True, slots=True)
class _Probe(Command):
    _command_parts: ClassVar[tuple[str, ...]] = ("probe",)
    flag: bool = False

    def _command_args(self) -> tuple[str, ...]:
        return ("-flag",) if self.flag else ()


def test_to_args_composes_executable_parts_auth_output_and_extra(
    tmp_path: Path,
) -> None:
    cfg = IstoolConfig(executable=_exe(tmp_path), verbose=True)
    cmd = _Probe(
        _config=cfg,
        _runner=Runner(),
        extra_args=("-x",),
        flag=True,
    )
    assert cmd.to_args() == (
        str(cfg.executable),
        "probe",
        "-verbose",
        "-flag",
        "-x",
    )


def test_render_round_trips_through_shlex(tmp_path: Path) -> None:
    cmd = _Probe(
        _config=IstoolConfig(executable=_exe(tmp_path)),
        _runner=Runner(),
        flag=True,
    )
    assert shlex.split(cmd.render()) == list(cmd.to_args())


def test_validate_called_before_rendering(tmp_path: Path) -> None:
    @dataclass(frozen=True, slots=True)
    class _Picky(Command):
        command_parts: ClassVar[tuple[str, ...]] = ("picky",)

        def validate(self) -> None:
            msg = "nope"
            raise CommandValidationError(msg)

        def _command_args(self) -> tuple[str, ...]:
            return ()

    cmd = _Picky(
        _config=IstoolConfig(executable=_exe(tmp_path)), _runner=Runner()
    )
    with pytest.raises(CommandValidationError):
        cmd.to_args()


def test_run_raises_typed_error_on_nonzero(
    fake_istool: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = IstoolConfig(executable=fake_istool)
    monkeypatch.setenv("FAKE_ISTOOL_EXIT_CODE", "1")
    cmd = _Probe(_config=cfg, _runner=Runner())
    with pytest.raises(IstoolWarning) as excinfo:
        cmd.run()
    assert excinfo.value.result.returncode == 1


def test_run_returns_result_on_success(fake_istool: Path) -> None:
    cfg = IstoolConfig(executable=fake_istool)
    cmd = _Probe(_config=cfg, _runner=Runner())
    result = cmd.run()
    assert isinstance(result, CommandResult)
    assert result.returncode == 0
