"""
round.py

Defines the `Round` enum representing the stages of the playoffs.
"""

import enum


class Round(enum.IntEnum):
    """
    Enumeration of playoff rounds for scoring and ordering.
    """

    FIRST_ROUND = 1
    SECOND_ROUND = 2
    CONFERENCE_FINALS = 3
    STANLEY_CUP_FINALS = 4