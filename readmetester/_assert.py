"""
readmetester._assert
====================
"""
import sys as _sys
import typing as _t
from pathlib import Path as _Path
from warnings import warn as _warn

import restructuredtext_lint as _restructuredtext_lint

from . import exceptions as _exceptions
from ._core import CROSS as _CROSS
from ._core import Readme as _Readme


def equality(
    actual: _t.Optional[str], expected: _t.Optional[str], code_block: str
) -> None:
    """Test actual value against expected value.

    :param actual: Actual command output.
    :param expected: Expected command output.
    :param code_block: code-block x of all code-blocks.
    :raises OutputDocumentError: If assertion fails.
    """
    if actual is not None and expected is not None:
        try:
            assert actual == expected

        except AssertionError as err:
            print(_CROSS)
            raise _exceptions.OutputNotEqualError(
                code_block, actual, expected
            ) from err


def actual_expected(
    actual: _t.Optional[str], expected: _t.Optional[str], code_block: str
) -> None:
    """Test equality of actual and expected results.

    :param actual: Actual output produced.
    :param expected: Expected output to be produced.
    :param code_block: code-block x of all code-blocks.
    :raise OutputExpectedError: Raises if output expected but none was
        produced.
    :raise OutputNotExpectedError: Raises if output was not expected
        and output was produced.
    """
    if actual is None and expected is not None:
        raise _exceptions.OutputExpectedError(code_block, expected)

    if actual is not None and expected is None:
        raise _exceptions.OutputNotExpectedError(code_block, actual)


def syntax(path: _Path) -> None:
    """Check README for valid syntax.

    :param path: Path to README.
    """
    errors = _restructuredtext_lint.lint_file(str(path))
    if errors:
        raise _exceptions.SyntaxDocumentError(errors[0].full_message)


def code_blocks(readme: _Readme) -> None:
    """If no code blocks in file, warn.

    :param readme. Instantiated ``Readme`` object.
    """
    if not readme:
        _warn("file contains no code-blocks", RuntimeWarning)
        _sys.exit(0)
