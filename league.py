"""
league.py

Defines the `League` class for managing a fantasy‐style playoff pool, including scoring
and leaderboard generation.
"""

from typing import Dict, List, Tuple

from bracket_node import BracketNode
from round import Round
from bracket import Bracket


def traverse_nodes(bracket: Bracket):
    """
    Yields every `BracketNode` in the bracket tree in depth‐first order.

    :param bracket: A `Bracket` instance to traverse.
    :yields: Each `BracketNode` encountered.
    """
    stack = [bracket.root]
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node.top, BracketNode):
            stack.append(node.top)
        if isinstance(node.bottom, BracketNode):
            stack.append(node.bottom)


class League:
    """
    Represents a fantasy-style league with customizable scoring.
    """
    def __init__(
        self,
        name: str,
        points_per_round: Dict[Round, int],
        brackets: List[Bracket],
        correct_bracket: Bracket
    ):
        """
        Initializes a `League`.

        :param name: Name of the league.
        :param points_per_round: Mapping from each `Round` to integer points per correct pick in the round.
        :param brackets: List of player `Bracket` instances to score.
        :param correct_bracket: The actual playoff `Bracket` for scoring reference.
        :returns: None
        """
        self.name = name
        self.points_per_round = points_per_round
        self.brackets = brackets
        self.correct_bracket = correct_bracket

    def score_bracket(self, predicted: Bracket) -> int:
        """
        Computes the total score for a predicted bracket.

        :param predicted: A player's `Bracket` with picks filled in.
        :returns: Total integer score based on correct picks.
        """
        total = 0
        for actual_node, pred_node in zip(
            traverse_nodes(self.correct_bracket),
            traverse_nodes(predicted)
        ):
            if actual_node.winner and pred_node.winner:
                if pred_node.winner.name == actual_node.winner.name:
                    total += self.points_per_round[actual_node.round]
        return total

    def check_bracket(self, predicted: Bracket) -> Dict[BracketNode, str]:
        """
        Identifies incorrect branches in a predicted bracket for colouring.

        :param predicted: A player's `Bracket` to compare against `self.correct_bracket`.
        :returns: A dict mapping each incorrect `BracketNode` to a list of 'top'/'bottom' keys that were incorrect.
        """
        incorrect: Dict[BracketNode, str] = dict()

        for actual_node, pred_node in zip(
            traverse_nodes(self.correct_bracket),
            traverse_nodes(predicted)
        ):
            if actual_node.winner and pred_node.winner:
                if pred_node.winner.name != actual_node.winner.name:
                    # BracketNode children
                    if isinstance(pred_node.top, BracketNode):
                        if (
                            pred_node.top.winner.name != actual_node.winner.name
                            and pred_node.top.winner.name == pred_node.winner.name
                        ):
                            incorrect[pred_node] = "top"
                        else:
                            incorrect[pred_node] = "bottom"
                    # Leaf-team children
                    else:
                        if pred_node.top.name == pred_node.winner.name:
                            incorrect[pred_node] = "top"
                        else:
                            incorrect[pred_node] = "bottom"

        return incorrect

    def leaderboard(self) -> List[Tuple[int, Bracket, int]]:
        """
        Generates a sorted leaderboard of player scores.

        :returns: A list of tuples (rank, Bracket, score), sorted by score descending.
        """
        scores = {br: self.score_bracket(br) for br in self.brackets}
        sorted_scores = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

        ranked: List[Tuple[int, Bracket, int]] = []
        last_score = None
        last_rank = 0

        for idx, (br, score) in enumerate(sorted_scores, start=1):
            if score != last_score:
                rank = idx
                last_score = score
                last_rank = rank
            else:
                rank = last_rank
            ranked.append((rank, br, score))

        return ranked
