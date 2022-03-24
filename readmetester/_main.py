"""
readmetester
============
"""
from . import exceptions as _exceptions
from ._core import CROSS as _CROSS
from ._core import CatchStdout as _CatchStdout
from ._core import Holder as _Holder
from ._core import Parser as _Parser
from ._core import Readme as _Readme
from ._core import color as _color
from ._core import command as _command
from ._core import parenthesis as _parenthesis


def process(lines: str, holder: _Holder) -> None:
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
    for line in lines:

        # any lines beginning with ``>>> `` or ``... `` are
        # considered commands
        if any(line.startswith(i) for i in (">>> ", "... ")):
            holder["total"].append_command(line)
            _command.append(line)

            # if command ends with a colon if is a statement with a
            # continuation
            # append the continuation to execute as one command
            _parenthesis.eval(str(_command))
            if _parenthesis.command_ready(str(_command)):
                with _CatchStdout() as stdout:
                    _command.exec()

                value = stdout.getparts()
                if value is not None:
                    holder["actual"].extend(value)
                    holder["total"].extend(value)
        elif line != ">>>":

            # remove quotes from documented ``str`` output
            if line.startswith("'") and line.endswith("'"):
                line = line[1:-1:]

            holder["expected"].append(line)


def run_assertion(holder: _Holder, position: int, code_block: str) -> None:
    """Test actual value against expected value.

    :param holder:                  Object containing expected, actual,
                                    and total values.
    :param position:                Index of expected and actual lists.
    :param code_block:              code-block x of all code-blocks.
    :raises OutputDocumentError:    If assertion fails.
    """
    actual = holder["actual"][position]
    expected = holder["expected"][position]
    try:
        assert actual == expected

    except AssertionError as err:
        print(_CROSS)
        raise _exceptions.OutputDocumentError(
            f"{code_block}: {expected} != {actual}"
        ) from err


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
    readme = _Readme(parser.file)
    if readme:
        for count, element in enumerate(readme):
            code_block = f"code-block {count + 1}"
            holder["total"].append_header(code_block)
            process(element, holder)
            if not holder["expected"] and holder["actual"]:
                raise _exceptions.OutputDocumentError(
                    "command returned output but no output is expected"
                )

            for position, _ in enumerate(holder["actual"]):
                run_assertion(holder, position, code_block)

            for line in holder["total"]:
                print(line)

            holder.clear()

        print(f"\n{80 * '-'}\n{_color.green.bold.get('Success!')}")
    else:
        print("File contains no code-blocks")
