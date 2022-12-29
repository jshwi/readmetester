"""
tests._test
===========
"""

# pylint: disable=protected-access
from pathlib import Path

import pytest
import templatest

import readmetester

# noinspection PyUnresolvedReferences
from . import templates  # noqa pylint: disable=unused-import
from . import (
    EnterDir,
    MakeReadmeType,
    MockMainType,
    NoColorCapsys,
    PatchArgvType,
)


@pytest.mark.parametrize(
    "_,template,expected",
    templatest.templates.registered.filtergroup("err"),
    ids=templatest.templates.registered.filtergroup("err").getids(),
)
def test_returns(
    nocolorcapsys: NoColorCapsys,
    main: MockMainType,
    make_readme: MakeReadmeType,
    _: str,
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
    "_,template,expected",
    templatest.templates.registered.getgroup("err"),
    ids=templatest.templates.registered.getgroup("err").getids(),
)
def test_output_document_error(
    main: MockMainType,
    make_readme: MakeReadmeType,
    _: str,
    template: str,
    expected: str,
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
    with pytest.raises(readmetester.exceptions.DocumentError) as err:
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
    readme = make_readme(templatest.templates.registered[0][1])
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


def test_getopbracket_not_bracket() -> None:
    """Test ``getopbracket`` returns None when no brackets."""
    # noinspection PyUnresolvedReferences
    code = readmetester._core.Code("code")
    assert code.getopbracket() is None


def test_readme_no_exist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, patch_argv: PatchArgvType
) -> None:
    """Test that ``IndexError`` is not raised by version request.

    Instead, ``restructuredtext_lint`` should raise
    ``FileNotFoundError``.

    :param tmp_path: Fixture for creating and returning temporary
        directory.
    :param monkeypatch: Mock patch environment and attributes.
    :param patch_argv: Set args with ``sys.argv``. Clears pytest
        arguments for this test.
    """
    patch_argv()
    monkeypatch.setattr("readmetester._core._Path.cwd", lambda: tmp_path)
    with pytest.raises(FileNotFoundError) as err:
        readmetester.main()

    assert (
        str(err.value)
        == f"[Errno 2] No such file or directory: '{Path.cwd() /'README.rst'}'"
    )
