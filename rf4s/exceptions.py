"""
A module reserved for exception classes.
"""


class FishHookedError(Exception):
    """A fish is hooked during a wrong routine."""


class FishCapturedError(Exception):
    """A fish is captured during a wrong routine."""


class LineAtEndError(Exception):
    """Fishing line is at the end during retrieval."""


class LineSnaggedError(Exception):
    """Fishing line is snagged."""


class ItemNotFoundError(Exception):
    """Failed to find an available item for replacement."""


class LureBrokenError(Exception):
    """Lure is broken."""


class TackleBrokenError(Exception):
    """Tackle is broken."""


class DisconnectedError(Exception):
    """Disconnected from the game."""


class TicketExpiredError(Exception):
    """Ticket expired."""
