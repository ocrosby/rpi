"""
This module contains the WinsIndex class.
"""

from typing import List, Tuple
from ripper.models.match import Match
from ripper.indices.base import BaseIndex
from ripper.utils import list_team_names


class WinsIndex(BaseIndex[int]):
    """
    Calculate the number of wins for each team
    """

    def calculate(self, matches: List[Match]) -> List[Tuple[int, str, int]]:
        # Initialize Team Wins
        team_wins = {team_name: 0 for team_name in list_team_names(matches)}

        # Calculate Team Wins
        for match in matches:
            team_wins[match.winner()] += 1

        result = [
            (i + 1, team, wins) for i, (team, wins) in enumerate(team_wins.items())
        ]

        return sorted(result, key=lambda x: (-x[2], x[1]))
