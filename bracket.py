"""
bracket.py

This module defines the `Bracket` class for representing and visualizing a playoff bracket structure,
specifically designed for the Stanley Cup Playoffs. It allows generating a full bracket from a list of
teams and their seeds, and rendering a visual bracket with team logos.

"""

from bracket_node import BracketNode
from collections import defaultdict
from matplotlib.lines import Line2D

from round import Round
from team import Team
from pathlib import Path
from typing import Dict, List, Union
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Module-level constants
IMG_WIDTH = 1600
IMG_HEIGHT = 600
DPI = 100


def draw_connection(draw_seg, x, y, dx, dy, direction, colours):
    """
    Draws the three‐segment connection lines between bracket nodes.

    :param draw_seg: Callable that draws a single line segment.
    :param x: X coordinate of the origin point in pixels.
    :param y: Y coordinate of the origin point in pixels.
    :param dx: Horizontal offset for the branch in pixels.
    :param dy: Vertical offset for the branch in pixels.
    :param direction: +1 for East side, -1 for West side.
    :param colours: Mapping with keys 'center', 'top', 'bottom' specifying line colours.
    :returns: None
    """

    # 1) center horizontal
    draw_seg(x, y, x + direction * dx / 2, y,
             color=colours['center'], linewidth=1)

    # 2) branch out to top and bottom
    for branch, col in (('top', colours['top']),
                        ('bottom', colours['bottom'])):
        y_off = y + (dy if branch == 'bottom' else -dy)
        # vertical
        draw_seg(x + direction * dx / 2, y,
                 x + direction * dx / 2, y_off,
                 color=col, linewidth=1)
        # horizontal
        draw_seg(x + direction * dx / 2, y_off,
                 x + direction * dx,    y_off,
                 color=col, linewidth=1)


