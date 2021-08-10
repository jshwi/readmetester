"""
readmetester
============
"""
import os

from .src import (
    CROSS,
    ArgumentParser,
    CatchStdout,
    Holder,
    Mapping,
    Readme,
    Seq,
    color,
    command,
    parenthesis,
)

__version__ = "1.0.1"

os.environ["PYCHARM_HOSTED"] = "True"


class OutputDocumentError(Exception):
    """Base for errors resulting from incorrectly documented code."""


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
    for line in lines:

        # any lines beginning with ``>>> `` or ``... `` are
        # considered commands
        if any([line.startswith(i) for i in (">>> ", "... ")]):
            holder["total"].append_command(line)
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
                    holder["actual"].extend(value)
                    holder["total"].extend(value)
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
    parser = ArgumentParser()
    holder = Holder()
    readme = Readme(parser.args.file)
    if readme:
        for count, element in enumerate(readme):
            code_block = f"code-block {count + 1}"
            holder["total"].append_header(code_block)
            process(element, holder)
            if not holder["expected"] and holder["actual"]:
                raise OutputDocumentError(
                    "command returned output but no output is expected"
                )

            for position, _ in enumerate(holder["actual"]):
                run_assertion(holder, position, code_block)

            for line in holder["total"]:
                print(line)

            holder.clear()

        print(f"\n{80 * '-'}\n{color.green.bold.get('Success!')}")
    else:
        print("File contains no code-blocks")
