"""Enums to be used in test cases
"""
from enum import IntEnum


class Band(IntEnum):
    """
    This is an enumerator class that contains Dish Band values.
    """

    NONE = 0
    B1 = 1
    B2 = 2
    B3 = 3
    B4 = 4
    B5a = 5  # pylint: disable=invalid-name
    B5b = 6  # pylint: disable=invalid-name
    UNKNOWN = 7
