"""
readmetester.exceptions
=======================
"""


class DocumentError(Exception):
    """Base for error for all documentation."""


class OutputDocumentError(DocumentError):
    """Base for errors resulting from incorrectly documented code.

    :param code_block:  Code block that error is raised for.
    :param message:     Error message.
    """

    def __init__(self, code_block: str, message: str) -> None:
        super().__init__(f"{code_block}: {message}")


class SyntaxDocumentError(DocumentError):
    """Base for errors resulting from invalid document syntax."""


class OutputNotExpectedError(OutputDocumentError):
    """Output was provided, but no output is expected.

    :param code_block:  Code block that error is raised for.
    :param actual:      Actual output produced.
    """

    def __init__(self, code_block: str, actual: str) -> None:
        super().__init__(
            code_block, f"command returned `{actual}` which is not expected"
        )


class OutputExpectedError(OutputDocumentError):
    """Output was not provided, but output is expected.

    :param code_block:  Code block that error is raised for.
    :param expected:    Expected output.
    """

    def __init__(self, code_block: str, expected: str) -> None:
        super().__init__(
            code_block,
            f"command did not return `{expected}` which is expected",
        )


class OutputNotEqualError(OutputDocumentError):
    """Actual code not equal to expected code.

    :param code_block:  Code block that error is raised for.
    :param actual:      Actual output produced.
    :param expected:    Expected output.
    """

    def __init__(self, code_block: str, actual: str, expected: str) -> None:
        super().__init__(code_block, f"{expected} != {actual}")
