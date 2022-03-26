"""
tests._test
===========
"""
# pylint: disable=protected-access
import pytest

import readmetester

from . import EnterDir, strings


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
def test_returns(nocolorcapsys, main, make_readme, template, expected):
    """Test standard README and return values.

    :param nocolorcapsys:   ``capsys`` without ANSI color codes.
    :param main:            Mock the main function for the package.
                            Provide test arguments to ``sys.argv`` as
                            function parameters.
    :param make_readme:     Create a README.rst file in the temp dir
                            containing the provided ``str``.
    :param template:        ``str`` to write to the test README.
    :param expected:        Expected stdout.
    """
    readme = make_readme(template)
    main(readme)
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
def test_output_document_error(main, make_readme, template, expected, error):
    """Test error when no output documentation provided.

    :param main:            Mock the main function for the package.
                            Provide test arguments to ``sys.argv`` as
                            function parameters.
    :param make_readme:     Create a README.rst file in the temp dir
                            containing the provided ``str``.
    :param template:        ``str`` to write to the test README.
    :param expected:        Expected output.
    """
    readme = make_readme(template)
    with pytest.raises(error) as err:
        main(readme)

    assert str(err.value) == expected


def test_fallback_readme(tmpdir, make_readme, patch_argv):
    """Test fallback README.rst is used if no args are provided and a
    README.rst file is present in the current working dir.

    :param tmpdir:      Fixture for creating and returning temporary
                        directory.
    :param make_readme: Create a README.rst file in the temp dir
                        containing the provided ``str``.
    :param patch_argv:  Set args with ``sys.argv``. Clears pytest
                        arguments for this test.
    """
    patch_argv()
    readme = make_readme("")
    with EnterDir(tmpdir):
        parser = readmetester._main.ArgumentParser()

    assert parser.args.file == readme


def test_no_code_block_found(make_readme, main):
    """Test appropriate stdout is produced when no code-block has been
    parsed from file.

    :param make_readme: Create a README.rst file in the temp dir
                        containing the provided ``str``. Empty README
                        in this case.
    :param main:        Mock the main function for the package. Provide
                        test arguments to ``sys.argv`` as function
                        parameters.
    """
    readme = make_readme("")
    with pytest.raises(SystemExit):
        with pytest.warns(
            RuntimeWarning, match="file contains no code-blocks"
        ):
            main(str(readme))


def test_seq():
    """Get coverage on ``Seq`` abstract methods."""
    # noinspection PyUnresolvedReferences
    seq = readmetester._core.Seq()
    seq.append("key")
    assert seq[0] == "key"
    seq[0] = "value"
    assert seq[0] == "value"
    del seq[0]
    assert not seq
    seq_repr = repr(seq)
    assert seq_repr == "<Seq []>"
    seq_str = str(seq)
    assert seq_str == "[]"


def test_no_pyproject_toml(tmpdir, main, make_readme, patch_argv):
    """Test no error is raised when no pyproject.toml in project.

    No need to run assertion. Test passes if ``FileNotFoundError`` not
    raised.

    :param tmpdir:      Fixture for creating and returning temporary
                        directory.
    :param make_readme: Create a README.rst file in the temp dir
                        containing the provided ``str``.
    :param patch_argv:  Set args with ``sys.argv``. Clears pytest
                        arguments for this test.
    """
    patch_argv()
    readme = make_readme(strings.Simple().template)
    with EnterDir(tmpdir):
        main(readme)


def test_print_version(monkeypatch, main, nocolorcapsys) -> None:
    """Test printing of version on commandline.

    :param monkeypatch:     Mock patch environment and attributes.
    :param main:            Patch package entry point.
    :param nocolorcapsys:   Capture system output while stripping ANSI
                            color codes.
    """
    monkeypatch.setattr("readmetester._core.__version__", "1.0.0")
    with pytest.raises(SystemExit):
        main("--version")

    out = nocolorcapsys.stdout().strip()
    assert out == "1.0.0"
