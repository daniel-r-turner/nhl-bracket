"""
team.py

Defines the `Team` class representing an NHL team with its seed and conference.
"""


class Team:
    """
    Represents an NHL team.
    """

    def __init__(self, name: str, seed: int, conference: str) -> None:
        """
        Initializes a `Team`.

        :param name: Official team name (e.g., 'Toronto Maple Leafs').
        :param seed: Numeric seed in the conference (1–8).
        :param conference: Conference name ('East' or 'West').
        :returns: None
        """
        self.name = name
        self.seed = seed
        self.conference = conference

    def __repr__(self) -> str:
        """
        Returns a string representation of a team

        :returns: String in the format `<Team {name} (Seed {conference}{seed})>`.
        """
        return f"<Team {self.name} (Seed {self.conference}{self.seed})>"
