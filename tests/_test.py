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
    strings.TEMPLATES,
    ids=[
        "simple",
        "multiple",
        "object",
        "hanging-tuple",
        "hanging-list",
        "hanging-dict",
        "nested-hanging",
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
    "template,expected",
    strings.ERRORS,
    ids=["no-output-expected", "actual-ne-expected"],
)
def test_output_document_error(main, make_readme, template, expected):
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
    with pytest.raises(readmetester.exceptions.OutputDocumentError) as err:
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


def test_no_code_block_found(make_readme, main, capsys):
    """Test appropriate stdout is produced when no code-block has been
    parsed from file.

    :param make_readme: Create a README.rst file in the temp dir
                        containing the provided ``str``. Empty README
                        in this case.
    :param main:        Mock the main function for the package. Provide
                        test arguments to ``sys.argv`` as function
                        parameters.
    :param capsys:      ``pytest`` fixture for capturing output stream.
    """
    readme = make_readme("")
    main(readme)
    output = capsys.readouterr()
    assert output.out.strip() == "File contains no code-blocks"


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


def test_mapping():
    """Get coverage on ``Mapping`` abstract methods."""
    # noinspection PyUnresolvedReferences
    mapping = readmetester._core.Mapping()
    mapping_repr = repr(mapping)
    assert mapping_repr == "<Mapping {}>"
    mapping_str = str(mapping)
    assert mapping_str == "{}"
