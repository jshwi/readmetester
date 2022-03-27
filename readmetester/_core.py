"""
readmetester._core
==================
"""
# pylint: disable=consider-using-f-string
from __future__ import annotations

import os as _os
import sys as _sys
import typing as _t
from argparse import ArgumentParser as _ArgumentParser
from collections.abc import MutableSequence as _MutableSequence
from io import StringIO as _StringIO
from pathlib import Path as _Path

from object_colors import Color as _Color
from pygments import highlight as _highlight
from pygments.formatters.terminal256 import (
    Terminal256Formatter as _Terminal256Formatter,
)

# noinspection PyUnresolvedReferences
from pygments.lexers.python import PythonLexer as _PythonLexer
from pyproject_parser import PyProject as _PyProject

from ._version import __version__

color = _Color()
color.populate("fore")
for foreground in color.colors:
    getattr(color, foreground).populate("effect")

CHECK = color.green.get("\u2713")
CROSS = color.red.get("\u2716")


_os.environ["PYCHARM_HOSTED"] = "True"


class Parser(_ArgumentParser):
    """Parse commandline arguments and hold the file path."""

    def __init__(self) -> None:
        readme = _Path.cwd() / "README.rst"
        if len(_sys.argv) < 2 and readme.is_file():
            _sys.argv.append(str(readme))

        super().__init__(prog=color.cyan.get("readmetester"))
        self._version_request()
        self.add_argument(
            "file", metavar="README.rst", nargs="?", action="store"
        )
        self._args = self.parse_args()
        self.file = _Path(self._args.file)

    def _version_request(self) -> None:
        # print version if `--version` is passed to commandline
        version = "--version"
        self.add_argument(
            version, action="store_true", help="show version and exit"
        )
        # the only exception for not providing positional args
        if _sys.argv[1] == version:
            print(__version__)
            _sys.exit(0)


class _Seq(_MutableSequence):
    """Replicate subclassing of ``list`` objects."""

    def __init__(self) -> None:
        self._list: _t.List[_t.Any] = []

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._list}>"

    def __str__(self) -> str:
        return str(self._list)

    def __len__(self) -> int:
        return len(self._list)

    def __delitem__(self, key: _t.Any) -> None:
        self._list.__delitem__(key)

    def __setitem__(self, index: _t.Any, value: _t.Any) -> None:
        self._list.__setitem__(index, value)

    def __getitem__(self, index: _t.Any) -> _t.Any:
        return self._list.__getitem__(index)

    def insert(self, index: int, value: str) -> None:
        """Insert values into ``_list`` object.

        :param index: ``list`` index to insert ``value``.
        :param value: Value to insert into list.
        """
        self._list.insert(index, value)


