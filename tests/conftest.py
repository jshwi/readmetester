"""
tests.conftest
==============
"""
import os
import sys

import pytest

import readmetester

from . import NoColorCapsys


@pytest.fixture(name="patch_argv")
def fixture_patch_argv(monkeypatch):
    """Function for passing mock commandline arguments to ``sys.argv``.

    :param monkeypatch: ``pytest`` fixture for mocking attributes.
    :return:            Function for using this fixture.
    """

    def _argv(*args):
        args = [__name__, *args]
        monkeypatch.setattr(sys, "argv", args)

    return _argv


@pytest.fixture(name="main")
def fixture_main(patch_argv):
    """Function for passing mock ``readmetester.main`` commandline arguments
    to package's main function.

    :param patch_argv:  Set args with ``sys.argv``
    :return:            Function for using this fixture.
    """

    def _main(*args):
        """Run readmetester.main with custom args."""
        patch_argv(*args)
        readmetester.main()

    return _main


@pytest.fixture(name="make_readme")
def fixture_make_readme(tmpdir):
    """Make temp README.

    :param tmpdir:  Fixture for creating and returning temporary
                    directory.
    """

    def _make_readme(template):
        readme = os.path.join(tmpdir, "README.rst")
        with open(readme, "w") as fout:
            fout.write(template)

        return readme

    return _make_readme


@pytest.fixture(name="nocolorcapsys")
def fixture_nocolorcapsys(capsys):
    """Instantiate capsys with the regex method

    :param capsys: ``pytest`` fixture for capturing output stream.
    :return:        Instantiated ``NoColorCapsys`` object for capturing
                    output stream and sanitizing the string if it
                    contains ANSI escape codes.
    """
    return NoColorCapsys(capsys)
