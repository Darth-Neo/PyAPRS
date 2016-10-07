"""
Provides facilities for covertion from/to base91
"""
from math import log
from re import findall

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

__all__ = ["to_decimal", "from_decimal"]

def to_decimal(text):
    """
    Takes a base91 char string and returns decimal
    """

    if not isinstance(text, str):
        raise TypeError("expected str or unicode, %s given" % type(text))

    if findall(r"[\x00-\x20\x7c-\xff]", text):
        raise ValueError("invalid character in sequence")

    decimal = 0
    length = len(text) - 1
    for i, char in enumerate(text):
        decimal += (ord(char) - 33) * (91 ** (length - i))

    rm =  decimal if text != "" else 0
    return rm


def from_decimal(number, padding=1):
    """
    Takes a decimal and returns base91 char string.
    With optional padding to a specific length.
    """
    text = []

    if not isinstance(number, int):
        raise TypeError("Expected number to be int, got %s", type(number))
    elif not isinstance(padding, int):
        raise TypeError("Expected padding to be int, got %s", type(number))
    elif number < 0:
        raise ValueError("Expected number to be positive integer")
    elif padding < 1:
        raise ValueError("Expected padding to be >0")
    elif number > 0:
        for divisor in [91**e for e in reversed(range(int(log(number) / log(91)) + 1))]:
            quotient = number // divisor
            number %= divisor
            text.append(chr(33 + quotient))

    # add padding if necessary
    text = ["!"] * (padding-len(text)) + text

    rm = "".join(text)
    return rm
