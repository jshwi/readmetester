"""
readmetester
============
"""
import typing as _t
from pathlib import Path as _Path

from . import exceptions as _exceptions
from ._core import Holder as _Holder
from ._core import Parser as _Parser
from ._core import Readme as _Readme
from ._core import color as _color
from ._core import process as _process
from ._core import run_assertion as _run_assertion
from ._core import version_request as _version_request


def main(path: _t.Union[str, _Path] = _Path.cwd() / "README.rst") -> None:
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
    _version_request()
    parser = _Parser(path)
    holder = _Holder()
    readme = _Readme(parser.file)
    if readme:
        for count, element in enumerate(readme):
            code_block = f"code-block {count + 1}"
            holder["total"].append_header(code_block)
            _process(element, holder)
            if not holder["expected"] and holder["actual"]:
                raise _exceptions.OutputDocumentError(
                    "command returned output but no output is expected"
                )

            for position, _ in enumerate(holder["actual"]):
                _run_assertion(holder, position, code_block)

            for line in holder["total"]:
                print(line)

            holder.clear()

        print(f"\n{80 * '-'}\n{_color.green.bold.get('Success!')}")
    else:
        print("File contains no code-blocks")
