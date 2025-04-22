"""
bracket_node.py

This module defines `BracketNode`, the fundamental node type in a playoff bracket tree.
Each node holds two competitors (either two `Team` instances, or two `BracketNode` instances
which each have some winner) and records the winner.
"""

import uuid
from round import Round
from team import Team
from typing import Union, Optional

class BracketNode:
    """
    Node in a playoff bracket tree. Holds two sides (either Team or BracketNode), the round,
    and records the winner once known.
    """
    def __init__(

        self,
        round_: Round,
        top: Union['BracketNode', Team],
        bottom: Union['BracketNode', Team]
    ):
        """
        Initializes a `BracketNode`.

        :param round_: The `Round` enum for this matchup.
        :param top: The top competitor (either a `Team` or previous `BracketNode`).
        :param bottom: The bottom competitor (either a `Team` or previous `BracketNode`).
        :returns: None
        """
        self.round = round_
        self.top = top
        self.bottom = bottom

        self._uid: uuid.UUID = uuid.uuid4()

        self.winner: Optional[Team] = None

    def __hash__(self):
        """
        Enables usage in sets and as dict keys.

        :returns: Hash based on the node's UUID.
        """
        return hash(self._uid)

    def set_winner(self, team: Team) -> None:
        """
        Records the winning team for this matchup.

        :param team: A `Team` instance that must match one of the two sides.
        :raises ValueError: If `team` is not one of the current competitors.
        :returns: None
        """
        if team not in (self._leaf_top(), self._leaf_bottom()):
            raise ValueError(f"Team {team} not in this matchup.")
        self.winner = team

    def _leaf_top(self) -> Team:
        """
        Retrieves the top competitor as a `Team`.

        :returns: The `Team` at the top side, may be None if winner not set.
        """
        return self.top if isinstance(self.top, Team) else self.top.winner  # may be None

    def _leaf_bottom(self) -> Team:
        """
        Retrieves the bottom competitor as a `Team`.

        :returns: The `Team` at the bottom side, may be None if winner not set.
        """
        return self.bottom if isinstance(self.bottom, Team) else self.bottom.winner  # may be None
