"""
readmetester
============
"""
from itertools import zip_longest as _zip_longest

from . import _assert
from ._core import CatchStdout as _CatchStdout
from ._core import Command as _Command
from ._core import Holder as _Holder
from ._core import Parenthesis as _Parenthesis
from ._core import Parser as _Parser
from ._core import Readme as _Readme


def _process(lines: str, holder: _Holder) -> None:
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
    command = _Command()
    parenthesis = _Parenthesis()
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
                with _CatchStdout() as stdout:
                    command.exec()

                value = stdout.getvalue()
                if value is not None:
                    holder.catch_output(value)
        elif line != ">>>":

            # remove quotes from documented ``str`` output
            if line.startswith("'") and line.endswith("'"):
                line = line[1:-1:]

            holder.expected.append(line)


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
    parser = _Parser()
    holder = _Holder()
    _assert.syntax(parser.file)
    readme = _Readme(parser.file)
    _assert.code_blocks(readme)
    for count, element in enumerate(readme):
        code_block = f"code-block {count + 1}"
        holder.total.append_header(code_block)
        _process(element, holder)
        for position, _ in enumerate(
            _zip_longest(holder.actual, holder.expected)
        ):
            actual, expected = holder.getpair(position)
            _assert.actual_expected(actual, expected, code_block)
            _assert.equality(actual, expected, code_block)

    holder.display()