class Code(str):
    """Represents a line of code."""

    _START_CODE = ">>> "
    _CONTINUATION = "... "
    _QUOTE = "'"
    _START_BLOCK = ".. code-block:: python"
    _END_DOT = ".."
    _LINEBREAK = ""
    _CODE_BREAK = ">>>"
    _COLON = ":"
    _COMMA = ","
    _PARENS = "(", ")"
    _CURLY = "{", "}"
    _SQUARE = "[", "]"
    _OPEN_BRACKETS = _PARENS[0], _CURLY[0], _SQUARE[0]
    _CLOSE_BRACKETS = _PARENS[1], _CURLY[1], _SQUARE[1]
    _BRACKETS = _OPEN_BRACKETS, _CLOSE_BRACKETS
    _STARTERS = _START_CODE, _CONTINUATION
    _CONTINUED = _COLON, _COMMA

    def __new__(cls, item: str) -> Code:
        return super().__new__(cls, item.lstrip())

    def iscode(self) -> bool:
        """Test if this is a line of code.

        :return: Line of code, True or False.
        """
        return any(self.startswith(i) for i in self._STARTERS)

    def iscodebreak(self) -> bool:
        """Test if this is a code linebreak.

        :return: Line of code, True or False.
        """
        return self == self._CODE_BREAK

    def isquoted(self) -> bool:
        """Test if this is quoted.

        :return: Quoted, True or False.
        """
        return self.startswith(self._QUOTE) and self.endswith(self._QUOTE)

    def dequote(self) -> Code:
        """Return a ``Code`` instance without leading and ending quotes.

        :return: Instance of ``Code`` without quotes.
        """
        return Code(self[1:-1:]) if self.isquoted() else self

    def isstartblock(self) -> bool:
        """Test that this starts a block.

        :return: This starts a block, True or False.
        """
        return self == self._START_BLOCK

    def isenddot(self) -> bool:
        """Test that this is a dot to end a block.

        :return: This an ending dot, True or False.
        """
        return self == self._END_DOT

    def islinebreak(self) -> bool:
        """Test that this is a linebreak.

        :return: This an linebreak, True or False.
        """
        return self == self._LINEBREAK

    def demark(self) -> Code:
        """Return ``Code`` object without starter symbols.

        :return: Instance of ``Code`` without starters.
        """
        return Code(self[4:])

    def splitlines(self, keepends: bool = False) -> _t.List[str]:
        return [Code(i) for i in super().splitlines(keepends)]

    def iscontinued(self) -> bool:
        """Test that this is a continuation of code.

        :return: This an continuation, True or False.
        """
        return any(self.endswith(i) for i in self._CONTINUED)

    def getcloser(self) -> Code:
        """Return closing mark.

        :return: Instance of closing ``Code``.
        """
        return Code(self[-1])

    def isopenbracket(self) -> bool:
        """Test that this is an opening bracket.

        :return: This an opening bracket, True or False.
        """
        return self in self._OPEN_BRACKETS

    def isbracket(self) -> bool:
        """Test that this is a bracket.

        :return: This a bracket, True or False.
        """
        return self.isopenbracket() or self.isclosebracket()

    def isclosebracket(self) -> bool:
        """Test that this is a closing bracket.

        :return: This a closing bracket, True or False.
        """
        return self in self._CLOSE_BRACKETS

    def getbracket(self) -> _t.Optional[Code]:
        """Get bracket, if this is one.

        :return: Bracket if it exists else None.
        """
        closer = self.getcloser()
        return closer if closer.isbracket() else None

    def getopbracket(self) -> _t.Optional[Code]:
        """Get opposing bracket.

        :return: Instance of opposite bracket ``Code``, else None
        """
        try:
            return Code(
                self._BRACKETS[int(self.isopenbracket())][
                    self._BRACKETS[int(self.isclosebracket())].index(self)
                ]
            )
        except ValueError:
            return None


class OpenReadme:
    """Read README into a list of ``Code`` objects.

    :param path: Path to README.
    """

    def __init__(self, path: _Path) -> None:
        self._fin = open(  # pylint: disable=consider-using-with
            path, encoding="utf-8"
        )

    def __enter__(self) -> OpenReadme:
        return self

    def __exit__(
        self, exc_type: _t.Any, exc_val: _t.Any, exc_tb: _t.Any
    ) -> None:
        self._fin.close()

    def read(self) -> Code:
        """Read file contents into ``Code`` object.

        :return: ``Code`` object.
        """
        return Code(self._fin.read())


class Readme(_Seq):
    """Behaves like``list`` object.

    Read and hold ines from README file.
    """

    def __init__(self) -> None:
        super().__init__()
        self._end_line_switch = False

    def _partition_blocks(
        self, elements: _t.Iterator[_t.Any], block: bool = False
    ) -> _t.Iterator[_t.Any]:
        for element in elements:
            if element.isstartblock():
                yield list(self._partition_blocks(elements, block=True))

            elif block:
                if element.isenddot():

                    # block completed with two dots and not a second
                    # newline
                    self._end_line_switch = False
                    return

                if element.islinebreak():

                    # block completed with second newline
                    if self._end_line_switch:
                        self._end_line_switch = False
                        return

                    # block commenced with first newline
                    self._end_line_switch = True
                    continue

                yield element

    def load(self, path: _Path) -> None:
        """Read README to object.

        :param path: Path to README.
        """
        with OpenReadme(path) as fin:
            self.extend(fin.read().splitlines())

    def extend(self, values: _t.Iterable[_t.Any]) -> None:
        super().extend(self._partition_blocks(iter(values)))


