"""
A module reserved for exception classes.
"""


class FishHookedError(Exception):
    """A fish is hooked during a wrong routine."""


class FishCapturedError(Exception):
    """A fish is captured during a wrong routine."""


# already a built-in exception
# class TimeoutError(Exception):
#     """The timeout of a routine is reached."""


class LineAtEndError(Exception):
    """The line is at the end during retrieval."""


class IterationLimitExceedError(Exception):
    """The iteration count of "retrieval with pause" exceeded the limit."""


class RetrieveFinishedError(Exception):
    """Retrieval with pause is finished, but no fish is hooked."""

class FishGotAwayError(Exception):
    """A hooked fish got away during pulling stage."""