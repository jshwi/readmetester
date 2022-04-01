"""
readmetester._core
==================
"""
# pylint: disable=consider-using-f-string
from __future__ import annotations

import argparse
import collections
import io
import os
import sys
from pathlib import Path
from typing import Any, Iterator, List, Optional, Tuple, Union

import object_colors
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter

# noinspection PyUnresolvedReferences
from pygments.lexers.python import PythonLexer
from pyproject_parser import PyProject

from ._version import __version__

color = object_colors.Color()
color.populate("fore")
for foreground in color.colors:
    getattr(color, foreground).populate("effect")

CHECK = color.green.get("\u2713")
CROSS = color.red.get("\u2716")


os.environ["PYCHARM_HOSTED"] = "True"


class ArgumentParser(argparse.ArgumentParser):
    """Parse commandline arguments and hold the file path.."""

    def __init__(self) -> None:
        readme = os.path.join(os.getcwd(), "README.rst")
        if len(sys.argv) < 2 and os.path.isfile(readme):
            sys.argv.append(readme)

        super().__init__(prog=color.cyan.get("readmetester"))
        self._version_request()
        self.add_argument(
            "file", metavar="README.rst", nargs="?", action="store"
        )
        self.args = self.parse_args()

    def _version_request(self) -> None:
        # print version if `--version` is passed to commandline
        version = "--version"
        self.add_argument(
            version, action="store_true", help="show version and exit"
        )
        # the only exception for not providing positional args
        if sys.argv[1] == version:
            print(__version__)
            sys.exit(0)


class Seq(collections.MutableSequence):
    """Replicate subclassing of ``list`` objects."""

    def __init__(self) -> None:
        self._list: List[Any] = []

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._list}>"

    def __str__(self) -> str:
        return str(self._list)

    def __len__(self) -> int:
        return len(self._list)

    def __delitem__(self, key: Any) -> None:
        self._list.__delitem__(key)

    def __setitem__(self, index: Any, value: Any) -> None:
        self._list.__setitem__(index, value)

    def __getitem__(self, index: Any) -> Any:
        return self._list.__getitem__(index)

    def insert(self, index: int, value: str) -> None:
        """Insert values into ``_list`` object.

        :param index:   ``list`` index to insert ``value``.
        :param value:   Value to insert into list.
        """
        self._list.insert(index, value)


class Readme(Seq):  # pylint: disable=too-few-public-methods
    """Behaves like``list`` object.

    Read and hold ines from README file.
    """

    def __init__(self, filepath: Union[bytes, str, os.PathLike]) -> None:
        super().__init__()
        self._end_line_switch = False
        with open(filepath, encoding="utf-8") as fin:
            self.extend(
                self._partition_blocks(
                    iter([i.lstrip() for i in fin.read().splitlines()])
                )
            )

    def _partition_blocks(
        self, elements: Iterator[Any], block: bool = False
    ) -> Iterator[Any]:
        for element in elements:
            if element == ".. code-block:: python":
                yield [*self._partition_blocks(elements, block=True)]

            elif block:
                if element == "..":
                    self._end_line_switch = False
                    return

                if element == "":
                    if self._end_line_switch:
                        self._end_line_switch = False
                        return

                    self._end_line_switch = True
                    continue

                yield element


class Actual(Seq):  # pylint: disable=too-few-public-methods
    """``list`` for normalizing string entries for variable results."""

    def insert(self, index: int, value: str) -> None:
        """Remove hex substrings returned from classes.

        :param index:   ``list`` index to insert ``value``.
        :param value:   Value to insert into list.
        """
        string = []
        for substring in value.split(" "):
            substring = substring.strip()
            if substring != "object":
                if substring.startswith("0x"):
                    find_index = substring.find(">")
                    substring = substring[find_index:]

                string.append(substring)

        super().insert(index, " ".join(string))

    def getindex(self, index: int) -> Optional[str]:
        """Get value by index if it exists, else None.

        :param index: Index to get.
        :return: Value if it exists, else None.
        """
        try:
            return self[index]
        except IndexError:
            return None


