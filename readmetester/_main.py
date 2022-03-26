"""
readmetester
============
"""
import typing as _t
from itertools import zip_longest as _zip_longest

from . import _assert
from ._core import CatchStdout as _CatchStdout
from ._core import Code as _Code
from ._core import Command as _Command
from ._core import Holder as _Holder
from ._core import Parenthesis as _Parenthesis
from ._core import Parser as _Parser
from ._core import Readme as _Readme


def _process(lines: _t.List[_Code], holder: _Holder) -> None:
    """Populate items to their allocated ``list`` object.

    First split data by documented commands and documented command
    output.

        * Within the command section collect the header with ``total``
          and collect the  results from executed commands with ``total``
          and ``actual``.

        * Collect all non-command documentation as command output as
          this process is guaranteed to only run within a code-block.

    :param lines: Lines from README file.
    :param holder: Holding object.
    """
    command = _Command()
    parenthesis = _Parenthesis()
    for line in lines:

        # any lines beginning with ``>>> `` or ``... `` are considered
        # commands
        if line.iscode():
            holder.total.append_command(line)
            command.append(line)

            # if command ends with a colon it is a statement with a
            # continuation
            # append the continuation to execute as one command
            parenthesis.eval(_Code(str(command)))
            if parenthesis.command_ready(_Code(str(command))):
                with _CatchStdout() as stdout:
                    command.exec()

                value = stdout.getparts()
                if value is not None:
                    holder.catch_output(value)

        elif not line.iscodebreak():

            # remove quotes from documented `str` output
            holder.expected.append(line.dequote())


def main() -> None:
    """Parse README from commandline argument.

    Initialize ``Holder`` to contain expected, actual, and total values.

    Enumerate over parsed ``Readme`` and populate the three containers.

        1. Expected ``list`` from the README file directly
        2. Actual from the actual command output
        3. Total with a combination of both plus code-block headings

    Run assertions on the actual and expected commands and print output
    from the total ``list``.

    Clear and initialize base key-values on each iteration.

    If no errors are raised then print that the README is a success and
    there are no errors in testing.

    :raises OutputDocumentError: Raise if the expected ``list`` contains
        nothing even though command output was captured.
    """
    parser = _Parser()
    holder = _Holder()
    _assert.syntax(parser.file)
    readme = _Readme(parser.file)
    _assert.code_blocks(readme)
    for count, element in enumerate(readme, 1):
        code_block = f"code-block {count}"
        holder.total.append_header(code_block)
        _process(element, holder)
        for position, _ in enumerate(
            _zip_longest(holder.actual, holder.expected)
        ):
            actual, expected = holder.getpair(position)
            _assert.actual_expected(actual, expected, code_block)
            _assert.equality(actual, expected, code_block)

    holder.display()
