"""
This module contains the DrawsIndex class.
"""

from typing import List, Tuple
from ripper.models.match import Match
from ripper.indices.base import BaseIndex
from ripper.utils import list_team_names


class DrawsIndex(BaseIndex[int]):
    """
    Calculate the number of draws for each team
    """

    def calculate(self, matches: List[Match]) -> List[Tuple[int, str, int]]:
        """
        Calculate the number of draws for each team
        :param matches:
        :return:
        """
        team_draws = {team_name: 0 for team_name in list_team_names(matches)}

        # Calculate Team Draws
        for match in matches:
            if match.is_draw():
                team_draws[match.home_team] += 1
                team_draws[match.away_team] += 1

        # Sort the results
        sorted_results = sorted(team_draws.items(), key=lambda x: (x[2], x[1]))

        # Update the first element in the tuple after sorting
        result = [
            (i + 1, team, draws) for i, (team, draws) in enumerate(team_draws.items())
        ]

        return result
