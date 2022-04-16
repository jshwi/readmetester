"""
tests
=====
"""
from __future__ import annotations

import os
import re
import typing as t
from pathlib import Path

from pytest import CaptureFixture
from templatest import BaseTemplate, templates

from .strings import CHECK, SUCCESS

PatchArgvType = t.Callable[..., None]
MockMainType = t.Callable[..., None]
MakeReadmeType = t.Callable[[str], Path]


class NoColorCapsys:
    """Capsys but with a regex to remove ANSI escape codes.

    Class is preferable for this as we can instantiate the instance
    as a fixture that also contains the same attributes as capsys

    We can make sure that the class is instantiated without executing
    capsys immediately thus losing control of what stdout and stderr
    we are to capture

    :param capsys: ``pytest`` fixture for capturing output stream.
    """

    def __init__(self, capsys: CaptureFixture) -> None:
        self.capsys = capsys

    @staticmethod
    def regex(out: str) -> str:
        """Remove all ANSI escape codes.

        Prefer to test colored output this way as colored strings can
        be tricky and the effort in testing their validity really isn't
        worth it (also hard to read expected strings when they contain
        the codes).

        :param out: String to strip of ANSI escape codes
        :return: Same string but without ANSI codes
        """
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", out)

    def readouterr(self) -> t.List[str]:
        """Call as capsys ``readouterr`` and strip ANSI escape codes.

        :return: A tuple (just like the capsys) containing stdout in the
            first index and stderr in the second
        """
        return [
            "\n".join([i.strip() for i in s.split("\n")]).strip()
            for s in [self.regex(r) for r in self.capsys.readouterr()]
        ]

    def _readouterr_index(self, idx: int) -> str:
        return self.readouterr()[idx]

    def stdout(self) -> str:
        """Call this to return the stdout without referencing  indices.

        :return: Stdout.
        """
        return self._readouterr_index(0)


class EnterDir:
    """Change directory and back on exit.

    :param new_path: The directory to temporarily change to.
    """

    def __init__(self, new_path: Path) -> None:
        self.saved_path = Path.cwd()
        os.chdir(new_path.expanduser())

    def __enter__(self) -> EnterDir:
        return self

    def __exit__(self, exc_type: t.Any, exc_val: t.Any, exc_tb: t.Any) -> None:
        os.chdir(self.saved_path)


@templates.register
class _Simple(BaseTemplate):
    """Test for simple code-block."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> print("Hello, world!")
    'Hello, world!'

"""

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> print("Hello, world!")
{CHECK} Hello, world!
{SUCCESS}\
"""


@templates.register
class _SimpleLineBreak(BaseTemplate):
    """Test for simple code-block with line break."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> print("Hello, world!")
    >>>
    >>> print("Hello, world!")
    'Hello, world!'
    'Hello, world!'

"""

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> print("Hello, world!")
{CHECK} Hello, world!
. >>> print("Hello, world!")
{CHECK} Hello, world!
{SUCCESS}\
"""


@templates.register
class _EndingDots(BaseTemplate):
    """Test for simple code-block with no closing dots."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> print("Hello, world!")
    'Hello, world!'
..
.. code-block:: python

    >>> print("Hello, world!")
    'Hello, world!'
..
"""

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> print("Hello, world!")
{CHECK} Hello, world!

code-block 2
. >>> print("Hello, world!")
{CHECK} Hello, world!
{SUCCESS}\
"""


@templates.register
class _NoEndingDots(BaseTemplate):
    """Test for simple code-block with no closing dots."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> print("Hello, world!")
    'Hello, world!'

.. code-block:: python

    >>> print("Hello, world!")
    'Hello, world!'

"""

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> print("Hello, world!")
{CHECK} Hello, world!

code-block 2
. >>> print("Hello, world!")
{CHECK} Hello, world!
{SUCCESS}\
"""


@templates.register
class _NoEndingDotsBrackets(BaseTemplate):
    """Test for code-block containing a hanging dict."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> d = {
    ...     "one": 1,
    ...     "two": 2,
    ...     "three": 3,
    ...     "four": 4,
    ...     "five": 5,
    ... }

.. code-block:: python

    >>> print("Hello, world!")
    'Hello, world!'

"""

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> d = {{
. ...     "one": 1,
. ...     "two": 2,
. ...     "three": 3,
. ...     "four": 4,
. ...     "five": 5,
. ... }}

code-block 2
. >>> print("Hello, world!")
✓ Hello, world!
{SUCCESS}\
"""


@templates.register
class _NoEndingDotsBracketsNoMatch(BaseTemplate):
    """Test for code-block containing a hanging dict."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> d = {
    ...     "one": 1,
    ...     "two": 2,
    ...     "three": 3,
    ...     "four": 4,
    ...     "five": 5,

