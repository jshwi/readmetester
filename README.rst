READMETester
============
.. image:: https://github.com/jshwi/readmetester/workflows/build/badge.svg
    :target: https://github.com/jshwi/readmetester/workflows/build/badge.svg
    :alt: build
.. image:: https://img.shields.io/badge/python-3.8-blue.svg
    :target: https://www.python.org/downloads/release/python-380
    :alt: python3.8
.. image:: https://img.shields.io/pypi/v/readmetester
    :target: https://img.shields.io/pypi/v/readmetester
    :alt: pypi
.. image:: https://codecov.io/gh/jshwi/readmetester/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jshwi/readmetester
    :alt: codecov.io
.. image:: https://readthedocs.org/projects/readmetester/badge/?version=latest
    :target: https://readmetester.readthedocs.io/en/latest/?badge=latest
    :alt: readthedocs.org
.. image:: https://img.shields.io/badge/License-MIT-blue.svg
    :target: https://lbesson.mit-license.org/
    :alt: mit
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: black

Parse and test README.rst Python code-blocks

**Installation**

.. code-block:: console

    $ pip install readmetester
..

Code blocks need to begin with

``.. code-block:: python``

followed by a blank line

and end with

``..``

**Usage**

``readmetester [-h] file``

If a README.rst file is present in the current working directory it will be used if no arguments are provided

.. code-block:: console

    $ readmetester README.rst
..

**Documenting**

Documented code needs to be indented

Python code begins with ``">>> "``

.. note::

    The length of the string is 4 including the whitespace at the end
..

Expected output can be single quoted or unquoted (no double quotes)

.. code-block:: RST

    .. code-block:: python

        >>> print("Hello, world!")
        'Hello, world!'
    ..
..

Continuation lines begin with ``"... "``

.. code-block:: RST

    .. code-block:: python

        >>> n = [
        ...     "zero",
        ...     "one",
        ...     "two",
        ... ]
        >>> for c, i in enumerate(n):
        ...     print(c, i)
        0 zero
        1 one
        2 two
    ..
..

