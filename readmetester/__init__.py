"""
readmetester
============
"""
from . import exceptions
from ._core import Mapping, Seq
from ._main import main
from ._version import __version__

__all__ = ["__version__", "Mapping", "Seq", "exceptions", "main"]