class Bracket:
    """
    Represents an entire playoff bracket as a tree of BracketNode.
    """
    def __init__(self, root: BracketNode, name: str):
        """
        Initializes a `Bracket` instance.

        :param root: Root `BracketNode` of the complete playoff tree.
        :param name: Identifier/name for this bracket (e.g., player_name or 'empty').
        :returns: None
        """
        self.root = root
        self.name = name

    @classmethod
    def from_team_list(cls, teams: List[Team], name: str) -> 'Bracket':
        """
        Constructs a full bracket tree from a list of team tuples.

        Teams are seeded within each conference and paired 1v8, 2v7, 3v6, 4v5 in round one.

        :param teams: List of Team objects.
        :param name: Name to assign to the resulting bracket.
        :returns: A `Bracket` instance with all rounds linked.
        """
        # Convert to Team objects and group by conference
        conf_groups: Dict[str, List[Team]] = {"West": [], "East": []}
        for team in teams:
            conf_groups[team.conference].append(team)

        # Sort by seed ascending
        for conf in conf_groups:
            conf_groups[conf].sort(key=lambda t: t.seed)

        # Create first-round nodes per conference
        first_round_nodes: Dict[str, List[BracketNode]] = {}
        for conf, team_list in conf_groups.items():
            nodes = []
            n = len(team_list)
            for i in range(n // 2):
                high_seed = team_list[i]
                low_seed = team_list[-(i + 1)]
                node = BracketNode(Round.FIRST_ROUND, high_seed, low_seed)
                nodes.append(node)
            first_round_nodes[conf] = nodes

        # Build subsequent rounds
        def build_round(prev_round_nodes: List[BracketNode], round_enum: Round) -> List[BracketNode]:
            new_nodes: List[BracketNode] = []
            for i in range(0, len(prev_round_nodes), 2):
                node = BracketNode(round_enum,
                                   prev_round_nodes[i],
                                   prev_round_nodes[i + 1])
                new_nodes.append(node)
            return new_nodes

        # Second round (Conference Semifinals)
        second_round_nodes = {
            conf: build_round(nodes, Round.SECOND_ROUND)
            for conf, nodes in first_round_nodes.items()
        }
        # Conference Finals
        conf_final_nodes = {
            conf: build_round(nodes, Round.CONFERENCE_FINALS)
            for conf, nodes in second_round_nodes.items()
        }
        # Stanley Cup Final (across conferences)
        final_node = BracketNode(
            Round.STANLEY_CUP_FINALS,
            conf_final_nodes["West"][0],
            conf_final_nodes["East"][0]
        )

        return cls(root=final_node, name=name)

    def collect_nodes_by_round(self) -> Dict[Round, List[BracketNode]]:
        """
        Traverses the bracket tree and groups nodes by their round.

        :returns: A dict mapping each `Round` to the list of `BracketNode`s in that round.
        """
        rounds: Dict[Round, List[BracketNode]] = defaultdict(list)

        def dfs(node: BracketNode):
            rounds[node.round].append(node)
            if isinstance(node.top, BracketNode):
                dfs(node.top)
            if isinstance(node.bottom, BracketNode):
                dfs(node.bottom)

        dfs(self.root)
        return rounds

    def draw_bracket(self, filename: str,
                     colour_lines: bool = False,
                     league: "League" = None):
        """
        Renders and saves the bracket visualization including team logos and optional colouring.

        :param filename: Name of the output PNG file (saved under `bracket_results/`).
        :param colour_lines: If True, highlights incorrect predictions in red.
        :param league: A `League` instance used to check and colour incorrect lines.
        :returns: None
        """
        rounds = self.collect_nodes_by_round()

        fig = plt.figure(
            figsize=(IMG_WIDTH / DPI, IMG_HEIGHT / DPI),
            dpi=DPI
        )
        ax = fig.add_axes((0, 0, 1, 1))
        ax.axis('off')

        def draw_seg(x1, y1, x2, y2, **line_kwargs):
            """
            Local helper for drawing line segments

            :param x1: x coordinate at start of line segment
            :param y1: y coordinate at start of line segment
            :param x2: x coordinate at end of line segment
            :param y2: y coordinate at end of line segment
            :param line_kwargs: line width and colour
            """
            fx1, fy1 = x1 / IMG_WIDTH, 1 - (y1 / IMG_HEIGHT)
            fx2, fy2 = x2 / IMG_WIDTH, 1 - (y2 / IMG_HEIGHT)
            line = Line2D([fx1, fx2], [fy1, fy2],
                          transform=fig.transFigure, **line_kwargs)
            fig.add_artist(line)

        num_rounds = max(rounds.keys()) + 1
        dx = IMG_WIDTH / (2 * num_rounds)
        base_dy = IMG_HEIGHT / (2 * sum(1 / i for i in range(1, num_rounds)))

        incorrect_predictions = {}
        if colour_lines and league:
            incorrect_predictions = league.check_bracket(self)

        def dfs(node: Union[BracketNode, Team],
                x, y,
                dy: float = base_dy,
                first_pass: bool = False):
            if isinstance(node, BracketNode):
                conf = node.winner.conference
                top_line_colour = bottom_line_colour = 'gray'
                if node in incorrect_predictions:
                    top_line_colour = 'red' if 'top' in incorrect_predictions[node] else 'gray'
                    bottom_line_colour = 'red' if 'bottom' in incorrect_predictions[node] else 'gray'

                if first_pass:
                    direction = +1 if conf == "East" else -1
                    center_colour = top_line_colour if top_line_colour == bottom_line_colour else "red"
                    draw_connection(
                        draw_seg, x, y, dx, 0, direction,
                        {'center': center_colour, 'top': center_colour, 'bottom': center_colour}
                    )

                    dfs(node.top,    x - dx, y,      dy)
                    dfs(node.bottom, x + dx, y,      dy)
                else:
                    direction = +1 if conf == "East" else -1
                    draw_connection(
                        draw_seg, x, y, dx, dy, direction,
                        {'center': top_line_colour if top_line_colour == bottom_line_colour else 'red',
                         'top':    top_line_colour,
                         'bottom': bottom_line_colour}
                    )
                    dfs(node.top,    x + direction * dx, y - dy, dy / 2)
                    dfs(node.bottom, x + direction * dx, y + dy, dy / 2)

            # Draw team logo
            img_size = (150, 150) if first_pass else (50, 50)
            if isinstance(node, BracketNode):
                img_path = f"team_logos/{node.winner.name.replace(' ', '_')}.png"
            else:
                img_path = f"team_logos/{node.name.replace(' ', '_')}.png"

            img = Image.open(img_path).resize(img_size)
            fx = (x - img_size[0] / 2) / IMG_WIDTH
            fy = 1 - ((y + img_size[1] / 2) / IMG_HEIGHT)
            logo_ax = fig.add_axes(
                (fx, fy, img_size[0] / IMG_WIDTH, img_size[1] / IMG_HEIGHT),
                facecolor='none', frameon=False, zorder=2
            )
            logo_ax.imshow(np.array(img))
            logo_ax.axis('off')

        dfs(self.root, IMG_WIDTH / 2, IMG_HEIGHT / 2, first_pass=True)

        plt.savefig(Path("bracket_results") / filename)

    def __str__(self) -> str:
        """
        Generates a human‐readable textual representation of the bracket.

        :returns: Multi‐line string listing each matchup by round and the final winner.
        """
        def describe_matchup(n: BracketNode) -> str:
            def name_of(side):
                if isinstance(side, Team):
                    return side.name
                elif side.winner is not None:
                    return side.winner.name
                top = name_of(side.top)
                bottom = name_of(side.bottom)
                return f"Winner of ({top} vs {bottom})"

            return f"  {name_of(n.top)} vs {name_of(n.bottom)}"

        rounds = self.collect_nodes_by_round()

        lines = []
        for rnd in sorted(rounds):
            lines.append(f"Round {rnd.name}:")
            for node in rounds[rnd]:
                lines.append(describe_matchup(node))

        stanley_cup_winner = rounds[Round.STANLEY_CUP_FINALS][0].winner
        if stanley_cup_winner is not None:
            lines.append(f"The {stanley_cup_winner.name} win the stanley cup!")

        return "\n".join(lines)
