"""
readmetester._assert
====================
"""
import sys
from typing import Optional
from warnings import warn

import restructuredtext_lint

from . import exceptions
from ._core import CROSS, Readme


def equality(
    actual: Optional[str], expected: Optional[str], code_block: str
) -> None:
    """Test actual value against expected value.

    :param actual:                  Actual command output.
    :param expected:                Expected command output.
    :param code_block:              code-block x of all code-blocks.
    :raises OutputDocumentError:    If assertion fails.
    """
    if actual is not None and expected is not None:
        try:
            assert actual == expected

        except AssertionError as err:
            print(CROSS)
            raise exceptions.OutputNotEqualError(
                code_block, actual, expected
            ) from err


def actual_expected(
    actual: Optional[str], expected: Optional[str], code_block: str
) -> None:
    """Test equality of actual and expected results.

    :param actual:                  Actual output produced.
    :param expected:                Expected output to be produced.
    :param code_block:              code-block x of all code-blocks.
    :raise OutputExpectedError:     Raises if output expected but none
                                    was produced.
    :raise OutputNotExpectedError:  Raises if output was not expected
                                    and output was produced.
    """
    if actual is None and expected is not None:
        raise exceptions.OutputExpectedError(code_block, expected)

    if actual is not None and expected is None:
        raise exceptions.OutputNotExpectedError(code_block, actual)


def syntax(path: str) -> None:
    """Check README for valid syntax.

    :param path: Path to README.
    """
    errors = restructuredtext_lint.lint_file(str(path))
    if errors:
        raise exceptions.SyntaxDocumentError(errors[0].full_message)


def code_blocks(readme: Readme) -> None:
    """If no code blocks in file, warn.

    :param readme. Instantiated ``Readme`` object.
    """
    if not readme:
        warn("file contains no code-blocks", RuntimeWarning)
        sys.exit(0)
