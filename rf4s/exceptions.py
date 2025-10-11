"""
A module reserved for exception classes.
"""


class FishHookedError(Exception):
    """A fish is hooked during resetting."""


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


class RestartError(Exception):
    """User want to restart the app."""


class PreviousError(Exception):
    """User want to use the value in the previous run."""


class PreviousRemainingError(Exception):
    """User want to use the value in the previous run for remaining parts."""


class SkipError(Exception):
    """User want to skip a component during tackle's stat calculation."""


class SkipRemainingError(Exception):
    """User want to skip the remaing components during tackle's stat calculation."""


class QuitError(Exception):
    """User want to quit the app."""


class CoffeeTimeoutError(Exception):
    """Coffee timeout is reached"""


class GearRatioTimeoutError(Exception):
    """Gear ratio timeout is reached"""


class PirkTimeoutError(Exception):
    """Pirking times out."""


class LiftTimeoutError(Exception):
    """Lifting times out."""


class BaitNotChosenError(Exception):
    """Bait is not chosen."""


class DryMixNotChosenError(Exception):
    """Dry mix is not chosen."""


class StuckAtCastingError(Exception):
    """Stuck at casting stage."""


class DryMixNotFoundError(Exception):
    """Dry mix cannot be found."""


class DriftTimeoutError(Exception):
    """Bait drifting times out during float fishing"""
