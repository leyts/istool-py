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
    abort_after_errors: int | None = None,
) -> ImportCommand:
    return ImportCommand(
        _config=IstoolConfig(executable=_exe(tmp_path)),
        _runner=Runner(),
        archive=Path("pkg.isx"),
        preview=preview,
        replace_existing=replace_existing,
        abort_after_errors=abort_after_errors,
    )


def test_defaults_emit_neither_preview_nor_replace(tmp_path: Path) -> None:
    cmd = _new(tmp_path).datastage(server="srv", project="proj")
    args = cmd.to_args()
    assert "-preview" not in args
    assert "-replace" not in args


def test_preview_emits_flag(tmp_path: Path) -> None:
    cmd = _new(tmp_path, preview=True).datastage(server="srv", project="proj")
    assert "-preview" in cmd.to_args()


def test_replace_existing_emits_flag(tmp_path: Path) -> None:
    cmd = _new(tmp_path, replace_existing=True).datastage(
        server="srv", project="proj"
    )
    assert "-replace" in cmd.to_args()


def test_datastage_emits_server_slash_project(tmp_path: Path) -> None:
    cmd = _new(tmp_path).datastage(server="srv", project="proj")
    idx = cmd.to_args().index("-datastage")
    inner = shlex.split(cmd.to_args()[idx + 1])
    assert inner == ["srv/proj"]


def test_datastage_emits_nodesign_when_design_objects_false(
    tmp_path: Path,
) -> None:
    cmd = _new(tmp_path).datastage(
        server="srv", project="proj", design_objects=False
    )
    idx = cmd.to_args().index("-datastage")
    inner = shlex.split(cmd.to_args()[idx + 1])
    assert inner == ["-nodesign", "srv/proj"]


def test_validate_requires_selection(tmp_path: Path) -> None:
    with pytest.raises(CommandValidationError):
        _new(tmp_path).to_args()


def test_abort_after_errors_omitted_by_default(tmp_path: Path) -> None:
    cmd = _new(tmp_path).datastage(server="srv", project="proj")
    assert "-abortAfter" not in cmd.to_args()


def test_abort_after_errors_emits_flag_and_value(tmp_path: Path) -> None:
    cmd = _new(tmp_path, abort_after_errors=5).datastage(
        server="srv", project="proj"
    )
    args = cmd.to_args()
    idx = args.index("-abortAfter")
    assert args[idx + 1] == "5"


def test_abort_after_errors_emitted_before_selections(tmp_path: Path) -> None:
    cmd = _new(tmp_path, abort_after_errors=3).datastage(
        server="srv", project="proj"
    )
    args = cmd.to_args()
    assert args.index("-abortAfter") < args.index("-datastage")


@pytest.mark.parametrize("value", [0, -1])
def test_abort_after_errors_rejects_non_positive(
    tmp_path: Path, value: int
) -> None:
    cmd = _new(tmp_path, abort_after_errors=value).datastage(
        server="srv", project="proj"
    )
    with pytest.raises(CommandValidationError):
        cmd.to_args()
