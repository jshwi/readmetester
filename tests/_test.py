"""
tests._test
===========
"""
import typing as t

# pylint: disable=protected-access
from pathlib import Path

import pytest

import readmetester

from . import (
    EnterDir,
    MakeReadmeType,
    MockMainType,
    NoColorCapsys,
    PatchArgvType,
    strings,
)


@pytest.mark.parametrize(
    "template,expected",
    strings.templates,
    ids=[
        "simple",
        "simple-line-break",
        "ending-dots",
        "no-ending-dots",
        "no-ending-dots-brackets",
        "no-ending-dots-brackets-no-match",
        "multiple",
        "object",
        "hanging-tuple",
        "hanging-list",
        "hanging-dict",
        "nested-hanging",
        "this-readme",
        "no-output-or-expected",
    ],
)
def test_returns(
    nocolorcapsys: NoColorCapsys,
    main: MockMainType,
    make_readme: MakeReadmeType,
    template: str,
    expected: str,
) -> None:
    """Test standard README and return values.

    :param nocolorcapsys: ``capsys`` without ANSI color codes.
    :param main: Mock the main function for the package. Provide test
        arguments to ``sys.argv`` as function parameters.
    :param make_readme: Create a README.rst file in the temp dir
        containing the provided ``str``.
    :param template: ``str`` to write to the test README.
    :param expected: Expected stdout.
    """
    readme = make_readme(template)
    main(str(readme))
    output = nocolorcapsys.stdout()
    assert output == expected


@pytest.mark.parametrize(
    "template,expected,error",
    strings.errors,
    ids=[
        "no-output-expected",
        "actual-ne-expected",
        "output-expected",
        "actual-ne-multi",
        "actual-ne-multi-block",
        "bad-syntax",
    ],
)
def test_output_document_error(
    main: MockMainType,
    make_readme: MakeReadmeType,
    template: str,
    expected: str,
    error: t.Type[readmetester.exceptions.DocumentError],
) -> None:
    """Test error when no output documentation provided.

    :param main: Mock the main function for the package. Provide test
        arguments to ``sys.argv`` as function parameters.
    :param make_readme: Create a README.rst file in the temp dir
        containing the provided ``str``.
    :param template: ``str`` to write to the test README.
    :param expected: Expected output.
    """
    readme = make_readme(template)
    with pytest.raises(error) as err:
        main(str(readme))

    assert str(err.value) == expected


def test_fallback_readme(
    tmp_path: Path, make_readme: MakeReadmeType, patch_argv: PatchArgvType
) -> None:
    """Test fallback README.rst.

    Test README is used if no args are provided and a README.rst file is
    present in the current working dir.

    :param tmp_path: Fixture for creating and returning temporary
        directory.
    :param make_readme: Create a README.rst file in the temp dir
        containing the provided ``str``.
    :param patch_argv:  Set args with ``sys.argv``. Clears pytest
        arguments for this test.
    """
    patch_argv()
    readme = make_readme("")
    with EnterDir(tmp_path):
        parser = readmetester._main._Parser()

    assert parser.file == readme


def test_no_code_block_found(
    make_readme: MakeReadmeType, main: MockMainType
) -> None:
    """Test message is produced when no code-block exists in file.

    :param make_readme: Create a README.rst file in the temp dir
        containing the provided ``str``. Empty README in this case.
    :param main: Mock the main function for the package. Provide test
        arguments to ``sys.argv`` as function parameters.
    """
    readme = make_readme("")
    with pytest.raises(SystemExit):
        with pytest.warns(
            RuntimeWarning, match="file contains no code-blocks"
        ):
            main(str(readme))


def test_seq() -> None:
    """Get coverage on ``Seq`` abstract methods."""
    # noinspection PyUnresolvedReferences
    seq = readmetester._core._Seq()
    seq.append("key")
    assert seq[0] == "key"
    seq[0] = "value"
    assert seq[0] == "value"
    del seq[0]
    assert not seq
    seq_repr = repr(seq)
    assert seq_repr == "<_Seq []>"
    seq_str = str(seq)
    assert seq_str == "[]"


def test_no_pyproject_toml(
    tmp_path: Path,
    main: MockMainType,
    make_readme: MakeReadmeType,
    patch_argv: PatchArgvType,
) -> None:
    """Test no error is raised when no pyproject.toml in project.

    No need to run assertion. Test passes if ``FileNotFoundError`` not
    raised.

    :param tmp_path: Fixture for creating and returning temporary
        directory.
    :param make_readme: Create a README.rst file in the temp dir
        containing the provided ``str``.
    :param patch_argv: Set args with ``sys.argv``. Clears pytest
        arguments for this test.
    """
    patch_argv()
    readme = make_readme(strings.Simple().template)
    with EnterDir(tmp_path):
        main(str(readme))


def test_print_version(
    monkeypatch: pytest.MonkeyPatch,
    main: MockMainType,
    nocolorcapsys: NoColorCapsys,
) -> None:
    """Test printing of version on commandline.

    :param monkeypatch: Mock patch environment and attributes.
    :param main: Patch package entry point.
    :param nocolorcapsys: Capture system output while stripping ANSI
        color codes.
    """
    monkeypatch.setattr("readmetester._core.__version__", "1.0.0")
    with pytest.raises(SystemExit):
        main("--version")

    out = nocolorcapsys.stdout().strip()
    assert out == "1.0.0"
