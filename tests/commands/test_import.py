import shlex
from pathlib import Path

import pytest

from istool_py._config import IstoolConfig
from istool_py._exceptions import CommandValidationError
from istool_py._runner import Runner
from istool_py.commands import ImportCommand


def _exe(tmp_path: Path) -> Path:
    p = tmp_path / "istool.sh"
    p.write_text("#!/usr/bin/env bash\nexit 0\n")
    return p


def _new(
    tmp_path: Path,
    *,
    preview: bool = False,
    replace_existing: bool = False,
) -> ImportCommand:
    return ImportCommand(
        _config=IstoolConfig(executable=_exe(tmp_path)),
        _runner=Runner(),
        archive=Path("pkg.isx"),
        preview=preview,
        replace_existing=replace_existing,
    )


def test_defaults_emit_neither_preview_nor_replace(tmp_path: Path) -> None:
    cmd = _new(tmp_path).datastage(project="proj")
    args = cmd.to_args()
    assert "-preview" not in args
    assert "-replace" not in args


def test_preview_emits_flag(tmp_path: Path) -> None:
    cmd = _new(tmp_path, preview=True).datastage(project="proj")
    assert "-preview" in cmd.to_args()


def test_replace_existing_emits_flag(tmp_path: Path) -> None:
    cmd = _new(tmp_path, replace_existing=True).datastage(project="proj")
    assert "-replace" in cmd.to_args()


def test_datastage_emits_project_only_when_no_server(tmp_path: Path) -> None:
    cmd = _new(tmp_path).datastage(project="proj")
    idx = cmd.to_args().index("-datastage")
    inner = shlex.split(cmd.to_args()[idx + 1])
    assert inner == ["proj"]


def test_datastage_emits_server_slash_project_when_server_set(
    tmp_path: Path,
) -> None:
    cmd = _new(tmp_path).datastage(project="proj", server="srv")
    idx = cmd.to_args().index("-datastage")
    inner = shlex.split(cmd.to_args()[idx + 1])
    assert inner == ["srv/proj"]


def test_datastage_emits_nodesign_when_include_design_false(
    tmp_path: Path,
) -> None:
    cmd = _new(tmp_path).datastage(project="proj", include_design=False)
    idx = cmd.to_args().index("-datastage")
    inner = shlex.split(cmd.to_args()[idx + 1])
    assert inner == ["-nodesign", "proj"]


def test_validate_requires_selection(tmp_path: Path) -> None:
    with pytest.raises(CommandValidationError):
        _new(tmp_path).to_args()
