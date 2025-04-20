from enum import auto, StrEnum


class GameType(StrEnum):
    SINGLE = auto()
    HOST = auto()
    CLIENT = auto()

class KeyType(StrEnum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
