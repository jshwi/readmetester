"""
readmetester
============

Parse, test, and assert RST code-blocks
"""
from . import exceptions
from ._main import main
from ._version import __version__

__all__ = ["__version__", "exceptions", "main"]
