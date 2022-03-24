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
        """Replace ANSI color codes with empty strings i.e. remove all
        escape codes.

        Prefer to test colored output this way as colored strings can
        be tricky and the effort in testing their validity really isn't
        worth it (also hard to read expected strings when they contain
        the codes).

        :param out: String to strip of ANSI escape codes
        :return:    Same string but without ANSI codes
        """
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", out)

    def readouterr(self) -> t.List[str]:
        """Call as capsys ``readouterr`` but regex the strings for
        escape codes at the same time.

        :return:    A tuple (just like the capsys) containing stdout in
                    the first index and stderr in the second
        """
        return [
            "\n".join([i.strip() for i in s.split("\n")]).strip()
            for s in [self.regex(r) for r in self.capsys.readouterr()]
        ]

    def _readouterr_index(self, idx: int) -> str:
        return self.readouterr()[idx]

    def stdout(self) -> str:
        """Call this to return the stdout without referencing the tuple
        indices.

        :return: Stdout.
        """
        return self._readouterr_index(0)


class EnterDir:
    """Change to the selected directory entered as an argument and when
    actions are complete return to the previous directory.

    :param new_path: Enter the directory to temporarily change to
    """

    def __init__(self, new_path: Path) -> None:
        self.saved_path = Path.cwd()
        os.chdir(new_path.expanduser())

    def __enter__(self) -> EnterDir:
        return self

    def __exit__(self, exc_type: t.Any, exc_val: t.Any, exc_tb: t.Any) -> None:
        os.chdir(self.saved_path)
