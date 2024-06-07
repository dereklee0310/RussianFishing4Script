"""
A module reserved for exception classes.
"""


class FishHookedError(Exception):
    """A fish is hooked during a wrong routine."""


class FishCapturedError(Exception):
    """A fish is captured during a wrong routine."""


class LineAtEndError(Exception):
    """The line is at the end during retrieval."""


class FishGotAwayError(Exception):
    """A hooked fish got away during pulling stage."""
