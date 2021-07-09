from enum import Enum


class BatchStatus(Enum):
    INCOMPLETE = 0
    RECIEVED = 1
    CONVERTED = 2
    IN_PROGRESS = 3
    COMPLETE = 4