class Total(Actual):
    """List containing total output to display."""

    @staticmethod
    def _highlight(value):
        style = "default"
        pyproject_file = Path.cwd() / "pyproject.toml"
        if pyproject_file.is_file():
            pyproject_obj = PyProject.load(pyproject_file)
            style = pyproject_obj.tool.get("readmetester", {}).get(
                "style", style
            )

        return highlight(
            value, PythonLexer(), Terminal256Formatter(style=style)
        )

    def append_header(self, value: str) -> None:
        """Append ``str`` to total as stylized header.

        :param value: Header ``str``.
        """
        self.append(
            "{}\n{}".format(
                color.cyan.underline.get(80 * " "),
                color.cyan.underline.get(value + (80 - len(value)) * " "),
            )
        )

    def append_command(self, value: Any) -> None:
        """Append value prefixed with a dotpoint.

        :param value: ``str`` to append with dotpoint.
        """
        self.append(f". {self._highlight(value).strip()}")

    def extend(self, values: Any) -> None:
        """Append value prefixed with a check symbol.

        :param values: ``str`` to append with check symbol.
        """
        super().append("\n".join([f"{CHECK} {i}" for i in values]))

    def get(self) -> str:
        """Get the final total result.

        :return: Final total result.
        """
        return "\n".join(self)


class Expected(Actual):
    """List containing expected code."""

    def append(self, value: str) -> None:
        """Append ``str`` and retain escape codes.

        :param value: Value to append to self.
        """
        super().append(bytes(value, "utf-8").decode("unicode_escape"))


class CatchStdout(io.StringIO):
    """Context action for capturing stdout."""

    def __init__(self) -> None:
        super().__init__()
        self._freeze = sys.stdout
        sys.stdout = self

    def getvalue(self) -> Any:
        value = super().getvalue()
        return (
            None if value == "" else [i for i in value.split("\n") if i != ""]
        )

    def __enter__(self) -> CatchStdout:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        sys.stdout = self._freeze


class Holder:
    """Object for holding README data."""

    _SUCCESS_MESSAGE = f"\n{80 * '-'}\n{color.green.bold.get('Success!')}"

    def __init__(self) -> None:
        super().__init__()
        self._actual = Actual()
        self._expected = Expected()
        self._total = Total()

    @property
    def actual(self) -> Actual:
        """``list`` containing actual code."""
        return self._actual

    @property
    def expected(self) -> Expected:
        """``list`` containing expected code."""
        return self._expected

    @property
    def total(self) -> Total:
        """``list`` containing total to display."""
        return self._total

    def catch_output(self, value: List[str]) -> None:
        """Capture command output and add to actual and total objects.

        :param value: Output from executed command.
        """
        self._actual.extend(value)
        self._total.extend(value)

    def display(self) -> None:
        """Consume the total command, actual, and expected result."""
        print(self.total.get())
        print(self._SUCCESS_MESSAGE)

    def getpair(self, index: int) -> Tuple[Optional[str], Optional[str]]:
        """Get actual and expected results.

        :param index: Index of each respectively.
        :return: A tuple of actual and expected results.
        """
        return self.actual.getindex(index), self.expected.getindex(index)


class Parenthesis(Seq):
    """Record opening and closing parenthesis."""

    _brackets = {"open": ("(", "{", "["), "close": (")", "}", "]")}

    def _reverse(self, key: Any, bracket: str) -> str:
        other = "open" if key == "close" else "close"
        return self._brackets[other][self._brackets[key].index(bracket)]

    def _current(self) -> str:
        return self[-1]

    def eval(self, cmd: str) -> None:
        """Evaluate string to set bracket status to open or closed.

        :param cmd: Python code.
        """
        bracket = cmd[-1]
        if bracket in self._brackets["open"]:
            self.append(bracket)

        elif (
            bracket in self._brackets["close"]
            and self
            and self._current() == self._reverse("close", bracket)
        ):
            self.pop()

    def command_ready(self, cmd: str) -> bool:
        """Boolean value for whether command is ready to execute or not.

        :param cmd: Python code.
        """
        return not any(cmd.endswith(i) for i in (":", ",")) and not self


class Command(Seq):
    """Compile commands then execute the Python code."""

    def __str__(self) -> str:
        return "".join(self)

    def append(self, value: str) -> None:
        """Append line from statement minus the ">>> "  and "... ".

        :param value: Line of Python code.
        """
        super().append(value[4:])

    def exec(self) -> None:
        """Execute compiled Python command."""
        exec(str(self), globals())  # pylint: disable=exec-used
        self.clear()
