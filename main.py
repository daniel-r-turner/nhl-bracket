"""
main.py

Entry point for the NHL playoff bracket application.

This script allows users to:
- Choose between a default 2025 playoff bracket or customize their own.
- Input player brackets and playoff results.
- Score each bracket against the actual outcomes.
- Generate and save visualizations of each bracket.

"""


import copy
from bracket import Bracket
from bracket_node import BracketNode
from league import League
from pathlib import Path
from round import Round
from team import Team
from typing import Dict, List, Set, Tuple


def create_league() -> None:
    """
    Manages the full workflow:
    1. Prompt for team list (custom or default).
    2. Generate an empty bracket and save it.
    3. Collect player brackets.
    4. Prompt for actual playoff results and draw the correct bracket.
    5. Ask for scoring rules and compute league standings.
    6. Create and save each player's bracket with scores.

    :returns: None
    """
    league_name = input("Enter the league name: ")
    teams = prompt_team_list()

    empty_bracket = Bracket.from_team_list(teams, "empty")
    print("\nGenerated Initial Playoff Bracket:\n")
    print(empty_bracket)

    brackets = get_player_brackets(empty_bracket)

    print("---- Enter the results of the playoffs ----")
    correct_bracket = copy.deepcopy(empty_bracket)
    correct_bracket.name = "correct"
    prompt_picks(correct_bracket)

    # Save the correct bracket image
    correct_bracket.draw_bracket(filename="Correct_Bracket.png")

    # Build and score the league
    points_per_round = prompt_points()
    league = League(
        name=league_name,
        points_per_round=points_per_round,
        brackets=brackets,
        correct_bracket=correct_bracket
    )

    league_leaderboard = league.leaderboard()
    # Output standings and save each player's bracket
    print(f"--- {league.name} Scoreboard ---")
    for rank, bracket, score in league_leaderboard:
        print(f"{rank}, {bracket.name} with {score} points")
        bracket.draw_bracket(
            filename=f"{bracket.name}_Bracket.png",
            colour_lines=True,
            league=league
        )
    print(f"Bracket results available at {Path.cwd() / 'bracket_results'}")


def ask_choice(prompt: str, choices: Tuple[str, str]) -> str:
    """
    Prompt the user to choose from a set of allowed options.

    :param prompt: The text to display before the choices.
    :param choices: A tuple of two valid lowercase strings.
    :returns: The user's choice (one of the provided options).
    """
    prompt_str = f"{prompt} ({'/'.join(choices)}): "
    while True:
        response = input(prompt_str).strip().lower()
        if response in choices:
            return response
        print(f"Please choose one of {choices}.")


def load_default_teams() -> List[Team]:
    """
    Return the hard-coded default 2025 playoff teams.

    Each entry is a Team containing:
    - team_name: Name of the team.
    - seed: The team's seed in its conference.
    - conference: 'East' or 'West'.

    :returns: A list of Team instances.
    """
    return [
        Team("Toronto Maple Leafs",  1, "East"),
        Team("Tampa Bay Lightning",  2, "East"),
        Team("Washington Capitals",  3, "East"),
        Team("Carolina Hurricanes",  4, "East"),
        Team("New Jersey Devils",    5, "East"),
        Team("Montreal Canadiens",   6, "East"),
        Team("Florida Panthers",     7, "East"),
        Team("Ottawa Senators",      8, "East"),
        Team("Winnipeg Jets",        1, "West"),
        Team("Dallas Stars",         2, "West"),
        Team("Vegas Golden Knights", 3, "West"),
        Team("Los Angeles Kings",    4, "West"),
        Team("Edmonton Oilers",      5, "West"),
        Team("Minnesota Wild",       6, "West"),
        Team("Colorado Avalanche",   7, "West"),
        Team("St Louis Blues",       8, "West"),
    ]


