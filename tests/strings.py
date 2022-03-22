"""
tests.strings
=============
"""


def prepend_lines(prepend, iterable):
    """Prepend every line in iterable with ``str``, most probably
    ``CHECK``.

    :param prepend:     ``str`` to prepend to every line in iterable.
    :param iterable:    Iterable to prepend with ``str``.
    :return:            Constructed ``str``.
    """
    return "\n".join([f"{prepend} {i}" for i in iterable])


SUCCESS = f"\n{80 * '-'}\nSuccess!"
CHECK = "\u2713"
SIMPLE = """
.. code-block:: python

    >>> print("Hello, world!")
    'Hello, world!'
..
"""
SIMPLE_LINE_BREAK = """
.. code-block:: python

    >>> print("Hello, world!")
    >>>
    >>> print("Hello, world!")
    'Hello, world!'
    'Hello, world!'
..
"""
MULTILINE = """
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
..
"""
OBJECT = """
.. code-block:: python

    >>> class Object:
    ...     pass
    >>> o = Object()
    >>> print(o)
    <readmetester._core.Object object at 0x7f4f52cf12e0>
..
"""
HANGING_TUPLE = """
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
.."""
HANGING_LIST = """
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
.."""
HANGING_DICT = """
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
..
"""
NESTED_HANGING = """
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
..
"""
TEMPLATES = [
    (
        SIMPLE,
        'code-block 1\n. >>> print("Hello, world!")\n{} Hello, world!\n{}'.format(
            CHECK, SUCCESS
        ),
    ),
    (
        SIMPLE_LINE_BREAK,
        'code-block 1\n. >>> print("Hello, world!")\n{0} Hello, world!\n. >>> print("Hello, world!")\n{0} Hello, world!\n{1}'.format(
            CHECK, SUCCESS
        ),
    ),
    (
        MULTILINE,
        (
            "code-block 1\n"
            '. >>> colors = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]\n'
            ". >>> for i, c in enumerate(colors):\n"
            ". ...     print(i, c)\n"
        )
        + prepend_lines(
            CHECK,
            (
                "0 black",
                "1 red",
                "2 green",
                "3 yellow",
                "4 blue",
                "5 magenta",
                "6 cyan",
                "7 white",
            ),
        )
        + "\n"
        + (
            '. >>> effects = ["none", "bold", "dim", "italic", "underline", "blink", "blinking", "negative", "empty", "strikethrough"]\n'
            ". >>> for i, e in enumerate(effects):\n"
            ". ...     print(i, e)\n"
        )
        + prepend_lines(
            CHECK,
            (
                "0 none",
                "1 bold",
                "2 dim",
                "3 italic",
                "4 underline",
                "5 blink",
                "6 blinking",
                "7 negative",
                "8 empty",
                "9 strikethrough",
            ),
        )
        + "\n"
        + SUCCESS,
    ),
    (
        OBJECT,
        (
            "code-block 1\n"
            ". >>> class Object:\n"
            ". ...     pass\n"
            ". >>> o = Object()\n"
            ". >>> print(o)\n"
            + CHECK
            + " <readmetester._core.Object at >\n"
            + SUCCESS
        ),
    ),
    (
        HANGING_TUPLE,
        (
            "code-block 1\n"
            ". >>> t = (\n"
            '. ...     "zero",\n'
            '. ...     "one",\n'
            '. ...     "two",\n'
            '. ...     "three",\n'
            '. ...     "four",\n'
            '. ...     "five",\n'
            ". ... )\n"
            ". >>> for c, i in enumerate(t):\n"
            ". ...     print(c, i)\n"
            + prepend_lines(
                CHECK,
                (
                    "0 zero",
                    "1 one",
                    "2 two",
                    "3 three",
                    "4 four",
                    "5 five",
                ),
            )
            + "\n"
            + SUCCESS
        ),
    ),
    (
        HANGING_LIST,
        (
            "code-block 1\n"
            ". >>> l = [\n"
            '. ...     "zero",\n'
            '. ...     "one",\n'
            '. ...     "two",\n'
            '. ...     "three",\n'
            '. ...     "four",\n'
            '. ...     "five",\n'
            ". ... ]\n"
            ". >>> for c, i in enumerate(l):\n"
            ". ...     print(c, i)\n"
            + prepend_lines(
                CHECK,
                (
                    "0 zero",
                    "1 one",
                    "2 two",
                    "3 three",
                    "4 four",
                    "5 five",
                ),
            )
            + "\n"
            + SUCCESS
        ),
    ),
    (
        HANGING_DICT,
        (
            "code-block 1\n"
            ". >>> d = {\n"
            '. ...     "one": 1,\n'
            '. ...     "two": 2,\n'
            '. ...     "three": 3,\n'
            '. ...     "four": 4,\n'
            '. ...     "five": 5,\n'
            ". ... }\n"
            ". >>> for k, v in d.items():\n"
            ". ...     print(k, v)\n"
            + prepend_lines(
                CHECK,
                (
                    "one 1",
                    "two 2",
                    "three 3",
                    "four 4",
                    "five 5",
                ),
            )
            + "\n"
            + SUCCESS
        ),
    ),
    (
        NESTED_HANGING,
        (
            "code-block 1\n"
            ". >>> n = {\n"
            '. ...     "nested": (\n'
            '. ...         "a",\n'
            '. ...         "nested",\n'
            '. ...         "tuple",\n'
            ". ...     )\n"
            ". ... }\n"
            '. >>> for i in n["nested"]:\n'
            ". ...     print(i)\n"
            + prepend_lines(
                CHECK,
                (
                    "a",
                    "nested",
                    "tuple",
                ),
            )
            + "\n"
            + SUCCESS
        ),
    ),
]
ERR_NO_OUTPUT_EXPECTED = """
.. code-block:: python

    >>> print("Hello, world")
..
"""
ERR_ACTUAL_NE_EXPECTED = """
.. code-block:: python

    >>> print("Hello, world!")
    'Hello, world!'
    >>> print("Goodbye, world...")
    'Hello, world!'
..
"""
ERRORS = [
    (
        ERR_NO_OUTPUT_EXPECTED,
        "command returned output but no output is expected",
    ),
    (
        ERR_ACTUAL_NE_EXPECTED,
        "code-block 1: Hello, world! != Goodbye, world...",
    ),
]
