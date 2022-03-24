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
from collections.abc import MutableMapping as _MutableMapping
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

color = _Color()
color.populate("fore")
for foreground in color.colors:
    getattr(color, foreground).populate("effect")

_CHECK = color.green.get("\u2713")
CROSS = color.red.get("\u2716")


_os.environ["PYCHARM_HOSTED"] = "True"


class Parser(_ArgumentParser):
    """Parse commandline arguments and hold the file path.."""

    def __init__(self) -> None:
        readme = _Path.cwd() / "README.rst"
        if len(_sys.argv) < 2 and readme.is_file():
            _sys.argv.append(str(readme))

        super().__init__()
        self.add_argument("file", action="store")
        self._args = self.parse_args()
        self.file = _Path(self._args.file)


class Seq(_MutableSequence):
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

        :param index:   ``list`` index to insert ``value``.
        :param value:   Value to insert into list.
        """
        self._list.insert(index, value)


class Readme(Seq):  # pylint: disable=too-few-public-methods
    """Behaves like``list`` object.

    Read and hold ines from README file.
    """

    def __init__(self, filepath: _Path) -> None:
        super().__init__()
        self._end_line_switch = False
        with open(filepath, encoding="utf-8") as fin:
            self.extend(
                self._partition_blocks(
                    iter([i.lstrip() for i in fin.read().splitlines()])
                )
            )

    def _partition_blocks(
        self, elements: _t.Iterator[_t.Any], block: bool = False
    ) -> _t.Iterator[_t.Any]:
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


class _Actual(Seq):  # pylint: disable=too-few-public-methods
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


class _Total(_Actual):
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
        super().append("\n".join([f"{_CHECK} {i}" for i in values]))


class _Expected(_Actual):
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


class Mapping(_MutableMapping):
    """Inherit to replicate subclassing of ``dict`` objects."""

    def __init__(self) -> None:
        self._dict: _t.Dict[_t.Any, _t.Any] = {}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._dict}>"

    def __str__(self) -> str:
        return str(self._dict)

    def __getitem__(self, key: _t.Any) -> _t.Any:
        return self._dict[key]

    def __setitem__(self, key: _t.Any, value: _t.Any) -> _t.Any:
        self._dict[key] = value

    def __delitem__(self, key: _t.Any) -> _t.Any:
        del self._dict[key]

    def __iter__(self) -> _t.Iterator[_t.Any]:
        return iter(self._dict)

    def __len__(self) -> int:
        """Not implemented."""


class Holder(Mapping):  # pylint: disable=too-few-public-methods
    """Object for holding README data."""

    def __init__(self) -> None:
        super().__init__()
        self._init_object()

    def _init_object(self) -> None:
        self.update(
            {"actual": _Actual(), "expected": _Expected(), "total": _Total()}
        )

    def clear(self) -> None:
        """Clear contents but maintain initial key-value pairs."""
        super().clear()
        self._init_object()


class _Parenthesis(Seq):
    """Record opening and closing parenthesis."""

    _brackets = {"open": ("(", "{", "["), "close": (")", "}", "]")}

    def _reverse(self, key: str, bracket: str) -> str:
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


class _Command(Seq):
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


command = _Command()
parenthesis = _Parenthesis()