class Actual(_Seq):
    """``list`` for normalizing string entries for variable results."""

    @staticmethod
    def _normalize_hex(value: str) -> str:
        # remove hex substrings returned from classes
        string = []
        for substring in value.split(" "):
            if substring != "object":
                if substring.startswith("0x"):
                    find_index = substring.find(">")
                    substring = substring[find_index:]

                string.append(substring)

        return " ".join(string)

    def insert(self, index: int, value: str) -> None:
        super().insert(index, self._normalize_hex(value))

    def getindex(self, index: int) -> _t.Optional[str]:
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
    def _highlight(value: str) -> str:
        style = "default"
        pyproject_file = _Path.cwd() / "pyproject.toml"
        if pyproject_file.is_file():
            pyproject_obj = _PyProject.load(pyproject_file)
            style = pyproject_obj.tool.get("readmetester", {}).get(
                "style", style
            )

        return _highlight(
            value, _PythonLexer(), _Terminal256Formatter(style=style)
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

    def append_command(self, value: str) -> None:
        """Append value prefixed with a dotpoint.

        :param value: ``str`` to append with dotpoint.
        """
        self.append(f". {self._highlight(value).strip()}")

    def extend(self, values: _t.Iterable[_t.Any]) -> None:
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
    """t.List containing expected code."""

    def append(self, value: str) -> None:
        """Append ``str`` and retain escape codes.

        :param value: Value to append to self.
        """
        super().append(bytes(value, "utf-8").decode("unicode_escape"))


class CatchStdout(_StringIO):
    """Context action for capturing stdout."""

    def __init__(self) -> None:
        super().__init__()
        self._freeze = _sys.stdout
        _sys.stdout = self

    def getparts(self) -> _t.Optional[_t.List[str]]:
        """Get list of stdout if captured, else None.

        :return: List object if stdout captured, else None.
        """
        value = super().getvalue()
        return (
            None if value == "" else [i for i in value.split("\n") if i != ""]
        )

    def __enter__(self) -> CatchStdout:
        return self

    def __exit__(
        self, exc_type: _t.Any, exc_val: _t.Any, exc_tb: _t.Any
    ) -> None:
        _sys.stdout = self._freeze


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

    def catch_output(self, value: _t.List[str]) -> None:
        """Capture command output and add to actual and total objects.

        :param value: Output from executed command.
        """
        self._actual.extend(value)
        self._total.extend(value)

    def display(self) -> None:
        """Consume the total command, actual, and expected result."""
        print(self.total.get())
        print(self._SUCCESS_MESSAGE)

    def getpair(
        self, index: int
    ) -> _t.Tuple[_t.Optional[str], _t.Optional[str]]:
        """Get actual and expected results.

        :param index: Index of each respectively.
        :return: A tuple of actual and expected results.
        """
        return self.actual.getindex(index), self.expected.getindex(index)


class Parenthesis(_Seq):
    """Record opening and closing parenthesis."""

    def eval(self, cmd: Code) -> None:
        """Evaluate string to set bracket status to open or closed.

        :param cmd: Python code.
        """
        bracket = cmd.getbracket()
        if bracket is not None:
            if bracket.isopenbracket():
                self.append(bracket)

            elif (
                bracket.isclosebracket()
                and self
                and self[-1] == bracket.getopbracket()
            ):
                self.pop()

    def command_ready(self, cmd: Code) -> bool:
        """Boolean value for whether command is ready to execute or not.

        :param cmd: Python code.
        """
        return not cmd.iscontinued() and not self


class Command(_Seq):
    """Compile commands then execute the Python code."""

    def __str__(self) -> str:
        return "".join(self)

    def ascode(self) -> Code:
        """Return command as code.

        :return: Instance of ``Code`` object.
        """
        return Code(str(self))

    def append(self, value: Code) -> None:
        """Append line from statement minus the ">>> "  and "... ".

        :param value: Line of Python code.
        """
        super().append(value.demark())

    def exec(self) -> None:
        """Execute compiled Python command."""
        exec(str(self), globals())  # pylint: disable=exec-used
        self.clear()
