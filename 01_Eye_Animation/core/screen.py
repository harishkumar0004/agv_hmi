from enum import Enum, auto

class Screen(Enum):
    IDLE = auto()
    ASSIGNMENT = auto()
    CONFIRMATION = auto()
    STATUS = auto()
    ARRIVED = auto()