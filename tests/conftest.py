"""
tests.conftest
==============
"""
import sys
from pathlib import Path

import pytest

import readmetester

from . import MakeReadmeType, MockMainType, NoColorCapsys, PatchArgvType


@pytest.fixture(name="patch_argv")
def fixture_patch_argv(monkeypatch: pytest.MonkeyPatch) -> PatchArgvType:
    """Function for passing mock commandline arguments to ``sys.argv``.

    :param monkeypatch: ``pytest`` fixture for mocking attributes.
    :return: Function for using this fixture.
    """

    def _argv(*args: str) -> None:
        _args = [__name__, *args]
        monkeypatch.setattr(sys, "argv", _args)

    return _argv


@pytest.fixture(name="main")
def fixture_main(patch_argv: PatchArgvType) -> MockMainType:
    """Pass mock ``readmetester.main`` commandline args to main.

    :param patch_argv: Set args with ``sys.argv``
    :return: Function for using this fixture.
    """

    def _main(*args: str) -> None:
        """Run readmetester.main with custom args."""
        patch_argv(*args)
        readmetester.main()

    return _main


@pytest.fixture(name="make_readme")
def fixture_make_readme(tmp_path: Path) -> MakeReadmeType:
    """Make temp README.

    :param tmp_path: Fixture for creating and returning temporary
        directory.
    :return: Function for using this fixture.
    """

    def _make_readme(template: str) -> Path:
        readme = tmp_path / "README.rst"
        readme.write_text(template, encoding="utf-8")
        return readme

    return _make_readme


@pytest.fixture(name="nocolorcapsys")
def fixture_nocolorcapsys(capsys: pytest.CaptureFixture) -> NoColorCapsys:
    """Instantiate capsys with the regex method.

    :param capsys: ``pytest`` fixture for capturing output stream.
    :return: Instantiated ``NoColorCapsys`` object for capturing output
        stream and sanitizing the string if it contains ANSI escape
        codes.
    """
    return NoColorCapsys(capsys)
