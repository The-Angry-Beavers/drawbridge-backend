from enum import StrEnum, auto


class DataTypeEnum(StrEnum):
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    DATETIME = auto()

class OperatorEnum(StrEnum):
    EQ = "="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