def prompt_custom_teams() -> List[Team]:
    """
    Prompt the user to enter each seed for both conferences.

    Validates entered team names against available logo filenames.

    :returns: A list of Team instances.
    """
    logo_directory = "team_logos"
    valid = set(f.stem.replace('_', ' ') for f in Path(logo_directory).iterdir())

    teams: List[Team] = []
    for conf in ("East", "West"):
        for seed in range(1, 9):
            while True:
                name = input(
                    f"Enter seed {seed} of the {conf}ern Conference: "
                ).strip().title()
                if name in valid:
                    teams.append(Team(name, seed, conf))
                    valid.remove(name)
                    break
                print(f"Invalid or duplicated name. Choose from: {', '.join(valid)}")
    return teams

def prompt_team_list() -> List[Team]:
    """
    Decide whether to load default teams or prompt for custom ones.

    :returns: A list of Team instances.
    """
    choice = ask_choice(
        "Customize bracket or use default 2025 playoffs?",
        ("custom", "default")
    )
    return (
        prompt_custom_teams()
        if choice == "custom"
        else load_default_teams()
    )


def get_player_brackets(empty_bracket: Bracket) -> List[Bracket]:
    """
    Collects bracket predictions from multiple players.

    :param empty_bracket: A Bracket instance with no winners set.
    :returns: A list of Bracket instances populated with each player's picks.
    """
    while True:
        try:
            num_brackets = int(
                input("Enter the number of players in the Fantasy League: ")
            )
            if num_brackets > 0:
                break
        except ValueError:
            pass
        print("The number of players in the league must be a positive integer! Try again")
    names: Set[str] = set()
    brackets: List[Bracket] = []

    for bracket_num in range(num_brackets):
        while True:
            player_name = input(
                f"Player {bracket_num + 1} Name: "
            ).strip()
            if player_name and player_name not in names:
                names.add(player_name)
                break
            print("Player names must be non-empty and unique!")

        bracket = copy.deepcopy(empty_bracket)
        bracket.name = player_name
        print(f"---- Picks for {bracket.name} ----")
        prompt_picks(bracket)
        brackets.append(bracket)

    return brackets


def prompt_pick(node: BracketNode) -> Team:
    """
    Ask the user to choose a winner for a single matchup.

    Continues prompting until a valid choice ('A' or 'B') is made.

    :param node: A BracketNode representing the matchup.
    :returns: The chosen Team instance.
    """
    while node.winner is None:
        team_a = node.top if isinstance(node.top, Team) else node.top.winner
        team_b = node.bottom if isinstance(node.bottom, Team) else node.bottom.winner

        choice = input(f"Winner of {team_a.name} (A) vs {team_b.name} (B)?: ").strip().upper()
        if choice == "A":
            node.set_winner(team_a)
        elif choice == "B":
            node.set_winner(team_b)
        else:
            print(
                f"Error: enter 'A' for {team_a.name} or 'B' for {team_b.name}."
            )
    return node.winner


def prompt_picks(bracket: Bracket) -> None:
    """
    Walk through each round of the bracket and collect winners from the user.

    :param bracket: A Bracket instance whose nodes will be populated with winners.
    :returns: None
    """
    rounds = bracket.collect_nodes_by_round()
    for rnd in sorted(rounds):
        for node in rounds[rnd]:
            prompt_pick(node)


def prompt_points() -> Dict[Round, int]:
    """
    Ask the user for point values for each playoff round.

    :returns: A mapping from Round enum to an integer point value for correct guesses in that Round.
    """
    points_prompt = "Enter the number of points awarded for a correct guess in the"
    round_order = [
        Round.FIRST_ROUND,
        Round.SECOND_ROUND,
        Round.CONFERENCE_FINALS,
        Round.STANLEY_CUP_FINALS
    ]
    results = {}
    for rnd in round_order:
        while True:
            try:
                value = int(input(f"{points_prompt} {rnd.name.replace('_', ' ').title()}: "))
                results[rnd] = value
                break
            except ValueError:
                print("Invalid input. Please enter a valid integer.")
    return results


if __name__ == "__main__":
    create_league()
