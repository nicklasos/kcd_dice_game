"""
Custom exceptions for the KCD dice game.
"""


class InvalidMoveException(Exception):
    """Raised when a player attempts an illegal move."""

    pass


class GameRuleException(Exception):
    """Raised when a game rule is violated."""

    pass


class GameStateException(Exception):
    """Raised when an invalid game state transition is attempted."""

    pass
