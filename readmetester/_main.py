"""
readmetester
============
"""
from itertools import zip_longest
from typing import Optional

from . import exceptions
from ._core import (
    CROSS,
    ArgumentParser,
    CatchStdout,
    Command,
    Holder,
    Parenthesis,
    Readme,
)


def process(lines: str, holder: Holder) -> None:
    """Populate items to their allocated ``list`` object. First split
    data by documented commands and documented command output.

        * Within the command section collect the header with ``total``
          and collect the  results from executed commands with ``total``
          and ``actual``.

        * Collect all non-command documentation as command output as
          this process is guaranteed to only run within a code-block.

    :param lines:   Lines from README file.
    :param holder:  Holding object.
    """
    command = Command()
    parenthesis = Parenthesis()
    for line in lines:

        # any lines beginning with ``>>> `` or ``... `` are
        # considered commands
        if any(line.startswith(i) for i in (">>> ", "... ")):
            holder.total.append_command(line)
            command.append(line)

            # if command ends with a colon if is a statement with a
            # continuation
            # append the continuation to execute as one command
            parenthesis.eval(str(command))
            if parenthesis.command_ready(str(command)):
                with CatchStdout() as stdout:
                    command.exec()

                value = stdout.getvalue()
                if value is not None:
                    holder.catch_output(value)
        elif line != ">>>":

            # remove quotes from documented ``str`` output
            if line.startswith("'") and line.endswith("'"):
                line = line[1:-1:]

            holder.expected.append(line)


def run_assertion(
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


def main() -> None:
    """Parse README from commandline argument and initialize ``Holder``
    to contain expected, actual, and total values. Enumerate over parsed
    ``Readme``. Populate the three containers. Expected ``list`` from
    the README file directly, actual from the actual command output and
    total with a combination of both plus code-block headings. Run
    assertions on the actual and expected commands. Print output from
    the total ``list``. Clear and initialize base key-values on each
    iteration. If no errors are raised then print that the README is a
    success and there are no errors in testing.

    :raises OutputDocumentError:    Raise if the expected ``list``
                                    contains nothing even though command
                                    output was captured.
    """
    parser = ArgumentParser()
    holder = Holder()
    readme = Readme(parser.args.file)
    if readme:
        for count, element in enumerate(readme):
            code_block = f"code-block {count + 1}"
            holder.total.append_header(code_block)
            process(element, holder)
            for position, _ in enumerate(
                zip_longest(holder.actual, holder.expected)
            ):
                actual, expected = holder.getpair(position)
                actual_expected(actual, expected, code_block)
                run_assertion(actual, expected, code_block)

        holder.display()
    else:
        print("File contains no code-blocks")
