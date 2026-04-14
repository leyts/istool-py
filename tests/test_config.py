from typing import TYPE_CHECKING

import pytest

from istool_py._config import IstoolConfig
from istool_py._exceptions import CommandValidationError

if TYPE_CHECKING:
    from pathlib import Path


def _exe(tmp_path: Path) -> Path:
    p = tmp_path / "istool.sh"
    p.write_text("#!/usr/bin/env bash\nexit 0\n")
    return p


def test_minimal_config(tmp_path: Path) -> None:
    cfg = IstoolConfig(executable=_exe(tmp_path))
    assert cfg.to_auth_args() == ()
    assert cfg.to_output_args() == ()


def test_authfile_renders_single_flag(tmp_path: Path) -> None:
    auth = tmp_path / "auth"
    auth.write_text("")
    cfg = IstoolConfig(executable=_exe(tmp_path), authfile=auth)
    assert cfg.to_auth_args() == ("-authfile", str(auth))


def test_credential_triple_renders(tmp_path: Path) -> None:
    cfg = IstoolConfig(
        executable=_exe(tmp_path),
        domain="d.example",
        username="alice",
        password="s3cret",
    )
    assert cfg.to_auth_args() == (
        "-domain",
        "d.example",
        "-username",
        "alice",
        "-password",
        "s3cret",
    )


def test_verbose_and_silent_are_mutually_exclusive(tmp_path: Path) -> None:
    with pytest.raises(CommandValidationError):
        IstoolConfig(executable=_exe(tmp_path), verbose=True, silent=True)


def test_authfile_conflicts_with_credential_triple(tmp_path: Path) -> None:
    with pytest.raises(CommandValidationError):
        IstoolConfig(
            executable=_exe(tmp_path),
            authfile=tmp_path / "auth",
            domain="d",
            username="u",
            password="p",
        )


def test_partial_credentials_emit_only_set_flags(tmp_path: Path) -> None:
    cfg = IstoolConfig(
        executable=_exe(tmp_path),
        domain="d.example",
        username="alice",
    )
    assert cfg.to_auth_args() == ("-domain", "d.example", "-username", "alice")


def test_username_only_renders(tmp_path: Path) -> None:
    cfg = IstoolConfig(executable=_exe(tmp_path), username="alice")
    assert cfg.to_auth_args() == ("-username", "alice")


def test_password_only_renders(tmp_path: Path) -> None:
    cfg = IstoolConfig(executable=_exe(tmp_path), password="s3cret")
    assert cfg.to_auth_args() == ("-password", "s3cret")


def test_password_not_in_repr(tmp_path: Path) -> None:
    cfg = IstoolConfig(
        executable=_exe(tmp_path),
        domain="d",
        username="u",
        password="s3cret",
    )
    assert "s3cret" not in repr(cfg)


def test_verbose_output_args(tmp_path: Path) -> None:
    cfg = IstoolConfig(executable=_exe(tmp_path), verbose=True)
    assert cfg.to_output_args() == ("-verbose",)


def test_silent_output_args(tmp_path: Path) -> None:
    cfg = IstoolConfig(executable=_exe(tmp_path), silent=True)
    assert cfg.to_output_args() == ("-silent",)


def test_executable_must_exist(tmp_path: Path) -> None:
    with pytest.raises(
        CommandValidationError, match="executable does not exist"
    ):
        IstoolConfig(executable=tmp_path / "nope.sh")


def test_authfile_must_exist_when_provided(tmp_path: Path) -> None:
    with pytest.raises(
        CommandValidationError, match="authfile does not exist"
    ):
        IstoolConfig(
            executable=_exe(tmp_path),
            authfile=tmp_path / "missing-auth",
        )
