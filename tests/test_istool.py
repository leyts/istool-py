import shlex
from pathlib import Path

import pytest

from istool_py._config import IstoolConfig
from istool_py._exceptions import IstoolInvalidArchive, IstoolWarning
from istool_py._istool import Istool
from istool_py.commands import ExportCommand, ImportCommand, RawCommand


def _exe(tmp_path: Path) -> Path:
    p = tmp_path / "istool.sh"
    p.write_text("#!/usr/bin/env bash\nexit 0\n")
    return p


def test_construct_with_kwargs(tmp_path: Path) -> None:
    istool = Istool(executable=_exe(tmp_path))
    assert isinstance(istool.export(archive=Path("a.isx")), ExportCommand)


def test_construct_with_config(tmp_path: Path) -> None:
    cfg = IstoolConfig(executable=_exe(tmp_path))
    istool = Istool(config=cfg)
    assert isinstance(istool.export(archive=Path("a.isx")), ExportCommand)


def test_export_passes_mode(tmp_path: Path) -> None:
    istool = Istool(executable=_exe(tmp_path))
    cmd = istool.export(archive=Path("a.isx"), mode="update")
    assert cmd.mode == "update"


def test_export_passes_extra_args(tmp_path: Path) -> None:
    istool = Istool(executable=_exe(tmp_path))
    cmd = istool.export(archive=Path("a.isx"), extra_args=["-x"])
    assert cmd.extra_args == ("-x",)


def test_import_factory(tmp_path: Path) -> None:
    istool = Istool(executable=_exe(tmp_path))
    cmd = istool.import_(
        archive=Path("a.isx"),
        preview=True,
        replace_existing=True,
    )
    assert isinstance(cmd, ImportCommand)
    assert cmd.preview is True
    assert cmd.replace_existing is True


def test_raw_factory(tmp_path: Path) -> None:
    istool = Istool(executable=_exe(tmp_path))
    cmd = istool.raw("glossary", "export")
    assert isinstance(cmd, RawCommand)
    assert cmd.argv == ("glossary", "export")


def test_end_to_end_export_argv_matches_expected_shape(
    fake_istool: Path,
) -> None:
    istool = Istool(executable=fake_istool, verbose=True)
    cmd = istool.export(archive=Path("pkg.isx")).datastage(
        paths=["/DS1/Jobs/Daily/*"],
        include_dependent=True,
    )
    result = cmd.run()
    echoed = result.stdout.splitlines()[0].removeprefix("argv: ")
    parsed = shlex.split(echoed)
    assert parsed == [
        "export",
        "-verbose",
        "-archive",
        "pkg.isx",
        "-datastage",
        "-includedependent '/DS1/Jobs/Daily/*'",
    ]


def test_end_to_end_raises_on_nonzero_exit(
    fake_istool: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_ISTOOL_EXIT_CODE", "5")
    istool = Istool(executable=fake_istool)
    cmd = istool.export(archive=Path("x.isx")).datastage(paths=["/A"])
    with pytest.raises(IstoolInvalidArchive):
        cmd.run()


def test_end_to_end_warning_is_catchable_then_result_accessible(
    fake_istool: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_ISTOOL_EXIT_CODE", "1")
    istool = Istool(executable=fake_istool)
    cmd = istool.export(archive=Path("x.isx")).datastage(paths=["/A"])
    with pytest.raises(IstoolWarning) as excinfo:
        cmd.run()
    assert excinfo.value.result.returncode == 1
