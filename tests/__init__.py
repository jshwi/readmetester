"""
tests
=====
"""
import os
import re


class NoColorCapsys:
    """Capsys but with a regex to remove ANSI escape codes

    Class is preferable for this as we can instantiate the instance
    as a fixture that also contains the same attributes as capsys

    We can make sure that the class is instantiated without executing
    capsys immediately thus losing control of what stdout and stderr
    we are to capture

    :param capsys: ``pytest`` fixture for capturing output stream.
    """

    def __init__(self, capsys):
        self.capsys = capsys

    @staticmethod
    def regex(out):
        """Replace ANSI color codes with empty strings i.e. remove all
        escape codes

        Prefer to test colored output this way as colored strings can
        be tricky and the effort in testing their validity really isn't
        worth it. Also hard to read expected strings when they contain
        the codes.

        :param out: String to strip of ANSI escape codes
        :return:    Same string but without ANSI codes
        """
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", out)

    def readouterr(self):
        """Call as capsys ``readouterr`` but regex the strings for
        escape codes at the same time

        :return:    A tuple (just like the capsys) containing stdout in
                    the first index and stderr in the second
        """
        return [
            "\n".join([i.strip() for i in s.split("\n")]).strip()
            for s in [self.regex(r) for r in self.capsys.readouterr()]
        ]

    def _readouterr_index(self, idx):
        return self.readouterr()[idx]

    def stdout(self):
        """Call this to return the stdout without referencing the tuple
        indices

        :return: Stdout.
        """
        return self._readouterr_index(0)


class EnterDir:
    """Change to the selected directory entered as an argument and when
    actions are complete return to the previous directory

    :param new_path: Enter the directory to temporarily change to
    """

    def __init__(self, new_path):
        self.saved_path = os.getcwd()
        self.enter_path = os.path.expanduser(new_path)

    def __enter__(self):
        os.chdir(self.enter_path)

    def __exit__(self, _, value, __):
        os.chdir(self.saved_path)
