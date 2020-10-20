from enum import Enum, unique


@unique
class FieldType(Enum):
    UNDEFINED = 0
    BOOLEAN = 1
    STRING = 2
    INTEGER = 3
    FLOAT = 4
    NULL_BOOLEAN = 5
    TIMESTAMP = 6
