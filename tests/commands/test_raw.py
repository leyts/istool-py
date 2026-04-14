from typing import TYPE_CHECKING

from istool_py._config import IstoolConfig
from istool_py._runner import Runner
from istool_py.commands import RawCommand

if TYPE_CHECKING:
    from pathlib import Path


def _cfg(tmp_path: Path) -> IstoolConfig:
    exe = tmp_path / "istool.sh"
    exe.write_text("#!/usr/bin/env bash\nexit 0\n")
    return IstoolConfig(executable=exe, verbose=True)


def test_raw_inherits_auth_and_output_flags(tmp_path: Path) -> None:
    cmd = RawCommand(
        _config=_cfg(tmp_path),
        _runner=Runner(),
        argv=("glossary", "export", "-archive", "g.isx"),
    )
    args = cmd.to_args()
    assert "-verbose" in args
    assert args[-4:] == ("glossary", "export", "-archive", "g.isx")


def test_raw_extra_args_trail(tmp_path: Path) -> None:
    cmd = RawCommand(
        _config=_cfg(tmp_path),
        _runner=Runner(),
        argv=("query", "-list"),
        extra_args=("-verbose",),
    )
    assert cmd.to_args()[-1] == "-verbose"
