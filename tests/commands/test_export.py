import shlex
from dataclasses import replace
from pathlib import Path

import pytest

from istool_py._config import IstoolConfig
from istool_py._exceptions import CommandValidationError
from istool_py._runner import Runner
from istool_py.commands import (
    ArchiveMode,
    DataStageExportSelection,
    ExportCommand,
)


def _exe(tmp_path: Path) -> Path:
    p = tmp_path / "istool.sh"
    p.write_text("#!/usr/bin/env bash\nexit 0\n")
    return p


def _new(
    tmp_path: Path,
    *,
    mode: ArchiveMode = "overwrite",
    extra_args: tuple[str, ...] = (),
) -> ExportCommand:
    return ExportCommand(
        _config=IstoolConfig(executable=_exe(tmp_path)),
        _runner=Runner(),
        archive=Path("pkg.isx"),
        mode=mode,
        extra_args=extra_args,
    )


def test_overwrite_mode_omits_updatearchive(tmp_path: Path) -> None:
    cmd = _new(tmp_path).datastage(paths=["/DS1/Jobs/*"])
    args = cmd.to_args()
    assert "-archive" in args
    assert "pkg.isx" in args
    assert "-updatearchive" not in args


def test_update_mode_emits_updatearchive(tmp_path: Path) -> None:
    cmd = _new(tmp_path, mode="update").datastage(paths=["/DS1/Jobs/*"])
    assert "-updatearchive" in cmd.to_args()


def test_datastage_nested_token_is_single_argv_entry(tmp_path: Path) -> None:
    cmd = _new(tmp_path).datastage(
        paths=["/DS1/Jobs/A", "/DS1/Jobs/B"],
        include_dependent=True,
    )
    args = cmd.to_args()
    idx = args.index("-datastage")
    inner = args[idx + 1]
    decoded = shlex.split(inner)
    assert decoded == ["-includedependent", "/DS1/Jobs/A", "/DS1/Jobs/B"]


def test_datastage_path_with_whitespace_is_double_quoted(
    tmp_path: Path,
) -> None:
    cmd = _new(tmp_path).datastage(paths=["/DEV/Jobs/User Folders/job"])
    idx = cmd.to_args().index("-datastage")
    inner = cmd.to_args()[idx + 1]
    assert inner == '"/DEV/Jobs/User Folders/job"'


def test_datastage_path_with_embedded_double_quote_is_escaped(
    tmp_path: Path,
) -> None:
    cmd = _new(tmp_path).datastage(paths=['/DEV/Jobs/x"folder/job'])
    idx = cmd.to_args().index("-datastage")
    inner = cmd.to_args()[idx + 1]
    assert inner == '"/DEV/Jobs/x\\"folder/job"'


def test_render_matches_istool_quoting_for_path_with_whitespace(
    tmp_path: Path,
) -> None:
    cmd = _new(tmp_path).datastage(
        paths=["/DEV/Jobs/User Folders/user/JSON_test"]
    )
    rendered = cmd.render()
    assert (
        " -datastage '\"/DEV/Jobs/User Folders/user/JSON_test\"'" in rendered
    )


def test_no_design_flag_emitted_when_include_design_false(
    tmp_path: Path,
) -> None:
    cmd = _new(tmp_path).datastage(paths=["/DS1/Jobs/*"], include_design=False)
    idx = cmd.to_args().index("-datastage")
    inner = shlex.split(cmd.to_args()[idx + 1])
    assert "-nodesign" in inner


def test_validate_requires_at_least_one_selection(tmp_path: Path) -> None:
    cmd = _new(tmp_path)
    with pytest.raises(CommandValidationError):
        cmd.to_args()


def test_datastage_rejects_empty_paths(tmp_path: Path) -> None:
    cmd = _new(tmp_path).datastage(paths=["   "])
    with pytest.raises(CommandValidationError):
        cmd.to_args()


def test_multiple_datastage_calls_accumulate(tmp_path: Path) -> None:
    cmd = _new(tmp_path).datastage(paths=["/A"]).datastage(paths=["/B"])
    args = cmd.to_args()
    assert args.count("-datastage") == 2


def test_builder_is_immutable(tmp_path: Path) -> None:
    a = _new(tmp_path)
    b = a.datastage(paths=["/A"])
    assert a is not b
    assert a._selections == ()
    assert len(b._selections) == 1


def test_selection_validates_standalone() -> None:
    sel = DataStageExportSelection(paths=())
    with pytest.raises(CommandValidationError):
        sel.validate()


def test_extra_args_trail_after_structured(tmp_path: Path) -> None:
    cmd = replace(
        _new(tmp_path).datastage(paths=["/A"]),
        extra_args=("-preview",),
    )
    args = cmd.to_args()
    assert args[-1] == "-preview"
