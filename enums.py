"""Enums module"""

from enum import auto, StrEnum


class GameType(StrEnum):
    """Game type enum"""
    SINGLE = auto()
    COOP = auto()

class KeyType(StrEnum):
    """Directions enum"""
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

class Facing(StrEnum):
    """Directions enum"""
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
