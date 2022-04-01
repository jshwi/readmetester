"""
tests.strings
=============
"""
import os
import typing as t
from abc import ABC, abstractmethod

import readmetester.exceptions

templates = []
errors = []


class TemplateExpected(ABC):
    """Base class for README template/expected tests."""

    SUCCESS = f"\n{80 * '-'}\nSuccess!"
    CHECK = "\u2713"

    @property
    @abstractmethod
    def template(self) -> str:
        """Template to test."""

    @property
    @abstractmethod
    def expected(self) -> str:
        """Expected result."""


class TemplateExpectedError(TemplateExpected):
    """Base class for README template/expected tests for errors."""

    @property
    @abstractmethod
    def template(self) -> str:
        """Template to test."""

    @property
    @abstractmethod
    def expected(self) -> str:
        """Expected result."""

    @property
    @abstractmethod
    def error(self) -> t.Type[readmetester.exceptions.DocumentError]:
        """Expected error."""


def register_template(
    template_expected: t.Type[TemplateExpected],
) -> t.Type[TemplateExpected]:
    """Register template/expected str objects for successful tests.

    :param template_expected: ``TemplateExpected`` object.
    :returns: ``TemplateExpected`` object.
    """
    instance = template_expected()
    templates.append((instance.template, instance.expected))
    return template_expected


def register_error(
    template_expected_error: t.Type[TemplateExpectedError],
) -> t.Type[TemplateExpectedError]:
    """Register template/expected str objects for testing errors.

    :param template_expected_error: ``TemplateExpectedError`` object.
    :returns: ``TemplateExpectedError`` object.
    """
    instance = template_expected_error()
    errors.append((instance.template, instance.expected, instance.error))
    return template_expected_error


@register_template
class Simple(TemplateExpected):
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
{self.CHECK} Hello, world!
{self.SUCCESS}\
"""


@register_template
class SimpleLineBreak(TemplateExpected):
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
{self.CHECK} Hello, world!
. >>> print("Hello, world!")
{self.CHECK} Hello, world!
{self.SUCCESS}\
"""


@register_template
class EndingDots(TemplateExpected):
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
{self.CHECK} Hello, world!

code-block 2
. >>> print("Hello, world!")
{self.CHECK} Hello, world!
{self.SUCCESS}\
"""


@register_template
class NoEndingDots(TemplateExpected):
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
{self.CHECK} Hello, world!

code-block 2
. >>> print("Hello, world!")
{self.CHECK} Hello, world!
{self.SUCCESS}\
"""


@register_template
class NoEndingDotsBrackets(TemplateExpected):
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
{self.SUCCESS}\
"""


@register_template
class NoEndingDotsBracketsNoMatch(TemplateExpected):
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
{self.SUCCESS}\
"""


@register_template
class Multiline(TemplateExpected):
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
{self.CHECK} 0 black
{self.CHECK} 1 red
{self.CHECK} 2 green
{self.CHECK} 3 yellow
{self.CHECK} 4 blue
{self.CHECK} 5 magenta
{self.CHECK} 6 cyan
{self.CHECK} 7 white
. >>> effects = ["none", "bold", "dim", "italic", "underline", "blink", "blinking", "negative", "empty", "strikethrough"]
. >>> for i, e in enumerate(effects):
. ...     print(i, e)
{self.CHECK} 0 none
{self.CHECK} 1 bold
{self.CHECK} 2 dim
{self.CHECK} 3 italic
{self.CHECK} 4 underline
{self.CHECK} 5 blink
{self.CHECK} 6 blinking
{self.CHECK} 7 negative
{self.CHECK} 8 empty
{self.CHECK} 9 strikethrough
{self.SUCCESS}\
"""


@register_template
class ObjectCheck(TemplateExpected):
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
{self.CHECK} <readmetester._core.Object at >
{self.SUCCESS}\
"""


@register_template
class HangingTuple(TemplateExpected):
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
{self.CHECK} 0 zero
{self.CHECK} 1 one
{self.CHECK} 2 two
{self.CHECK} 3 three
{self.CHECK} 4 four
{self.CHECK} 5 five
{self.SUCCESS}\
"""


@register_template
class HangingList(TemplateExpected):
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
{self.CHECK} 0 zero
{self.CHECK} 1 one
{self.CHECK} 2 two
{self.CHECK} 3 three
{self.CHECK} 4 four
{self.CHECK} 5 five
{self.SUCCESS}\
"""


@register_template
class HangingDict(TemplateExpected):
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
{self.CHECK} one 1
{self.CHECK} two 2
{self.CHECK} three 3
{self.CHECK} four 4
{self.CHECK} five 5
{self.SUCCESS}\
"""


@register_template
class NestedHanging(TemplateExpected):
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
{self.CHECK} a
{self.CHECK} nested
{self.CHECK} tuple
{self.SUCCESS}\
"""


@register_template
class ThisReadme(TemplateExpected):
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
{self.CHECK} Hello, world!

code-block 2
. >>> n = [
. ...     "zero",
. ...     "one",
. ...     "two",
. ... ]
. >>> for c, i in enumerate(n):
. ...     print(c, i)
{self.CHECK} 0 zero
{self.CHECK} 1 one
{self.CHECK} 2 two
{self.SUCCESS}\
"""


@register_template
class NoOutputOrExpected(TemplateExpected):
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
{self.SUCCESS}\
"""


@register_error
class OutputNotExpectedError(TemplateExpectedError):
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

    @property
    def error(self) -> t.Type[readmetester.exceptions.DocumentError]:
        return readmetester.exceptions.OutputExpectedError


@register_error
class OutputNotEqualError(TemplateExpectedError):
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

    @property
    def error(self) -> t.Type[readmetester.exceptions.DocumentError]:
        return readmetester.exceptions.OutputNotEqualError


@register_error
class OutputExpectedError(TemplateExpectedError):
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

    @property
    def error(self) -> t.Type[readmetester.exceptions.DocumentError]:
        return readmetester.exceptions.OutputNotExpectedError


@register_error
class OutputNEMultiError(TemplateExpectedError):
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
    def error(self) -> t.Type[readmetester.exceptions.DocumentError]:
        return readmetester.exceptions.OutputExpectedError

    @property
    def expected(self) -> str:
        return "code-block 1: command did not return `2 two` which is expected"


@register_error
class OutputNEMultiBlockError(TemplateExpectedError):
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
    def error(self) -> t.Type[readmetester.exceptions.DocumentError]:
        return readmetester.exceptions.OutputExpectedError

    @property
    def expected(self) -> str:
        return "code-block 1: command did not return `2 two` which is expected"
