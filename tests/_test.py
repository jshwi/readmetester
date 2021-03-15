"""
tests._test
===========
"""

import pytest

import readmetester
from . import strings


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
    """Test standard README and return values."""
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
    """Test error when no output documentation provided."""
    readme = make_readme(template)
    with pytest.raises(readmetester.OutputDocumentError) as err:
        main(readme)

    assert str(err.value) == expected


def test_seq():
    """Get coverage on ``Seq`` abstract methods."""
    seq = readmetester.Seq()
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
    mapping = readmetester.Mapping()
    mapping_repr = repr(mapping)
    assert mapping_repr == "<Mapping {}>"
    mapping_str = str(mapping)
    assert mapping_str == "{}"
