"""
readmetester.src
================
"""
from __future__ import annotations

import argparse
import collections
import io
import os
import sys
from typing import Any, Dict, Iterator, List, Union

import object_colors
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.python import PythonLexer

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

        super().__init__()
        self.add_argument("file", action="store")
        self.args = self.parse_args()


class Seq(collections.MutableSequence):
    """Replicate subclassing of ``list`` objects."""

    def __init__(self) -> None:
        self._list: List[Any] = list()

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
        with open(filepath) as fin:
            self.extend(
                self._partition_blocks(
                    iter(
                        [
                            i.lstrip()
                            for i in fin.read().splitlines()
                            if i != ""
                        ]
                    )
                )
            )

    def _partition_blocks(
        self, elements: Iterator[Any], block: bool = False
    ) -> Iterator[Any]:
        for element in elements:
            if element == ".. code-block:: python":
                yield [*self._partition_blocks(elements, block=True)]

            elif block:
                if element.endswith(".."):
                    return

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


class Total(Actual):
    """List containing total output to display."""

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
        value = highlight(
            value, PythonLexer(), Terminal256Formatter(style="monokai")
        )
        self.append(f". {value.strip()}")

    def extend(self, values: Any) -> None:
        """Append value prefixed with a check symbol.

        :param values: ``str`` to append with check symbol.
        """
        super().append("\n".join([f"{CHECK} {i}" for i in values]))


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


class Mapping(collections.MutableMapping):
    """Inherit to replicate subclassing of ``dict`` objects."""

    def __init__(self) -> None:
        self._dict: Dict[Any, Any] = dict()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._dict}>"

    def __str__(self) -> str:
        return str(self._dict)

    def __getitem__(self, key: Any) -> Any:
        return self._dict[key]

    def __setitem__(self, key: Any, value: Any) -> Any:
        self._dict[key] = value

    def __delitem__(self, key: Any) -> Any:
        del self._dict[key]

    def __iter__(self) -> Iterator[Any]:
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
            {
                "actual": Actual(),
                "expected": Expected(),
                "total": Total(),
            }
        )

    def clear(self) -> None:
        """Clear contents but maintain initial key-value pairs."""
        super().clear()
        self._init_object()


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
        """Append line from statement minus the ``>>> `` and ``... ``.

        :param value: Line of Python code.
        """
        super().append(value[4:])

    def exec(self) -> None:
        """Execute compiled Python command."""
        exec(str(self), globals())  # pylint: disable=exec-used
        self.clear()


command = Command()
parenthesis = Parenthesis()
