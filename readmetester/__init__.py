"""
readmetester
============
"""
import os
from typing import List

from .src import (
    ArgumentParser,
    CROSS,
    CatchStdout,
    Holder,
    Mapping,
    Parenthesis,
    Readme,
    Seq,
    color,
)

__version__ = "1.0.0"

os.environ["PYCHARM_HOSTED"] = "True"


class OutputDocumentError(Exception):
    """Base for errors resulting from incorrectly documented code."""


def fmt_header(header: str, fore: str) -> str:
    """Return ``str`` as stylized header.

    :param header:  Header ``str``.
    :param fore:    Foreground color for ``object_colors.Color``
    :return:        Stylized ``str`` object.
    """
    color_obj = getattr(color, fore)
    top = color_obj.underline.get(80 * " ")
    bottom = color_obj.underline.get(header + (80 - len(header)) * " ")
    return top + "\n" + bottom


def run_command(command: str) -> List[str]:
    """Execute collected commands and return the command output.

    :param command: Command collected from README file.
    :return:        ``list`` of command output.
    """
    with CatchStdout() as stdout:
        exec(command, globals())  # pylint: disable=exec-used

    return stdout.getvalue()


def populate(lines: str, holder: Holder) -> None:
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
    command = ""
    parenthesis = Parenthesis()
    for line in lines:

        # any lines beginning with ``>>> `` or ``... `` are
        # considered commands
        if any([line.startswith(i) for i in (">>> ", "... ")]):
            holder["total"].append_command(line)
            command += line[4:]

            # if command ends with a colon if is a statement with a
            # continuation
            # append the continuation to execute as one command
            parenthesis.eval(command)
            if parenthesis.command_ready(command):
                value = run_command(command)
                if value is not None:
                    holder["actual"].extend(value)
                    holder["total"].extend(value)

                command = ""
        else:

            # remove quotes from documented ``str`` output
            if line.startswith("'") and line.endswith("'"):
                line = line[1:-1:]

            holder["expected"].append(line)


def run_assertion(holder: Holder, position: int, code_block: str) -> None:
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
        print(CROSS)
        raise OutputDocumentError(
            "{}: {} != {}".format(code_block, expected, actual)
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
    parser = ArgumentParser()
    readme = Readme(parser.args.file)
    holder = Holder()
    for count, element in enumerate(readme):
        code_block = "code-block {}".format(count + 1)
        holder["total"].append(fmt_header(code_block, "cyan"))
        populate(element, holder)
        if not holder["expected"] and holder["actual"]:
            raise OutputDocumentError(
                "command returned output but no output is expected"
            )

        for position, _ in enumerate(holder["actual"]):
            run_assertion(holder, position, code_block)

        for line in holder["total"]:
            print(line)

        holder.clear()

    print(fmt_header("Success!", "green"))