.. code-block:: python

    >>> print("Hello, world!")
    'Hello, world!'

"""

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> d = {{
. ...     "one": 1,
. ...     "two": 2,
. ...     "three": 3,
. ...     "four": 4,
. ...     "five": 5,

code-block 2
. >>> print("Hello, world!")
✓ Hello, world!
{SUCCESS}\
"""


@templates.register
class _Multiline(BaseTemplate):
    """Test for multiline code-block."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> colors = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    >>> for i, c in enumerate(colors):
    ...     print(i, c)
    0 black
    1 red
    2 green
    3 yellow
    4 blue
    5 magenta
    6 cyan
    7 white
    >>> effects = ["none", "bold", "dim", "italic", "underline", "blink", "blinking", "negative", "empty", "strikethrough"]
    >>> for i, e in enumerate(effects):
    ...     print(i, e)
    0 none
    1 bold
    2 dim
    3 italic
    4 underline
    5 blink
    6 blinking
    7 negative
    8 empty
    9 strikethrough

"""

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> colors = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
. >>> for i, c in enumerate(colors):
. ...     print(i, c)
{CHECK} 0 black
{CHECK} 1 red
{CHECK} 2 green
{CHECK} 3 yellow
{CHECK} 4 blue
{CHECK} 5 magenta
{CHECK} 6 cyan
{CHECK} 7 white
. >>> effects = ["none", "bold", "dim", "italic", "underline", "blink", "blinking", "negative", "empty", "strikethrough"]
. >>> for i, e in enumerate(effects):
. ...     print(i, e)
{CHECK} 0 none
{CHECK} 1 bold
{CHECK} 2 dim
{CHECK} 3 italic
{CHECK} 4 underline
{CHECK} 5 blink
{CHECK} 6 blinking
{CHECK} 7 negative
{CHECK} 8 empty
{CHECK} 9 strikethrough
{SUCCESS}\
"""


@templates.register
class _ObjectCheck(BaseTemplate):
    """Test for code-block containing object and ID."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> class Object:
    ...     pass
    >>> o = Object()
    >>> print(o)
    <readmetester._core.Object object at 0x7f4f52cf12e0>

"""

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> class Object:
. ...     pass
. >>> o = Object()
. >>> print(o)
{CHECK} <readmetester._core.Object at >
{SUCCESS}\
"""


@templates.register
class _HangingTuple(BaseTemplate):
    """Test for code-block containing a hanging tuple."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> t = (
    ...     "zero",
    ...     "one",
    ...     "two",
    ...     "three",
    ...     "four",
    ...     "five",
    ... )
    >>> for c, i in enumerate(t):
    ...     print(c, i)
    0 zero
    1 one
    2 two
    3 three
    4 four
    5 five

"""

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> t = (
. ...     "zero",
. ...     "one",
. ...     "two",
. ...     "three",
. ...     "four",
. ...     "five",
. ... )
. >>> for c, i in enumerate(t):
. ...     print(c, i)
{CHECK} 0 zero
{CHECK} 1 one
{CHECK} 2 two
{CHECK} 3 three
{CHECK} 4 four
{CHECK} 5 five
{SUCCESS}\
"""


@templates.register
class _HangingList(BaseTemplate):
    """Test for code-block containing a hanging list."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> l = [
    ...     "zero",
    ...     "one",
    ...     "two",
    ...     "three",
    ...     "four",
    ...     "five",
    ... ]
    >>> for c, i in enumerate(l):
    ...     print(c, i)
    0 zero
    1 one
    2 two
    3 three
    4 four
    5 five

"""

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> l = [
. ...     "zero",
. ...     "one",
. ...     "two",
. ...     "three",
. ...     "four",
. ...     "five",
. ... ]
. >>> for c, i in enumerate(l):
. ...     print(c, i)
{CHECK} 0 zero
{CHECK} 1 one
{CHECK} 2 two
{CHECK} 3 three
{CHECK} 4 four
{CHECK} 5 five
{SUCCESS}\
"""


@templates.register
class _HangingDict(BaseTemplate):
    """Test for code-block containing a hanging dict."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> d = {
    ...     "one": 1,
    ...     "two": 2,
    ...     "three": 3,
    ...     "four": 4,
    ...     "five": 5,
    ... }
    >>> for k, v in d.items():
    ...     print(k, v)
    one 1
    two 2
    three 3
    four 4
    five 5

"""

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> d = {{
. ...     "one": 1,
. ...     "two": 2,
. ...     "three": 3,
. ...     "four": 4,
. ...     "five": 5,
. ... }}
. >>> for k, v in d.items():
. ...     print(k, v)
{CHECK} one 1
{CHECK} two 2
{CHECK} three 3
{CHECK} four 4
{CHECK} five 5
{SUCCESS}\
"""


@templates.register
class _NestedHanging(BaseTemplate):
    """Test for code-block containing a nested hanging tuple."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> n = {
    ...     "nested": (
    ...         "a",
    ...         "nested",
    ...         "tuple",
    ...     )
    ... }
    >>> for i in n["nested"]:
    ...     print(i)
    a
    nested
    tuple

"""

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> n = {{
. ...     "nested": (
. ...         "a",
. ...         "nested",
. ...         "tuple",
. ...     )
. ... }}
. >>> for i in n["nested"]:
. ...     print(i)
{CHECK} a
{CHECK} nested
{CHECK} tuple
{SUCCESS}\
"""


@templates.register
class _ThisReadme(BaseTemplate):
    """Test against the README of this project."""

    README = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "README.rst",
    )

    @property
    def template(self) -> str:
        with open(self.README, encoding="utf-8") as fin:
            return fin.read()

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> print("Hello, world!")
{CHECK} Hello, world!

code-block 2
. >>> n = [
. ...     "zero",
. ...     "one",
. ...     "two",
. ... ]
. >>> for c, i in enumerate(n):
. ...     print(c, i)
{CHECK} 0 zero
{CHECK} 1 one
{CHECK} 2 two

code-block 3
. >>> import readmetester
. >>> readmetester.main()
{CHECK} recursive exec not implemented
{SUCCESS}\
"""


@templates.register
class _NoOutputOrExpected(BaseTemplate):
    """Test against the README of this project."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> n = {
    ...     "nested": (
    ...         "a",
    ...         "nested",
    ...         "tuple",
    ...     )
    ... }

"""

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> n = {{
. ...     "nested": (
. ...         "a",
. ...         "nested",
. ...         "tuple",
. ...     )
. ... }}
{SUCCESS}\
"""


@templates.register
class _RecursiveExec(BaseTemplate):
    """Test output of recursive exec."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> import readmetester
    >>> readmetester.main()
    'recursive exec not implemented'
"""

    @property
    def expected(self) -> str:
        return f"""\
code-block 1
. >>> import readmetester
. >>> readmetester.main()
{CHECK} recursive exec not implemented
{SUCCESS}\
"""


@templates.register
class _ErrOutputNotExpected(BaseTemplate):
    """Test error when output expected and expected is not provided."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> import os
    'Hello, world!'
"""

    @property
    def expected(self) -> str:
        return "code-block 1: command did not return `Hello, world!` which is expected"


@templates.register
class _ErrOutputNotEqual(BaseTemplate):
    """Test error when actual result is not equal to expected."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> print("Hello, world!")
    'Hello, world!'
    >>> print("Goodbye, world...")
    'Hello, world!'

"""

    @property
    def expected(self) -> str:
        return "code-block 1: Hello, world! != Goodbye, world..."


@templates.register
class _ErrOutputExpected(BaseTemplate):
    """Test error when output expected and expected is not provided."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> print("Hello, world")

"""

    @property
    def expected(self) -> str:
        return "code-block 1: command returned `Hello, world` which is not expected"


@templates.register
class _ErrOutputNEMulti(BaseTemplate):
    """Test error when output expected and expected is not provided."""

    _ACTUAL = """\
0 zero
1 one\
"""
    _EXPECTED = """\
0 zero
1 one
2 two\
"""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> n = [
    ...     "zero",
    ...     "one",
    ... ]
    >>> for c, i in enumerate(n):
    ...     print(c, i)
    0 zero
    1 one
    2 two

"""

    @property
    def expected(self) -> str:
        return "code-block 1: command did not return `2 two` which is expected"


@templates.register
class _ErrOutputNEMultiBlock(BaseTemplate):
    """Test error when output expected and expected is not provided."""

    _ACTUAL = """\
0 zero
1 one\
"""
    _EXPECTED = """\
0 zero
1 one
2 two\
"""

    @property
    def template(self) -> str:
        return """
.. code-block:: python

    >>> n = [
    ...     "zero",
    ...     "one"
    ... ]
    >>> for c, i in enumerate(n):
    ...     print(c, i)
    0 zero
    1 one
    2 two

.. code-block:: python

    >>> import readmetester
    >>> readmetester.main()
    'recursive exec not implemented'

"""

    @property
    def expected(self) -> str:
        return "code-block 1: command did not return `2 two` which is expected"


@templates.register
class _ErrInvalidSyntax(BaseTemplate):
    """Test for code-block containing a hanging dict."""

    @property
    def template(self) -> str:
        return """
.. code-block:: python
    >>> print("Hello, world!")
    'Hello, world!'

"""

    @property
    def expected(self) -> str:
        return """\
Error in "code-block" directive:
maximum 1 argument(s) allowed, 6 supplied.

.. code-block:: python
    >>> print("Hello, world!")
    'Hello, world!'
"""
